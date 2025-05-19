"""Factory for creating webhook handlers."""
from api.models import WebhookRequest
from core.logger import LoggerService
from core.models.errors import ValidationError
from dreamer.orchestrator import Orchestrator
from mcp_clients.carrot_quest.models import WebhookType

from .base import BaseEventHandler
from .conversation import ConversationEventHandler
from .default import DefaultEventHandler
from .trigger import TriggerWebhookHandler


class HandlerFactory:
    """Factory for creating webhook handlers."""

    def __init__(
        self,
        logger: LoggerService,
    ) -> None:
        """Initialize factory.

        Args:
            logger: Logger service instance
        """
        self.logger = logger

    def create(
        self, event: WebhookRequest, orchestrator: Orchestrator
    ) -> BaseEventHandler:
        """Create appropriate handler for webhook event.

        Args:
            event: Webhook event data
            orchestrator: Assistant orchestrator instance

        Returns:
            Handler instance for the event

        Raises:
            ValidationError: If event type is not supported or event data is invalid
        """
        if event.type == WebhookType.TRIGGER:
            return TriggerWebhookHandler(
                logger=self.logger,
                orchestrator=orchestrator,
            )

        if event.type == WebhookType.CONVERSATION:
            if not event.conversation:
                raise ValidationError(
                    message="Missing conversation data",
                    field="conversation",
                )

            return ConversationEventHandler(
                logger=self.logger,
                orchestrator=orchestrator,
            )

        if event.type == WebhookType.EVENT:
            if not event.event:
                raise ValidationError(
                    message="Missing event data",
                    field="event",
                )

            if not event.event_name:
                raise ValidationError(
                    message="Missing event name",
                    field="event_name",
                )

            # Use DefaultEventHandler for all event types
            return DefaultEventHandler(
                logger=self.logger,
                orchestrator=orchestrator,
            )

        raise ValidationError(
            message=f"Unsupported webhook type: {event.type}",
            field="type",
        )
