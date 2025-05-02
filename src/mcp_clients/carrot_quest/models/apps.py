"""Pydantic models for Carrot Quest Apps API responses."""
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from .objects import Channel, Conversation, ResponseMeta, User


class UserListItem(BaseModel):
    """User object returned by /apps/{id}/users endpoint."""

    id: int = Field(..., description="User identifier")
    presence: Literal["online", "idle", "offline"] = Field(
        ..., description="User presence status"
    )
    props: Dict[str, Any] = Field(
        ...,
        description=(
            "All user properties as a single dictionary "
            "(system, custom and event properties combined)"
        ),
    )


class AppUsersData(BaseModel):
    """Data model for app users response."""

    total: int = Field(..., description="Total number of users matching filters")
    users: List[UserListItem] = Field(
        ..., description="List of simplified user objects"
    )


class ActiveUsersResponse(BaseModel):
    """Response model for active users endpoint."""

    meta: ResponseMeta = Field(
        ...,
        description="Response metadata including status",
    )
    data: List[User] = Field(..., description="List of active users")


class AppUsersResponse(BaseModel):
    """Response model for app users endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: AppUsersData = Field(
        ...,
        description="Response data containing total users count and users list",
    )


class AppConversationsResponse(BaseModel):
    """Response model for app conversations endpoint."""

    meta: ResponseMeta = Field(
        ...,
        description="Response metadata including status and pagination info",
    )
    data: List[Conversation] = Field(
        ...,
        description="List of conversations",
    )


class AppChannelsResponse(BaseModel):
    """Response model for app channels endpoint."""

    meta: ResponseMeta = Field(..., description="Response metadata including status")
    data: List[Channel] = Field(..., description="List of channels")
