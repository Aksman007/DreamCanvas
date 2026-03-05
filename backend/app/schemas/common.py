"""Common Schemas - Shared Pydantic schemas used across the application."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class PaginatedResponse(BaseSchema, Generic[T]):  # noqa: UP046
    """Generic paginated response."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(
        cls, items: list[T], total: int, page: int, page_size: int
    ) -> "PaginatedResponse[T]":
        pages = (total + page_size - 1) // page_size
        return cls(items=items, total=total, page=page, page_size=page_size, pages=pages)


class SuccessResponse(BaseSchema):
    """Generic success response."""

    success: bool = True
    message: str = "Operation completed successfully"


class ErrorResponse(BaseSchema):
    """Generic error response."""

    error: str
    message: str
    details: dict[str, Any] | None = None


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str
    service: str
    version: str
    environment: str
    checks: dict[str, str]


class TokenPair(BaseSchema):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
