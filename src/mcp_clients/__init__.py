"""MCP utilities package."""

# Carrot Quest Models
from .carrot_quest.models import (
    # Enums
    AdminType,
    MessageType,
    PopupType,
    DeviceType,
    EmailStatus,
    PresenceStatus,
    WebhookType,
    
    # Models
    Admin,
    MessageSender,
    Attachment,
    ConversationPart,
    Channel,
    Conversation,
    EventType,
    Event,
    Note,
    UserTag,
    User,
    WebhookEvent,
)

# Carrot Quest Client
from .carrot_quest.client import CarrotQuestMCPClient

# OpenAI Client
from .openai import OpenAIMCPClient

__all__ = [
    # Carrot Quest Enums
    "AdminType",
    "MessageType",
    "PopupType",
    "DeviceType",
    "EmailStatus",
    "PresenceStatus",
    "WebhookType",
    
    # Carrot Quest Models
    "Admin",
    "MessageSender",
    "Attachment",
    "ConversationPart",
    "Channel",
    "Conversation",
    "EventType",
    "Event",
    "Note",
    "UserTag",
    "User",
    "WebhookEvent",
    
    # Clients
    "CarrotQuestMCPClient",
    "OpenAIMCPClient",
]
