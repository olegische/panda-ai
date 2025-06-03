"""Dreamer: Node definitions for PocketFlow-based agent execution."""

import asyncio
from typing import Any, Dict, List, Optional

from pocketflow import AsyncNode, Node

from src.llm.assistant_client import AssistantClient

from ..reasoning_cache import ReasoningCache


class DreamerAgentNode(AsyncNode):
    """Base agent node for Dreamer runtime.

    Each LLM-created agent becomes one of these nodes, responsible for executing
    a specific task using the OpenAI Assistant API.
    """

    def __init__(
        self,
        agent_id: str,
        task: str,
        reasoning_cache: ReasoningCache,
        assistant_client: AssistantClient,
        max_retries: int = 3,
        wait: int = 2,
    ):
        """Initialize a DreamerAgentNode.

        Args:
            agent_id: Unique identifier for this agent
            task: The task this agent needs to accomplish
            reasoning_cache: Cache for storing reasoning steps and results
            assistant_client: Client for interacting with the OpenAI Assistant API
            max_retries: Maximum number of retries for failed executions
            wait: Wait time in seconds between retries
        """
        super().__init__(max_retries=max_retries, wait=wait)
        self.agent_id = agent_id
        self.task = task
        self.cache = reasoning_cache
        self.assistant_client = assistant_client

    async def prep_async(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for agent execution, checking cache first.

        Args:
            shared: Shared state dictionary

        Returns:
            Dictionary with task information or cached result
        """
        # Check cache if this agent was already executed
        if await self.cache.is_done(self.agent_id):
            return {
                "cached": True,
                "result": await self.cache.get_last_state(self.agent_id),
            }

        # Read messages or inputs from shared (either from parent or message queues)
        return {"cached": False, "task": self.task, "shared": shared}

    async def exec_async(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent using Assistant API.

        Args:
            prep_res: Result from prep_async

        Returns:
            Dictionary with execution results and tool calls
        """
        if prep_res["cached"]:
            return prep_res["result"]

        # Create/use thread for this agent
        thread_id = self.assistant_client.create_thread()
        self.assistant_client.send_user_message(thread_id, prep_res["task"])
        run_id = self.assistant_client.start_run(thread_id)

        # Poll until complete or requires action
        run_status = await asyncio.to_thread(
            self.assistant_client.poll_run_status, thread_id, run_id
        )

        # Check for tool_calls (potentially to create more agents)
        tool_calls = self.assistant_client.get_tool_calls(run_id)

        # Get final response
        result = self.assistant_client.get_final_result(thread_id)

        return {
            "result": result,
            "tool_calls": tool_calls,
            "thread_id": thread_id,
            "run_id": run_id,
        }

    async def post_async(
        self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]
    ) -> str:
        """Process execution results and determine next action.

        Args:
            shared: Shared state dictionary
            prep_res: Result from prep_async
            exec_res: Result from exec_async

        Returns:
            Action string for flow control
        """
        # Store result in cache
        await self.cache.log_step(self.agent_id, {"result": exec_res["result"]})

        # Store result in shared state
        shared[f"agent_result_{self.agent_id}"] = exec_res["result"]

        # If agent created more agents, they need to be created and connected
        if "tool_calls" in exec_res and exec_res["tool_calls"]:
            shared["tool_calls"] = exec_res["tool_calls"]
            shared["parent_agent_id"] = self.agent_id
            return "created_agents"

        # Mark this agent as done
        await self.cache.mark_done(self.agent_id)
        return "complete"


class AgentCreatorNode(AsyncNode):
    """Node that dynamically creates new agent nodes based on tool_calls.

    Responsible for processing tool calls from agents and creating new agent nodes
    in the runtime.
    """

    def __init__(self, runtime: "DreamerRuntime"):
        """Initialize the AgentCreatorNode.

        Args:
            runtime: Reference to the DreamerRuntime for adding nodes
        """
        super().__init__()
        self.runtime = runtime

    async def prep_async(self, shared: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepare for agent creation by checking for tool_calls.

        Args:
            shared: Shared state dictionary

        Returns:
            Tool calls information or None if no tool calls
        """
        if "tool_calls" not in shared:
            return None

        return {
            "tool_calls": shared["tool_calls"],
            "parent_agent_id": shared.get("parent_agent_id"),
        }

    async def exec_async(
        self, prep_res: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process tool calls to create new agents.

        Args:
            prep_res: Result from prep_async

        Returns:
            List of created agent information
        """
        if not prep_res:
            return []

        created_agents = []

        for tool_call in prep_res["tool_calls"]:
            if tool_call["function"]["name"] == "create_agent":
                args = tool_call["function"]["arguments"]
                agent_name = args.get("name", "unnamed_agent")
                agent_goal = args.get("goal", "")

                # Create a unique agent ID
                agent_id = f"{agent_name}_{len(self.runtime.nodes)}"

                # Create the new agent
                self.runtime.add_agent(agent_id, agent_goal)

                # Connect to parent if available
                if prep_res["parent_agent_id"]:
                    self.runtime.connect(
                        prep_res["parent_agent_id"], agent_id, "created_agents"
                    )

                created_agents.append(
                    {"agent_id": agent_id, "name": agent_name, "goal": agent_goal}
                )

        return created_agents

    async def post_async(
        self,
        shared: Dict[str, Any],
        prep_res: Optional[Dict[str, Any]],
        exec_res: List[Dict[str, Any]],
    ) -> str:
        """Update shared state with created agents and determine next action.

        Args:
            shared: Shared state dictionary
            prep_res: Result from prep_async
            exec_res: Result from exec_async

        Returns:
            Action string for flow control
        """
        # Clear tool_calls to prevent reprocessing
        if "tool_calls" in shared:
            del shared["tool_calls"]

        if "parent_agent_id" in shared:
            del shared["parent_agent_id"]

        # Store created agents in shared state
        shared["created_agents"] = exec_res

        return "continue"
