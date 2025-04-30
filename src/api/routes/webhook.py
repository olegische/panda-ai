"""Webhook router implementation for Carrot Quest events."""
import hashlib
import hmac
import json
from typing import Any, Dict

from fastapi import Header, Request
from fastapi.responses import JSONResponse

from src.agent import AssistantOrchestrator
from src.api.routes.base import BaseRouter
from src.core.logger import LoggerService
from src.core.models.errors import AgentError, ValidationError

# Define header parameters
carrot_signature_header = Header(
    None,
    description="Carrot Quest webhook signature for validation",
)


class WebhookValidator:
    """Validates Carrot Quest webhook signatures."""

    def __init__(self, webhook_secret: str):
        """Initialize validator.

        Args:
            webhook_secret: Secret key for webhook validation
        """
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
        self.validator = WebhookValidator(webhook_secret)

    def _setup_routes(self) -> None:
        """Setup router endpoints."""
        self.router.add_api_route(
            "/webhook/carrot-quest",
            self.handle_webhook,
            methods=["POST"],
            response_model=Dict[str, str],
            summary="Carrot Quest Webhook",
            description="Handle Carrot Quest webhook events.",
            operation_id="handle_carrot_quest_webhook_v1",
            responses={
                200: {
                    "description": "Webhook processed successfully",
                    "content": {
                        "application/json": {"example": {"status": "processing"}}
                    },
                },
                400: {
                    "description": "Invalid request",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Invalid JSON payload"}
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
    ) -> JSONResponse:
        """Handle Carrot Quest webhook.

        Args:
            request: FastAPI request object
            x_carrot_signature: Webhook signature header

        Returns:
            JSON response with processing status
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
        if not self.validator.validate_signature(x_carrot_signature, body):
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

        # Parse webhook data
        try:
            data = json.loads(body)
            event_type = data.get("type")
            if not event_type:
                self.logger.warning(
                    "Missing event type",
                    extra={
                        "request_id": getattr(request.state, "request_id", None),
                        "data": data,
                    },
                )
                raise ValidationError(message="Missing event type", field="type")
        except json.JSONDecodeError as e:
            self.logger.error(
                "Invalid JSON payload",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "body": body.decode(),
                    "error": str(e),
                },
            )
            raise AgentError(
                code=400, message="Invalid JSON payload", details={"error": str(e)}
            )

        # Process event
        try:
            result = await self.process_event(event_type, data)
            return JSONResponse(
                status_code=200,
                content=result,
            )
        except AgentError:
            # Re-raise AgentError to be handled by middleware
            raise
        except Exception as e:
            self.logger.error(
                "Error processing webhook event",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "event_type": event_type,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise AgentError(
                code=500,
                message="Error processing webhook event",
                details={"error": str(e), "event_type": event_type},
            )

    async def process_event(
        self, event_type: str, data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Process webhook event.

        Args:
            event_type: Type of webhook event
            data: Event data

        Returns:
            Response data
        """
        if event_type == "new_message":
            # Extract message details
            conversation_id = data.get("conversation", {}).get("id")
            user_id = data.get("user", {}).get("id")
            message = data.get("message", {}).get("body")

            if not all([conversation_id, user_id, message]):
                self.logger.warning(
                    "Missing required fields in webhook data",
                    extra={
                        "data": data,
                    },
                )

                # Determine which field is missing
                missing_fields = []
                if not conversation_id:
                    missing_fields.append("conversation_id")
                if not user_id:
                    missing_fields.append("user_id")
                if not message:
                    missing_fields.append("message")

                raise ValidationError(
                    message="Missing required fields in webhook data",
                    field=", ".join(missing_fields),
                )

            # Process message through orchestrator
            self.logger.info(
                "Processing new message",
                extra={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "message_length": len(message),
                },
            )
            await self.orchestrator.process_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message=message,
                context=data,
            )

            return {"status": "processing"}

        elif event_type == "conversation_closed":
            # Handle conversation closed event
            conversation_id = data.get("conversation", {}).get("id")
            if conversation_id:
                self.logger.info(
                    "Handling conversation closed event",
                    extra={
                        "conversation_id": conversation_id,
                    },
                )
                await self.orchestrator.handle_conversation_closed(conversation_id)
            return {"status": "processed"}

        self.logger.info(
            "Ignoring unsupported event type",
            extra={
                "event_type": event_type,
            },
        )
        return {"status": "ignored"}
