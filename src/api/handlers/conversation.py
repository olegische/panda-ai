"""Conversation webhook handlers."""
from typing import Dict

from api.models import WebhookRequest, WebhookStatus
from mcp_clients.carrot_quest.models import ConversationEventType

from .base import BaseEventHandler


class ConversationEventHandler(BaseEventHandler):
    """Handler for conversation events.

    Handles events like conversation start, message replies, etc.
    """

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle conversation event.

        Args:
            event: Webhook event data

        Returns:
            Response data with status
        """
        if not event.event:
            self.logger.warning(
                "Missing event data",
                extra={
                    "event_name": event.event_name,
                    "user_id": event.user_id,
                },
            )
            return {"status": WebhookStatus.IGNORED}

        # Log event processing
        self.logger.info(
            "Processing conversation event",
            extra={
                "event_name": event.event_name,
                "user_id": event.user_id,
                "event_data": event.event,
            },
        )

        # Get event data fields
        conversation_id = event.event.get("$conversation_id")
        body = event.event.get("$body", "")

        # Process event based on type
        if event.event_name == ConversationEventType.CONVERSATION_STARTED:
            # For conversation start, we need conversation_id
            if not conversation_id:
                self.logger.warning(
                    "Missing $conversation_id in conversation start event",
                    extra={"user_id": event.user_id},
                )
                return {"status": WebhookStatus.IGNORED}

        # Pass event to orchestrator
        _ = self.orchestrator.process_message(
            conversation_id=conversation_id,
            user_id=event.user_id,
            message=body,
            context=event.model_dump(exclude_none=True),
        )

        return {"status": WebhookStatus.ACCEPTED}
