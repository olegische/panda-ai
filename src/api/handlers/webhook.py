"""Webhook event handlers implementation."""
from abc import ABC, abstractmethod
from typing import Dict, Protocol, runtime_checkable

from agent.orchestrator import Orchestrator
from api.models import WebhookRequest, WebhookStatus
from core.logger import LoggerService
from core.models.errors import ValidationError
from mcp_clients.carrot_quest.models import WebhookType


@runtime_checkable
class WebhookEventHandler(Protocol):
    """Protocol defining webhook event handler interface."""

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle webhook event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        ...


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


class MessageWebhookHandler(BaseEventHandler):
    """Handler for message webhook events."""

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle message webhook event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        self._validate_message(event)
        self._validate_conversation(event)

        self.logger.info(
            "Processing message webhook",
            extra={
                "message_id": event.message_id,
                "message_name": event.message_name,
                "user_id": event.user_id,
            },
        )

        # Start message processing in background
        _ = self.orchestrator.process_message(
            conversation_id=event.conversation.id,
            user_id=event.user_id,
            message=event.message.body,
            context=event.dict(exclude_none=True),
        )
        return {"status": WebhookStatus.ACCEPTED}


class ConversationStartedHandler(BaseEventHandler):
    """Handler for conversation started events."""

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle conversation started event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        self._validate_conversation(event)

        self.logger.info(
            "Processing new conversation",
            extra={
                "conversation_id": event.conversation.id,
                "user_id": event.user_id,
            },
        )

        # Start conversation processing in background
        _ = self.orchestrator.process_message(
            conversation_id=event.conversation.id,
            user_id=event.user_id,
            message="",  # No initial message for conversation start event
            context=event.dict(exclude_none=True),
        )
        return {"status": WebhookStatus.ACCEPTED}


class MessageRepliedHandler(BaseEventHandler):
    """Handler for message replied events."""

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle message replied event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        self._validate_conversation(event)

        self.logger.info(
            "Processing message reply",
            extra={
                "conversation_id": event.conversation.id,
                "user_id": event.user_id,
                "message_id": event.message_id,
            },
        )

        # Start reply processing in background
        _ = self.orchestrator.process_message(
            conversation_id=event.conversation.id,
            user_id=event.user_id,
            message=event.message.body if event.message else "",
            context=event.dict(exclude_none=True),
        )
        return {"status": WebhookStatus.ACCEPTED}


class ConversationClosedHandler(BaseEventHandler):
    """Handler for conversation closed events."""

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle conversation closed event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        self._validate_conversation(event)

        self.logger.info(
            "Handling conversation closed event",
            extra={
                "conversation_id": event.conversation.id,
            },
        )

        _ = self.orchestrator.handle_conversation_closed(event.conversation.id)
        return {"status": WebhookStatus.ACCEPTED}


class DefaultEventHandler(BaseEventHandler):
    """Default handler for unhandled event types."""

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle unhandled event type.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        self.logger.info(
            "Processing event",
            extra={
                "event_name": event.event_name,
                "event_data": event.event,
                "user_id": event.user_id,
            },
        )
        return {"status": WebhookStatus.PROCESSED}


class WebhookEventDispatcher:
    """Dispatcher for webhook events."""

    def __init__(
        self,
        logger: LoggerService,
        orchestrator: "Orchestrator",
    ) -> None:
        """Initialize dispatcher.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
        """
        self.logger = logger.get_logger(__name__)
        self._handlers: Dict[str, WebhookEventHandler] = {}

        # Initialize handlers
        self._init_handlers(logger, orchestrator)

    def _init_handlers(
        self,
        logger: LoggerService,
        orchestrator: "Orchestrator",
    ) -> None:
        """Initialize event handlers.

        Args:
            logger: Logger service instance
            orchestrator: Assistant orchestrator instance
        """
        # Message webhook handler
        self._handlers[WebhookType.MESSAGE] = MessageWebhookHandler(
            logger=logger,
            orchestrator=orchestrator,
        )

        # Event handlers
        self._handlers["$conversation_user_started"] = ConversationStartedHandler(
            logger=logger,
            orchestrator=orchestrator,
        )
        self._handlers["$message_replied"] = MessageRepliedHandler(
            logger=logger,
            orchestrator=orchestrator,
        )
        self._handlers["$conversation_part_group_closed"] = ConversationClosedHandler(
            logger=logger,
            orchestrator=orchestrator,
        )

        # Default handler for unhandled events
        self._default_handler = DefaultEventHandler(
            logger=logger,
            orchestrator=orchestrator,
        )

    async def dispatch(self, event: WebhookRequest) -> Dict[str, str]:
        """Dispatch webhook event to appropriate handler.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        # Handle message webhooks
        if event.type == WebhookType.MESSAGE:
            return await self._handlers[WebhookType.MESSAGE].handle(event)

        # Handle event webhooks
        elif event.type == WebhookType.EVENT:
            if not event.event:
                raise ValidationError(
                    message="Missing event data",
                    field="event",
                )

            # Get handler for event name or use default
            handler = self._handlers.get(
                event.event_name,
                self._default_handler,
            )

            # Handle event
            return await handler.handle(event)

        # Ignore unsupported event types
        self.logger.info(
            "Ignoring unsupported event",
            extra={
                "type": event.type,
                "event_name": event.event_name,
            },
        )
        return {"status": WebhookStatus.IGNORED}
