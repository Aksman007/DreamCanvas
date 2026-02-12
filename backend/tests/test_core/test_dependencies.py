"""
Tests for dependencies module - authentication and dependency injection.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.dependencies import (
    PaginationParams,
    get_current_active_superuser,
    get_current_token,
    get_current_user,
    get_optional_current_user,
    get_pagination,
    get_token_from_header,
)
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User

# ==================== Token Extraction Tests ====================


class TestGetTokenFromHeader:
    """Test extracting JWT token from Authorization header."""

    @pytest.mark.asyncio
    async def test_get_token_from_header_success(self):
        """Test extracting token from valid credentials."""
        # Mock HTTPAuthorizationCredentials
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid-jwt-token-here"

        token = await get_token_from_header(mock_credentials)

        assert token == "valid-jwt-token-here"

    @pytest.mark.asyncio
    async def test_get_token_from_header_no_credentials(self):
        """Test that missing credentials raises 401."""
        with pytest.raises(HTTPException) as exc_info:
            await get_token_from_header(None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


# ==================== Token Validation Tests ====================


class TestGetCurrentToken:
    """Test JWT token validation."""

    @pytest.mark.asyncio
    async def test_get_current_token_valid(self):
        """Test validating a valid access token."""
        user_id = str(uuid4())
        token = create_access_token(subject=user_id)

        payload = await get_current_token(token)

        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "access"

    @pytest.mark.asyncio
    async def test_get_current_token_invalid(self):
        """Test that invalid token raises 401."""
        invalid_token = "not-a-valid-jwt-token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"

    @pytest.mark.asyncio
    async def test_get_current_token_expired(self):
        """Test that expired token raises 401."""
        user_id = str(uuid4())
        expires_delta = timedelta(seconds=-10)  # Expired
        token = create_access_token(subject=user_id, expires_delta=expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"

    @pytest.mark.asyncio
    async def test_get_current_token_wrong_type(self):
        """Test that refresh token is rejected as access token."""
        user_id = str(uuid4())
        refresh_token = create_refresh_token(subject=user_id)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_token(refresh_token)

        assert exc_info.value.status_code == 401


# ==================== Get Current User Tests ====================


class TestGetCurrentUser:
    """Test getting current authenticated user."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, db_session, test_user):
        """Test getting user with valid token."""
        # Create token payload mock
        mock_token = MagicMock()
        mock_token.sub = str(test_user.id)

        user = await get_current_user(token=mock_token, db=db_session)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, db_session):
        """Test that non-existent user raises 401."""
        mock_token = MagicMock()
        mock_token.sub = str(uuid4())  # Random UUID that doesn't exist

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=mock_token, db=db_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User not found"

    @pytest.mark.asyncio
    async def test_get_current_user_inactive(self, db_session, inactive_user):
        """Test that inactive user raises 403."""
        mock_token = MagicMock()
        mock_token.sub = str(inactive_user.id)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=mock_token, db=db_session)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "User account is deactivated"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_uuid(self, db_session):
        """Test that invalid UUID format raises 401."""
        mock_token = MagicMock()
        mock_token.sub = "not-a-valid-uuid"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=mock_token, db=db_session)

        assert exc_info.value.status_code == 401
        assert "Invalid token: bad user ID format" in exc_info.value.detail


# ==================== Get Current Superuser Tests ====================


class TestGetCurrentSuperuser:
    """Test getting current superuser."""

    @pytest.mark.asyncio
    async def test_get_current_superuser_success(self, db_session):
        """Test that superuser can access superuser-only endpoint."""
        # Create superuser
        superuser = User(
            email="super@example.com",
            hashed_password="hashed",
            display_name="Super User",
            is_active=True,
            is_superuser=True,
        )
        db_session.add(superuser)
        await db_session.commit()
        await db_session.refresh(superuser)

        user = await get_current_active_superuser(current_user=superuser)

        assert user is not None
        assert user.is_superuser is True

    @pytest.mark.asyncio
    async def test_get_current_superuser_not_superuser(self, test_user):
        """Test that regular user is rejected from superuser endpoint."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_superuser(current_user=test_user)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Superuser access required"


# ==================== Optional Authentication Tests ====================


class TestGetOptionalCurrentUser:
    """Test optional authentication (user or None)."""

    @pytest.mark.asyncio
    async def test_get_optional_user_with_valid_token(self, db_session, test_user):
        """Test getting user with valid credentials."""
        # Mock credentials
        mock_credentials = MagicMock()
        token = create_access_token(subject=str(test_user.id))
        mock_credentials.credentials = token

        user = await get_optional_current_user(
            credentials=mock_credentials,
            db=db_session,
        )

        assert user is not None
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_get_optional_user_without_credentials(self, db_session):
        """Test that None is returned when no credentials provided."""
        user = await get_optional_current_user(
            credentials=None,
            db=db_session,
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_with_invalid_token(self, db_session):
        """Test that None is returned for invalid token."""
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"

        user = await get_optional_current_user(
            credentials=mock_credentials,
            db=db_session,
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_with_expired_token(self, db_session, test_user):
        """Test that None is returned for expired token."""
        mock_credentials = MagicMock()
        expires_delta = timedelta(seconds=-10)
        token = create_access_token(
            subject=str(test_user.id),
            expires_delta=expires_delta,
        )
        mock_credentials.credentials = token

        user = await get_optional_current_user(
            credentials=mock_credentials,
            db=db_session,
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_with_nonexistent_user(self, db_session):
        """Test that None is returned when user doesn't exist."""
        mock_credentials = MagicMock()
        random_id = str(uuid4())
        token = create_access_token(subject=random_id)
        mock_credentials.credentials = token

        user = await get_optional_current_user(
            credentials=mock_credentials,
            db=db_session,
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_with_inactive_user(self, db_session, inactive_user):
        """Test that None is returned for inactive user."""
        mock_credentials = MagicMock()
        token = create_access_token(subject=str(inactive_user.id))
        mock_credentials.credentials = token

        user = await get_optional_current_user(
            credentials=mock_credentials,
            db=db_session,
        )

        assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_with_invalid_uuid(self, db_session):
        """Test that None is returned for invalid UUID format."""
        mock_credentials = MagicMock()
        token = create_access_token(subject="not-a-uuid")
        mock_credentials.credentials = token

        user = await get_optional_current_user(
            credentials=mock_credentials,
            db=db_session,
        )

        assert user is None


# ==================== Pagination Tests ====================


class TestPagination:
    """Test pagination parameters."""

    @pytest.mark.asyncio
    async def test_get_pagination_defaults(self):
        """Test pagination with default values."""
        pagination = await get_pagination()

        assert pagination.page == 1
        assert pagination.page_size == 20
        assert pagination.offset == 0
        assert pagination.limit == 20

    @pytest.mark.asyncio
    async def test_get_pagination_custom_values(self):
        """Test pagination with custom values."""
        pagination = await get_pagination(page=3, page_size=50)

        assert pagination.page == 3
        assert pagination.page_size == 50
        assert pagination.offset == 100  # (3-1) * 50
        assert pagination.limit == 50

    @pytest.mark.asyncio
    async def test_pagination_params_calculation(self):
        """Test PaginationParams offset calculation."""
        params = PaginationParams(page=1, page_size=10)
        assert params.offset == 0

        params = PaginationParams(page=2, page_size=10)
        assert params.offset == 10

        params = PaginationParams(page=5, page_size=25)
        assert params.offset == 100

    @pytest.mark.asyncio
    async def test_pagination_params_min_page(self):
        """Test that page can't be less than 1."""
        params = PaginationParams(page=0, page_size=10)
        assert params.page == 1

        params = PaginationParams(page=-5, page_size=10)
        assert params.page == 1

    @pytest.mark.asyncio
    async def test_pagination_params_min_page_size(self):
        """Test that page_size can't be less than 1."""
        params = PaginationParams(page=1, page_size=0)
        assert params.page_size == 1

        params = PaginationParams(page=1, page_size=-10)
        assert params.page_size == 1

    @pytest.mark.asyncio
    async def test_pagination_params_max_page_size(self):
        """Test that page_size is capped at max."""
        params = PaginationParams(page=1, page_size=200, max_page_size=100)
        assert params.page_size == 100

        params = PaginationParams(page=1, page_size=1000, max_page_size=50)
        assert params.page_size == 50

    @pytest.mark.asyncio
    async def test_pagination_params_limit_property(self):
        """Test that limit property returns page_size."""
        params = PaginationParams(page=1, page_size=30)
        assert params.limit == params.page_size
        assert params.limit == 30
