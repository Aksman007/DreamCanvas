"""
User Model - Defines the User database model.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel

if TYPE_CHECKING:
    pass  # Future imports for relationships


class User(BaseModel):
    """User model for authentication and profile data."""

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Profile
    display_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Status Flags
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Preferences (JSON)
    preferences: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False,
    )

    # Usage Tracking
    generation_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_generation_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def full_name(self) -> str:
        """Get user's display name or email username."""
        if self.display_name:
            return self.display_name
        return self.email.split("@")[0]

    def update_preferences(self, new_prefs: dict) -> None:
        """Merge new preferences with existing ones."""
        self.preferences = {**self.preferences, **new_prefs}

    def increment_generation_count(self) -> None:
        """Increment generation counter and update timestamp."""
        self.generation_count += 1
        self.last_generation_at = datetime.now()
