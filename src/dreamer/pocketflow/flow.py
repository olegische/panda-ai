"""Dreamer: Flow creation and configuration for PocketFlow-based agent execution."""

from typing import Optional

from pocketflow import AsyncFlow

from src.llm.assistant_client import AssistantClient

from ..reasoning_cache import ReasoningCache
from .nodes import AgentCreatorNode, DreamerAgentNode
from .runtime import DreamerRuntime


class DreamerFlowFactory:
    """Factory class for creating and configuring PocketFlow-based agent execution flows."""

    def __init__(
        self,
        reasoning_cache: ReasoningCache,
        assistant_client: AssistantClient,
        runtime: DreamerRuntime,
    ) -> None:
        """Initialize the DreamerFlowFactory with required dependencies.

        Args:
            reasoning_cache: Cache for storing reasoning steps and results
            assistant_client: Client for interacting with the OpenAI Assistant API
            runtime: Reference to the DreamerRuntime for adding nodes
        """
        self.reasoning_cache = reasoning_cache
        self.assistant_client = assistant_client
        self.runtime = runtime

    def create_dreamer_flow(self) -> AsyncFlow:
        """Create and configure the Dreamer agent flow.

        Returns:
            Configured AsyncFlow for Dreamer agent execution
        """
        # Create the agent creator node
        agent_creator = AgentCreatorNode(self.runtime)

        # Connect agent creator back to itself for handling nested agent creation
        agent_creator - "continue" >> agent_creator

        # Create the flow with the start node
        flow = AsyncFlow(start=agent_creator)

        # Store the agent creator node for later reference
        flow.agent_creator = agent_creator

        return flow

    def add_agent_to_flow(
        self,
        flow: AsyncFlow,
        agent_id: str,
        task: str,
        parent_id: Optional[str] = None,
        action: str = "created_agents",
    ) -> None:
        """Add an agent node to the flow and connect it to its parent if specified.

        Args:
            flow: The AsyncFlow to add the agent to
            agent_id: Unique identifier for the agent
            task: The task this agent needs to accomplish
            parent_id: Optional parent agent ID to connect from
            action: Action string for the transition from parent to this agent
        """
        # Create the agent node
        agent = DreamerAgentNode(
            agent_id=agent_id,
            task=task,
            reasoning_cache=self.reasoning_cache,
            assistant_client=self.assistant_client,
        )

        # Connect the agent to the agent creator
        agent - "created_agents" >> flow.agent_creator

        # Connect from parent if specified
        if parent_id and parent_id in flow.nodes:
            parent_node = flow.nodes[parent_id]
            parent_node - action >> agent

        # Add the agent to the flow's nodes dictionary for future reference
        if not hasattr(flow, "nodes"):
            flow.nodes = {}
        flow.nodes[agent_id] = agent
