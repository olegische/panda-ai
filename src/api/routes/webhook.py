"""Webhook router implementation for Carrot Quest events."""
from fastapi import Request

from api.handlers import WebhookEventDispatcher
from api.models import WebhookResponse
from api.routes.base import BaseRouter
from api.services.webhook_parser import WebhookParser
from core.logger import LoggerService
from core.models.errors import AgentError
from core.settings import Settings
from dreamer import Orchestrator
from mcp_clients.carrot_quest.models import WebhookType


class WebhookRouter(BaseRouter):
    """Webhook router implementation for Carrot Quest events."""

    def __init__(
        self,
        logger: LoggerService,
        orchestrator: Orchestrator,
        settings: Settings,
    ) -> None:
        """Initialize router.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
            settings: Application settings
        """
        super().__init__(logger=logger, tags=["webhook"])
        self.logger = logger.get_logger(__name__)
        self.event_dispatcher = WebhookEventDispatcher(
            logger=logger,
            orchestrator=orchestrator,
        )
        self.webhook_parser = WebhookParser(
            logger=logger,
            settings=settings,
        )

    def _setup_routes(self) -> None:
        """Setup router endpoints."""
        # Conversation events endpoint
        self.router.add_api_route(
            "/webhook/carrot-quest/conversations",
            self.handle_conversation_webhook,
            methods=["POST"],
            response_model=WebhookResponse,
            summary="Carrot Quest Conversation Events",
            description="Handle Carrot Quest conversation events (type=event).",
            operation_id="handle_carrot_quest_conversation_webhook_v1",
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
                            "example": {"detail": "Invalid webhook token"}
                        }
                    },
                },
            },
        )

        # Message events endpoint
        self.router.add_api_route(
            "/webhook/carrot-quest/messages",
            self.handle_message_webhook,
            methods=["POST"],
            response_model=WebhookResponse,
            summary="Carrot Quest Message Events",
            description="Handle Carrot Quest message events (type=message_webhook).",
            operation_id="handle_carrot_quest_message_webhook_v1",
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
                            "example": {"detail": "Invalid webhook token"}
                        }
                    },
                },
            },
        )

    async def handle_conversation_webhook(self, request: Request) -> WebhookResponse:
        """Handle Carrot Quest conversation webhook.

        Args:
            request: FastAPI request object

        Returns:
            WebhookResponse with processing status

        Raises:
            AgentError: If webhook type is not 'event'
        """
        self.logger.debug(
            "Conversation webhook received",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
                "headers": dict(request.headers),
            },
        )

        # Parse and validate request data
        webhook_data = await self.webhook_parser.parse_request(request)

        # Verify this is a conversation event
        if webhook_data.type != WebhookType.EVENT:
            raise AgentError(
                code=400,
                message="Invalid webhook type",
                details={"expected": "event", "received": webhook_data.type},
            )

        # Process conversation event
        try:
            result = await self.event_dispatcher.dispatch_event(webhook_data)
            return WebhookResponse(**result)
        except AgentError:
            raise
        except Exception as e:
            self.logger.error(
                "Error processing conversation event",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "event_type": webhook_data.type,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise AgentError(
                code=500,
                message="Error processing conversation event",
                details={"error": str(e), "event_type": webhook_data.type},
            )

    async def handle_message_webhook(self, request: Request) -> WebhookResponse:
        """Handle Carrot Quest message webhook.

        Args:
            request: FastAPI request object

        Returns:
            WebhookResponse with processing status

        Raises:
            AgentError: If webhook type is not 'message_webhook'
        """
        self.logger.debug(
            "Message webhook received",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
                "headers": dict(request.headers),
            },
        )

        # Parse and validate request data
        webhook_data = await self.webhook_parser.parse_request(request)

        # Verify this is a message webhook
        if webhook_data.type != WebhookType.MESSAGE:
            raise AgentError(
                code=400,
                message="Invalid webhook type",
                details={"expected": "message_webhook", "received": webhook_data.type},
            )

        # Process message webhook
        try:
            result = await self.event_dispatcher.dispatch_message(webhook_data)
            return WebhookResponse(**result)
        except AgentError:
            # Re-raise AgentError to be handled by middleware
            raise
        except Exception as e:
            self.logger.error(
                "Error processing message webhook",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "event_type": webhook_data.type,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise AgentError(
                code=500,
                message="Error processing message webhook",
                details={"error": str(e), "event_type": webhook_data.type},
            )
