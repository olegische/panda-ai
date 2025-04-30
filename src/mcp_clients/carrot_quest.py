"""Carrot Quest MCP client implementation."""
from typing import Optional, Dict, Any
from mcp import ClientSession, types
from mcp.client.sse import sse_client


class CarrotQuestMCPClient:
    """Client for Carrot Quest MCP server."""

    def __init__(self, server_url: str):
        """Initialize client.
        
        Args:
            server_url: URL of the Carrot Quest MCP server
        """
        self.server_url = server_url
        self._session: Optional[ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self):
        """Connect to MCP server using SSE."""
        if self._session is None:
            async with sse_client(self.server_url) as (read, write):
                self._session = ClientSession(read, write)
                await self._session.initialize()

    async def disconnect(self):
        """Disconnect from MCP server."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> ClientSession:
        """Get current session."""
        if self._session is None:
            raise RuntimeError("Client is not connected. Use 'async with' or call connect()")
        return self._session

    # Apps Tools
    async def get_active_users(self, app_id: str, paginate_position: Optional[str] = None) -> Dict[str, Any]:
        """Get online users on the site."""
        return await self.session.call_tool(
            "get_active_users",
            arguments={
                "app_id": app_id,
                "paginate_position": paginate_position
            }
        )

    async def get_app_users(
        self, 
        app_id: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_prop: str = "$last_seen",
        sort_order: str = "desc",
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get users (leads) from the app."""
        return await self.session.call_tool(
            "get_app_users",
            arguments={
                "app_id": app_id,
                "filters": filters,
                "sort_prop": sort_prop,
                "sort_order": sort_order,
                "offset": offset,
                "limit": limit
            }
        )

    # Conversations Tools
    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation by ID."""
        return await self.session.call_tool(
            "get_conversation",
            arguments={"conversation_id": conversation_id}
        )

    async def reply_to_conversation(
        self,
        conversation_id: str,
        body: str,
        from_admin: str = "default_admin",
        type_: str = "reply_admin",
        **kwargs
    ) -> Dict[str, Any]:
        """Reply to a conversation."""
        return await self.session.call_tool(
            "reply_to_conversation",
            arguments={
                "conversation_id": conversation_id,
                "body": body,
                "from_admin": from_admin,
                "type_": type_,
                **kwargs
            }
        )

    async def set_typing(
        self,
        conversation_id: str,
        body: str,
        from_admin: str = "default_admin"
    ) -> Dict[str, Any]:
        """Set typing status in conversation."""
        return await self.session.call_tool(
            "set_typing",
            arguments={
                "conversation_id": conversation_id,
                "body": body,
                "from_admin": from_admin
            }
        )

    # Users Tools
    async def get_user(
        self,
        user_id: str,
        by_user_id: bool = False,
        props: bool = True,
        props_custom: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Get user data by ID."""
        return await self.session.call_tool(
            "get_user",
            arguments={
                "user_id": user_id,
                "by_user_id": by_user_id,
                "props": props,
                "props_custom": props_custom,
                **kwargs
            }
        )

    async def set_user_props(
        self,
        user_id: str,
        operations: list,
        by_user_id: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Set user properties."""
        return await self.session.call_tool(
            "set_user_props",
            arguments={
                "user_id": user_id,
                "operations": operations,
                "by_user_id": by_user_id,
                **kwargs
            }
        )

    async def record_user_event(
        self,
        user_id: str,
        event: str,
        params: Optional[Dict[str, Any]] = None,
        by_user_id: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Record user event."""
        return await self.session.call_tool(
            "record_user_event",
            arguments={
                "user_id": user_id,
                "event": event,
                "params": params,
                "by_user_id": by_user_id,
                **kwargs
            }
        )
