"""Carrot Quest MCP client implementation."""
from typing import Any, Dict, List, Optional, cast

from mcp import ClientSession
from mcp.client.sse import sse_client

from src.core.logger import LoggerService
from src.core.settings import Settings
from src.mcp_clients.carrot_quest.models import Conversation, Message, User


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

    # Apps Tools
    async def get_active_users(
        self, app_id: str, paginate_position: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get online users on the site."""
        result = await self.session.call_tool(
            "get_active_users",
            arguments={"app_id": app_id, "paginate_position": paginate_position},
        )
        return cast(Dict[str, Any], result)

    async def get_app_conversations(
        self,
        app_id: str,
        tags: List[str],
        limit: int = 10,
    ) -> Dict[str, List[Conversation]]:
        """Get conversations from the app.

        Args:
            app_id: App ID
            tags: List of conversation tags
            limit: Maximum number of conversations to return

        Returns:
            Dict containing conversations
        """
        result = await self.session.call_tool(
            "get_app_conversations",
            arguments={
                "app_id": app_id,
                "tags": tags,
                "limit": limit,
            },
        )
        return cast(Dict[str, List[Conversation]], result)

    async def get_app_users(
        self,
        app_id: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_prop: str = "$last_seen",
        sort_order: str = "desc",
        offset: int = 0,
        limit: int = 20,
    ) -> Dict[str, List[User]]:
        """Get users (leads) from the app."""
        result = await self.session.call_tool(
            "get_app_users",
            arguments={
                "app_id": app_id,
                "filters": filters,
                "sort_prop": sort_prop,
                "sort_order": sort_order,
                "offset": offset,
                "limit": limit,
            },
        )
        return cast(Dict[str, List[User]], result)

    # Conversations Tools
    async def get_conversation(self, conversation_id: str) -> Conversation:
        """Get conversation by ID."""
        result = await self.session.call_tool(
            "get_conversation", arguments={"conversation_id": conversation_id}
        )
        return Conversation(**result)

    async def reply_to_conversation(
        self,
        conversation_id: str,
        body: str,
        from_admin: str = "default_admin",
        type_: str = "reply_admin",
        **kwargs: Dict[str, Any],
    ) -> Message:
        """Reply to a conversation."""
        result = await self.session.call_tool(
            "reply_to_conversation",
            arguments={
                "conversation_id": conversation_id,
                "body": body,
                "from_admin": from_admin,
                "type_": type_,
                **kwargs,
            },
        )
        return Message(**result)

    async def set_typing(
        self, conversation_id: str, body: str, from_admin: str = "default_admin"
    ) -> Dict[str, Any]:
        """Set typing status in conversation."""
        result = await self.session.call_tool(
            "set_typing",
            arguments={
                "conversation_id": conversation_id,
                "body": body,
                "from_admin": from_admin,
            },
        )
        return cast(Dict[str, Any], result)

    # Users Tools
    async def get_user(
        self,
        user_id: str,
        by_user_id: bool = False,
        props: bool = True,
        props_custom: bool = False,
        **kwargs: Dict[str, Any],
    ) -> User:
        """Get user data by ID."""
        result = await self.session.call_tool(
            "get_user",
            arguments={
                "user_id": user_id,
                "by_user_id": by_user_id,
                "props": props,
                "props_custom": props_custom,
                **kwargs,
            },
        )
        return User(**result)

    async def set_user_props(
        self,
        user_id: str,
        operations: List[Dict[str, Any]],
        by_user_id: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Set user properties."""
        result = await self.session.call_tool(
            "set_user_props",
            arguments={
                "user_id": user_id,
                "operations": operations,
                "by_user_id": by_user_id,
                **kwargs,
            },
        )
        return cast(Dict[str, Any], result)

    async def record_user_event(
        self,
        user_id: str,
        event: str,
        params: Optional[Dict[str, Any]] = None,
        by_user_id: bool = False,
        **kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Record user event."""
        result = await self.session.call_tool(
            "record_user_event",
            arguments={
                "user_id": user_id,
                "event": event,
                "params": params,
                "by_user_id": by_user_id,
                **kwargs,
            },
        )
        return cast(Dict[str, Any], result)
