"""Carrot Quest API models."""
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


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


class DeviceType(str, Enum):
    """Device type enumeration."""

    PC = "pc"
    MOBILE = "mobile"
    TABLET = "tablet"


class User(BaseModel):
    """User model."""

    id: str = Field(..., description="User ID")
    name: Optional[str] = Field(None, description="User name")
    email: Optional[str] = Field(None, description="User email")
    phone: Optional[str] = Field(None, description="User phone")
    props: Optional[Dict] = Field(None, description="User properties")
    props_custom: Optional[Dict] = Field(None, description="Custom user properties")


class Message(BaseModel):
    """Message model."""

    id: str = Field(..., description="Message ID")
    body: str = Field(..., description="Message content")
    type: Optional[MessageType] = Field(None, description="Message type (auto/manual)")
    name: Optional[str] = Field(None, description="Message name (for auto messages)")
    popup_type: Optional[PopupType] = Field(None, description="Type of popup message")
    from_admin: Optional[str] = Field(None, description="Admin who sent the message")
    created_at: Optional[str] = Field(None, description="Message creation timestamp")


class Conversation(BaseModel):
    """Conversation model."""

    id: str = Field(..., description="Conversation ID")
    messages: Optional[List[Message]] = Field(
        None, description="Messages in conversation"
    )
    tags: Optional[List[str]] = Field(None, description="Conversation tags")
    status: Optional[str] = Field(None, description="Conversation status")
    created_at: Optional[str] = Field(
        None, description="Conversation creation timestamp"
    )
    updated_at: Optional[str] = Field(None, description="Conversation update timestamp")


class SessionStartEvent(BaseModel):
    """Session start event attributes."""

    referrer: Optional[str] = Field(None, alias="$referrer")
    referrer_domain: Optional[str] = Field(None, alias="$referrer_domain")
    browser: Optional[str] = Field(None, alias="$browser")
    os: Optional[str] = Field(None, alias="$os")
    device: Optional[str] = Field(None, alias="$device")
    ip: Optional[str] = Field(None, alias="$ip")
    resolution: Optional[str] = Field(None, alias="$resolution")
    device_type: Optional[DeviceType] = Field(None, alias="$device_type")


class MessageEvent(BaseModel):
    """Message event attributes."""

    message_id: str = Field(..., alias="$message_id")
    message_type: MessageType = Field(..., alias="$message_type")
    message_name: Optional[str] = Field(None, alias="$message_name")
    type: PopupType = Field(..., alias="$type")


class OrderEvent(BaseModel):
    """Order event attributes."""

    order_id: str = Field(..., alias="$order_id")
    order_id_human: Optional[str] = Field(None, alias="$order_id_human")
    order_amount: Optional[float] = Field(None, alias="$order_amount")
    comment: Optional[str] = Field(None, alias="$comment")


class ProductEvent(BaseModel):
    """Product event attributes."""

    name: str = Field(..., alias="$name")
    url: str = Field(..., alias="$url")
    amount: float = Field(..., alias="$amount")
    img: str = Field(..., alias="$img")


class WebhookEvent(BaseModel):
    """Base webhook event model."""

    type: str = Field(..., description="Webhook event type")
    token: str = Field(..., description="Webhook verification token")
    user: User = Field(..., description="User associated with the event")
    user_id: str = Field(..., description="User ID")
    event_name: Optional[str] = Field(None, description="Event name")
    event: Optional[Dict] = Field(None, description="Event data")
    event_id: Optional[str] = Field(None, description="Event ID")
    conversation: Optional[Conversation] = Field(None, description="Conversation data")
    message: Optional[Message] = Field(None, description="Message data")
    message_id: Optional[str] = Field(None, description="Message ID")
    sending_id: Optional[str] = Field(None, description="Sending ID")
    message_name: Optional[str] = Field(None, description="Message name")
