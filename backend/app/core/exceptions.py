# app/core/exceptions.py

from typing import Any, Dict


class DreamCanvasException(Exception):
    """Base exception for all DreamCanvas errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: Dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ============== Authentication Errors ==============


class AuthenticationError(DreamCanvasException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401)


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    def __init__(self):
        super().__init__(message="Invalid email or password")


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""

    def __init__(self):
        super().__init__(message="Token has expired")


class InvalidTokenError(AuthenticationError):
    """Raised when a token is invalid."""

    def __init__(self):
        super().__init__(message="Invalid token")


# ============== Authorization Errors ==============


class AuthorizationError(DreamCanvasException):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class ResourceOwnershipError(AuthorizationError):
    """Raised when user doesn't own the resource."""

    def __init__(self, resource: str = "resource"):
        super().__init__(message=f"You don't have access to this {resource}")


# ============== Resource Errors ==============


class NotFoundError(DreamCanvasException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str = "Resource", identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with ID '{identifier}' not found"
        super().__init__(message=message, status_code=404)


class AlreadyExistsError(DreamCanvasException):
    """Raised when trying to create a duplicate resource."""

    def __init__(self, resource: str = "Resource", field: str = "identifier"):
        super().__init__(
            message=f"{resource} with this {field} already exists", status_code=409
        )


# ============== Validation Errors ==============


class ValidationError(DreamCanvasException):
    """Raised when validation fails."""

    def __init__(
        self, message: str = "Validation failed", details: Dict[str, Any] | None = None
    ):
        super().__init__(message=message, status_code=422, details=details)


# ============== Rate Limiting ==============


class RateLimitExceededError(DreamCanvasException):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit_type: str = "requests", retry_after: int | None = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=f"Rate limit exceeded for {limit_type}",
            status_code=429,
            details=details,
        )


class GenerationLimitExceededError(RateLimitExceededError):
    """Raised when image generation limit is exceeded."""

    def __init__(self, retry_after: int | None = None):
        super().__init__(limit_type="image generations", retry_after=retry_after)


# ============== External Service Errors ==============


class ExternalServiceError(DreamCanvasException):
    """Raised when an external service fails."""

    def __init__(self, service: str, message: str = "Service unavailable"):
        super().__init__(
            message=f"{service}: {message}",
            status_code=503,
            details={"service": service},
        )


class ClaudeAPIError(ExternalServiceError):
    """Raised when Claude API fails."""

    def __init__(self, message: str = "Claude API error"):
        super().__init__(service="Claude AI", message=message)


class ImageGenerationError(ExternalServiceError):
    """Raised when image generation fails."""

    def __init__(self, message: str = "Image generation failed"):
        super().__init__(service="Image Generation", message=message)


class StorageError(ExternalServiceError):
    """Raised when storage operations fail."""

    def __init__(self, message: str = "Storage operation failed"):
        super().__init__(service="Storage", message=message)
