"""Documentation router implementation."""
from typing import Any, Dict, cast

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

from api.routes.base import BaseRouter
from core.logger import LoggerService


class DocsRouter(BaseRouter):
    """Documentation router implementation."""

    def __init__(self, logger: LoggerService):
        """Initialize router.

        Args:
            logger: Logger service instance
        """
        if not logger:
            raise ValueError("Logger service is required")

        super().__init__(logger=logger, tags=["documentation"])
        self.logger = logger.get_logger(__name__)
        self.openapi_schema = None

    def _setup_routes(self) -> None:
        """Setup router endpoints."""
        self.router.add_api_route(
            "/docs",
            self.swagger_ui_html,
            methods=["GET"],
            include_in_schema=False,
        )
        self.router.add_api_route(
            "/redoc",
            self.redoc_html,
            methods=["GET"],
            include_in_schema=False,
        )

    async def swagger_ui_html(self, request: Request) -> HTMLResponse:
        """Serve custom Swagger UI.

        Args:
            request: FastAPI request object.

        Returns:
            HTML response
        """
        self.logger.debug(
            "Swagger UI requested",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
            },
        )
        swagger_js = (
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"
        )
        swagger_css = (
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css"
        )
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="Panda AI - Swagger UI",
            oauth2_redirect_url=None,
            swagger_js_url=swagger_js,
            swagger_css_url=swagger_css,
        )

    async def redoc_html(self, request: Request) -> HTMLResponse:
        """Serve ReDoc UI.

        Args:
            request: FastAPI request object.

        Returns:
            HTML response
        """
        self.logger.debug(
            "ReDoc UI requested",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "client": request.client.host if request.client else None,
            },
        )
        redoc_js = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
        return get_redoc_html(
            openapi_url="/openapi.json",
            title="Panda AI - ReDoc",
            redoc_js_url=redoc_js,
        )

    def custom_openapi(self, app: FastAPI) -> Dict[str, Any]:
        """Generate custom OpenAPI schema.

        Args:
            app: FastAPI application instance

        Returns:
            OpenAPI schema
        """
        self.logger.debug(
            "Generating OpenAPI schema",
            extra={
                "app_title": app.title,
                "app_version": app.version,
            },
        )

        if self.openapi_schema:
            self.logger.debug("Returning cached OpenAPI schema")
            return cast(Dict[str, Any], self.openapi_schema)

        # Filter out internal routes
        public_routes = [
            route
            for route in app.routes
            if "internal" not in (getattr(route, "tags", []) or [])
        ]

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=public_routes,
        )

        # Ensure components exist in the schema
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        # Ensure securitySchemes exist in components
        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}

        # Add BearerAuth to securitySchemes
        openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",  # Optional, but recommended for clarity
        }

        # Apply BearerAuth globally
        openapi_schema["security"] = [{"BearerAuth": []}]

        self.openapi_schema = openapi_schema
        return cast(Dict[str, Any], openapi_schema)

    def register_custom_openapi(self, app: FastAPI) -> None:
        """Register the custom OpenAPI schema generator with the FastAPI app.

        Args:
            app: FastAPI application instance
        """
        app.openapi = lambda: self.custom_openapi(app)
