"""Webhook request parsing service."""
import hashlib
import hmac
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

    def __init__(self, logger: LoggerService, webhook_secret: str) -> None:
        """Initialize parser.

        Args:
            logger: Logger service instance for logging
            webhook_secret: Secret for validating webhook signatures
        """
        self.logger = logger.get_logger(__name__)
        self.webhook_secret = webhook_secret

    def _validate_signature(self, signature: str, body: bytes) -> bool:
        """Validate webhook signature.

        Args:
            signature: Signature from X-Carrot-Signature header
            body: Raw request body bytes

        Returns:
            True if signature is valid
        """
        expected = hmac.new(
            self.webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    def _parse_required_fields(self, form_data: dict) -> Dict[str, Any]:
        """Parse required fields from form data.

        Args:
            form_data: Form data from request

        Returns:
            Dictionary with required fields
        """
        return {
            "type": WebhookType(str(form_data["type"])),
            "token": str(form_data["token"]),
            "user_id": str(form_data["user_id"]),
            "user": User(**json.loads(str(form_data["user"]))),
        }

    def _parse_optional_fields(self, form_data: dict) -> Dict[str, Any]:
        """Parse optional string fields from form data.

        Args:
            form_data: Form data from request

        Returns:
            Dictionary with optional fields
        """
        optional_fields = {}
        for field in [
            "event_name",
            "event_id",
            "message_id",
            "sending_id",
            "message_name",
        ]:
            if field in form_data:
                optional_fields[field] = str(form_data[field])
        return optional_fields

    def _parse_nested_objects(self, form_data: dict) -> Dict[str, Any]:
        """Parse optional nested objects from form data.

        Args:
            form_data: Form data from request

        Returns:
            Dictionary with nested objects
        """
        nested_objects = {}
        if "event" in form_data:
            nested_objects["event"] = Event(**json.loads(str(form_data["event"])))
        if "conversation" in form_data:
            nested_objects["conversation"] = Conversation(
                **json.loads(str(form_data["conversation"]))
            )
        if "message" in form_data:
            nested_objects["message"] = ConversationPart(
                **json.loads(str(form_data["message"]))
            )
        return nested_objects

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
            # Get raw body for signature validation
            body = await request.body()

            # Validate signature
            signature = request.headers.get("X-Carrot-Signature")
            if not signature:
                self.logger.warning(
                    "Missing webhook signature",
                    extra={
                        "request_id": getattr(request.state, "request_id", None),
                        "client": request.client.host if request.client else None,
                    },
                )
                raise AgentError(
                    code=401,
                    message="Missing webhook signature",
                    details={"header": "X-Carrot-Signature"},
                )

            if not self._validate_signature(signature, body):
                self.logger.warning(
                    "Invalid webhook signature",
                    extra={
                        "request_id": getattr(request.state, "request_id", None),
                        "client": request.client.host if request.client else None,
                        "signature_length": len(signature),
                        "body_length": len(body),
                    },
                )
                raise AgentError(
                    code=401,
                    message="Invalid webhook signature",
                    details={"header": "X-Carrot-Signature"},
                )

            # Parse form data
            form_data = await request.form()

            # Build webhook data dictionary
            webhook_data_dict = {}
            webhook_data_dict.update(self._parse_required_fields(form_data))
            webhook_data_dict.update(self._parse_optional_fields(form_data))
            webhook_data_dict.update(self._parse_nested_objects(form_data))

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
