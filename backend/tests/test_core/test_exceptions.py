"""
Tests for custom exception classes.
"""


from app.core.exceptions import (
    AccountDeactivatedError,
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ClaudeAPIError,
    ConversationNotFoundError,
    DatabaseError,
    DreamCanvasError,
    EmailAlreadyExistsError,
    ExternalServiceError,
    GenerationLimitExceededError,
    GenerationNotFoundError,
    ImageGenerationError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidInputError,
    InvalidTokenError,
    MissingTokenError,
    NotFoundError,
    RateLimitExceededError,
    ResourceOwnershipError,
    StorageError,
    TokenExpiredError,
    UserNotFoundError,
    ValidationError,
)

# ==================== Base Exception Tests ====================


class TestDreamCanvasError:
    """Test base DreamCanvas exception."""

    def test_base_exception_default(self) -> None:
        """Test base exception with defaults."""
        exc = DreamCanvasError()

        assert exc.message == "An error occurred"
        assert exc.status_code == 500
        assert exc.error_code == "DreamCanvasError"
        assert exc.details == {}

    def test_base_exception_custom_message(self) -> None:
        """Test base exception with custom message."""
        exc = DreamCanvasError(message="Custom error message")

        assert exc.message == "Custom error message"
        assert exc.status_code == 500

    def test_base_exception_custom_status_code(self) -> None:
        """Test base exception with custom status code."""
        exc = DreamCanvasError(message="Test", status_code=400)

        assert exc.status_code == 400

    def test_base_exception_custom_error_code(self) -> None:
        """Test base exception with custom error code."""
        exc = DreamCanvasError(error_code="CUSTOM_ERROR")

        assert exc.error_code == "CUSTOM_ERROR"

    def test_base_exception_with_details(self) -> None:
        """Test base exception with additional details."""
        details = {"field": "email", "value": "test@example.com"}
        exc = DreamCanvasError(details=details)

        assert exc.details == details

    def test_base_exception_to_dict(self) -> None:
        """Test converting exception to dictionary."""
        exc = DreamCanvasError(
            message="Test error",
            error_code="TEST_ERROR",
            details={"foo": "bar"},
        )

        result = exc.to_dict()

        assert result == {
            "error": "TEST_ERROR",
            "message": "Test error",
            "details": {"foo": "bar"},
        }

    def test_base_exception_str(self) -> None:
        """Test string representation of exception."""
        exc = DreamCanvasError(message="Test error")

        assert str(exc) == "Test error"


# ==================== Authentication Exception Tests ====================


class TestAuthenticationExceptions:
    """Test authentication-related exceptions."""

    def test_authentication_error(self) -> None:
        """Test base authentication error."""
        exc = AuthenticationError()

        assert exc.message == "Authentication failed"
        assert exc.status_code == 401

    def test_invalid_credentials_error(self) -> None:
        """Test invalid credentials error."""
        exc = InvalidCredentialsError()

        assert exc.message == "Invalid email or password"
        assert exc.status_code == 401
        assert exc.error_code == "INVALID_CREDENTIALS"

    def test_token_expired_error(self) -> None:
        """Test token expired error."""
        exc = TokenExpiredError()

        assert exc.message == "Token has expired"
        assert exc.status_code == 401
        assert exc.error_code == "TOKEN_EXPIRED"

    def test_invalid_token_error(self) -> None:
        """Test invalid token error."""
        exc = InvalidTokenError()

        assert exc.message == "Invalid token"
        assert exc.status_code == 401
        assert exc.error_code == "INVALID_TOKEN"

    def test_invalid_token_error_custom_reason(self) -> None:
        """Test invalid token error with custom reason."""
        exc = InvalidTokenError(reason="Token malformed")

        assert exc.message == "Token malformed"

    def test_missing_token_error(self) -> None:
        """Test missing token error."""
        exc = MissingTokenError()

        assert exc.message == "Authentication required"
        assert exc.status_code == 401
        assert exc.error_code == "MISSING_TOKEN"


# ==================== Authorization Exception Tests ====================


class TestAuthorizationExceptions:
    """Test authorization-related exceptions."""

    def test_authorization_error(self) -> None:
        """Test base authorization error."""
        exc = AuthorizationError()

        assert exc.message == "Permission denied"
        assert exc.status_code == 403
        assert exc.error_code == "FORBIDDEN"

    def test_insufficient_permissions_error(self) -> None:
        """Test insufficient permissions error."""
        exc = InsufficientPermissionsError()

        assert "permission" in exc.message.lower()
        assert exc.status_code == 403
        assert exc.error_code == "INSUFFICIENT_PERMISSIONS"

    def test_insufficient_permissions_error_with_required(self) -> None:
        """Test insufficient permissions with required permission."""
        exc = InsufficientPermissionsError(required_permission="admin")

        assert exc.details["required_permission"] == "admin"

    def test_resource_ownership_error(self) -> None:
        """Test resource ownership error."""
        exc = ResourceOwnershipError()

        assert "access" in exc.message.lower()
        assert exc.status_code == 403
        assert exc.error_code == "RESOURCE_OWNERSHIP_ERROR"

    def test_resource_ownership_error_custom_type(self) -> None:
        """Test resource ownership error with custom resource type."""
        exc = ResourceOwnershipError(resource_type="generation")

        assert "generation" in exc.message
        assert exc.details["resource_type"] == "generation"

    def test_account_deactivated_error(self) -> None:
        """Test account deactivated error."""
        exc = AccountDeactivatedError()

        assert "deactivated" in exc.message.lower()
        assert exc.status_code == 403
        assert exc.error_code == "ACCOUNT_DEACTIVATED"


# ==================== Resource Exception Tests ====================


class TestResourceExceptions:
    """Test resource-related exceptions (404, 409)."""

    def test_not_found_error(self) -> None:
        """Test base not found error."""
        exc = NotFoundError()

        assert exc.message == "Resource not found"
        assert exc.status_code == 404
        assert exc.error_code == "NOT_FOUND"

    def test_not_found_error_custom_resource_type(self) -> None:
        """Test not found error with custom resource type."""
        exc = NotFoundError(resource_type="User")

        assert exc.message == "User not found"
        assert exc.details["resource_type"] == "User"

    def test_not_found_error_with_id(self) -> None:
        """Test not found error with resource ID."""
        exc = NotFoundError(resource_type="User", resource_id="123")

        assert "123" in exc.message
        assert exc.details["resource_id"] == "123"

    def test_user_not_found_error(self) -> None:
        """Test user not found error."""
        exc = UserNotFoundError()

        assert "User" in exc.message
        assert exc.status_code == 404

    def test_user_not_found_error_with_id(self) -> None:
        """Test user not found error with ID."""
        exc = UserNotFoundError(user_id="user-123")

        assert "user-123" in exc.message

    def test_generation_not_found_error(self) -> None:
        """Test generation not found error."""
        exc = GenerationNotFoundError()

        assert "Generation" in exc.message
        assert exc.status_code == 404

    def test_generation_not_found_error_with_id(self) -> None:
        """Test generation not found error with ID."""
        exc = GenerationNotFoundError(generation_id="gen-456")

        assert "gen-456" in exc.message

    def test_conversation_not_found_error(self) -> None:
        """Test conversation not found error."""
        exc = ConversationNotFoundError()

        assert "Conversation" in exc.message
        assert exc.status_code == 404

    def test_already_exists_error(self) -> None:
        """Test already exists error."""
        exc = AlreadyExistsError()

        assert "already exists" in exc.message
        assert exc.status_code == 409
        assert exc.error_code == "ALREADY_EXISTS"

    def test_already_exists_error_custom(self) -> None:
        """Test already exists error with custom details."""
        exc = AlreadyExistsError(
            resource_type="User",
            field="email",
            value="test@example.com",
        )

        assert "User" in exc.message
        assert "email" in exc.message
        assert exc.details["value"] == "test@example.com"

    def test_email_already_exists_error(self) -> None:
        """Test email already exists error."""
        exc = EmailAlreadyExistsError()

        assert exc.status_code == 409
        assert exc.details["field"] == "email"

    def test_email_already_exists_error_with_email(self) -> None:
        """Test email already exists error with email value."""
        exc = EmailAlreadyExistsError(email="test@example.com")

        assert exc.details["value"] == "test@example.com"


# ==================== Validation Exception Tests ====================


class TestValidationExceptions:
    """Test validation-related exceptions."""

    def test_validation_error(self) -> None:
        """Test base validation error."""
        exc = ValidationError()

        assert exc.message == "Validation failed"
        assert exc.status_code == 422
        assert exc.error_code == "VALIDATION_ERROR"

    def test_validation_error_with_errors(self) -> None:
        """Test validation error with error list."""
        errors = [
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Password too short"},
        ]
        exc = ValidationError(errors=errors)

        assert exc.details["errors"] == errors

    def test_bad_request_error(self) -> None:
        """Test bad request error."""
        exc = BadRequestError()

        assert exc.message == "Bad request"
        assert exc.status_code == 400
        assert exc.error_code == "BAD_REQUEST"

    def test_bad_request_error_custom_message(self) -> None:
        """Test bad request error with custom message."""
        exc = BadRequestError(message="Invalid JSON")

        assert exc.message == "Invalid JSON"

    def test_invalid_input_error(self) -> None:
        """Test invalid input error."""
        exc = InvalidInputError(field="email", reason="Invalid format")

        assert "email" in exc.message
        assert "Invalid format" in exc.message
        assert exc.status_code == 400
        assert exc.details["field"] == "email"
        assert exc.details["reason"] == "Invalid format"


# ==================== Rate Limiting Exception Tests ====================


class TestRateLimitExceptions:
    """Test rate limiting exceptions."""

    def test_rate_limit_exceeded_error(self) -> None:
        """Test base rate limit error."""
        exc = RateLimitExceededError()

        assert "rate limit" in exc.message.lower()
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"

    def test_rate_limit_exceeded_error_custom_type(self) -> None:
        """Test rate limit error with custom limit type."""
        exc = RateLimitExceededError(limit_type="API calls")

        assert "API calls" in exc.message
        assert exc.details["limit_type"] == "API calls"

    def test_rate_limit_exceeded_error_with_retry_after(self) -> None:
        """Test rate limit error with retry_after."""
        exc = RateLimitExceededError(retry_after=3600)

        assert exc.details["retry_after_seconds"] == 3600

    def test_generation_limit_exceeded_error(self) -> None:
        """Test generation limit exceeded error."""
        exc = GenerationLimitExceededError()

        assert "generation" in exc.message.lower()
        assert exc.status_code == 429

    def test_generation_limit_exceeded_error_with_limit(self) -> None:
        """Test generation limit error with limit value."""
        exc = GenerationLimitExceededError(limit=10, retry_after=3600)

        assert exc.details["limit"] == 10
        assert exc.details["retry_after_seconds"] == 3600


# ==================== External Service Exception Tests ====================


class TestExternalServiceExceptions:
    """Test external service exceptions."""

    def test_external_service_error(self) -> None:
        """Test base external service error."""
        exc = ExternalServiceError(service="TestService")

        assert "TestService" in exc.message
        assert exc.status_code == 503
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.details["service"] == "TestService"

    def test_external_service_error_custom_message(self) -> None:
        """Test external service error with custom message."""
        exc = ExternalServiceError(
            service="TestService",
            message="Connection timeout",
        )

        assert "Connection timeout" in exc.message

    def test_claude_api_error(self) -> None:
        """Test Claude API error."""
        exc = ClaudeAPIError()

        assert "Claude AI" in exc.message
        assert exc.status_code == 503

    def test_claude_api_error_custom_message(self) -> None:
        """Test Claude API error with custom message."""
        exc = ClaudeAPIError(message="Rate limit exceeded")

        assert "Rate limit exceeded" in exc.message

    def test_image_generation_error(self) -> None:
        """Test image generation error."""
        exc = ImageGenerationError()

        assert "Image generation" in exc.message
        assert exc.status_code == 503

    def test_image_generation_error_with_provider(self) -> None:
        """Test image generation error with provider."""
        exc = ImageGenerationError(provider="DALL-E")

        assert exc.details["provider"] == "DALL-E"

    def test_storage_error(self) -> None:
        """Test storage error."""
        exc = StorageError()

        assert "Storage" in exc.message
        assert exc.status_code == 503

    def test_storage_error_with_operation(self) -> None:
        """Test storage error with operation."""
        exc = StorageError(operation="upload")

        assert exc.details["operation"] == "upload"

    def test_database_error(self) -> None:
        """Test database error."""
        exc = DatabaseError()

        assert "Database" in exc.message
        assert exc.status_code == 500
        assert exc.error_code == "DATABASE_ERROR"

    def test_database_error_custom_message(self) -> None:
        """Test database error with custom message."""
        exc = DatabaseError(message="Connection failed")

        assert exc.message == "Connection failed"


# ==================== Exception Inheritance Tests ====================


class TestExceptionInheritance:
    """Test that exceptions inherit correctly."""

    def test_all_inherit_from_base(self) -> None:
        """Test that all custom exceptions inherit from DreamCanvasError."""
        exceptions_to_test = [
            AuthenticationError(),
            AuthorizationError(),
            NotFoundError(),
            ValidationError(),
            RateLimitExceededError(),
            ExternalServiceError(service="test"),
        ]

        for exc in exceptions_to_test:
            assert isinstance(exc, DreamCanvasError)

    def test_auth_exceptions_inherit_from_authentication_error(self) -> None:
        """Test that auth exceptions inherit from AuthenticationError."""
        exceptions_to_test = [
            InvalidCredentialsError(),
            TokenExpiredError(),
            InvalidTokenError(),
            MissingTokenError(),
        ]

        for exc in exceptions_to_test:
            assert isinstance(exc, AuthenticationError)
            assert isinstance(exc, DreamCanvasError)

    def test_authz_exceptions_inherit_from_authorization_error(self) -> None:
        """Test that authz exceptions inherit from AuthorizationError."""
        exceptions_to_test = [
            InsufficientPermissionsError(),
            ResourceOwnershipError(),
            AccountDeactivatedError(),
        ]

        for exc in exceptions_to_test:
            assert isinstance(exc, AuthorizationError)
            assert isinstance(exc, DreamCanvasError)

    def test_not_found_exceptions_inherit_from_not_found_error(self) -> None:
        """Test that not found exceptions inherit from NotFoundError."""
        exceptions_to_test = [
            UserNotFoundError(),
            GenerationNotFoundError(),
            ConversationNotFoundError(),
        ]

        for exc in exceptions_to_test:
            assert isinstance(exc, NotFoundError)
            assert isinstance(exc, DreamCanvasError)
