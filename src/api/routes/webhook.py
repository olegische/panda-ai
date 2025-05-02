"""Webhook router implementation for Carrot Quest events."""
from fastapi import Request

from agent import Orchestrator
from api.handlers.webhook import WebhookEventDispatcher
from api.models import WebhookResponse
from api.routes.base import BaseRouter
from api.services.webhook_parser import WebhookParser
from core.logger import LoggerService
from core.models.errors import AgentError


class WebhookRouter(BaseRouter):
    """Webhook router implementation for Carrot Quest events."""

    def __init__(
        self,
        logger: LoggerService,
        orchestrator: Orchestrator,
    ) -> None:
        """Initialize router.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
        """
        super().__init__(logger=logger, tags=["webhook"])
        self.logger = logger.get_logger(__name__)
        self.event_dispatcher = WebhookEventDispatcher(
            logger=logger,
            orchestrator=orchestrator,
        )
        self.webhook_parser = WebhookParser(logger=logger)

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

    async def handle_webhook(self, request: Request) -> WebhookResponse:
        """Handle Carrot Quest webhook.

        Args:
            request: FastAPI request object

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

        # Parse and validate request data
        webhook_data = await self.webhook_parser.parse_request(request)

        # Process event
        try:
            result = await self.event_dispatcher.dispatch(webhook_data)
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
