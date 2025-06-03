"""Dreamer: Main runtime for PocketFlow-based agent execution."""

from typing import Any, Dict, Optional, Union

from pocketflow import AsyncNode, Node

from src.llm.assistant_client import AssistantClient

from ..reasoning_cache import ReasoningCache
from .flow import add_agent_to_flow, create_dreamer_flow


class DreamerRuntime:
    """Manages the construction and execution of the PocketFlow agent graph.

    Responsible for building and executing the agent graph based on LLM plans,
    managing agent nodes, and collecting results.
    """

    def __init__(
        self, assistant_client: AssistantClient, reasoning_cache: ReasoningCache
    ):
        """Initialize the DreamerRuntime.

        Args:
            assistant_client: Client for interacting with the OpenAI Assistant API
            reasoning_cache: Cache for storing reasoning steps and results
        """
        self.reasoning_cache = reasoning_cache
        self.assistant_client = assistant_client
        self.nodes = {}
        self.flow = create_dreamer_flow(reasoning_cache, assistant_client, self)

    async def build_graph(self, plan: Dict[str, Any]) -> None:
        """Build the agent graph from the LLM plan specification.

        Args:
            plan: Plan specification with root agent information
        """
        # Reset the flow
        self.reset()

        # Create the initial agent from the plan
        root_agent_id = plan.get("root_agent_id", "root")
        root_task = plan.get("root_task", "")

        # Add the root agent
        self.add_agent(root_agent_id, root_task)

        # Set the root agent as the entrypoint
        self.set_entrypoint(root_agent_id)

    async def run(self, shared: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the agent graph, possibly in parallel.

        Args:
            shared: Initial shared state dictionary

        Returns:
            Dictionary with aggregated results from all agents
        """
        if shared is None:
            shared = {}

        # Run the flow
        await self.flow.run_async(shared)

        # Collect and aggregate results from all nodes
        results = {}
        for node_id in self.nodes:
            if node_id != "agent_creator" and await self.reasoning_cache.is_done(
                node_id
            ):
                results[node_id] = await self.reasoning_cache.get_last_state(node_id)

        return results

    def add_agent(self, agent_id: str, task: str) -> str:
        """Add an agent node to the graph.

        Args:
            agent_id: Unique identifier for the agent
            task: The task this agent needs to accomplish

        Returns:
            The agent ID
        """
        add_agent_to_flow(
            flow=self.flow,
            agent_id=agent_id,
            task=task,
            reasoning_cache=self.reasoning_cache,
            assistant_client=self.assistant_client,
        )

        # Keep track of the node
        self.nodes[agent_id] = True

        return agent_id

    def add_node(self, node_id: str, node: Union[AsyncNode, Node]) -> None:
        """Add a node to the agent graph.

        Args:
            node_id: Unique identifier for the node
            node: The node to add
        """
        self.nodes[node_id] = True
        self.flow.add_node(node_id, node)

    def connect(self, from_id: str, to_id: str, action: str = "default") -> None:
        """Connect two nodes in the agent graph with an action-based transition.

        Args:
            from_id: Source node ID
            to_id: Target node ID
            action: Action string for the transition
        """
        self.flow.connect(from_id, to_id, action)

    def set_entrypoint(self, node_id: str) -> None:
        """Set the entrypoint (start node) for the agent graph.

        Args:
            node_id: ID of the node to set as entrypoint
        """
        self.flow.set_entrypoint(node_id)

    def reset(self) -> None:
        """Reset the agent graph to an empty state."""
        # Create a new flow
        self.flow = create_dreamer_flow(
            self.reasoning_cache, self.assistant_client, self
        )

        # Reset nodes tracking
        self.nodes = {"agent_creator": True}
