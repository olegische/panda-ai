"""Panda AI FastAPI application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI

from agent import AssistantOrchestrator
from app import PandaApp
from core.cache import RedisClient
from core.logger import LoggerService
from core.settings import settings
from mcp_clients.carrot_quest import CarrotQuestMCPClient
from mcp_clients.openai import OpenAIMCPClient
from neural_network.analyzer import ConversationAnalyzer


@asynccontextmanager
async def lifespan(app: PandaApp) -> AsyncGenerator[None, None]:
    """Manage application lifespan.

    This function handles startup and shutdown events for the application.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    app_logger = app.state.logger.get_logger(__name__)
    app_logger.info("Application configured successfully")

    # Initialize Redis
    try:
        await app.state.redis_client.ping()  # Ensure Redis is reachable
        app_logger.info("Redis client initialized successfully")
    except Exception as e:
        app_logger.error(
            "Failed to connect to Redis",
            extra={
                "error": str(e),
            },
        )

    try:
        yield
    finally:
        app_logger.info("Shutting down application")

        # Close Redis connection
        await app.state.redis_client.close()
        app_logger.info("Redis client closed")


def init_app() -> FastAPI:
    """Initialize FastAPI application."""
    # Create the app with lifespan
    app = PandaApp(lifespan=lifespan)

    # Set up dependencies
    logger = LoggerService(settings_instance=settings)

    # Create Redis connection
    redis_connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
    )

    # Create Redis client
    redis_client = RedisClient(
        redis=redis_connection,
        logger=logger,
        settings=settings,
    )

    # Create MCP clients
    carrot_quest_client = CarrotQuestMCPClient(
        logger=logger,
        settings=settings,
    )
    openai_client = OpenAIMCPClient(
        logger=logger,
        settings=settings,
    )

    # Create analyzer
    analyzer = ConversationAnalyzer(
        logger=logger,
        settings=settings,
        cache=redis_client,
        carrot_quest=carrot_quest_client,
    )

    # Create orchestrator with all dependencies
    orchestrator = AssistantOrchestrator(
        cache=redis_client,
        carrot_quest=carrot_quest_client,
        openai=openai_client,
        analyzer=analyzer,
        logger=logger,
    )

    # Set dependencies on app state
    app.state.logger = logger
    app.state.settings = settings
    app.state.redis_client = redis_client
    app.state.orchestrator = orchestrator

    # Configure the application
    app.configure()

    return app


# Initialize application at the module level for uvicorn
def get_app() -> FastAPI:
    """Factory function to create the FastAPI app."""
    return init_app()


if __name__ == "__main__":
    app = init_app()

    # Get host and port from environment variables
    host = settings.HOST
    port = int(settings.PORT)

    # Run server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,
    )
