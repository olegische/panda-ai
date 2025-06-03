"""Pydantic models for Carrot Quest Users API responses."""
from typing import Dict, List

from pydantic import BaseModel, Field

from .objects import Conversation, Event, ResponseMeta, User


class GetUserResponse(BaseModel):
    """Response model for get user endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: User = Field(..., description="User data")


class SetUserPropsResponse(BaseModel):
    """Response model for set user properties endpoint."""

    meta: ResponseMeta = Field(
        ...,
        description="Response metadata including status and operation results",
    )
    data: Dict[str, int] = Field(
        ...,
        description="Response data containing user ID and app ID",
    )


class GetUserEventsResponse(BaseModel):
    """Response model for get user events endpoint."""

    meta: ResponseMeta = Field(
        ...,
        description="Response metadata including status and pagination info",
    )
    data: List[Event] = Field(..., description="List of user events")


class RecordUserEventResponse(BaseModel):
    """Response model for record user event endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Event = Field(..., description="Created event data")


class GetUserConversationsResponse(BaseModel):
    """Response model for get user conversations endpoint."""

    meta: ResponseMeta = Field(
        ...,
        description="Response metadata including status and pagination info",
    )
    data: List[Conversation] = Field(..., description="List of user conversations")


class SendMessageResponse(BaseModel):
    """Response model for send message endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Dict[str, int] = Field(
        ...,
        description="Response data containing conversation and message IDs",
    )


class StartConversationResponse(BaseModel):
    """Response model for start conversation endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Dict[str, int] = Field(
        ...,
        description="Response data containing conversation ID",
    )


class SetPresenceResponse(BaseModel):
    """Response model for set presence endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Dict = Field(default_factory=dict, description="Empty response data")


class UnsubscribeEmailResponse(BaseModel):
    """Response model for unsubscribe email endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: Dict = Field(default_factory=dict, description="Empty response data")
