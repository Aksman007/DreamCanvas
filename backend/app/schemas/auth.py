"""
Auth Schemas - Pydantic schemas for authentication endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password (min 8 chars, must contain letter and number)",
        examples=["SecurePass123"],
    )
    display_name: str | None = Field(
        default=None,
        max_length=100,
        description="User's display name",
        examples=["John Doe"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "display_name": "John Doe",
            }
        },
    )


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(
        description="User's email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        description="User's password",
        examples=["SecurePass123"],
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
            }
        },
    )


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(
        description="Refresh token from login response",
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}},
    )


class TokenResponse(BaseModel):
    """Schema for token response (login/refresh)."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token expiry in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        },
    )


class UserResponseForAuth(BaseModel):
    """Simplified user response for auth endpoints."""

    id: str
    email: str
    display_name: str | None
    is_active: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_user(cls, user) -> "UserResponseForAuth":
        """Create from User model."""
        return cls(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )


class AuthResponse(BaseModel):
    """Schema for authentication response with user data."""

    user: UserResponseForAuth
    tokens: TokenResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "display_name": "John Doe",
                    "is_active": True,
                    "is_verified": False,
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIs...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                },
            }
        },
    )


# ============================================================================
# NEW: Profile Schemas for GET /me and PATCH /me
# ============================================================================


class UserProfileResponse(BaseModel):
    """
    Full user profile response for GET /auth/me.

    Contains all user information visible to the user themselves.
    """

    id: UUID
    email: EmailStr
    display_name: str | None
    avatar_url: str | None
    bio: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    preferences: dict
    generation_count: int
    last_generation_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "AI art enthusiast and digital creator",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "preferences": {"theme": "dark", "default_style": "photorealistic"},
                "generation_count": 42,
                "last_generation_at": "2024-01-15T10:30:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        },
    )


class UpdateProfileRequest(BaseModel):
    """
    Schema for updating user profile via PATCH /auth/me.

    All fields are optional - only provided fields are updated.
    """

    display_name: str | None = Field(
        default=None,
        max_length=100,
        description="User's display name",
        examples=["John Doe"],
    )
    bio: str | None = Field(
        default=None,
        max_length=500,
        description="User's biography (max 500 chars)",
        examples=["AI art enthusiast and digital creator"],
    )
    avatar_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to user's avatar image",
        examples=["https://example.com/avatar.jpg"],
    )
    preferences: dict | None = Field(
        default=None,
        description="User preferences to merge with existing",
        examples=[{"theme": "dark", "default_style": "anime"}],
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "display_name": "John Doe",
                "bio": "AI art enthusiast",
                "preferences": {"theme": "dark"},
            }
        },
    )


class UpdatePasswordRequest(BaseModel):
    """Schema for updating user password."""

    current_password: str = Field(
        description="Current password for verification",
        examples=["OldPassword123"],
    )
    new_password: str = Field(
        min_length=8,
        max_length=100,
        description="New password (min 8 chars)",
        examples=["NewSecurePass456"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldPassword123",
                "new_password": "NewSecurePass456",
            }
        },
    )
