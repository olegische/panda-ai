"""Carrot Quest MCP client implementation."""
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.sse import sse_client

from core.logger import LoggerService
from core.settings import Settings

from .models.apps import (
    ActiveUsersResponse,
    AppChannelsResponse,
    AppConversationsResponse,
    AppUsersResponse,
)
from .models.conversations import (
    ConversationAssignResponse,
    ConversationReplyResponse,
    ConversationTagResponse,
    EmptyResponse,
    GetConversationPartsResponse,
    GetConversationResponse,
)
from .models.users import (
    GetUserConversationsResponse,
    GetUserEventsResponse,
    GetUserResponse,
    RecordUserEventResponse,
    SendMessageResponse,
    SetPresenceResponse,
    SetUserPropsResponse,
    StartConversationResponse,
    UnsubscribeEmailResponse,
)


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

    # -------------------------------------------------------------------------
    # Apps Tools
    # -------------------------------------------------------------------------
    async def get_active_users(
        self, app_id: str, paginate_position: Optional[str] = None
    ) -> ActiveUsersResponse:
        """Get online users on the site."""
        result = await self.session.call_tool(
            "get_active_users",
            arguments={"app_id": app_id, "paginate_position": paginate_position},
        )
        return ActiveUsersResponse(**result)

    async def get_app_conversations(
        self,
        app_id: str,
        tags: List[str],
        limit: int = 10,
    ) -> AppConversationsResponse:
        """Get conversations from the app.

        Args:
            app_id: App ID
            tags: List of conversation tags
            limit: Maximum number of conversations to return

        Returns:
            Response containing conversations list and metadata
        """
        result = await self.session.call_tool(
            "get_app_conversations",
            arguments={
                "app_id": app_id,
                "tags": tags,
                "limit": limit,
            },
        )
        return AppConversationsResponse(**result)

    async def get_app_users(
        self,
        app_id: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_prop: str = "$last_seen",
        sort_order: str = "desc",
        offset: int = 0,
        limit: int = 20,
    ) -> AppUsersResponse:
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
        return AppUsersResponse(**result)

    async def get_app_channels(self, app_id: str) -> AppChannelsResponse:
        """Get list of channels for the app."""
        result = await self.session.call_tool(
            "get_app_channels",
            arguments={"app_id": app_id},
        )
        return AppChannelsResponse(**result)

    # -------------------------------------------------------------------------
    # Conversations Tools
    # -------------------------------------------------------------------------
    async def get_conversation(self, conversation_id: str) -> GetConversationResponse:
        """Get conversation by ID."""
        result = await self.session.call_tool(
            "get_conversation", arguments={"conversation_id": conversation_id}
        )
        return GetConversationResponse(**result)

    async def reply_to_conversation(
        self,
        conversation_id: str,
        body: str,
        from_admin: str = "default_admin",
        type_: str = "reply_admin",
        **kwargs: Dict[str, Any],
    ) -> ConversationReplyResponse:
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
        return ConversationReplyResponse(**result)

    async def set_typing(
        self, conversation_id: str, body: str, from_admin: str = "default_admin"
    ) -> EmptyResponse:
        """Set typing status in conversation."""
        result = await self.session.call_tool(
            "set_typing",
            arguments={
                "conversation_id": conversation_id,
                "body": body,
                "from_admin": from_admin,
            },
        )
        return EmptyResponse(**result)

    async def get_conversation_parts(
        self,
        conversation_id: str,
        paginate_position: Optional[List[int]] = None,
    ) -> GetConversationPartsResponse:
        """Get conversation parts (messages)."""
        result = await self.session.call_tool(
            "get_conversation_parts",
            arguments={
                "conversation_id": conversation_id,
                "paginate_position": paginate_position,
            },
        )
        return GetConversationPartsResponse(**result)

    async def assign_conversation(
        self,
        conversation_id: str,
        admin: Optional[int] = None,
        from_admin: str = "default_admin",
        random_id: Optional[int] = None,
    ) -> ConversationAssignResponse:
        """Assign conversation to an admin."""
        result = await self.session.call_tool(
            "assign_conversation",
            arguments={
                "conversation_id": conversation_id,
                "admin": admin,
                "from_admin": from_admin,
                "random_id": random_id,
            },
        )
        return ConversationAssignResponse(**result)

    async def add_conversation_tag(
        self,
        conversation_id: str,
        tag: str,
        from_admin: str = "default_admin",
        random_id: Optional[int] = None,
    ) -> ConversationTagResponse:
        """Add a tag to a conversation."""
        result = await self.session.call_tool(
            "add_conversation_tag",
            arguments={
                "conversation_id": conversation_id,
                "tag": tag,
                "from_admin": from_admin,
                "random_id": random_id,
            },
        )
        return ConversationTagResponse(**result)

    async def delete_conversation_tag(
        self,
        conversation_id: str,
        tag: str,
        from_admin: str = "default_admin",
        random_id: Optional[int] = None,
    ) -> ConversationTagResponse:
        """Delete a tag from a conversation."""
        result = await self.session.call_tool(
            "delete_conversation_tag",
            arguments={
                "conversation_id": conversation_id,
                "tag": tag,
                "from_admin": from_admin,
                "random_id": random_id,
            },
        )
        return ConversationTagResponse(**result)

    async def close_conversation(
        self,
        conversation_id: str,
        from_admin: str = "default_admin",
        random_id: Optional[int] = None,
    ) -> EmptyResponse:
        """Close a conversation."""
        result = await self.session.call_tool(
            "close_conversation",
            arguments={
                "conversation_id": conversation_id,
                "from_admin": from_admin,
                "random_id": random_id,
            },
        )
        return EmptyResponse(**result)

    # -------------------------------------------------------------------------
    # Users Tools
    # -------------------------------------------------------------------------
    async def get_user(
        self,
        user_id: str,
        by_user_id: bool = False,
        props: bool = True,
        props_custom: bool = False,
        **kwargs: Dict[str, Any],
    ) -> GetUserResponse:
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
        return GetUserResponse(**result)

    async def set_user_props(
        self,
        user_id: str,
        operations: List[Dict[str, Any]],
        by_user_id: bool = False,
        **kwargs: Dict[str, Any],
    ) -> SetUserPropsResponse:
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
        return SetUserPropsResponse(**result)

    async def get_user_events(
        self,
        user_id: str,
        by_user_id: bool = False,
        filter_name: Optional[str] = None,
        props_as_string: bool = False,
        paginate_position: Optional[List[int]] = None,
        app: Optional[int] = None,
    ) -> GetUserEventsResponse:
        """Get user events."""
        result = await self.session.call_tool(
            "get_user_events",
            arguments={
                "user_id": user_id,
                "by_user_id": by_user_id,
                "filter_name": filter_name,
                "props_as_string": props_as_string,
                "paginate_position": paginate_position,
                "app": app,
            },
        )
        return GetUserEventsResponse(**result)

    async def get_user_conversations(
        self,
        user_id: str,
        by_user_id: bool = False,
        with_user_replies_only: bool = False,
        recipient_type: str = "web",
        paginate_after: Optional[float] = None,
        app: Optional[int] = None,
    ) -> GetUserConversationsResponse:
        """Get user conversations."""
        result = await self.session.call_tool(
            "get_user_conversations",
            arguments={
                "user_id": user_id,
                "by_user_id": by_user_id,
                "with_user_replies_only": with_user_replies_only,
                "recipient_type": recipient_type,
                "paginate_after": paginate_after,
                "app": app,
            },
        )
        return GetUserConversationsResponse(**result)

    async def send_message(
        self,
        user_id: str,
        body: str,
        type_: str = "popup_chat",
        by_user_id: bool = False,
        app: Optional[int] = None,
    ) -> SendMessageResponse:
        """Send message to user."""
        result = await self.session.call_tool(
            "send_message",
            arguments={
                "user_id": user_id,
                "body": body,
                "type_": type_,
                "by_user_id": by_user_id,
                "app": app,
            },
        )
        return SendMessageResponse(**result)

    async def start_conversation(
        self,
        user_id: str,
        body: Optional[str] = None,
        attachment: Optional[bytes] = None,
        attachment_file_name: Optional[str] = None,
        random_id: Optional[int] = None,
        referrer: Optional[str] = None,
        by_user_id: bool = False,
        app: Optional[int] = None,
    ) -> StartConversationResponse:
        """Start conversation as user."""
        result = await self.session.call_tool(
            "start_conversation",
            arguments={
                "user_id": user_id,
                "body": body,
                "attachment": attachment,
                "attachment_file_name": attachment_file_name,
                "random_id": random_id,
                "referrer": referrer,
                "by_user_id": by_user_id,
                "app": app,
            },
        )
        return StartConversationResponse(**result)

    async def set_presence(
        self,
        user_id: str,
        presence: str,
        current_page: Optional[str] = None,
        current_url: Optional[str] = None,
        app: Optional[int] = None,
    ) -> SetPresenceResponse:
        """Set user presence status."""
        result = await self.session.call_tool(
            "set_presence",
            arguments={
                "user_id": user_id,
                "presence": presence,
                "current_page": current_page,
                "current_url": current_url,
                "app": app,
            },
        )
        return SetPresenceResponse(**result)

    async def unsubscribe_email(
        self,
        user_id: str,
        by_user_id: bool = False,
        app: Optional[int] = None,
    ) -> UnsubscribeEmailResponse:
        """Unsubscribe user from email."""
        result = await self.session.call_tool(
            "unsubscribe_email",
            arguments={
                "user_id": user_id,
                "by_user_id": by_user_id,
                "app": app,
            },
        )
        return UnsubscribeEmailResponse(**result)

    async def record_user_event(
        self,
        user_id: str,
        event: str,
        params: Optional[Dict[str, Any]] = None,
        by_user_id: bool = False,
        **kwargs: Dict[str, Any],
    ) -> RecordUserEventResponse:
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
        return RecordUserEventResponse(**result)
