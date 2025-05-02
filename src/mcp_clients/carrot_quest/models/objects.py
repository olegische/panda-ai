"""Common Pydantic models for Carrot Quest API."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator


class AdminType(str, Enum):
    """Admin type enumeration."""

    ADMIN = "admin"
    BOT = "bot"


class MessageType(str, Enum):
    """Message type enumeration."""

    AUTO = "auto"
    MANUAL = "manual"


class PopupType(str, Enum):
    """Popup type enumeration."""

    POPUP_CHAT = "popup_chat"
    POPUP_BIG = "popup_big"
    POPUP_SMALL = "popup_small"
    EMAIL = "email"
    BLOCK_POPUP_SMALL = "block_popup_small"
    BLOCK_POPUP_BIG = "block_popup_big"
    LEAD_BOT = "lead_bot"
    ROUTING_BOT = "routing_bot"
    PUSH = "push"
    SDK_PUSH = "sdk_push"


class DeviceType(str, Enum):
    """Device type enumeration."""

    PC = "pc"
    MOBILE = "mobile"
    TABLET = "tablet"


class EmailStatusEnum(str, Enum):
    """Email status enumeration."""

    VALIDATION = "validation"
    NOT_VALID = "not_valid"
    NOT_CONFIRMED = "not_confirmed"
    CONFIRMED = "confirmed"
    BOUNCED = "bounced"
    SPAM = "spam"
    UNSUBSCRIBED = "unsubscribed"
    BLACK_LIST = "black_list"


class ChannelType(str, Enum):
    """Channel type enumeration."""

    EMAIL = "email"
    MOBILE = "mobile"
    MANUAL = "manual"
    VK = "vk"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    YANDEX_DIALOGS = "yandex_dialogs"
    VIBER = "viber"
    WHATSAPP = "whatsapp"


class ConversationType(str, Enum):
    """Conversation type enumeration."""

    EMAIL = "email"
    INCOMING_EMAIL = "incoming_email"
    POPUP_SMALL = "popup_small"
    POPUP_BIG = "popup_big"
    BLOCK_POPUP_SMALL = "block_popup_small"
    BLOCK_POPUP_BIG = "block_popup_big"
    POPUP_CHAT = "popup_chat"
    LEAD_BOT = "lead_bot"
    ROUTING_BOT = "routing_bot"
    PUSH = "push"
    SDK_PUSH = "sdk_push"


class ConversationPartType(str, Enum):
    """Conversation part type enumeration."""

    REPLY_USER = "reply_user"
    REPLY_ADMIN = "reply_admin"
    AUTO_REPLY = "auto_reply"
    NOTE = "note"
    TAG_ADDED = "tag_added"
    TAG_DELETED = "tag_deleted"
    ASSIGNED = "assigned"
    CLOSED = "closed"
    FINAL_CLOSED = "final_closed"
    DELAYED = "delayed"
    CHANNEL_CHANGED = "channel_changed"
    VOTE = "vote"
    ARTICLE = "article"
    CHAT_BOT_ADMIN = "chat_bot_admin"
    CHAT_BOT_USER = "chat_bot_user"
    SERVICE = "service"


class SentViaType(str, Enum):
    """Message sending method enumeration."""

    WEB_USER = "web_user"
    EMAIL_USER = "email_user"
    WEB_PANEL = "web_panel"
    EMAIL_ADMIN = "email_admin"
    APP_ANDROID = "app_android"
    APP_IOS = "app_ios"
    APP_CHROME = "app_chrome"
    APP_DESKTOP = "app_desktop"
    MESSAGE_AUTO = "message_auto"
    MESSAGE_MANUAL = "message_manual"
    MESSAGE_CHAT_BOT = "message_chat_bot"
    API = "api"
    INTEGRATIONS = "integrations"
    SYSTEM = "system"
    AUTO_REPLY = "auto_reply"


class DirectionType(str, Enum):
    """Message direction enumeration."""

    ADMIN_TO_USER = "a2u"
    USER_TO_ADMIN = "u2a"


class ReplyType(str, Enum):
    """Reply type enumeration."""

    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    PUSH = "push"
    BUTTON = "button"
    NO = "no"


class MessageStatus(str, Enum):
    """Message sending status enumeration."""

    CREATED = "created"
    RENDERED = "rendered"
    SENT = "sent"
    ACCEPTED = "accepted"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    DROPPED = "dropped"
    ERROR = "error"


class AssistantType(str, Enum):
    """Assistant type enumeration."""

    DIALOGFLOW = "dialogflow"
    YANDEX_AI = "yandex_ai"
    LEAD_BOT = "lead_bot"
    ROUTING_BOT = "routing_bot"
    FACEBOOK_BOT = "facebook_bot"
    TELEGRAM_BOT = "telegram_bot"
    WIDGET_BOT = "widget_bot"


class RecipientType(str, Enum):
    """Message recipient type enumeration."""

    ALL = "all"
    WEB = "web"
    SDK = "sdk"


class PresenceStatus(str, Enum):
    """User presence status enumeration."""

    ONLINE = "online"
    IDLE = "idle"
    OFFLINE = "offline"


class MessageSender(BaseModel):
    """Message sender model."""

    id: int = Field(..., description="Unique sender identifier")
    name: str = Field(..., description="Sender name")
    email_name: str = Field(..., description="Email address prefix (before @)")
    is_default: bool = Field(..., description="Whether this is the default sender")
    is_removed: bool = Field(..., description="Whether sender is soft-deleted")
    is_bot: bool = Field(..., description="Whether sender is a bot")
    avatar: str = Field(..., description="URL to sender's avatar")
    type: Literal["message_sender"] = Field(
        "message_sender",
        description="Always 'message_sender' for compatibility with Admin",
    )


class Admin(BaseModel):
    """Administrator or operator model."""

    id: int = Field(..., description="Unique administrator identifier")
    name: str = Field(..., description="Administrator name displayed in chat")
    avatar: str = Field(..., description="URL to administrator's avatar")
    type: AdminType = Field(
        AdminType.ADMIN, description="Type of administrator (admin or bot)"
    )
    name_internal: Optional[str] = Field(
        None, description="Internal administrator name shown only in admin panel"
    )


class Attachment(BaseModel):
    """Attachment in conversation part model."""

    id: int = Field(..., description="Unique attachment identifier")
    type: Literal["file"] = Field("file", description="Attachment type, always 'file'")
    filename: str = Field(..., description="Original filename with extension")
    mime_type: str = Field(..., description="File MIME type")
    size: int = Field(..., description="File size in bytes")
    url: str = Field(..., description="Download URL for the file")
    created: float = Field(..., description="Creation timestamp")


class EventType(BaseModel):
    """Event type model."""

    id: int = Field(..., description="Unique event type identifier")
    name: str = Field(..., description="Event type name")
    score: int = Field(..., description="Event rating/score")
    visible: Optional[bool] = Field(
        None, description="Whether visible in admin panel selection lists"
    )
    active: Optional[bool] = Field(
        None, description="Whether event has occurred at least once"
    )


class Event(BaseModel):
    """Event model."""

    id: int = Field(..., description="Unique event identifier")
    created: float = Field(..., description="Event creation timestamp")
    type: EventType = Field(..., description="Event type information")
    user: int = Field(..., description="User ID who performed the event")
    props: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Event properties. Values can be: "
            "int (-9007199254740992..+9007199254740992), "
            "str (max 255 chars), datetime (ISO 8601: YYYY-MM-DD[THH:MM:SS]), bool, "
            "List[str] (max 30 elements), Dict[str, str] (max 30 elements)"
        ),
    )

    @field_validator("props")
    def validate_props(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event properties according to API constraints."""
        for key, value in v.items():
            if isinstance(value, int) and not (
                -9007199254740992 <= value <= 9007199254740992
            ):
                raise ValueError(f"Integer value {value} is outside allowed range")
            elif isinstance(value, str) and len(value) > 255:
                raise ValueError(f"String value for {key} exceeds 255 characters")
            elif isinstance(value, list) and len(value) > 30:
                raise ValueError(f"Array value for {key} exceeds 30 elements")
            elif isinstance(value, dict) and len(value) > 30:
                raise ValueError(f"Dictionary value for {key} exceeds 30 elements")
        return v


class Segment(BaseModel):
    """User segment model."""

    id: int = Field(..., description="Unique segment identifier")
    app: int = Field(..., description="App ID in Carrot quest")
    name: str = Field(..., description="Segment name")
    filters: str = Field(..., description="JSON-encoded segment filters")


class Note(BaseModel):
    """User note model."""

    id: int = Field(..., description="Unique note identifier")
    app: int = Field(..., description="App ID in Carrot quest")
    user: int = Field(..., description="User ID the note is about")
    author: Admin = Field(..., description="Note author")
    body: str = Field(..., description="Note text content")
    created: float = Field(..., description="Note creation timestamp")


class UserTag(BaseModel):
    """User tag model."""

    id: int = Field(..., description="Unique tag identifier")
    app: int = Field(..., description="App ID in Carrot quest")
    name: str = Field(..., description="JSON-encoded tag name")
    removed: Optional[float] = Field(None, description="Removal timestamp if deleted")


class EmailStatus(BaseModel):
    """Email subscription status model."""

    id: int = Field(..., description="Unique status identifier")
    app: int = Field(..., description="App ID in Carrot quest")
    status: EmailStatusEnum = Field(..., description="Email subscription status")
    updated: datetime = Field(..., description="Last status update timestamp")


class PresenceDetails(BaseModel):
    """User presence details model."""

    page: Optional[str] = Field(None, description="Current page title")
    url: Optional[str] = Field(None, description="Current page URL")
    session_started: Optional[int] = Field(None, description="Session start timestamp")
    presence: PresenceStatus = Field(..., description="User presence status")


class UserEventInfo(BaseModel):
    """User event information model."""

    event_type: EventType = Field(..., description="Event type information")
    first: float = Field(..., description="First occurrence timestamp")
    last: float = Field(..., description="Last occurrence timestamp")
    count: int = Field(..., description="Number of occurrences")


class User(BaseModel):
    """User model."""

    id: int = Field(..., description="Unique user identifier")
    user_id: str = Field(..., description="Unique string identifier in app")
    removed: Optional[datetime] = Field(
        None, description="Removal timestamp if deleted"
    )
    map_url: Optional[str] = Field(None, description="Google Maps location URL")
    props: Optional[Dict[str, Any]] = Field(None, description="System user properties")
    props_custom: Dict[str, Any] = Field(
        default_factory=dict, description="Custom user properties"
    )
    props_events: Optional[Dict[str, Any]] = Field(
        None, description="Event-related properties"
    )
    email_status: Optional[EmailStatus] = Field(
        None, description="Email subscription status"
    )
    presence: Optional[PresenceStatus] = Field(None, description="User presence status")
    presence_details: Optional[PresenceDetails] = Field(
        None, description="User presence details"
    )
    segments: Optional[List[Segment]] = Field(None, description="User segments")
    notes: Optional[List[Note]] = Field(None, description="User notes")
    tags: Optional[List[UserTag]] = Field(None, description="User tags")
    events: Optional[List[UserEventInfo]] = Field(
        None, description="User events information in list format"
    )
    timezone_offset: Optional[float] = Field(
        None, description="User timezone offset in minutes from UTC"
    )


class Channel(BaseModel):
    """Channel model."""

    id: int = Field(..., description="Unique channel identifier")
    name: str = Field(..., description="Channel name")
    avatar: str = Field(..., description="Channel avatar URL")
    type: ChannelType = Field(
        ...,
        description="Channel type",
    )
    droppable: Optional[bool] = Field(
        None, description="Whether manual transfer to this channel is possible"
    )
    operators: Optional[List[Admin]] = Field(
        None,
        description="List of administrators with access to channel dialogs",
    )
    not_assigned_count: Optional[int] = Field(
        None, description="Number of unassigned dialogs in channel"
    )
    not_read_count: Optional[int] = Field(
        None, description="Number of unread dialogs in channel"
    )
    read_permission: Optional[bool] = Field(
        None,
        description="Whether current operator has read permission for this channel",
    )
    priority: Optional[int] = Field(None, description="Channel priority")
    auto_set: Optional[bool] = Field(
        None, description="Whether auto-assignment works for this channel"
    )
    auto_set_settings: Optional[Dict[str, Any]] = Field(
        None, description="Auto-assignment settings"
    )


class ConversationAction(BaseModel):
    """Model for conversation message actions (buttons, inputs, links etc)."""

    # This will be expanded based on actual action types from the API
    type: str = Field(..., description="Action type")
    data: Dict[str, Any] = Field(..., description="Action-specific data")


class ConversationPart(BaseModel):
    """Conversation part (message) model."""

    id: int = Field(..., description="Unique message identifier")
    created: int = Field(..., description="Message creation timestamp")
    conversation: Union[int, "Conversation"] = Field(
        ..., description="Parent conversation ID or object"
    )
    body: str = Field(..., description="Message text content")
    type: ConversationPartType = Field(
        ...,
        description="Message type",
    )
    sent_via: SentViaType = Field(
        ...,
        description="Message sending method",
    )
    from_: Optional[Union[int, Admin, MessageSender]] = Field(
        None,
        alias="from",
        description="Message sender (user ID, Admin or MessageSender object)",
    )
    read: Optional[bool] = Field(None, description="Whether message has been read")
    first: Optional[bool] = Field(
        None, description="Whether this is first message in conversation"
    )
    edited: Optional[int] = Field(None, description="Last edit timestamp")
    removed: Optional[int] = Field(
        None, description="Removal timestamp if message was deleted"
    )
    part_group: Optional[int] = Field(
        None, description="Question ID this message belongs to"
    )
    body_json: Optional[Dict[str, Any]] = Field(
        None, description="JSON content for complex message types"
    )
    direction: Optional[DirectionType] = Field(
        None, description="Message direction (admin-to-user or user-to-admin)"
    )
    meta_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional message metadata"
    )
    reply_type: Optional[ReplyType] = Field(None, description="Expected reply type")
    actions: Optional[List[ConversationAction]] = Field(
        None, description="Available message actions"
    )
    external_id: Optional[str] = Field(
        None, description="Message ID in external service"
    )
    inbound_email: Optional[int] = Field(
        None, description="ID of original email for email integration messages"
    )
    random_id: Optional[str] = Field(
        None, description="Frontend message correlation ID"
    )
    attachments: Optional[List[Attachment]] = Field(
        None, description="Message attachments"
    )


class Conversation(BaseModel):
    """Conversation model."""

    id: int = Field(..., description="Unique conversation identifier")
    created: int = Field(..., description="Conversation creation timestamp")
    replied: bool = Field(
        ..., description="Whether conversation is visible in admin panel list"
    )
    delayed_until: Optional[int] = Field(
        None, description="Timestamp until conversation is delayed"
    )
    closed: bool = Field(..., description="Whether conversation is closed")
    message: Optional[int] = Field(
        None, description="ID of message that started conversation"
    )
    type: ConversationType = Field(
        ...,
        description="Conversation type",
    )
    reply_type: ReplyType = Field(
        ...,
        description="Expected reply type",
    )
    removed: Optional[int] = Field(
        None, description="Removal timestamp if conversation was deleted"
    )
    reply_last_type: Optional[ConversationPartType] = Field(
        None,
        description="Type of last reply (reply_user or reply_admin)",
    )
    parts_count: int = Field(
        ..., description="Total number of messages in conversation"
    )
    assignee: Optional[Admin] = Field(
        None, description="Administrator assigned to conversation"
    )
    sended_time: datetime = Field(..., description="First message send time")
    admin_unread_count: int = Field(..., description="Number of unread user messages")
    user_unread_count: int = Field(
        ..., description="Number of unread operator messages"
    )
    not_answered_admin_replies: int = Field(
        ...,
        description="Number of unanswered operator messages",
    )
    unread_parts_count: Optional[int] = Field(
        None, description="Legacy: duplicates user_unread_count"
    )
    replies_count: Optional[int] = Field(
        None, description="Total number of user/operator replies"
    )
    last_admin: Optional[Admin] = Field(
        None,
        description="Last administrator who participated in conversation",
    )
    last_update: int = Field(..., description="Last update timestamp")
    tags: List[str] = Field(..., description="Conversation tags")
    important: Optional[bool] = Field(
        None, description="Whether conversation requires urgent response"
    )
    external_service: Optional[str] = Field(
        None, description="Messenger integration type"
    )
    external_id: Optional[str] = Field(
        None, description="Conversation ID in messenger integration"
    )
    last_user_reply_time: Optional[datetime] = Field(
        None, description="Timestamp of last user reply"
    )
    status: Optional[MessageStatus] = Field(
        None, description="Message sending status for auto/manual messages"
    )
    assistant_type: Optional[AssistantType] = Field(
        None, description="Type of assistant managing conversation"
    )
    recipient_type: Optional[RecipientType] = Field(
        None, description="Message recipient type"
    )
    user: Optional[User] = Field(None, description="User participating in conversation")
    channel: Optional[Channel] = Field(
        None, description="Channel conversation belongs to"
    )
    part_last: Optional[ConversationPart] = Field(
        None, description="Last message including system messages"
    )
    important_part_last: Optional[ConversationPart] = Field(
        None,
        description="Last important message",
    )
    reply_last: Optional[ConversationPart] = Field(
        None, description="Last user/operator reply"
    )


class ResponseMeta(BaseModel):
    """Common response metadata model."""

    status: int = Field(..., description="Response status code")
    next_after: Optional[float] = Field(
        None, description="Pagination timestamp for next page"
    )
