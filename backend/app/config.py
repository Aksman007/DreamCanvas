"""
DreamCanvas API Configuration

Loads settings from environment variables with validation.
Uses pydantic-settings for type coercion and defaults.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden by environment variables.
    Example: APP_NAME env var overrides app_name setting.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars
    )

    # ==================== Application ====================
    app_name: str = Field(
        default="DreamCanvas API", description="Application name shown in docs"
    )
    app_version: str = Field(default="1.0.0", description="API version")
    app_description: str = Field(
        default="AI-Powered Visual Storytelling API",
        description="API description for docs",
    )
    debug: bool = Field(
        default=False, description="Enable debug mode (shows detailed errors)"
    )
    environment: str = Field(
        default="development",
        description="Current environment: development, staging, production",
    )
    api_v1_prefix: str = Field(default="/api/v1", description="API version 1 prefix")

    # ==================== Server ====================
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=True, description="Enable auto-reload in development")

    # ==================== Database ====================
    database_url: str = Field(
        default="postgresql+asyncpg://dreamcanvas:localdev123@localhost:5432/dreamcanvas",
        description="PostgreSQL async connection URL",
    )
    db_pool_size: int = Field(
        default=5, ge=1, le=20, description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        default=10, ge=0, le=20, description="Max overflow connections"
    )
    db_pool_timeout: int = Field(
        default=30, ge=5, description="Connection pool timeout in seconds"
    )
    db_echo: bool = Field(default=False, description="Echo SQL queries (for debugging)")

    # ==================== Redis ====================
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_cache_ttl: int = Field(
        default=3600, description="Default cache TTL in seconds"
    )

    # ==================== Security ====================
    secret_key: str = Field(
        default="dev-secret-key-change-in-production-min-32-chars",
        min_length=32,
        description="Secret key for JWT encoding (min 32 chars)",
    )
    algorithm: str = Field(default="HS256", description="JWT encoding algorithm")
    access_token_expire_minutes: int = Field(
        default=30, ge=5, le=1440, description="Access token expiry in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, ge=1, le=30, description="Refresh token expiry in days"
    )

    # ==================== CORS ====================
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8081",
            "http://127.0.0.1:8081",
            "exp://localhost:8081",
        ],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(
        default=True, description="Allow credentials in CORS"
    )
    cors_allow_methods: List[str] = Field(
        default=["*"], description="Allowed HTTP methods"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"], description="Allowed HTTP headers"
    )

    # ==================== External APIs ====================
    anthropic_api_key: str = Field(
        default="", description="Anthropic API key for Claude"
    )
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514", description="Claude model to use"
    )

    openai_api_key: str = Field(default="", description="OpenAI API key for DALL-E")
    openai_model: str = Field(default="dall-e-3", description="DALL-E model to use")

    stability_api_key: str = Field(default="", description="Stability AI API key")

    # ==================== Storage (S3/R2) ====================
    s3_bucket_name: str = Field(
        default="dreamcanvas-images", description="S3 bucket for image storage"
    )
    s3_region: str = Field(default="us-east-1", description="S3 region")
    s3_access_key: str = Field(default="", description="S3 access key")
    s3_secret_key: str = Field(default="", description="S3 secret key")
    s3_endpoint_url: str | None = Field(
        default=None, description="Custom S3 endpoint (for R2/MinIO)"
    )

    # ==================== Rate Limiting ====================
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(
        default=60, ge=1, description="Max requests per minute per user"
    )
    generation_limit_per_hour: int = Field(
        default=10, ge=1, description="Max image generations per hour per user"
    )

    # ==================== Celery ====================
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", description="Celery result backend URL"
    )

    # ==================== Logging ====================
    log_level: str = Field(
        default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format",
    )

    # ==================== Validators ====================
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Ensure environment is valid."""
        allowed = {"development", "staging", "production", "testing"}
        if v.lower() not in allowed:
            raise ValueError(f"environment must be one of: {allowed}")
        return v.lower()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of: {allowed}")
        return v.upper()

    # ==================== Computed Properties ====================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    @property
    def sync_database_url(self) -> str:
        """Get sync database URL for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "")

    @property
    def docs_enabled(self) -> bool:
        """Check if API docs should be enabled."""
        return not self.is_production


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are only loaded once.
    Use as FastAPI dependency: settings = Depends(get_settings)

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Global settings instance for direct imports
# Usage: from app.config import settings
settings = get_settings()
