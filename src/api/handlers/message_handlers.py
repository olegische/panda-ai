"""Message webhook handlers."""
from typing import Dict

from api.models import WebhookRequest, WebhookStatus

from .base_handler import BaseEventHandler


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
            context=event.model_dump(exclude_none=True),
        )
        return {"status": WebhookStatus.ACCEPTED}
