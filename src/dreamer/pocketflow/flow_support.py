"""Support agent flow for Dreamer PocketFlow architecture."""

from pocketflow import AsyncFlow

from src.dreamer.pocketflow.nodes_support import (
    AskMoreNode,
    AssignAdminNode,
    ReplyNode,
    SupportAgentNode,
)
from src.llm.assistant_client import AssistantClient
from src.mcp_clients.carrot_quest.client import CarrotQuestClient


def create_support_flow(
    assistant_client: AssistantClient, cq_client: CarrotQuestClient
) -> AsyncFlow:
    """Create action-based support flow with LLM-driven branching."""
    support_agent = SupportAgentNode(assistant_client, cq_client)
    reply_node = ReplyNode()
    assign_admin_node = AssignAdminNode()
    ask_more_node = AskMoreNode()

    # Action-based transitions
    support_agent - "reply" >> reply_node
    support_agent - "assign_admin" >> assign_admin_node
    support_agent - "ask_more" >> ask_more_node

    # Можно добавить финальный узел, если нужно
    # reply_node >> done_node
    # assign_admin_node >> done_node
    # ask_more_node >> done_node

    return AsyncFlow(start=support_agent)
