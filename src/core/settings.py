"""Application settings."""
from typing import List, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Project
    PROJECT_NAME: str = "xrouter-server"
    VERSION: str

    # Host
    HOST: str = "0.0.0.0"
    PORT: int = 8900

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Validate CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Cache
    CACHE_TTL: int = 60 * 60  # 1 hour
    CACHE_PREFIX: str = "cache"
    API_KEY_CACHE_TTL: int = 900  # 15 minutes - specific TTL for API key caching

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"  # Local Redis instance in container
    REDIS_PREFIX: str = "panda-ai"
    REDIS_PASSWORD: str = (
        ""  # Redis password for authentication when ENABLE_AUTH is True
    )

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # Доступные форматы: json, text, structured
    LOG_EXTRA_FIELDS: list[str] = []  # Дополнительные поля для логов

    # Carrot Quest
    CARROT_QUEST_WEBHOOK_TOKEN: str = (
        ""  # Token from Carrot Quest admin panel for webhook verification
    )

    # OpenAI
    OPENAI_API_KEY: str = ""  # OpenAI API key
    OPENAI_ORG_ID: str = ""  # OpenAI organization ID
    ORCHESTRATOR_MODEL: str = "gpt-4-turbo-preview"  # Model for meta-orchestrator
    OPENAI_MODELS_CACHE_TTL: int = 3600  # 1 hour - cache TTL for available models list

    class Config:
        """Configuration for settings loading."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
