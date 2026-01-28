"""
Generation Schemas - Pydantic schemas for image generation.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.generation import GenerationStatus, ImageProvider


# ============================================================================
# Request Schemas
# ============================================================================


class GenerationRequest(BaseModel):
    """Schema for creating a new generation request."""

    prompt: str = Field(
        min_length=1,
        max_length=4000,
        description="Text description of the image to generate",
        examples=["A serene mountain landscape at sunset with a lake reflection"],
    )

    enhance_prompt: bool = Field(
        default=True,
        description="Whether to use Claude to enhance the prompt",
    )

    negative_prompt: str | None = Field(
        default=None,
        max_length=1000,
        description="What to avoid in the image",
        examples=["blurry, low quality, distorted"],
    )

    style: str | None = Field(
        default=None,
        max_length=50,
        description="Style preset (vivid, natural, anime, photorealistic)",
        examples=["vivid"],
    )

    size: str = Field(
        default="1024x1024",
        description="Image dimensions",
        examples=["1024x1024", "1792x1024", "1024x1792"],
    )

    quality: str = Field(
        default="standard",
        description="Quality setting (standard, hd)",
        examples=["standard", "hd"],
    )

    provider: ImageProvider | None = Field(
        default=None,
        description="Image provider (dalle, stability). Uses default if not specified.",
    )

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: str) -> str:
        allowed_sizes = ["1024x1024", "1792x1024", "1024x1792", "512x512"]
        if v not in allowed_sizes:
            raise ValueError(f"Size must be one of: {', '.join(allowed_sizes)}")
        return v

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: str) -> str:
        allowed = ["standard", "hd"]
        if v not in allowed:
            raise ValueError(f"Quality must be one of: {', '.join(allowed)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "A magical forest with glowing mushrooms and fireflies",
                "enhance_prompt": True,
                "style": "vivid",
                "size": "1024x1024",
                "quality": "standard",
            }
        },
    )


class ChatRequest(BaseModel):
    """Schema for chat/prompt assistance request."""

    message: str = Field(
        min_length=1,
        max_length=2000,
        description="User's message for prompt assistance",
        examples=["Help me create a prompt for a fantasy landscape"],
    )

    conversation_history: list[dict] | None = Field(
        default=None,
        description="Previous messages in the conversation",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "I want to create an image of a dragon, but make it cute",
                "conversation_history": [
                    {"role": "user", "content": "Help me with a dragon image"},
                    {
                        "role": "assistant",
                        "content": "I'd love to help! What style are you thinking?",
                    },
                ],
            }
        },
    )


# ============================================================================
# Response Schemas
# ============================================================================


class GenerationResponse(BaseModel):
    """Schema for generation response."""

    id: UUID
    user_id: UUID
    original_prompt: str
    enhanced_prompt: str | None
    negative_prompt: str | None
    status: GenerationStatus
    provider: ImageProvider
    model: str
    style: str | None
    size: str
    quality: str
    image_url: str | None
    thumbnail_url: str | None
    error_message: str | None
    error_code: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    # Computed fields
    duration_seconds: float | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "original_prompt": "A mountain landscape",
                "enhanced_prompt": "A breathtaking mountain landscape at golden hour...",
                "status": "completed",
                "provider": "dalle",
                "model": "dall-e-3",
                "size": "1024x1024",
                "quality": "standard",
                "image_url": "https://storage.example.com/images/abc123.png",
                "thumbnail_url": "https://storage.example.com/thumbnails/abc123.png",
                "created_at": "2024-01-20T10:00:00Z",
            }
        },
    )

    @classmethod
    def from_generation(cls, generation) -> "GenerationResponse":
        """Create from Generation model with computed fields."""
        return cls(
            id=generation.id,
            user_id=generation.user_id,
            original_prompt=generation.original_prompt,
            enhanced_prompt=generation.enhanced_prompt,
            negative_prompt=generation.negative_prompt,
            status=generation.status,
            provider=generation.provider,
            model=generation.model,
            style=generation.style,
            size=generation.size,
            quality=generation.quality,
            image_url=generation.image_url,
            thumbnail_url=generation.thumbnail_url,
            error_message=generation.error_message,
            error_code=generation.error_code,
            started_at=generation.started_at,
            completed_at=generation.completed_at,
            created_at=generation.created_at,
            updated_at=generation.updated_at,
            duration_seconds=generation.duration_seconds,
        )


class GenerationListResponse(BaseModel):
    """Schema for listing generations (gallery)."""

    items: list[GenerationResponse]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "pages": 3,
            }
        },
    )


class ChatResponse(BaseModel):
    """Schema for chat/prompt assistance response."""

    message: str = Field(description="Claude's response")
    suggested_prompt: str | None = Field(
        default=None,
        description="A suggested prompt if applicable",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Here's a refined prompt for your cute dragon...",
                "suggested_prompt": "An adorable baby dragon with big sparkly eyes...",
            }
        },
    )


class PromptEnhanceResponse(BaseModel):
    """Schema for prompt enhancement response."""

    original_prompt: str
    enhanced_prompt: str
    style_suggestions: list[str] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_prompt": "A dragon",
                "enhanced_prompt": "A majestic dragon with iridescent scales...",
                "style_suggestions": ["fantasy art", "digital painting", "concept art"],
            }
        },
    )
