"""Webhook event dispatcher implementation."""
from typing import Dict

from api.models import WebhookRequest
from core.logger import LoggerService
from dreamer.orchestrator import Orchestrator

from .factory import HandlerFactory


class WebhookEventDispatcher:
    """Dispatcher for webhook events."""

    def __init__(
        self,
        logger: LoggerService,
        orchestrator: Orchestrator,
    ) -> None:
        """Initialize dispatcher.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
        """
        self.logger = logger.get_logger(__name__)
        self.orchestrator = orchestrator
        self.factory = HandlerFactory(logger=logger)

    async def dispatch(self, event: WebhookRequest) -> Dict[str, str]:
        """Dispatch webhook event to appropriate handler.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        handler = self.factory.create(event, orchestrator=self.orchestrator)
        return await handler.handle(event)
