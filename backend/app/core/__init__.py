"""
Core Module - Contains security, exceptions, middleware, and dependencies.
"""

from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ClaudeAPIError,
    DreamCanvasError,
    ExternalServiceError,
    ImageGenerationError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidTokenError,
    MissingTokenError,
    NotFoundError,
    RateLimitExceededError,
    ResourceOwnershipError,
    StorageError,
    TokenExpiredError,
    ValidationError,
)
from app.core.security import (
    TokenPair,
    TokenPayload,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    generate_api_key,
    generate_verification_token,
    hash_password,
    verify_password,
    verify_token,
)

# Note: Don't import dependencies here to avoid circular imports
# Import them directly where needed: from app.core.dependencies import ...

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
    "DreamCanvasError",
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
]
