"""Schemas Module - All Pydantic schemas are exported from here."""

from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UpdatePasswordRequest,
    UpdateProfileRequest,
    UserProfileResponse,
    UserResponseForAuth,
)
from app.schemas.common import (
    BaseSchema,
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    SuccessResponse,
    TokenPair,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserPublicResponse,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # Common
    "BaseSchema",
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "SuccessResponse",
    "TokenPair",
    # User
    "UserCreate",
    "UserLogin",
    "UserPublicResponse",
    "UserResponse",
    "UserUpdate",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "AuthResponse",
    "UserResponseForAuth",
    "UserProfileResponse",
    "UpdateProfileRequest",
    "UpdatePasswordRequest",
]
