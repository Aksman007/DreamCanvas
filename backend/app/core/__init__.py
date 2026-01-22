"""
Core Module

Contains security, exceptions, middleware, and dependencies.
"""

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    verify_token,
    generate_api_key,
    generate_verification_token,
    TokenPayload,
    TokenPair,
)

from app.core.exceptions import (
    DreamCanvasException,
    AuthenticationError,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError,
    MissingTokenError,
    AuthorizationError,
    InsufficientPermissionsError,
    ResourceOwnershipError,
    NotFoundError,
    AlreadyExistsError,
    ValidationError,
    BadRequestError,
    RateLimitExceededError,
    ExternalServiceError,
    ClaudeAPIError,
    ImageGenerationError,
    StorageError,
)

from app.core.dependencies import (
    SettingsDep,
    DBSession,
    TokenDep,
    CurrentUser,
    SuperUser,
    OptionalUser,
    Pagination,
    RequestID,
)

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "decode_token",
    "verify_token",
    "generate_api_key",
    "generate_verification_token",
    "TokenPayload",
    "TokenPair",
    # Exceptions
    "DreamCanvasException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "InvalidTokenError",
    "MissingTokenError",
    "AuthorizationError",
    "InsufficientPermissionsError",
    "ResourceOwnershipError",
    "NotFoundError",
    "AlreadyExistsError",
    "ValidationError",
    "BadRequestError",
    "RateLimitExceededError",
    "ExternalServiceError",
    "ClaudeAPIError",
    "ImageGenerationError",
    "StorageError",
    # Dependencies
    "SettingsDep",
    "DBSession",
    "TokenDep",
    "CurrentUser",
    "SuperUser",
    "OptionalUser",
    "Pagination",
    "RequestID",
]
