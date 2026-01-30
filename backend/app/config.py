"""
Application Configuration - Environment-based settings using Pydantic.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== Application ====================
    app_name: str = "DreamCanvas API"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered image generation platform"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # ==================== Server ====================
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    workers: int = 1

    # ==================== API ====================
    api_v1_prefix: str = "/api/v1"

    # ==================== Security ====================
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ==================== Database ====================
    database_url: str = "postgresql+asyncpg://dreamcanvas:localdev123@localhost:5432/dreamcanvas"
    sync_database_url: str = "postgresql://dreamcanvas:localdev123@localhost:5432/dreamcanvas"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_echo: bool = False

    # ==================== Redis ====================
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 3600

    # ==================== Celery ====================
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    celery_task_always_eager: bool = False  # Set True for testing without worker
    celery_task_time_limit: int = 300  # 5 minutes max per task
    celery_task_soft_time_limit: int = 270  # Soft limit before hard limit

    # ==================== CORS ====================
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8081"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # ==================== Rate Limiting ====================
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    generation_limit_per_hour: int = 10

    # ==================== Logging ====================
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ==================== Claude API (Anthropic) ====================
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 1024
    claude_temperature: float = 0.7

    # ==================== OpenAI API (DALL-E) ====================
    openai_api_key: str = ""
    dalle_model: str = "dall-e-3"
    dalle_default_size: str = "1024x1024"
    dalle_default_quality: str = "standard"
    dalle_default_style: str = "vivid"

    # ==================== Stability AI (Stable Diffusion) ====================
    stability_api_key: str = ""
    stability_model: str = "stable-diffusion-xl-1024-v1-0"

    # ==================== Image Generation ====================
    default_image_provider: Literal["dalle", "stability"] = "dalle"
    max_prompt_length: int = 4000
    generation_async: bool = True  # Use background tasks

    # ==================== Storage (S3/R2) ====================
    storage_provider: Literal["s3", "r2", "local"] = "local"
    s3_bucket_name: str = ""
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint_url: str = ""
    s3_public_url: str = ""

    local_storage_path: str = "./storage"
    local_storage_url: str = "http://localhost:8000/storage"

    # ==================== WebSocket ====================
    ws_heartbeat_interval: int = 30  # Seconds between heartbeats
    ws_max_connections_per_user: int = 5

    # ==================== Validators ====================
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper

    # ==================== Properties ====================
    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def docs_enabled(self) -> bool:
        return not self.is_production

    @property
    def has_claude(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_dalle(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_stability(self) -> bool:
        return bool(self.stability_api_key)

    @property
    def has_s3_storage(self) -> bool:
        return bool(self.s3_bucket_name and self.s3_access_key and self.s3_secret_key)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
