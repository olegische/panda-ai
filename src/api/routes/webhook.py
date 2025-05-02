"""Webhook router implementation for Carrot Quest events."""
import hashlib
import hmac
import json
from typing import Any, Dict

from fastapi import Header, Request

from agent import Orchestrator
from api.models import WebhookRequest, WebhookResponse, WebhookStatus
from api.routes.base import BaseRouter
from core.logger import LoggerService
from core.models.errors import AgentError, ValidationError
from mcp_clients.carrot_quest.models import (
    Conversation,
    ConversationPart,
    Event,
    User,
    WebhookType,
)

# Define header parameters
carrot_signature_header = Header(
    None,
    alias="X-Carrot-Signature",
    description="Carrot Quest webhook signature for validation",
)


class WebhookRouter(BaseRouter):
    """Webhook router implementation for Carrot Quest events."""

    def __init__(
        self,
        logger: LoggerService,
        orchestrator: Orchestrator,
        webhook_secret: str,
    ) -> None:
        """Initialize router.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
            webhook_secret: Secret for webhook validation
        """
        super().__init__(logger=logger, tags=["webhook"])
        self.logger = logger.get_logger(__name__)
        self.orchestrator = orchestrator
        self.webhook_secret = webhook_secret

    def validate_signature(self, signature: str, body: bytes) -> bool:
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

    def _setup_routes(self) -> None:
        """Setup router endpoints."""
        self.router.add_api_route(
            "/webhook/carrot-quest",
            self.handle_webhook,
            methods=["POST"],
            response_model=WebhookResponse,
            summary="Carrot Quest Webhook",
            description="Handle Carrot Quest webhook events.",
            operation_id="handle_carrot_quest_webhook_v1",
            responses={
                200: {
                    "model": WebhookResponse,
                    "description": "Webhook processed successfully",
                },
                400: {
                    "description": "Invalid request",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Invalid request payload"}
                        }
                    },
                },
                401: {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Invalid webhook signature"}
                        }
                    },
                },
            },
        )

    async def handle_webhook(
        self, request: Request, x_carrot_signature: str = carrot_signature_header
    ) -> WebhookResponse:
        """Handle Carrot Quest webhook.

        Args:
            request: FastAPI request object
            x_carrot_signature: Webhook signature header

        Returns:
            WebhookResponse with processing status
        """
        self.logger.debug(
            "Webhook received",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
                "headers": dict(request.headers),
            },
        )

        # Get raw body for signature validation
        body = await request.body()

        # Validate signature
        if not self.validate_signature(x_carrot_signature, body):
            self.logger.warning(
                "Invalid webhook signature",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "client": request.client.host if request.client else None,
                },
            )
            raise AgentError(
                code=401,
                message="Invalid webhook signature",
                details={"header": "X-Carrot-Signature"},
            )

        # Parse request data
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
            webhook_data = WebhookRequest(**webhook_data_dict)
        except Exception as e:
            self.logger.error(
                "Invalid request payload",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "body": body.decode(),
                    "error": str(e),
                },
            )
            raise AgentError(
                code=400,
                message="Invalid request payload",
                details={"error": str(e)},
            )

        # Process event
        try:
            result = await self.process_event(webhook_data)
            return WebhookResponse(**result)
        except AgentError:
            # Re-raise AgentError to be handled by middleware
            raise
        except Exception as e:
            self.logger.error(
                "Error processing webhook event",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "event_type": webhook_data.type,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise AgentError(
                code=500,
                message="Error processing webhook event",
                details={"error": str(e), "event_type": webhook_data.type},
            )

    async def process_event(self, data: WebhookRequest) -> Dict[str, str]:
        """Process webhook event.

        Args:
            data: Validated webhook request data

        Returns:
            Response data
        """
        # Handle message webhook events
        if data.type == WebhookType.MESSAGE:
            if not data.message or not data.message.body:
                raise ValidationError(
                    message="Missing message data",
                    field="message",
                )

            # Process message through orchestrator
            self.logger.info(
                "Processing message webhook",
                extra={
                    "message_id": data.message_id,
                    "message_name": data.message_name,
                    "user_id": data.user_id,
                },
            )

            # Ensure required fields are present
            if not data.conversation or not data.conversation.id:
                raise ValidationError(
                    message="Missing conversation data",
                    field="conversation",
                )

            if not data.message or not data.message.body:
                raise ValidationError(
                    message="Missing message data",
                    field="message",
                )

            # Ensure conversation_id is not None
            conversation_id = data.conversation.id
            if not conversation_id:
                raise ValidationError(
                    message="Missing conversation ID",
                    field="conversation.id",
                )

            # Start message processing in background
            _ = self.orchestrator.process_message(
                conversation_id=conversation_id,
                user_id=data.user_id,
                message=data.message.body,
                context=data.dict(exclude_none=True),
            )
            return {"status": WebhookStatus.ACCEPTED}

        # Handle event webhook
        elif data.type == WebhookType.EVENT:
            if not data.event:
                raise ValidationError(
                    message="Missing event data",
                    field="event",
                )

            self.logger.info(
                "Processing event webhook",
                extra={
                    "event_name": data.event_name,
                    "event_id": data.event_id,
                    "user_id": data.user_id,
                },
            )

            # Handle specific event types
            if data.event_name == "$conversation_user_started":
                if not data.conversation or not data.conversation.id:
                    raise ValidationError(
                        message="Missing conversation data",
                        field="conversation",
                    )

                self.logger.info(
                    "Processing new conversation",
                    extra={
                        "conversation_id": data.conversation.id,
                        "user_id": data.user_id,
                    },
                )
                # Start conversation processing in background
                _ = self.orchestrator.process_message(
                    conversation_id=data.conversation.id,
                    user_id=data.user_id,
                    message="",  # No initial message for conversation start event
                    context=data.dict(exclude_none=True),
                )
                return {"status": WebhookStatus.ACCEPTED}

            elif data.event_name == "$message_replied":
                if not data.conversation or not data.conversation.id:
                    raise ValidationError(
                        message="Missing conversation data",
                        field="conversation",
                    )

                self.logger.info(
                    "Processing message reply",
                    extra={
                        "conversation_id": data.conversation.id,
                        "user_id": data.user_id,
                        "message_id": data.message_id,
                    },
                )
                # Start reply processing in background
                _ = self.orchestrator.process_message(
                    conversation_id=data.conversation.id,
                    user_id=data.user_id,
                    message=data.message.body if data.message else "",
                    context=data.dict(exclude_none=True),
                )
                return {"status": WebhookStatus.ACCEPTED}

            elif data.event_name == "$conversation_part_group_closed":
                if not data.conversation or not data.conversation.id:
                    raise ValidationError(
                        message="Missing conversation data",
                        field="conversation",
                    )

                self.logger.info(
                    "Handling conversation closed event",
                    extra={
                        "conversation_id": data.conversation.id,
                    },
                )
                _ = self.orchestrator.handle_conversation_closed(data.conversation.id)
                return {"status": WebhookStatus.ACCEPTED}

            # Log event and return processed status
            self.logger.info(
                "Processing event",
                extra={
                    "event_name": data.event_name,
                    "event_data": data.event,
                    "user_id": data.user_id,
                },
            )
            return {"status": WebhookStatus.PROCESSED}

        self.logger.info(
            "Ignoring unsupported event",
            extra={
                "type": data.type,
                "event_name": data.event_name,
            },
        )
        return {"status": WebhookStatus.IGNORED}
