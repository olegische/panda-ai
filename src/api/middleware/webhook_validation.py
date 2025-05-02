"""Webhook validation middleware."""
import hashlib
import hmac
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.logger import LoggerService
from core.models.errors import AgentError


class WebhookValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating webhook signatures."""

    def __init__(
        self,
        app,
        webhook_secret: str,
        logger: LoggerService,
        webhook_path: str = "/webhook/carrot-quest",
    ) -> None:
        """Initialize middleware.

        Args:
            app: FastAPI application instance
            webhook_secret: Secret for webhook validation
            logger: Logger service instance
            webhook_path: Path to validate webhooks for
        """
        super().__init__(app)
        self.webhook_secret = webhook_secret
        self.logger = logger.get_logger(__name__)
        self.webhook_path = webhook_path

    def validate_signature(self, signature: str, body: bytes) -> bool:
        """Validate webhook signature.

        Args:
            signature: Signature from X-Carrot-Signature header
            body: Raw request body bytes

        Returns:
            True if signature is valid
        """
        expected = hmac.new(
            self.webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process request through middleware.

        Args:
            request: FastAPI request object
            call_next: Next middleware/endpoint in chain

        Returns:
            Response from next middleware/endpoint

        Raises:
            AgentError: If webhook signature is invalid
        """
        # Only validate webhook endpoints
        if not request.url.path.startswith(self.webhook_path):
            return await call_next(request)

        # Get signature header
        signature = request.headers.get("X-Carrot-Signature")
        if not signature:
            self.logger.warning(
                "Missing webhook signature",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "client": request.client.host if request.client else None,
                },
            )
            raise AgentError(
                code=401,
                message="Missing webhook signature",
                details={"header": "X-Carrot-Signature"},
            )

        # Get raw body for validation
        body = await request.body()

        # Validate signature
        if not self.validate_signature(signature, body):
            self.logger.warning(
                "Invalid webhook signature",
                extra={
                    "request_id": getattr(request.state, "request_id", None),
                    "client": request.client.host if request.client else None,
                },
            )
            raise AgentError(
                code=401,
                message="Invalid webhook signature",
                details={"header": "X-Carrot-Signature"},
            )

        # Continue processing
        return await call_next(request)
