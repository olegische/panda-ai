"""Agentic flow for OpenAI MCP agent (PocketFlow, MCP-style, per pocketflow-mcp example)."""

from pocketflow import Flow

from src.dreamer.pocketflow.openai_agent.nodes import (
    DecideToolNode,
    ExecuteToolNode,
    GetToolsNode,
)


def create_openai_mcp_agent_flow() -> Flow:
    """Create and connect nodes to form a complete OpenAI MCP agent flow.

    Returns:
        Flow: A complete agentic flow for OpenAI MCP tools.
    """
    get_tools_node = GetToolsNode()
    decide_node = DecideToolNode()
    execute_node = ExecuteToolNode()

    get_tools_node - "decide" >> decide_node
    decide_node - "execute" >> execute_node

    return Flow(start=get_tools_node)
