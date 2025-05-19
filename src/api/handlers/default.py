"""Default webhook handler."""
from typing import Dict

from api.models import WebhookRequest, WebhookStatus

from .base import BaseEventHandler


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
