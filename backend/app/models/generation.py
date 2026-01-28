"""
Generation Model - Stores image generation history and metadata.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class GenerationStatus(str, Enum):
    """Status of an image generation request."""

    PENDING = "pending"
    PROCESSING = "processing"
    ENHANCING = "enhancing"
    GENERATING = "generating"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageProvider(str, Enum):
    """Image generation provider."""

    DALLE = "dalle"
    STABILITY = "stability"


class Generation(BaseModel):
    """Generation model for tracking image generation requests."""

    __tablename__ = "generations"

    # ==================== User Relationship ====================
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ==================== Prompts ====================
    original_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    enhanced_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    negative_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================== Status ====================
    status: Mapped[GenerationStatus] = mapped_column(
        SQLEnum(GenerationStatus, name="generation_status"),
        default=GenerationStatus.PENDING,
        nullable=False,
        index=True,
    )

    # ==================== Generation Settings ====================
    provider: Mapped[ImageProvider] = mapped_column(
        SQLEnum(ImageProvider, name="image_provider"),
        default=ImageProvider.DALLE,
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    style: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    size: Mapped[str] = mapped_column(
        String(20),
        default="1024x1024",
        nullable=False,
    )

    quality: Mapped[str] = mapped_column(
        String(20),
        default="standard",
        nullable=False,
    )

    # ==================== Results ====================
    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    thumbnail_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================== Metadata (RENAMED) ====================
    generation_metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False,
    )

    # ==================== Error Handling ====================
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # ==================== Timing ====================
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ==================== Relationships ====================
    user: Mapped["User"] = relationship(
        "User",
        back_populates="generations",
        lazy="selectin",
    )

    # ==================== Methods ====================
    def __repr__(self) -> str:
        return f"<Generation {self.id} status={self.status}>"

    @property
    def duration_seconds(self) -> float | None:
        """Calculate generation duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def is_complete(self) -> bool:
        return self.status in (GenerationStatus.COMPLETED, GenerationStatus.FAILED)

    @property
    def is_successful(self) -> bool:
        return self.status == GenerationStatus.COMPLETED

    def mark_processing(self) -> None:
        self.status = GenerationStatus.PROCESSING
        self.started_at = datetime.now()

    def mark_enhancing(self) -> None:
        self.status = GenerationStatus.ENHANCING

    def mark_generating(self) -> None:
        self.status = GenerationStatus.GENERATING

    def mark_uploading(self) -> None:
        self.status = GenerationStatus.UPLOADING

    def mark_completed(self, image_url: str, thumbnail_url: str | None = None) -> None:
        self.status = GenerationStatus.COMPLETED
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url
        self.completed_at = datetime.now()

    def mark_failed(self, error_message: str, error_code: str | None = None) -> None:
        self.status = GenerationStatus.FAILED
        self.error_message = error_message
        self.error_code = error_code
        self.completed_at = datetime.now()
