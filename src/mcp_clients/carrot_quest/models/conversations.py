"""Pydantic models for Carrot Quest Conversations API responses."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .common import Conversation, ConversationPart, ResponseMeta


class GetConversationResponse(BaseModel):
    """Response model for get conversation endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Conversation = Field(..., description="Conversation data")


class GetConversationPartsResponse(BaseModel):
    """Response model for get conversation parts endpoint."""

    meta: ResponseMeta = Field(
        ...,
        description="Response metadata including status and pagination info",
    )
    data: List[ConversationPart] = Field(..., description="List of conversation parts")


class ConversationReplyResponse(BaseModel):
    """Response model for conversation reply endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: ConversationPart = Field(
        ...,
        description="Created conversation part",
    )
    assign_part: Optional[ConversationPart] = Field(
        None,
        description="Created assign part if auto_assign was specified",
    )


class ConversationAssignResponse(BaseModel):
    """Response model for conversation assign endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Dict[str, int] = Field(
        ...,
        description="Response data containing created part ID and part group ID",
    )


class ConversationTagResponse(BaseModel):
    """Response model for conversation tag endpoints (add/delete)."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Dict[str, int] = Field(
        ...,
        description="Response data containing created part ID and part group ID",
    )


class EmptyResponse(BaseModel):
    """Response model for endpoints that return empty data."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Dict = Field(default_factory=dict, description="Empty response data")
