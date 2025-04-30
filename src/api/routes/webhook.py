"""Webhook router implementation for Carrot Quest events."""
import hashlib
import hmac
import json
from typing import Dict
from urllib.parse import parse_qs

from fastapi import Header, Request
from fastapi.responses import JSONResponse

from src.agent import AssistantOrchestrator
from src.api.models.webhook import WebhookRequest, WebhookResponse
from src.api.routes.base import BaseRouter
from src.core.logger import LoggerService
from src.core.models.errors import AgentError, ValidationError

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

        # Parse form data
        try:
            form_data = parse_qs(body.decode())
            # Convert form data to dict, taking first value from lists
            data = {k: v[0] if len(v) == 1 else v for k, v in form_data.items()}
            
            # Parse nested JSON structures
            if "user" in data:
                data["user"] = json.loads(data["user"])
            if "event" in data:
                data["event"] = json.loads(data["event"])
            if "conversation" in data:
                data["conversation"] = json.loads(data["conversation"])
            if "message" in data:
                data["message"] = json.loads(data["message"])

            # Validate with Pydantic model
            webhook_data = WebhookRequest(**data)
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
            await self.orchestrator.process_message(
                conversation_id=data.conversation.id if data.conversation else None,
                user_id=data.user_id,
                message=data.message.body,
                context=data.dict(),
            )
            return {"status": "processing"}

        # Handle event webhooks
        elif data.type == "event":
            if data.event_name == "$conversation_user_started":
                # Handle new conversation
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
                # Add any specific conversation start handling here
                return {"status": "processed"}

            elif data.event_name == "$conversation_part_group_closed":
                # Handle conversation closed
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

        self.logger.info(
            "Ignoring unsupported event",
            extra={
                "type": data.type,
                "event_name": data.event_name,
            },
        )
        return {"status": "ignored"}
