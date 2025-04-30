"""Webhook models for API endpoints."""
from typing import Dict, Optional

from pydantic import BaseModel, Field

from src.mcp_clients.carrot_quest.models import WebhookEvent


class WebhookRequest(WebhookEvent):
    """Webhook request model extending Carrot Quest webhook event."""


class WebhookResponse(BaseModel):
    """Webhook response model."""

    status: str = Field(
        ..., description="Processing status (processing/processed/ignored)"
    )
    details: Optional[Dict] = Field(None, description="Additional response details")
