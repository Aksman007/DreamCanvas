# app/models/user.py

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.generation import Generation
    from app.models.conversation import Conversation
    from app.models.storyboard import Storyboard


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model for authentication and profile data.
    """

    __tablename__ = "users"

    # ============== Authentication ==============
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # ============== Profile ==============
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ============== Status Flags ==============
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ============== Preferences ==============
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # ============== Usage Tracking ==============
    generation_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_generation_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # ============== Relationships ==============
    generations: Mapped[List["Generation"]] = relationship(
        "Generation",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    storyboards: Mapped[List["Storyboard"]] = relationship(
        "Storyboard",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # ============== Methods ==============
    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def full_name(self) -> str:
        return self.display_name or self.email.split("@")[0]

    def update_preferences(self, new_prefs: dict) -> None:
        """Merge new preferences with existing ones."""
        self.preferences = {**self.preferences, **new_prefs}

    def increment_generation_count(self) -> None:
        """Increment generation counter and update timestamp."""
        self.generation_count += 1
        self.last_generation_at = datetime.now()
