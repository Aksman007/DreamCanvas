"""
Tests for authentication API endpoints.

Endpoints tested:
    - POST /api/v1/auth/register
    - POST /api/v1/auth/login
    - POST /api/v1/auth/refresh
    - GET /api/v1/auth/me
    - PATCH /api/v1/auth/me
"""

import pytest
from fastapi import status

# ==================== Registration Tests ====================


class TestRegister:
    """Test POST /api/v1/auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test successful user registration."""
        response = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check response structure
        assert "user" in data
        assert "tokens" in data

        # Check user data
        user = data["user"]
        assert user["email"] == user_data["email"]
        assert user["display_name"] == user_data["display_name"]
        assert "id" in user
        assert user["is_active"] is True
        assert user["is_verified"] is False

        # Check tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] > 0

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client, test_user, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test registration with duplicate email fails."""
        # Use existing user's email
        user_data["email"] = test_user.email

        response = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "already registered" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test registration with invalid email format."""
        user_data["email"] = "not-a-valid-email"

        response = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test registration with weak password."""
        user_data["password"] = "weak"  # Too short

        response = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_missing_email(self, async_client, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test registration without email."""
        del user_data["email"]

        response = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_missing_password(self, async_client, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test registration without password."""
        del user_data["password"]

        response = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_empty_display_name(self, async_client, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test registration with empty display name."""
        user_data["display_name"] = ""

        response = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_email_case_insensitive(self, async_client, user_data) -> None:  # type: ignore[no-untyped-def]
        """Test that email registration is case-insensitive."""
        # Register with lowercase
        response1 = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to register with uppercase (should fail)
        user_data["email"] = user_data["email"].upper()
        response2 = await async_client.post("/api/v1/auth/register", json=user_data)

        assert response2.status_code == status.HTTP_400_BAD_REQUEST


# ==================== Login Tests ====================


class TestLogin:
    """Test POST /api/v1/auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test successful login with valid credentials."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "password123"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check response structure
        assert "user" in data
        assert "tokens" in data

        # Check user data
        user = data["user"]
        assert user["email"] == test_user.email
        assert user["id"] == str(test_user.id)

        # Check tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test login with non-existent email."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, async_client, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test login with wrong password."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, async_client, inactive_user) -> None:  # type: ignore[no-untyped-def]
        """Test login with deactivated account."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": inactive_user.email, "password": "password123"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "deactivated" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_missing_email(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test login without email."""
        response = await async_client.post("/api/v1/auth/login", json={"password": "password123"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_login_missing_password(self, async_client, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test login without password."""
        response = await async_client.post("/api/v1/auth/login", json={"email": test_user.email})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_login_case_insensitive_email(self, async_client, test_user) -> None:  # type: ignore[no-untyped-def]
        """Test that login email is case-insensitive."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email.upper(), "password": "password123"},
        )

        assert response.status_code == status.HTTP_200_OK


# ==================== Token Refresh Tests ====================


class TestRefreshToken:
    """Test POST /api/v1/auth/refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client, test_user, refresh_token) -> None:  # type: ignore[no-untyped-def]
        """Test successful token refresh."""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check new tokens
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

        # New tokens should be different
        assert data["access_token"] != data["refresh_token"]

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test refresh with invalid token."""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-here"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_token_using_access_token(self, async_client, auth_token) -> None:  # type: ignore[no-untyped-def]
        """Test that access token cannot be used as refresh token."""
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_token},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_token_missing(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test refresh without token."""
        response = await async_client.post("/api/v1/auth/refresh", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_refresh_token_for_deleted_user(self, async_client, db_session) -> None:  # type: ignore[no-untyped-def]
        """Test refresh token fails if user is deleted."""
        # Create and delete a user
        from app.core.security import create_token_pair, hash_password
        from app.models.user import User

        user = User(
            email="delete-me@example.com",
            hashed_password=hash_password("password123"),
            display_name="Delete Me",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create token
        tokens = create_token_pair(str(user.id))

        # Delete user
        await db_session.delete(user)
        await db_session.commit()

        # Try to refresh
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens.refresh_token},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== Get Current User Tests ====================


class TestGetCurrentUser:
    """Test GET /api/v1/auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, async_client, test_user, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test getting current user profile."""
        response = await async_client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check user data
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["display_name"] == test_user.display_name
        assert "created_at" in data
        assert "updated_at" in data
        assert data["is_active"] is True

        # Check no sensitive data
        assert "hashed_password" not in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_no_auth(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test getting current user without authentication."""
        response = await async_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test getting current user with invalid token."""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_malformed_auth_header(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test with malformed authorization header."""
        # Missing 'Bearer' prefix
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "some-token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== Update Profile Tests ====================


class TestUpdateProfile:
    """Test PATCH /api/v1/auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_update_display_name(self, async_client, test_user, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating display name."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"display_name": "New Name"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["display_name"] == "New Name"
        assert data["email"] == test_user.email  # Unchanged

    @pytest.mark.asyncio
    async def test_update_bio(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating bio."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"bio": "This is my new bio"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bio"] == "This is my new bio"

    @pytest.mark.asyncio
    async def test_update_avatar_url(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating avatar URL."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"avatar_url": "https://example.com/avatar.jpg"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["avatar_url"] == "https://example.com/avatar.jpg"

    @pytest.mark.asyncio
    async def test_update_preferences(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating user preferences."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"preferences": {"theme": "dark", "notifications": True}},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["preferences"]["theme"] == "dark"
        assert data["preferences"]["notifications"] is True

    @pytest.mark.asyncio
    async def test_update_preferences_merge(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test that preferences are merged, not replaced."""
        # Set initial preferences
        await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"preferences": {"theme": "dark", "language": "en"}},
        )

        # Update with new preference (should merge)
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"preferences": {"notifications": True}},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should have both old and new preferences
        assert data["preferences"]["theme"] == "dark"
        assert data["preferences"]["language"] == "en"
        assert data["preferences"]["notifications"] is True

    @pytest.mark.asyncio
    async def test_update_multiple_fields(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating multiple fields at once."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={
                "display_name": "Updated Name",
                "bio": "Updated bio",
                "avatar_url": "https://example.com/new-avatar.jpg",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["display_name"] == "Updated Name"
        assert data["bio"] == "Updated bio"
        assert data["avatar_url"] == "https://example.com/new-avatar.jpg"

    @pytest.mark.asyncio
    async def test_update_profile_no_auth(self, async_client) -> None:  # type: ignore[no-untyped-def]
        """Test updating profile without authentication."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            json={"display_name": "New Name"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_update_profile_no_changes(self, async_client, test_user, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating with no fields returns current profile."""
        response = await async_client.patch("/api/v1/auth/me", headers=auth_headers, json={})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["display_name"] == test_user.display_name

    @pytest.mark.asyncio
    async def test_update_profile_invalid_display_name(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating with invalid display name."""
        # Display name too long
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"display_name": "x" * 101},  # Max is 100
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_update_profile_invalid_bio(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test updating with invalid bio."""
        # Bio too long
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"bio": "x" * 501},  # Max is 500
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_cannot_update_email(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test that email cannot be updated via this endpoint."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"email": "newemail@example.com"},
        )

        # Email should be ignored (not in UpdateProfileRequest schema)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] != "newemail@example.com"

    @pytest.mark.asyncio
    async def test_cannot_update_is_active(self, async_client, auth_headers) -> None:  # type: ignore[no-untyped-def]
        """Test that is_active cannot be updated via this endpoint."""
        response = await async_client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={"is_active": False},
        )

        # is_active should be ignored
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is True
