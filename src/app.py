"""Panda AI FastAPI application."""
from typing import Callable, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.routes.docs import DocsRouter
from src.api.routes.health import HealthRouter
from src.api.routes.webhook import WebhookRouter
from src.core.settings import settings as app_settings


class PandaApp(FastAPI):
    """Panda AI FastAPI application."""

    def __init__(
        self,
        lifespan: Optional[Callable] = None,
    ) -> None:
        """Initialize Panda AI application.

        Args:
            lifespan: Application lifespan manager
        """
        self._configured = False
        # Initialize FastAPI with custom settings
        super().__init__(
            title="Panda AI",
            description="""
            # Panda AI API

            Panda AI provides an intelligent assistant for Carrot Quest.
            """,
            version="0.1.0",  # Will be updated in configure()
            docs_url=None,  # Disable default docs
            redoc_url=None,  # Disable default redoc
            lifespan=lifespan,
        )

        # Dependencies will be set later
        self.state.logger = None
        self.state.settings = None
        self.state.redis_client = None
        self.state.orchestrator = None

    def configure(self) -> None:
        """Configure middleware and routes after dependencies are set."""
        if self._configured:
            raise RuntimeError("Application is already configured")

        # Update version from settings
        self.version = app_settings.VERSION

        if not all(
            [
                self.state.logger,
                self.state.settings,
                self.state.redis_client,
                self.state.orchestrator,
            ]
        ):
            raise RuntimeError("Dependencies must be set before configuring the app.")

        app_logger = self.state.logger.get_logger(__name__)
        logger = self.state.logger
        settings = self.state.settings
        orchestrator = self.state.orchestrator

        # Configure CORS middleware
        app_logger.info(
            "Configuring CORS middleware",
            extra={"allowed_origins": settings.BACKEND_CORS_ORIGINS},
        )
        self.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add middleware in correct order
        app_logger.info("Adding ErrorHandlerMiddleware")
        self.add_middleware(
            ErrorHandlerMiddleware,
            logger=logger,
            settings=settings,
        )

        # Add routers
        app_logger.info("Registering HealthRouter")
        health_router = HealthRouter(logger=logger)
        self.include_router(health_router.router)

        app_logger.info("Registering DocsRouter")
        docs_router = DocsRouter(logger=logger)
        docs_router.register_custom_openapi(self)
        self.include_router(docs_router.router)

        app_logger.info("Registering WebhookRouter")
        webhook_router = WebhookRouter(
            logger=logger,
            orchestrator=orchestrator,
            webhook_secret=settings.WEBHOOK_SECRET,
        )
        self.include_router(webhook_router.router)

        # Add global exception handlers
        app_logger.info("Registering global exception handlers")
        self.add_exception_handler(HTTPException, self._http_exception_handler)
        self.add_exception_handler(
            RequestValidationError, self._validation_exception_handler
        )

        app_logger.info(
            "Panda AI application configuration completed successfully",
            extra={
                "middleware_count": len(self.user_middleware),
                "router_count": len(self.router.routes),
            },
        )

        self._configured = True

    async def _http_exception_handler(
        self, request: Request, exc: HTTPException
    ) -> JSONResponse:  # type: ignore
        """Handle HTTP exceptions.

        Args:
            request: FastAPI request
            exc: HTTP exception

        Returns:
            JSON response with error details
        """
        self.state.logger.get_logger(__name__).error(
            "HTTP error occurred",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "client_host": request.client.host if request.client else None,
                "client_port": request.client.port if request.client else None,
            },
            exc_info=True,
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    async def _validation_exception_handler(
        self, request: Request, exc: RequestValidationError
    ) -> JSONResponse:  # type: ignore
        """Handle validation exceptions.

        Args:
            request: FastAPI request
            exc: Validation exception

        Returns:
            JSON response with validation errors
        """
        self.state.logger.get_logger(__name__).error(
            "Validation error",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors(),
                "client_host": request.client.host if request.client else None,
                "client_port": request.client.port if request.client else None,
                "body": (
                    (await request.body()).decode()
                    if request.method in ["POST", "PUT", "PATCH"]
                    else None
                ),
            },
            exc_info=True,
        )
        return JSONResponse(status_code=422, content={"detail": exc.errors()})
