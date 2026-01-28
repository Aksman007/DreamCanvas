"""
Generation Service - Orchestrates the image generation workflow.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.generation import Generation, GenerationStatus, ImageProvider
from app.models.user import User
from app.schemas.generation import GenerationRequest
from app.services.claude_service import get_claude_service
from app.services.image_gen_service import get_image_gen_service
from app.services.storage_service import get_storage_service

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for managing image generation workflow."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.claude = get_claude_service()
        self.image_gen = get_image_gen_service()
        self.storage = get_storage_service()

    async def create_generation(
        self,
        user: User,
        request: GenerationRequest,
    ) -> Generation:
        """
        Create a new generation record.

        Args:
            user: User making the request
            request: Generation request parameters

        Returns:
            Created Generation object
        """
        # Determine provider
        provider = request.provider or ImageProvider(settings.default_image_provider)

        # Determine model based on provider
        if provider == ImageProvider.DALLE:
            model = settings.dalle_model
        else:
            model = settings.stability_model

        # Create generation record
        generation = Generation(
            user_id=user.id,
            original_prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            status=GenerationStatus.PENDING,
            provider=provider,
            model=model,
            style=request.style,
            size=request.size,
            quality=request.quality,
        )

        self.db.add(generation)
        await self.db.commit()
        await self.db.refresh(generation)

        logger.info(f"Created generation {generation.id} for user {user.email}")
        return generation

    async def process_generation(
        self,
        generation: Generation,
        enhance_prompt: bool = True,
    ) -> Generation:
        """
        Process a generation request (enhance prompt, generate image, upload).

        Args:
            generation: Generation record to process
            enhance_prompt: Whether to use Claude to enhance the prompt

        Returns:
            Updated Generation object
        """
        try:
            # Mark as processing
            generation.mark_processing()
            await self.db.commit()

            # Step 1: Enhance prompt with Claude
            final_prompt = generation.original_prompt

            if enhance_prompt and self.claude.is_available:
                generation.mark_enhancing()
                await self.db.commit()

                try:
                    result = await self.claude.enhance_prompt(
                        prompt=generation.original_prompt,
                        style=generation.style,
                        negative_prompt=generation.negative_prompt,
                    )
                    final_prompt = result["enhanced_prompt"]
                    generation.enhanced_prompt = final_prompt

                    # Store style suggestions in metadata
                    if result.get("style_suggestions"):
                        generation.generation_metadata = {
                            **generation.generation_metadata,
                            "style_suggestions": result["style_suggestions"],
                        }
                    await self.db.commit()
                    logger.info(f"Enhanced prompt for generation {generation.id}")

                except Exception as e:
                    logger.warning(f"Failed to enhance prompt: {e}, using original")
                    generation.enhanced_prompt = None

            # Step 2: Generate image
            generation.mark_generating()
            await self.db.commit()

            image_result = await self.image_gen.generate(
                prompt=final_prompt,
                provider=generation.provider.value,
                size=generation.size,
                quality=generation.quality,
                style=generation.style,
            )

            if not image_result.success:
                generation.mark_failed(
                    error_message=image_result.error_message or "Image generation failed",
                    error_code=image_result.error_code,
                )
                await self.db.commit()
                return generation

            # Store revised prompt if DALL-E provided one
            if image_result.revised_prompt and not generation.enhanced_prompt:
                generation.enhanced_prompt = image_result.revised_prompt

            # Store generation metadata
            generation.generation_metadata = {
                **generation.generation_metadata,
                **image_result.metadata,
            }

            # Step 3: Upload to storage
            generation.mark_uploading()
            await self.db.commit()

            # Upload image (from URL or raw data)
            if image_result.image_url:
                storage_result = await self.storage.upload_from_url(
                    url=image_result.image_url,
                    create_thumbnail=True,
                )
            elif image_result.image_data:
                storage_result = await self.storage.upload_image(
                    image_data=image_result.image_data,
                    create_thumbnail=True,
                )
            else:
                generation.mark_failed(
                    error_message="No image data returned",
                    error_code="NO_IMAGE_DATA",
                )
                await self.db.commit()
                return generation

            if not storage_result.success:
                generation.mark_failed(
                    error_message=storage_result.error_message or "Upload failed",
                    error_code="UPLOAD_FAILED",
                )
                await self.db.commit()
                return generation

            # Step 4: Mark complete
            generation.mark_completed(
                image_url=storage_result.url,
                thumbnail_url=storage_result.thumbnail_url,
            )

            # Store storage key in metadata
            if storage_result.key:
                generation.generation_metadata = {
                    **generation.generation_metadata,
                    "storage_key": storage_result.key,
                }

            await self.db.commit()

            # Update user's generation count
            user_result = await self.db.execute(select(User).where(User.id == generation.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user.increment_generation_count()
                await self.db.commit()

            logger.info(f"Completed generation {generation.id}")
            return generation

        except Exception as e:
            logger.exception(f"Generation {generation.id} failed: {e}")
            generation.mark_failed(
                error_message=str(e),
                error_code="PROCESSING_ERROR",
            )
            await self.db.commit()
            return generation

    async def get_generation(
        self,
        generation_id: UUID,
        user_id: UUID | None = None,
    ) -> Generation | None:
        """
        Get a generation by ID, optionally filtered by user.

        Args:
            generation_id: Generation UUID
            user_id: Optional user ID to verify ownership

        Returns:
            Generation if found and authorized, None otherwise
        """
        query = select(Generation).where(Generation.id == generation_id)

        if user_id:
            query = query.where(Generation.user_id == user_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_generations(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: GenerationStatus | None = None,
    ) -> tuple[list[Generation], int]:
        """
        List generations for a user with pagination.

        Args:
            user_id: User UUID
            page: Page number (1-indexed)
            page_size: Items per page
            status: Optional status filter

        Returns:
            Tuple of (generations list, total count)
        """
        # Base query
        query = select(Generation).where(Generation.user_id == user_id)
        count_query = select(func.count(Generation.id)).where(Generation.user_id == user_id)

        # Apply status filter
        if status:
            query = query.where(Generation.status == status)
            count_query = count_query.where(Generation.status == status)

        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        query = query.order_by(desc(Generation.created_at)).offset(offset).limit(page_size)

        # Execute query
        result = await self.db.execute(query)
        generations = list(result.scalars().all())

        return generations, total

    async def delete_generation(
        self,
        generation: Generation,
    ) -> bool:
        """
        Delete a generation and its associated image.

        Args:
            generation: Generation to delete

        Returns:
            True if successful
        """
        # Delete from storage if there's a storage key
        if generation.generation_metadata.get("storage_key"):
            await self.storage.delete_image(generation.generation_metadata["storage_key"])

        # Delete from database
        await self.db.delete(generation)
        await self.db.commit()

        logger.info(f"Deleted generation {generation.id}")
        return True

    async def check_rate_limit(self, user: User) -> tuple[bool, str | None]:
        """
        Check if user has exceeded generation rate limit.

        Args:
            user: User to check

        Returns:
            Tuple of (is_allowed, error_message)
        """
        # Count generations in the last hour
        one_hour_ago = datetime.now().replace(microsecond=0)
        one_hour_ago = one_hour_ago.replace(
            hour=one_hour_ago.hour - 1 if one_hour_ago.hour > 0 else 23
        )

        result = await self.db.execute(
            select(func.count(Generation.id))
            .where(Generation.user_id == user.id)
            .where(Generation.created_at >= one_hour_ago)
        )
        count = result.scalar()

        limit = settings.generation_limit_per_hour

        if count >= limit:
            return False, f"Rate limit exceeded. Maximum {limit} generations per hour."

        return True, None


async def get_generation_service(db: AsyncSession) -> GenerationService:
    """Factory function to create GenerationService instance."""
    return GenerationService(db)
