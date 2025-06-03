"""FastAPI dependencies for dependency injection."""
from typing import Annotated, cast

from fastapi import Depends, Request

from core.logger import LoggerService
from core.settings import Settings
from dreamer.agent import DreamerAgent
from mcp_clients.carrot_quest.client import CarrotQuestMCPClient
from mcp_clients.openai import OpenAIMCPClient


def get_logger(request: Request) -> LoggerService:
    """Get logger service from app state.

    Args:
        request: FastAPI request object

    Returns:
        Logger service instance
    """
    return cast(LoggerService, request.app.state.logger)


def get_settings(request: Request) -> Settings:
    """Get settings from app state.

    Args:
        request: FastAPI request object

    Returns:
        Settings instance
    """
    return cast(Settings, request.app.state.settings)


def get_dreamer_agent(request: Request) -> DreamerAgent:
    """Get Dreamer agent from app state.

    Args:
        request: FastAPI request object

    Returns:
        DreamerAgent instance
    """
    return cast(DreamerAgent, request.app.state.dreamer_agent)


def get_carrot_quest_client(
    logger: Annotated[LoggerService, Depends(get_logger)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CarrotQuestMCPClient:
    """Create Carrot Quest MCP client instance.

    Args:
        logger: Logger service instance
        settings: Settings instance

    Returns:
        CarrotQuestMCPClient instance
    """
    return CarrotQuestMCPClient(logger=logger, settings=settings)


def get_openai_client(
    logger: Annotated[LoggerService, Depends(get_logger)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> OpenAIMCPClient:
    """Create OpenAI MCP client instance.

    Args:
        logger: Logger service instance
        settings: Settings instance

    Returns:
        OpenAIMCPClient instance
    """
    return OpenAIMCPClient(logger=logger, settings=settings)
