"""Message models for webhook gateway following OpenAI Assistant API format."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MessageSource(str, Enum):
    """Supported message source systems."""

    CARROT_QUEST = "carrot_quest"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    VIBER = "viber"
    # Add more as needed


class MessageRole(str, Enum):
    """Message role following OpenAI Assistant API format."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    DEVELOPER = "developer"


class InputText(BaseModel):
    """A text input to the model."""

    type: str = Field(
        default="input_text",
        description="The type of the input item. Always input_text",
    )
    text: str = Field(..., description="The text input to the model")


class InputFile(BaseModel):
    """A file input to the model."""

    type: str = Field(
        default="input_file",
        description="The type of the input item. Always input_file",
    )
    file_data: Optional[str] = Field(
        None, description="The content of the file to be sent to the model"
    )
    file_id: Optional[str] = Field(
        None, description="The ID of the file to be sent to the model"
    )
    filename: Optional[str] = Field(
        None, description="The name of the file to be sent to the model"
    )


class InputMessage(BaseModel):
    """A message input to the model.

    This represents a message with role-based hierarchy for instruction following.
    """

    role: MessageRole = Field(..., description="The role of the message input")
    content: Union[str, List[Union[InputText, InputFile]]] = Field(
        ...,
        description=(
            "Text, image, or file inputs to the model, " "used to generate a response"
        ),
    )
    type: str = Field(
        default="message", description="The type of the message input. Always message"
    )


class Message(BaseModel):
    """Message model for webhook gateway following OpenAI Assistant API format."""

    # OpenAI Assistant API format input
    input: Union[str, List[InputMessage]] = Field(
        ...,
        description=(
            "Text, image, or file inputs to the model, " "used to generate a response"
        ),
    )

    # Core identifiers
    message_id: str = Field(
        ..., description="Unique message identifier within the source system"
    )
    thread_id: str = Field(
        ..., description="Thread/conversation identifier (maps to OpenAI thread)"
    )
    user_id: str = Field(
        ..., description="Anonymous user identifier within the source system"
    )

    # Source information
    source: MessageSource = Field(..., description="Source system identifier")
    source_message_id: Optional[str] = Field(
        None, description="Original message ID from source system"
    )

    # Metadata
    timestamp: datetime = Field(..., description="Message timestamp")

    # Additional context from source system
    # (may contain personal data for debugging only)
    source_context: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "Additional context data from source system " "for debugging/logging"
        ),
    )

    # Reply context
    reply_to_message_id: Optional[str] = Field(
        None, description="ID of message being replied to"
    )

    # Channel-specific metadata
    channel_id: Optional[str] = Field(
        None, description="Channel/room identifier if applicable"
    )
    channel_type: Optional[str] = Field(
        None, description="Channel type (e.g., 'popup_chat', 'email')"
    )


class MessageStatus(str, Enum):
    """Message response status enumeration."""

    ACCEPTED = "accepted"  # Message received and validation passed
    PROCESSING = "processing"  # Processing started (legacy)
    PROCESSED = "processed"  # Processing completed (legacy)


class MessageResponse(BaseModel):
    """Message response model."""

    status: MessageStatus = Field(..., description="Processing status")
    details: Optional[Dict] = Field(None, description="Additional response details")
