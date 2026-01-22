"""
Custom Exceptions Module

Defines application-specific exceptions with HTTP status codes.
These are caught by exception handlers in main.py and converted to proper HTTP responses.
"""

from typing import Any


# ============================================================================
# BASE EXCEPTION
# ============================================================================


class DreamCanvasException(Exception):
    """
    Base exception for all DreamCanvas errors.

    All custom exceptions should inherit from this class.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code to return
        error_code: Machine-readable error code (optional)
        details: Additional error details (optional)
    """

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# ============================================================================
# AUTHENTICATION EXCEPTIONS (401)
# ============================================================================


class AuthenticationError(DreamCanvasException):
    """Base class for authentication errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
            details=details,
        )


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    def __init__(self) -> None:
        super().__init__(
            message="Invalid email or password",
            error_code="INVALID_CREDENTIALS",
        )


class TokenExpiredError(AuthenticationError):
    """Raised when a JWT token has expired."""

    def __init__(self) -> None:
        super().__init__(
            message="Token has expired",
            error_code="TOKEN_EXPIRED",
        )


class InvalidTokenError(AuthenticationError):
    """Raised when a JWT token is invalid or malformed."""

    def __init__(self, reason: str = "Invalid token") -> None:
        super().__init__(
            message=reason,
            error_code="INVALID_TOKEN",
        )


class MissingTokenError(AuthenticationError):
    """Raised when no authentication token is provided."""

    def __init__(self) -> None:
        super().__init__(
            message="Authentication required",
            error_code="MISSING_TOKEN",
        )


# ============================================================================
# AUTHORIZATION EXCEPTIONS (403)
# ============================================================================


class AuthorizationError(DreamCanvasException):
    """Base class for authorization errors."""

    def __init__(
        self,
        message: str = "Permission denied",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code or "FORBIDDEN",
            details=details,
        )


class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks required permissions."""

    def __init__(self, required_permission: str | None = None) -> None:
        details = {}
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(
            message="You don't have permission to perform this action",
            error_code="INSUFFICIENT_PERMISSIONS",
            details=details,
        )


class ResourceOwnershipError(AuthorizationError):
    """Raised when user doesn't own the requested resource."""

    def __init__(self, resource_type: str = "resource") -> None:
        super().__init__(
            message=f"You don't have access to this {resource_type}",
            error_code="RESOURCE_OWNERSHIP_ERROR",
            details={"resource_type": resource_type},
        )


class AccountDeactivatedError(AuthorizationError):
    """Raised when a deactivated account tries to access resources."""

    def __init__(self) -> None:
        super().__init__(
            message="Your account has been deactivated",
            error_code="ACCOUNT_DEACTIVATED",
        )


# ============================================================================
# RESOURCE EXCEPTIONS (404, 409)
# ============================================================================


class NotFoundError(DreamCanvasException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str = "Resource",
        resource_id: str | None = None,
    ) -> None:
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"

        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
            },
        )


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""

    def __init__(self, user_id: str | None = None) -> None:
        super().__init__(resource_type="User", resource_id=user_id)


class GenerationNotFoundError(NotFoundError):
    """Raised when a generation is not found."""

    def __init__(self, generation_id: str | None = None) -> None:
        super().__init__(resource_type="Generation", resource_id=generation_id)


class ConversationNotFoundError(NotFoundError):
    """Raised when a conversation is not found."""

    def __init__(self, conversation_id: str | None = None) -> None:
        super().__init__(resource_type="Conversation", resource_id=conversation_id)


class AlreadyExistsError(DreamCanvasException):
    """Raised when trying to create a duplicate resource."""

    def __init__(
        self,
        resource_type: str = "Resource",
        field: str = "identifier",
        value: str | None = None,
    ) -> None:
        message = f"{resource_type} with this {field} already exists"

        super().__init__(
            message=message,
            status_code=409,
            error_code="ALREADY_EXISTS",
            details={
                "resource_type": resource_type,
                "field": field,
                "value": value,
            },
        )


class EmailAlreadyExistsError(AlreadyExistsError):
    """Raised when email is already registered."""

    def __init__(self, email: str | None = None) -> None:
        super().__init__(
            resource_type="User",
            field="email",
            value=email,
        )


# ============================================================================
# VALIDATION EXCEPTIONS (400, 422)
# ============================================================================


class ValidationError(DreamCanvasException):
    """Raised when request validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"errors": errors or []},
        )


class BadRequestError(DreamCanvasException):
    """Raised for malformed or invalid requests."""

    def __init__(
        self,
        message: str = "Bad request",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details,
        )


class InvalidInputError(BadRequestError):
    """Raised when input data is invalid."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            message=f"Invalid {field}: {reason}",
            details={"field": field, "reason": reason},
        )


# ============================================================================
# RATE LIMITING EXCEPTIONS (429)
# ============================================================================


class RateLimitExceededError(DreamCanvasException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        limit_type: str = "requests",
        retry_after: int | None = None,
    ) -> None:
        details: dict[str, Any] = {"limit_type": limit_type}
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=f"Rate limit exceeded for {limit_type}",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class GenerationLimitExceededError(RateLimitExceededError):
    """Raised when image generation limit is exceeded."""

    def __init__(
        self,
        limit: int | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(
            limit_type="image generations",
            retry_after=retry_after,
        )
        if limit:
            self.details["limit"] = limit


# ============================================================================
# EXTERNAL SERVICE EXCEPTIONS (502, 503)
# ============================================================================


class ExternalServiceError(DreamCanvasException):
    """Base class for external service errors."""

    def __init__(
        self,
        service: str,
        message: str = "Service unavailable",
        details: dict[str, Any] | None = None,
    ) -> None:
        full_details = {"service": service}
        if details:
            full_details.update(details)

        super().__init__(
            message=f"{service}: {message}",
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=full_details,
        )


class ClaudeAPIError(ExternalServiceError):
    """Raised when Claude API fails."""

    def __init__(
        self,
        message: str = "Failed to communicate with Claude AI",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            service="Claude AI",
            message=message,
            details=details,
        )


class ImageGenerationError(ExternalServiceError):
    """Raised when image generation fails."""

    def __init__(
        self,
        message: str = "Image generation failed",
        provider: str = "unknown",
        details: dict[str, Any] | None = None,
    ) -> None:
        full_details = {"provider": provider}
        if details:
            full_details.update(details)

        super().__init__(
            service="Image Generation",
            message=message,
            details=full_details,
        )


class StorageError(ExternalServiceError):
    """Raised when storage operations fail."""

    def __init__(
        self,
        message: str = "Storage operation failed",
        operation: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        full_details: dict[str, Any] = {}
        if operation:
            full_details["operation"] = operation
        if details:
            full_details.update(details)

        super().__init__(
            service="Storage",
            message=message,
            details=full_details,
        )


class DatabaseError(DreamCanvasException):
    """Raised when database operations fail."""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )
