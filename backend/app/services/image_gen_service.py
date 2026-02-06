"""
Image Generation Service - DALL-E and Stability AI integration.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx
from openai import APIError as OpenAIAPIError
from openai import OpenAI
from openai import RateLimitError as OpenAIRateLimitError

from app.config import settings

logger = logging.getLogger(__name__)


class ImageGenerationResult:
    """Result of an image generation request."""

    def __init__(
        self,
        success: bool,
        image_url: str | None = None,
        image_data: bytes | None = None,
        revised_prompt: str | None = None,
        error_message: str | None = None,
        error_code: str | None = None,
        metadata: dict | None = None,
    ):
        self.success = success
        self.image_url = image_url
        self.image_data = image_data
        self.revised_prompt = revised_prompt
        self.error_message = error_message
        self.error_code = error_code
        self.metadata = metadata or {}


class BaseImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        **kwargs,
    ) -> ImageGenerationResult:
        """Generate an image from a prompt."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class DalleProvider(BaseImageProvider):
    """DALL-E image generation provider."""

    def __init__(self):
        if settings.has_dalle:
            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None

        self.model = settings.dalle_model
        self.default_size = settings.dalle_default_size
        self.default_quality = settings.dalle_default_quality
        self.default_style = settings.dalle_default_style

    @property
    def is_available(self) -> bool:
        return self.client is not None

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        **kwargs,
    ) -> ImageGenerationResult:
        """Generate an image using DALL-E."""
        if not self.is_available:
            return ImageGenerationResult(
                success=False,
                error_message="DALL-E is not configured",
                error_code="PROVIDER_NOT_CONFIGURED",
            )

        # Map style to DALL-E style parameter
        dalle_style = style if style in ["vivid", "natural"] else self.default_style

        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality=quality,
                style=dalle_style,
                n=1,
            )

            image_data = response.data[0]

            return ImageGenerationResult(
                success=True,
                image_url=image_data.url,
                revised_prompt=image_data.revised_prompt,
                metadata={
                    "model": self.model,
                    "size": size,
                    "quality": quality,
                    "style": dalle_style,
                },
            )

        except OpenAIRateLimitError as e:
            logger.error(f"DALL-E rate limit: {e}")
            return ImageGenerationResult(
                success=False,
                error_message="Rate limit exceeded. Please try again later.",
                error_code="RATE_LIMIT",
            )

        except OpenAIAPIError as e:
            logger.error(f"DALL-E API error: {e}")

            # Check for content policy violation
            if "content_policy_violation" in str(e).lower():
                return ImageGenerationResult(
                    success=False,
                    error_message="Your prompt was flagged by content moderation. Please revise and try again.",
                    error_code="CONTENT_POLICY",
                )

            return ImageGenerationResult(
                success=False,
                error_message=f"Image generation failed: {str(e)}",
                error_code="API_ERROR",
            )

        except Exception as e:
            logger.exception(f"Unexpected DALL-E error: {e}")
            return ImageGenerationResult(
                success=False,
                error_message="An unexpected error occurred",
                error_code="UNKNOWN_ERROR",
            )


class StabilityProvider(BaseImageProvider):
    """Stability AI image generation provider."""

    API_URL = "https://api.stability.ai/v1/generation"

    def __init__(self):
        self.api_key = settings.stability_api_key
        self.model = settings.stability_model

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        **kwargs,
    ) -> ImageGenerationResult:
        """Generate an image using Stability AI."""
        if not self.is_available:
            return ImageGenerationResult(
                success=False,
                error_message="Stability AI is not configured",
                error_code="PROVIDER_NOT_CONFIGURED",
            )

        # Parse size
        width, height = map(int, size.split("x"))

        # Map quality to steps
        steps = 50 if quality == "hd" else 30

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_URL}/{self.model}/text-to-image",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json={
                        "text_prompts": [{"text": prompt, "weight": 1.0}],
                        "cfg_scale": 7,
                        "height": height,
                        "width": width,
                        "steps": steps,
                        "samples": 1,
                    },
                    timeout=120.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    # Stability returns base64 encoded images
                    import base64

                    image_data = base64.b64decode(data["artifacts"][0]["base64"])

                    return ImageGenerationResult(
                        success=True,
                        image_data=image_data,
                        metadata={
                            "model": self.model,
                            "size": size,
                            "steps": steps,
                        },
                    )

                elif response.status_code == 429:
                    return ImageGenerationResult(
                        success=False,
                        error_message="Rate limit exceeded. Please try again later.",
                        error_code="RATE_LIMIT",
                    )

                else:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("message", "Unknown error")
                    return ImageGenerationResult(
                        success=False,
                        error_message=f"Generation failed: {error_msg}",
                        error_code="API_ERROR",
                    )

        except httpx.TimeoutException:
            return ImageGenerationResult(
                success=False,
                error_message="Request timed out. Please try again.",
                error_code="TIMEOUT",
            )

        except Exception as e:
            logger.exception(f"Stability AI error: {e}")
            return ImageGenerationResult(
                success=False,
                error_message="An unexpected error occurred",
                error_code="UNKNOWN_ERROR",
            )


class ImageGenerationService:
    """Main image generation service that coordinates providers."""

    def __init__(self):
        self.dalle = DalleProvider()
        self.stability = StabilityProvider()
        self.default_provider = settings.default_image_provider

    def get_provider(self, provider_name: str | None = None) -> BaseImageProvider:
        """Get the specified or default provider."""
        name = provider_name or self.default_provider

        if name == "dalle":
            return self.dalle
        elif name == "stability":
            return self.stability
        else:
            raise ValueError(f"Unknown provider: {name}")

    async def generate(
        self,
        prompt: str,
        provider: str | None = None,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str | None = None,
        **kwargs,
    ) -> ImageGenerationResult:
        """
        Generate an image using the specified or default provider.

        Args:
            prompt: Image generation prompt
            provider: Provider to use (dalle, stability)
            size: Image dimensions
            quality: Quality setting
            style: Style preset

        Returns:
            ImageGenerationResult with success status and image data/URL
        """
        image_provider = self.get_provider(provider)

        if not image_provider.is_available:
            # Try fallback provider
            fallback = "stability" if provider == "dalle" else "dalle"
            fallback_provider = self.get_provider(fallback)

            if fallback_provider.is_available:
                logger.info(f"Primary provider {provider} unavailable, using {fallback}")
                image_provider = fallback_provider
            else:
                return ImageGenerationResult(
                    success=False,
                    error_message="No image generation providers are configured",
                    error_code="NO_PROVIDER",
                )

        return await image_provider.generate(
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            **kwargs,
        )


# Singleton instance
_image_gen_service: ImageGenerationService | None = None


def get_image_gen_service() -> ImageGenerationService:
    """Get or create ImageGenerationService instance."""
    global _image_gen_service
    if _image_gen_service is None:
        _image_gen_service = ImageGenerationService()
    return _image_gen_service
