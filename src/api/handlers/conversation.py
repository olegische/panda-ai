"""Conversation webhook handlers."""
from typing import Dict

from api.models import WebhookRequest, WebhookStatus

from .base import BaseEventHandler


class ConversationEventHandler(BaseEventHandler):
    """Handler for chat message webhooks.

    Handles messages from chat (type=conversation).
    """

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle chat message webhook.

        Args:
            event: Webhook event data containing:
                - conversation: ConversationPart object with message details
                - user_id: ID of the user
                - user: User object

        Returns:
            Response data with status
        """
        if not event.conversation:
            self.logger.warning(
                "Missing conversation data in chat message webhook",
                extra={
                    "user_id": event.user_id,
                },
            )
            return {"status": WebhookStatus.IGNORED}

        # Log event processing
        self.logger.info(
            "Processing chat message webhook",
            extra={
                "conversation_id": event.conversation.conversation,
                "message_id": event.conversation.id,
                "user_id": event.user_id,
                "message_type": event.conversation.type,
                "direction": getattr(event.conversation, "direction", None),
            },
        )

        # Extract message details
        conversation_id = event.conversation.conversation
        message_body = event.conversation.body

        # Pass event to orchestrator
        _ = self.orchestrator.process_message(
            conversation_id=conversation_id,
            user_id=event.user_id,
            message=message_body,
            context=event.model_dump(exclude_none=True),
        )

        return {"status": WebhookStatus.ACCEPTED}
