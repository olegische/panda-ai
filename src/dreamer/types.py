"""Type definitions for the agent orchestrator."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AssistantMetadata(BaseModel):
    """Assistant metadata."""

    created_at: datetime
    last_used: datetime
    success_rate: float
    avg_response_time: float
    total_interactions: int
    context_source: str
    pattern_type: str


class AssistantConfig(BaseModel):
    """Assistant configuration."""

    model: str
    name: str
    description: str
    instructions: str
    tools: List[Dict[str, Any]]
    metadata: AssistantMetadata


class ConversationContext(BaseModel):
    """Conversation context."""

    user_id: str
    conversation_id: str
    app_id: str
    tags: List[str]
    user_properties: Dict[str, Any]
    similar_conversations: List[Dict[str, Any]]
    pattern_content: Dict[str, Any]


class ProcessingResult(BaseModel):
    """Message processing result."""

    success: bool
    response_time: float
    assistant_id: str
    thread_id: str
    pattern_hash: str
    error: Optional[str] = None


class AssistantMapping(BaseModel):
    """Assistant to conversation mapping."""

    assistant_id: str
    thread_id: str
    pattern_hash: str
    created_at: datetime
    last_used: datetime
    total_messages: int
