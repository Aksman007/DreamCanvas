"""User Schemas - Pydantic schemas for User model validation and serialization."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    display_name: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

    model_config = ConfigDict(str_strip_whitespace=True)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str

    model_config = ConfigDict(str_strip_whitespace=True)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    display_name: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(str_strip_whitespace=True)


class UserResponse(BaseModel):
    """Schema for user API responses."""

    id: UUID
    email: EmailStr
    display_name: str | None
    avatar_url: str | None
    bio: str | None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    generation_count: int
    last_generation_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPublicResponse(BaseModel):
    """Schema for public user data (visible to other users)."""

    id: UUID
    display_name: str | None
    avatar_url: str | None
    bio: str | None
    generation_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
