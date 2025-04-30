"""Webhook models for API endpoints."""
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from mcp_clients.carrot_quest.models import WebhookEvent


class WebhookStatus(str, Enum):
    """Webhook response status enumeration."""

    ACCEPTED = "accepted"  # Webhook received and validation passed
    PROCESSING = "processing"  # Processing started (legacy)
    PROCESSED = "processed"  # Processing completed (legacy)
    IGNORED = "ignored"  # Event type not supported


class WebhookRequest(WebhookEvent):
    """Webhook request model extending Carrot Quest webhook event."""


class WebhookResponse(BaseModel):
    """Webhook response model."""

    status: WebhookStatus = Field(..., description="Processing status")
    details: Optional[Dict] = Field(None, description="Additional response details")
