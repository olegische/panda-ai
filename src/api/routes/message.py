"""Message router implementation for external chat messages."""
from typing import Annotated

from fastapi import Depends, Request

from api.models.message import Message, MessageResponse, MessageStatus
from api.routes.base import BaseRouter
from core.dependencies import get_dreamer_agent
from core.logger import LoggerService
from core.settings import Settings
from dreamer.agent import DreamerAgent


class MessageRouter(BaseRouter):
    """Message router implementation for external chat messages."""

    def __init__(
        self,
        logger: LoggerService,
        settings: Settings,
    ) -> None:
        """Initialize router.

        Args:
            logger: Logger service instance
            settings: Application settings
        """
        super().__init__(logger=logger, tags=["message"])
        self.logger = logger.get_logger(__name__)
        self.settings = settings

    def _setup_routes(self) -> None:
        """Setup router endpoints."""
        # Message endpoint
        self.router.add_api_route(
            "/api/v1/message",
            self.handle_message,
            methods=["POST"],
            response_model=MessageResponse,
            summary="External Chat Messages",
            description="Handle messages from external chat systems.",
            operation_id="handle_external_message_v1",
            responses={
                200: {
                    "model": MessageResponse,
                    "description": "Message accepted successfully",
                },
                400: {
                    "description": "Invalid request",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Invalid message payload"}
                        }
                    },
                },
                401: {
                    "description": "Unauthorized",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Invalid authentication"}
                        }
                    },
                },
            },
        )

    async def handle_message(
        self,
        message: Message,
        request: Request,
        dreamer_agent: Annotated[DreamerAgent, Depends(get_dreamer_agent)],
    ) -> MessageResponse:
        """Handle external chat message.

        Args:
            message: Message model with chat message data
            request: FastAPI request object
            dreamer_agent: DreamerAgent instance for processing messages

        Returns:
            MessageResponse with processing status
        """
        self.logger.debug(
            "External message received",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
                "source": message.source,
                "thread_id": message.thread_id,
                "message_id": message.message_id,
            },
        )

        # TODO: Implement message processing logic
        # This would involve:
        # 1. Processing the message through chat completion
        # 2. Handling different message sources
        # 3. Integrating with the orchestrator

        # Process message through Dreamer agent
        # await dreamer_agent.process_message(message)

        # For now, just return accepted status
        return MessageResponse(status=MessageStatus.ACCEPTED)
