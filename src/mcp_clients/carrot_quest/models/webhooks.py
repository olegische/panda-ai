"""Webhook models for Carrot Quest API."""
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from .objects import ConversationPart, User


class WebhookType(str, Enum):
    """Webhook type enumeration."""

    EVENT = "event"
    TRIGGER = "message_webhook"  # Renamed from MESSAGE to TRIGGER for clarity
    CONVERSATION = "conversation"


class ConversationEventType(str, Enum):
    """Conversation event type enumeration."""

    CONVERSATION_STARTED = "$conversation_user_started"
    MESSAGE_SENT = "$message_sended"
    MESSAGE_READ = "$message_read"
    MESSAGE_REPLIED = "$message_replied"


class MessageType(str, Enum):
    """Message type enumeration."""

    AUTO = "auto"
    MANUAL = "manual"


class MessageDeliveryType(str, Enum):
    """Message delivery type enumeration."""

    POPUP_CHAT = "popup_chat"
    POPUP_BIG = "popup_big"
    POPUP_SMALL = "popup_small"
    EMAIL = "email"


class ConversationEventData(Dict):
    """Conversation event data model.

    Event data is a dictionary with fields prefixed with $, like:
    - $body: Message text (first 255 characters)
    - $conversation_id: Dialog ID
    - $message_id: Message ID
    - $message_type: Message type (auto/manual)
    - $message_name: Message name (for auto messages)
    - $type: Message delivery type
    """


class WebhookEvent(BaseModel):
    """Base webhook event model.

    As per Carrot Quest API documentation, webhook payloads contain
    only IDs and basic data, not full objects. Full objects must be
    fetched separately using the respective API endpoints.
    """

    type: WebhookType = Field(..., description="Webhook event type")
    token: str = Field(..., description="Webhook verification token")
    user: User = Field(..., description="User associated with the event")
    user_id: str = Field(..., description="User ID")

    # Fields for event type webhooks
    event_name: Optional[ConversationEventType] = Field(
        None, description="Event name (for type=event)"
    )
    event: Optional[ConversationEventData] = Field(
        None, description="Event data (for type=event)"
    )
    event_id: Optional[str] = Field(None, description="Event ID (for type=event)")

    # Fields for message_webhook type
    message_id: Optional[str] = Field(
        None, description="Message ID (for type=message_webhook)"
    )
    sending_id: Optional[str] = Field(
        None, description="Dialog ID (for type=message_webhook)"
    )
    message_name: Optional[str] = Field(
        None, description="Message name (for type=message_webhook)"
    )

    # Fields for conversation type webhooks (chat messages)
    conversation: Optional[ConversationPart] = Field(
        None, description="Conversation part data (for type=conversation)"
    )
