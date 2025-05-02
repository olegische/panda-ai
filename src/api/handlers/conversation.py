"""Conversation webhook handlers."""
from typing import Dict

from api.models import WebhookRequest, WebhookStatus

from .base_handler import BaseEventHandler


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
            context=event.model_dump(exclude_none=True),
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
            context=event.model_dump(exclude_none=True),
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
