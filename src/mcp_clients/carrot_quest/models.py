"""Carrot Quest API models."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


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


class EmailStatus(str, Enum):
    """Email status enumeration."""

    VALIDATION = "validation"
    NOT_VALID = "not_valid"
    NOT_CONFIRMED = "not_confirmed"
    CONFIRMED = "confirmed"
    BOUNCED = "bounced"
    SPAM = "spam"
    UNSUBSCRIBED = "unsubscribed"
    BLACK_LIST = "black_list"


class PresenceStatus(str, Enum):
    """User presence status enumeration."""

    ONLINE = "online"
    IDLE = "idle"
    OFFLINE = "offline"


class Admin(BaseModel):
    """Admin model."""

    id: str = Field(..., description="Admin ID")
    name: str = Field(..., description="Admin name shown in chat")
    avatar: str = Field(..., description="Admin avatar URL")
    type: AdminType = Field(..., description="Admin type (admin/bot)")
    name_internal: Optional[str] = Field(None, description="Internal admin name")


class MessageSender(BaseModel):
    """Message sender model."""

    id: str = Field(..., description="Sender ID")
    name: str = Field(..., description="Sender name")
    email_name: str = Field(..., description="Email name (before @)")
    is_default: bool = Field(..., description="Is default sender")
    is_removed: bool = Field(..., description="Is sender removed")
    avatar: str = Field(..., description="Sender avatar URL")
    is_bot: bool = Field(..., description="Is sender a bot")
    type: Optional[str] = Field("message_sender", description="Always 'message_sender'")


class Attachment(BaseModel):
    """Attachment model."""

    id: str = Field(..., description="Attachment ID")
    type: str = Field("file", description="Always 'file'")
    filename: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="File MIME type")
    size: int = Field(..., description="File size in bytes")
    url: str = Field(..., description="File download URL")
    created: float = Field(..., description="Creation timestamp")


class ConversationPart(BaseModel):
    """Conversation part (message) model."""

    id: str = Field(..., description="Message ID")
    created: float = Field(..., description="Creation timestamp")
    edited: Optional[float] = Field(None, description="Last edit timestamp")
    removed: Optional[float] = Field(None, description="Removal timestamp")
    conversation: str = Field(..., description="Conversation ID")
    part_group: str = Field(..., description="Part group ID")
    body: str = Field(..., description="Message text")
    body_json: Optional[Dict[str, Any]] = Field(
        None, description="Message JSON content"
    )
    direction: Optional[str] = Field(None, description="Message direction (a2u/u2a)")
    type: str = Field(..., description="Message type")
    from_: Optional[Union[str, Admin, MessageSender]] = Field(None, alias="from")
    sent_via: str = Field(..., description="Message sent via")
    meta_data: Dict[str, Any] = Field(
        default_factory=dict, description="Additional data"
    )
    reply_type: str = Field(..., description="Expected reply type")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="Message actions")
    external_id: Optional[str] = Field(None, description="External message ID")
    read: Optional[bool] = Field(None, description="Is message read")
    first: Optional[bool] = Field(None, description="Is first message")
    attachments: Optional[List[Attachment]] = Field(
        None, description="Message attachments"
    )
    random_id: Optional[str] = Field(None, description="Random ID for frontend")


class Channel(BaseModel):
    """Channel model."""

    id: str = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    avatar: str = Field(..., description="Channel avatar")
    type: str = Field(..., description="Channel type")
    droppable: Optional[bool] = Field(None, description="Can manually move to channel")
    operators: Optional[List[Admin]] = Field(None, description="Channel operators")
    not_assigned_count: Optional[int] = Field(
        None, description="Unassigned dialogs count"
    )
    not_read_count: Optional[int] = Field(None, description="Unread dialogs count")
    read_permission: Optional[bool] = Field(None, description="Has read permission")
    priority: Optional[int] = Field(None, description="Channel priority")
    auto_set: Optional[bool] = Field(None, description="Auto-assign enabled")
    auto_set_settings: Optional[Dict[str, Any]] = Field(
        None, description="Auto-assign settings"
    )


class Conversation(BaseModel):
    """Conversation model."""

    id: str = Field(..., description="Conversation ID")
    created: float = Field(..., description="Creation timestamp")
    replied: bool = Field(..., description="Is visible in admin panel")
    delayed_until: Optional[float] = Field(None, description="Delayed until timestamp")
    closed: bool = Field(..., description="Is conversation closed")
    message: Optional[str] = Field(None, description="Initial message ID")
    type: str = Field(..., description="Conversation type")
    reply_type: str = Field(..., description="Expected reply type")
    removed: Optional[float] = Field(None, description="Removal timestamp")
    reply_last_type: str = Field(..., description="Last reply type")
    parts_count: int = Field(..., description="Total parts count")
    assignee: Optional[Admin] = Field(None, description="Assigned admin")
    sended_time: datetime = Field(..., description="First message send time")
    admin_unread_count: int = Field(..., description="Admin unread count")
    user_unread_count: int = Field(..., description="User unread count")
    not_answered_admin_replies: int = Field(..., description="Unanswered admin replies")
    unread_parts_count: int = Field(..., description="Unread parts count")
    replies_count: int = Field(..., description="Total replies count")
    last_admin: Optional[Admin] = Field(None, description="Last admin in conversation")
    last_update: datetime = Field(..., description="Last update time")
    tags: List[str] = Field(default_factory=list, description="Conversation tags")
    important: bool = Field(..., description="Is conversation important")
    external_service: Optional[str] = Field(None, description="External service type")
    external_id: Optional[str] = Field(None, description="External conversation ID")
    last_user_reply_time: Optional[datetime] = Field(
        None, description="Last user reply time"
    )
    status: Optional[str] = Field(None, description="Message send status")
    assistant_type: Optional[str] = Field(None, description="Assistant type")
    recipient_type: str = Field(..., description="Recipient type")
    user: Optional["User"] = Field(None, description="Conversation user")
    channel: Optional[Channel] = Field(None, description="Conversation channel")
    part_last: Optional[ConversationPart] = Field(
        None, description="Last conversation part"
    )
    important_part_last: Optional[ConversationPart] = Field(
        None, description="Last important part"
    )
    reply_last: Optional[ConversationPart] = Field(None, description="Last reply")


class EventType(BaseModel):
    """Event type model."""

    id: str = Field(..., description="Event type ID")
    name: str = Field(..., description="Event type name")
    score: int = Field(..., description="Event score")
    visible: bool = Field(..., description="Is visible in admin panel")
    active: bool = Field(..., description="Has occurred at least once")


class Event(BaseModel):
    """Event model."""

    id: str = Field(..., description="Event ID")
    created: float = Field(..., description="Creation timestamp")
    type: EventType = Field(..., description="Event type")
    user: str = Field(..., description="User ID")
    props: Dict[str, Any] = Field(default_factory=dict, description="Event properties")


class Note(BaseModel):
    """User note model."""

    id: str = Field(..., description="Note ID")
    author: Admin = Field(..., description="Note author")
    body: str = Field(..., description="Note text")
    created: float = Field(..., description="Creation timestamp")


class UserTag(BaseModel):
    """User tag model."""

    id: str = Field(..., description="Tag ID")
    app: str = Field(..., description="App ID")
    name: str = Field(..., description="Tag name (JSON encoded)")
    removed: Optional[float] = Field(None, description="Removal timestamp")


class User(BaseModel):
    """User model."""

    id: str = Field(..., description="User ID")
    user_id: str = Field(..., description="External user ID")
    removed: Optional[datetime] = Field(None, description="Removal timestamp")
    map_url: Optional[str] = Field(None, description="Google Maps location URL")
    props: Optional[Dict[str, Any]] = Field(None, description="System properties")
    props_custom: Optional[Dict[str, Any]] = Field(
        None, description="Custom properties"
    )
    props_events: Optional[Dict[str, Any]] = Field(None, description="Event properties")
    email_status: Optional[EmailStatus] = Field(
        None, description="Email subscription status"
    )
    presence: Optional[PresenceStatus] = Field(None, description="User presence status")
    presence_details: Optional[Dict[str, Any]] = Field(
        None, description="Presence details"
    )
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="User segments")
    notes: Optional[List[Note]] = Field(None, description="User notes")
    tags: Optional[List[UserTag]] = Field(None, description="User tags")
    events: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="User events")
    timezone_offset: Optional[float] = Field(
        None, description="Timezone offset in minutes"
    )


class WebhookType(str, Enum):
    """Webhook type enumeration."""

    EVENT = "event"
    MESSAGE = "message_webhook"


class WebhookEvent(BaseModel):
    """Base webhook event model."""

    type: WebhookType = Field(..., description="Webhook event type")
    token: str = Field(..., description="Webhook verification token")
    user: User = Field(..., description="User associated with the event")
    user_id: str = Field(..., description="User ID")
    event_name: Optional[str] = Field(None, description="Event name")
    event: Optional[Dict] = Field(None, description="Event data")
    event_id: Optional[str] = Field(None, description="Event ID")
    conversation: Optional[Conversation] = Field(None, description="Conversation data")
    message: Optional[ConversationPart] = Field(None, description="Message data")
    message_id: Optional[str] = Field(None, description="Message ID")
    sending_id: Optional[str] = Field(None, description="Sending ID")
    message_name: Optional[str] = Field(None, description="Message name")


# Rebuild models with forward references
Conversation.model_rebuild()
