"""Factory for creating webhook handlers."""
from agent.orchestrator import Orchestrator
from api.models import WebhookRequest
from core.logger import LoggerService
from core.models.errors import ValidationError
from mcp_clients.carrot_quest.models import WebhookType

from .base_handler import BaseEventHandler
from .conversation_handlers import (
    ConversationClosedHandler,
    ConversationStartedHandler,
    MessageRepliedHandler,
)
from .default_handler import DefaultEventHandler
from .message_handlers import MessageWebhookHandler


class HandlerFactory:
    """Factory for creating webhook handlers."""

    def __init__(
        self,
        logger: LoggerService,
        orchestrator: Orchestrator,
    ) -> None:
        """Initialize factory.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
        """
        self.logger = logger
        self.orchestrator = orchestrator

    def create(self, event: WebhookRequest) -> BaseEventHandler:
        """Create appropriate handler for webhook event.

        Args:
            event: Webhook event data

        Returns:
            Handler instance for the event

        Raises:
            ValidationError: If event type is not supported or event data is invalid
        """
        if event.type == WebhookType.MESSAGE:
            return MessageWebhookHandler(
                logger=self.logger,
                orchestrator=self.orchestrator,
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

            # Create handler based on event name
            if event.event_name == "$conversation_user_started":
                return ConversationStartedHandler(
                    logger=self.logger,
                    orchestrator=self.orchestrator,
                )
            elif event.event_name == "$message_replied":
                return MessageRepliedHandler(
                    logger=self.logger,
                    orchestrator=self.orchestrator,
                )
            elif event.event_name == "$conversation_part_group_closed":
                return ConversationClosedHandler(
                    logger=self.logger,
                    orchestrator=self.orchestrator,
                )
            else:
                return DefaultEventHandler(
                    logger=self.logger,
                    orchestrator=self.orchestrator,
                )

        raise ValidationError(
            message=f"Unsupported webhook type: {event.type}",
            field="type",
        )
