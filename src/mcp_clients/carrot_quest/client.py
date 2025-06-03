"""Carrot Quest MCP client implementation."""
from typing import Any, Dict, Optional

from core.logger import LoggerService
from core.settings import Settings
from mcp import ClientSession
from mcp.client.sse import sse_client


class CarrotQuestMCPClient:
    """Client for Carrot Quest MCP server."""

    def __init__(
        self,
        logger: LoggerService,
        settings: Settings,
        server_url: Optional[str] = None,
    ):
        """Initialize client.

        Args:
            logger: Logger service instance
            settings: Application settings
            server_url: Optional URL of the Carrot Quest MCP server
        """
        self.logger = logger.get_logger(__name__)
        self.settings = settings
        self.server_url = server_url or settings.CARROT_QUEST_MCP_URL
        self._session: Optional[ClientSession] = None

    async def __aenter__(self) -> "CarrotQuestMCPClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self) -> None:
        """Connect to MCP server using SSE."""
        if self._session is None:
            async with sse_client(self.server_url) as (read, write):
                self._session = ClientSession(read, write)
                await self._session.initialize()

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> ClientSession:
        """Get current session."""
        if self._session is None:
            raise RuntimeError(
                "Client is not connected. Use 'async with' or call connect()"
            )
        return self._session

    async def list_tools(self) -> Dict[str, Any]:
        """Get list of available tools from the MCP server.

        This method queries the MCP server for all available tools and their schemas.
        Use this to verify that the client supports all server methods or to
        dynamically discover available functionality.

        Returns:
            Dictionary containing tool names and their schemas
        """
        return await self.session.list_tools()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Invoke a tool provided by the MCP server.

        This method calls a specific tool on the MCP server with the provided arguments.
        The tool must be available on the server (check with list_tools).

        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            The result of the tool execution

        Raises:
            RuntimeError: If the client is not connected
            ValueError: If the tool is not found
            Exception: If there's an error executing the tool
        """
        return await self.session.call_tool(tool_name, arguments=arguments)
