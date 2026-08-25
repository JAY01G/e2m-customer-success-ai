"""Application Configuration Module.

Defines the centralized Pydantic BaseSettings configuration for the
AI-Powered Customer Success Platform, including database connection,
Redis caching, JWT security, CORS policies, and AI provider integration.
"""

from functools import lru_cache
from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings and environment variables.

    Reads environment variables from system environment and `.env` file,
    providing type-safe configuration with default values for local development.

    Attributes:
        APP_NAME: Name of the application service.
        APP_ENV: Current environment mode (development, testing, production).
        DEBUG: Flag indicating if debug mode is active.
        API_V1_PREFIX: URL route prefix for v1 API endpoints.
        DATABASE_URL: Relational database connection string.
        REDIS_URL: Redis cache connection string.
        REDIS_TTL: Default cache time-to-live in seconds.
        CACHE_ENABLED: Flag to toggle Redis caching globally.
        JWT_SECRET: Cryptographic secret key used for signing JWT tokens.
        JWT_ALGORITHM: Cryptographic algorithm used for JWT generation.
        ACCESS_TOKEN_EXPIRE_MINUTES: Lifetime of access tokens in minutes.
        REFRESH_TOKEN_EXPIRE_DAYS: Lifetime of refresh tokens in days.
        CORS_ORIGINS: List of allowed cross-origin resource sharing URLs.
        AI_PROVIDER: Active AI provider identifier ('mock', 'openai', 'anthropic').
        AI_API_KEY: Secret API key for external LLM services.
        AI_MODEL: Targeted LLM model identifier.
        AI_TIMEOUT: Timeout duration in seconds for LLM API calls.
        AI_TEMPERATURE: Sampling temperature for AI generation.
        RATE_LIMIT_PER_MINUTE: API request rate limit threshold.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "AI-Powered Customer Success Platform"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/customer_success_db",
        description="PostgreSQL Database Connection URL"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis Connection URL"
    )
    REDIS_TTL: int = Field(default=60, description="Default cache TTL in seconds")
    CACHE_ENABLED: bool = True

    # Security & JWT
    JWT_SECRET: str = Field(
        default="super-secret-key-change-in-production-min-32-chars-length!",
        description="Secret key for JWT generation"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # AI Configuration
    AI_PROVIDER: str = Field(default="mock", description="AI Provider: openai, anthropic, or mock")
    AI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4o-mini"
    AI_TIMEOUT: int = 20
    AI_TEMPERATURE: float = 0.2

    def model_post_init(self, __context) -> None:
        """Auto-populate AI_API_KEY from OPENAI_API_KEY or ANTHROPIC_API_KEY if not explicitly set."""
        if self.AI_PROVIDER == "mock":
            return

        if not self.AI_API_KEY:
            if self.OPENAI_API_KEY:
                self.AI_API_KEY = self.OPENAI_API_KEY
                if not self.AI_PROVIDER:
                    self.AI_PROVIDER = "openai"
            elif self.ANTHROPIC_API_KEY:
                self.AI_API_KEY = self.ANTHROPIC_API_KEY
                if not self.AI_PROVIDER:
                    self.AI_PROVIDER = "anthropic"


    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse comma-separated strings or return list for CORS origins.

        Args:
            v: Input string or list of origins.

        Returns:
            List[str]: Parsed list of trimmed origin URLs.
        """
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []



@lru_cache()
def get_settings() -> Settings:
    """Retrieve cached application settings instance.

    Uses `functools.lru_cache` to ensure settings are loaded and parsed only once per process.

    Returns:
        Settings: Singleton application configuration instance.
    """
    return Settings()

