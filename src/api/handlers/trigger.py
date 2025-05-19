"""Trigger webhook handlers."""
from typing import Dict

from api.models import WebhookRequest, WebhookStatus

from .base import BaseEventHandler


class TriggerWebhookHandler(BaseEventHandler):
    """Handler for trigger message webhooks."""

    async def handle(self, event: WebhookRequest) -> Dict[str, str]:
        """Handle trigger message webhook event.

        Args:
            event: Webhook event data containing:
                - message_id: ID of the auto message
                - sending_id: ID of the dialog
                - message_name: Name of the auto message
                - user_id: ID of the user
                - user: User object

        Returns:
            Response data with status
        """
        if not event.message_id or not event.sending_id:
            self.logger.warning(
                "Missing required message webhook fields",
                extra={
                    "message_id": event.message_id,
                    "sending_id": event.sending_id,
                    "user_id": event.user_id,
                },
            )
            return {"status": WebhookStatus.IGNORED}

        self.logger.info(
            "Processing trigger message webhook",
            extra={
                "message_id": event.message_id,
                "message_name": event.message_name,
                "sending_id": event.sending_id,
                "user_id": event.user_id,
            },
        )

        # Start message processing in background
        _ = self.orchestrator.process_message(
            conversation_id=event.sending_id,  # Dialog ID from sending_id
            user_id=event.user_id,
            message="",  # No message body in trigger webhooks
            context=event.model_dump(exclude_none=True),
        )
        return {"status": WebhookStatus.ACCEPTED}
