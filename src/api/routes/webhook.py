"""Webhook router implementation for Carrot Quest events."""
import hashlib
import hmac
import json
from typing import Dict, cast

from fastapi import Header, Request

from src.agent import AssistantOrchestrator
from src.api.models.webhook import WebhookRequest, WebhookResponse
from src.api.routes.base import BaseRouter
from src.core.logger import LoggerService
from src.core.models.errors import AgentError, ValidationError
from src.mcp_clients.carrot_quest.models import (
    ConversationPart,
    Event,
    User,
    WebhookEvent,
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
        orchestrator: AssistantOrchestrator,
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
            data = {}

            # Parse nested JSON structures with type safety
            if "user" in form_data:
                data["user"] = User(**json.loads(str(form_data["user"])))
            if "event" in form_data:
                data["event"] = Event(**json.loads(str(form_data["event"])))
            if "conversation" in form_data:
                data["conversation"] = json.loads(str(form_data["conversation"]))
            if "message" in form_data:
                data["message"] = ConversationPart(**json.loads(str(form_data["message"])))

            # Add non-nested fields as strings
            data.update({
                field: str(form_data[field])
                for field in [
                    "type", "token", "user_id", "event_name", "event_id",
                    "message_id", "sending_id", "message_name"
                ]
                if field in form_data
            })

            # Validate with Pydantic model
            webhook_data = cast(WebhookRequest, WebhookEvent(**data))
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
        if data.type == "message_webhook":
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

            # Process message
            await self.orchestrator.process_message(
                conversation_id=conversation_id,
                user_id=data.user_id,
                message=data.message.body,
                context=data.dict(exclude_none=True),
            )
            return {"status": "processing"}

        # Handle event webhook
        elif data.type == "event":
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
                return {"status": "processed"}

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
                await self.orchestrator.handle_conversation_closed(data.conversation.id)
                return {"status": "processed"}

            # Log event and return processed status
            self.logger.info(
                "Processing event",
                extra={
                    "event_name": data.event_name,
                    "event_data": data.event.dict(exclude_none=True),
                    "user_id": data.user_id,
                },
            )
            return {"status": "processed"}

        self.logger.info(
            "Ignoring unsupported event",
            extra={
                "type": data.type,
                "event_name": data.event_name,
            },
        )
        return {"status": "ignored"}
