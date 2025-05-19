"""MCPClient: Interface for interacting with MCP servers and tools."""

from typing import Any, Dict, Optional


class MCPClient:
    """
    Provides access to MCP servers, tools, and resources for Dreamer agents.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP client with configuration (e.g., server registry).
        """
        pass

    def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """
        Invoke a tool provided by an MCP server.
        """
        pass

    def access_resource(self, server_name: str, uri: str) -> Any:
        """
        Access a resource provided by an MCP server.
        """
        pass

    def register_server(self, server_name: str, server_info: Dict[str, Any]) -> None:
        """
        Register a new MCP server for use.
        """
        pass

    def list_servers(self) -> Dict[str, Any]:
        """
        List all registered MCP servers.
        """
        pass

    def list_tools(self, server_name: str) -> Dict[str, Any]:
        """
        List all tools available on a given MCP server.
        """
        pass
