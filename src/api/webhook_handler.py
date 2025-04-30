"""Webhook handler for Carrot Quest events."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header, Request
import hmac
import hashlib
import json

from src.agent import AssistantOrchestrator

router = APIRouter()


class WebhookValidator:
    """Validates Carrot Quest webhook signatures."""

    def __init__(self, webhook_secret: str):
        """Initialize validator.
        
        Args:
            webhook_secret: Secret key for webhook validation
        """
        self.webhook_secret = webhook_secret

    def validate_signature(self, signature: str, body: bytes) -> bool:
        """Validate webhook signature.
        
        Args:
            signature: Signature from X-Carrot-Signature header
            body: Raw request body bytes
            
        Returns:
            True if signature is valid
        """
        expected = hmac.new(
            self.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)


class WebhookProcessor:
    """Processes Carrot Quest webhook events."""

    def __init__(self, orchestrator: AssistantOrchestrator):
        """Initialize processor.
        
        Args:
            orchestrator: Assistant orchestrator instance
        """
        self.orchestrator = orchestrator

    async def process_event(self, event_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process webhook event.
        
        Args:
            event_type: Type of webhook event
            data: Event data
            
        Returns:
            Optional response data
        """
        if event_type == "new_message":
            # Extract message details
            conversation_id = data.get("conversation", {}).get("id")
            user_id = data.get("user", {}).get("id")
            message = data.get("message", {}).get("body")
            
            if not all([conversation_id, user_id, message]):
                raise HTTPException(
                    status_code=400,
                    detail="Missing required fields in webhook data"
                )
            
            # Process message through orchestrator
            await self.orchestrator.process_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message=message,
                context=data
            )
            
            return {"status": "processing"}
            
        elif event_type == "conversation_closed":
            # Handle conversation closed event
            conversation_id = data.get("conversation", {}).get("id")
            if conversation_id:
                await self.orchestrator.handle_conversation_closed(conversation_id)
            return {"status": "processed"}
            
        return {"status": "ignored"}


def create_webhook_handler(
    webhook_secret: str,
    orchestrator: AssistantOrchestrator
) -> APIRouter:
    """Create webhook handler router.
    
    Args:
        webhook_secret: Secret for webhook validation
        orchestrator: Assistant orchestrator instance
        
    Returns:
        FastAPI router with webhook endpoints
    """
    validator = WebhookValidator(webhook_secret)
    processor = WebhookProcessor(orchestrator)
    
    @router.post("/webhook/carrot-quest")
    async def handle_webhook(
        request: Request,
        x_carrot_signature: str = Header(None)
    ):
        """Handle Carrot Quest webhook."""
        # Get raw body for signature validation
        body = await request.body()
        
        # Validate signature
        if not validator.validate_signature(x_carrot_signature, body):
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )
        
        # Parse webhook data
        try:
            data = json.loads(body)
            event_type = data.get("type")
            if not event_type:
                raise HTTPException(
                    status_code=400,
                    detail="Missing event type"
                )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON payload"
            )
        
        # Process event
        return await processor.process_event(event_type, data)
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return router
