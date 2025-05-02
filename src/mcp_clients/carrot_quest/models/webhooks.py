"""Webhook models for Carrot Quest API."""
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from .objects import Conversation, ConversationPart, User


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
