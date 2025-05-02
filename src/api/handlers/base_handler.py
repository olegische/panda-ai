"""Base handler for webhook events."""
from abc import ABC, abstractmethod
from typing import Dict

from agent.orchestrator import Orchestrator
from api.models import WebhookRequest
from core.logger import LoggerService
from core.models.errors import ValidationError


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

    def _validate_conversation(self, event: WebhookRequest) -> None:
        """Validate conversation data in event.

        Args:
            event: Webhook event data

        Raises:
            ValidationError: If conversation data is missing or invalid
        """
        if not event.conversation or not event.conversation.id:
            raise ValidationError(
                message="Missing conversation data",
                field="conversation",
            )

    def _validate_message(self, event: WebhookRequest) -> None:
        """Validate message data in event.

        Args:
            event: Webhook event data

        Raises:
            ValidationError: If message data is missing or invalid
        """
        if not event.message or not event.message.body:
            raise ValidationError(
                message="Missing message data",
                field="message",
            )

    @abstractmethod
    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle webhook event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        pass
