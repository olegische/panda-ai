"""Factory for creating webhook handlers."""
from agent.orchestrator import Orchestrator
from api.models import WebhookRequest
from core.logger import LoggerService
from core.models.errors import ValidationError
from mcp_clients.carrot_quest.models import WebhookType

from .base import BaseEventHandler
from .conversation import (
    ConversationClosedHandler,
    ConversationStartedHandler,
    MessageRepliedHandler,
)
from .default import DefaultEventHandler
from .message import MessageWebhookHandler


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
        if event.type == WebhookType.MESSAGE:
            return MessageWebhookHandler(
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

            # Create handler based on event name
            if event.event_name == "$conversation_user_started":
                return ConversationStartedHandler(
                    logger=self.logger,
                    orchestrator=orchestrator,
                )
            elif event.event_name == "$message_replied":
                return MessageRepliedHandler(
                    logger=self.logger,
                    orchestrator=orchestrator,
                )
            elif event.event_name == "$conversation_part_group_closed":
                return ConversationClosedHandler(
                    logger=self.logger,
                    orchestrator=orchestrator,
                )
            else:
                return DefaultEventHandler(
                    logger=self.logger,
                    orchestrator=orchestrator,
                )

        raise ValidationError(
            message=f"Unsupported webhook type: {event.type}",
            field="type",
        )
