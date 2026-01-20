# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for validation and type coercion.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # ============== Application ==============
    app_name: str = "DreamCanvas API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(
        default="development", pattern="^(development|staging|production)$"
    )
    api_v1_prefix: str = "/api/v1"

    # ============== Server ==============
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # ============== Database ==============
    database_url: str = Field(
        default="postgresql+asyncpg://dreamcanvas:localdev123@localhost:5432/dreamcanvas",
        description="PostgreSQL connection string (async)",
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_echo: bool = False  # Set True to log SQL queries

    # ============== Redis ==============
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    redis_cache_ttl: int = 3600  # 1 hour default cache TTL

    # ============== Security ==============
    secret_key: str = Field(
        default="change-me-in-production-use-openssl-rand-hex-32",
        min_length=32,
        description="Secret key for JWT encoding",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8081"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # ============== External APIs ==============
    anthropic_api_key: str = Field(
        default="", description="Anthropic API key for Claude"
    )
    anthropic_model: str = "claude-sonnet-4-20250514"

    openai_api_key: str = Field(default="", description="OpenAI API key for DALL-E")

    stability_api_key: str = Field(default="", description="Stability AI API key")

    # ============== Storage (S3/R2) ==============
    s3_bucket_name: str = "dreamcanvas-images"
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint_url: str | None = None  # For Cloudflare R2 or MinIO

    # ============== Rate Limiting ==============
    rate_limit_per_minute: int = 60
    generation_limit_per_hour: int = 10

    # ============== Celery ==============
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    @property
    def sync_database_url(self) -> str:
        """Convert async URL to sync for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Use dependency injection to access: settings = Depends(get_settings)
    """
    return Settings()


# Global settings instance for direct imports
settings = get_settings()
