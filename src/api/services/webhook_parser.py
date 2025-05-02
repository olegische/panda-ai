"""Webhook request parsing service."""
import json
from typing import Any, Dict

from fastapi import Request

from api.models import WebhookRequest
from core.logger import LoggerService
from core.models.errors import AgentError
from mcp_clients.carrot_quest.models import (
    Conversation,
    ConversationPart,
    Event,
    User,
    WebhookType,
)


class WebhookParser:
    """Service for parsing webhook request data."""

    def __init__(self, logger: LoggerService) -> None:
        """Initialize parser.

        Args:
            logger: Logger service instance
        """
        self.logger = logger.get_logger(__name__)

    async def parse_request(self, request: Request) -> WebhookRequest:
        """Parse webhook request data.

        Args:
            request: FastAPI request object

        Returns:
            Validated webhook request data

        Raises:
            AgentError: If request data is invalid
        """
        try:
            form_data = await request.form()

            # Create a dictionary with proper typing for all fields
            webhook_data_dict: Dict[str, Any] = {
                # Required fields with direct string values
                "type": WebhookType(str(form_data["type"])),
                "token": str(form_data["token"]),
                "user_id": str(form_data["user_id"]),
            }

            # Parse user object (required field)
            user_json = json.loads(str(form_data["user"]))
            webhook_data_dict["user"] = User(**user_json)

            # Optional fields with proper type conversion
            if "event_name" in form_data:
                webhook_data_dict["event_name"] = str(form_data["event_name"])

            if "event_id" in form_data:
                webhook_data_dict["event_id"] = str(form_data["event_id"])

            if "message_id" in form_data:
                webhook_data_dict["message_id"] = str(form_data["message_id"])

            if "sending_id" in form_data:
                webhook_data_dict["sending_id"] = str(form_data["sending_id"])

            if "message_name" in form_data:
                webhook_data_dict["message_name"] = str(form_data["message_name"])

            # Parse optional nested objects with proper models
            if "event" in form_data:
                event_json = json.loads(str(form_data["event"]))
                webhook_data_dict["event"] = Event(**event_json)

            if "conversation" in form_data:
                conversation_json = json.loads(str(form_data["conversation"]))
                webhook_data_dict["conversation"] = Conversation(**conversation_json)

            if "message" in form_data:
                message_json = json.loads(str(form_data["message"]))
                webhook_data_dict["message"] = ConversationPart(**message_json)

            # Validate entire structure with Pydantic
            return WebhookRequest(**webhook_data_dict)

        except Exception as e:
            self.logger.error(
                "Invalid request payload",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "error": str(e),
                },
            )
            raise AgentError(
                code=400,
                message="Invalid request payload",
                details={"error": str(e)},
            )
