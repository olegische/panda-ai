"""Base handler for webhook events."""
from abc import ABC, abstractmethod
from typing import Dict

from api.models import WebhookRequest
from core.logger import LoggerService
from dreamer.orchestrator import Orchestrator


class BaseEventHandler(ABC):
    """Base class for webhook event handlers."""

    def __init__(self, logger: LoggerService, orchestrator: Orchestrator) -> None:
        """Initialize handler.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
        """
        self.logger = logger.get_logger(self.__class__.__name__)
        self.orchestrator = orchestrator

    @abstractmethod
    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle webhook event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        pass
