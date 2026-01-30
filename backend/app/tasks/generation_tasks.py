"""
Generation Tasks - Celery tasks for image generation.
"""

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from celery import shared_task
from sqlalchemy import select

from app.celery_app import celery_app
from app.config import settings
from app.db.sync_session import get_sync_session
from app.models.generation import Generation, GenerationStatus
from app.models.user import User

logger = logging.getLogger(__name__)


def get_claude_service():
    """Get Claude service (lazy import to avoid circular imports)."""
    from app.services.claude_service import get_claude_service as _get_claude_service

    return _get_claude_service()


def get_image_gen_service():
    """Get image generation service (lazy import)."""
    from app.services.image_gen_service import get_image_gen_service as _get_image_gen_service

    return _get_image_gen_service()


def get_storage_service():
    """Get storage service (lazy import)."""
    from app.services.storage_service import get_storage_service as _get_storage_service

    return _get_storage_service()


@celery_app.task(
    bind=True,
    name="app.tasks.generation_tasks.process_generation_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
)
def process_generation_task(
    self,
    generation_id: str,
    enhance_prompt: bool = True,
) -> dict:
    """
    Process an image generation request in the background.

    Args:
        generation_id: UUID of the generation to process
        enhance_prompt: Whether to use Claude to enhance the prompt

    Returns:
        dict with status and result info
    """
    logger.info(f"Processing generation {generation_id}")

    # Get services
    claude = get_claude_service()
    image_gen = get_image_gen_service()
    storage = get_storage_service()

    with get_sync_session() as session:
        # Get the generation
        result = session.execute(select(Generation).where(Generation.id == UUID(generation_id)))
        generation = result.scalar_one_or_none()

        if generation is None:
            logger.error(f"Generation {generation_id} not found")
            return {"status": "error", "message": "Generation not found"}

        if generation.status not in (GenerationStatus.PENDING, GenerationStatus.FAILED):
            logger.warning(f"Generation {generation_id} already processed: {generation.status}")
            return {"status": "skipped", "message": f"Already {generation.status}"}

        try:
            # Mark as processing
            generation.status = GenerationStatus.PROCESSING
            generation.started_at = datetime.now(timezone.utc)
            session.commit()

            # Notify via WebSocket (if available)
            _notify_status(generation_id, "processing", "Starting generation...")

            # Step 1: Enhance prompt with Claude
            final_prompt = generation.original_prompt

            if enhance_prompt and claude.is_available:
                generation.status = GenerationStatus.ENHANCING
                session.commit()
                _notify_status(generation_id, "enhancing", "Enhancing prompt with AI...")

                try:
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(
                        claude.enhance_prompt(
                            prompt=generation.original_prompt,
                            style=generation.style,
                            negative_prompt=generation.negative_prompt,
                        )
                    )
                    loop.close()

                    final_prompt = result["enhanced_prompt"]
                    generation.enhanced_prompt = final_prompt

                    if result.get("style_suggestions"):
                        generation.generation_metadata = {
                            **generation.generation_metadata,
                            "style_suggestions": result["style_suggestions"],
                        }

                    session.commit()
                    logger.info(f"Enhanced prompt for generation {generation_id}")

                except Exception as e:
                    logger.warning(f"Failed to enhance prompt: {e}, using original")

            # Step 2: Generate image
            generation.status = GenerationStatus.GENERATING
            session.commit()
            _notify_status(generation_id, "generating", "Generating image...")

            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            image_result = loop.run_until_complete(
                image_gen.generate(
                    prompt=final_prompt,
                    provider=generation.provider.value,
                    size=generation.size,
                    quality=generation.quality,
                    style=generation.style,
                )
            )
            loop.close()

            if not image_result.success:
                raise Exception(image_result.error_message or "Image generation failed")

            # Store revised prompt if available
            if image_result.revised_prompt and not generation.enhanced_prompt:
                generation.enhanced_prompt = image_result.revised_prompt

            generation.generation_metadata = {
                **generation.generation_metadata,
                **image_result.metadata,
            }
            session.commit()

            # Step 3: Upload to storage
            generation.status = GenerationStatus.UPLOADING
            session.commit()
            _notify_status(generation_id, "uploading", "Saving image...")

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            if image_result.image_url:
                storage_result = loop.run_until_complete(
                    storage.upload_from_url(
                        url=image_result.image_url,
                        create_thumbnail=True,
                    )
                )
            elif image_result.image_data:
                storage_result = loop.run_until_complete(
                    storage.upload_image(
                        image_data=image_result.image_data,
                        create_thumbnail=True,
                    )
                )
            else:
                raise Exception("No image data returned from generator")

            loop.close()

            if not storage_result.success:
                raise Exception(storage_result.error_message or "Upload failed")

            # Step 4: Mark complete
            generation.status = GenerationStatus.COMPLETED
            generation.image_url = storage_result.url
            generation.thumbnail_url = storage_result.thumbnail_url
            generation.completed_at = datetime.now(timezone.utc)

            if storage_result.key:
                generation.generation_metadata = {
                    **generation.generation_metadata,
                    "storage_key": storage_result.key,
                }

            session.commit()

            # Update user's generation count
            user_result = session.execute(select(User).where(User.id == generation.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user.generation_count += 1
                user.last_generation_at = datetime.now(timezone.utc)
                session.commit()

            logger.info(f"Completed generation {generation_id}")
            _notify_status(
                generation_id,
                "completed",
                "Generation complete!",
                image_url=storage_result.url,
                thumbnail_url=storage_result.thumbnail_url,
            )

            return {
                "status": "completed",
                "generation_id": generation_id,
                "image_url": storage_result.url,
            }

        except Exception as e:
            logger.exception(f"Generation {generation_id} failed: {e}")

            generation.status = GenerationStatus.FAILED
            generation.error_message = str(e)
            generation.error_code = "PROCESSING_ERROR"
            generation.completed_at = datetime.now(timezone.utc)
            session.commit()

            _notify_status(generation_id, "failed", str(e))

            # Re-raise to trigger Celery retry if retries remaining
            if self.request.retries < self.max_retries:
                raise

            return {
                "status": "failed",
                "generation_id": generation_id,
                "error": str(e),
            }


@celery_app.task(
    name="app.tasks.generation_tasks.cleanup_failed_generations",
)
def cleanup_failed_generations() -> dict:
    """
    Periodic task to clean up old failed generations.

    Removes generations that:
    - Failed more than 24 hours ago
    - Are stuck in processing for more than 1 hour
    """
    logger.info("Running cleanup_failed_generations task")

    with get_sync_session() as session:
        now = datetime.now(timezone.utc)

        # Find old failed generations (older than 24 hours)
        cutoff_failed = now - timedelta(hours=24)
        failed_result = session.execute(
            select(Generation)
            .where(Generation.status == GenerationStatus.FAILED)
            .where(Generation.completed_at < cutoff_failed)
        )
        failed_generations = list(failed_result.scalars().all())

        # Find stuck generations (processing for more than 1 hour)
        cutoff_stuck = now - timedelta(hours=1)
        stuck_result = session.execute(
            select(Generation)
            .where(
                Generation.status.in_(
                    [
                        GenerationStatus.PROCESSING,
                        GenerationStatus.ENHANCING,
                        GenerationStatus.GENERATING,
                        GenerationStatus.UPLOADING,
                    ]
                )
            )
            .where(Generation.started_at < cutoff_stuck)
        )
        stuck_generations = list(stuck_result.scalars().all())

        # Mark stuck generations as failed
        for gen in stuck_generations:
            gen.status = GenerationStatus.FAILED
            gen.error_message = "Generation timed out"
            gen.error_code = "TIMEOUT"
            gen.completed_at = now

        session.commit()

        # Get storage service for cleanup
        storage = get_storage_service()

        # Delete old failed generations
        deleted_count = 0
        for gen in failed_generations:
            try:
                # Delete from storage
                if gen.generation_metadata.get("storage_key"):
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        storage.delete_image(gen.generation_metadata["storage_key"])
                    )
                    loop.close()

                session.delete(gen)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete generation {gen.id}: {e}")

        session.commit()

        logger.info(
            f"Cleanup complete: {len(stuck_generations)} stuck marked failed, "
            f"{deleted_count} old failed deleted"
        )

        return {
            "stuck_marked_failed": len(stuck_generations),
            "old_failed_deleted": deleted_count,
        }


def _notify_status(
    generation_id: str,
    status: str,
    message: str,
    **extra_data,
) -> None:
    """
    Send status notification via Redis pub/sub for WebSocket delivery.

    Args:
        generation_id: Generation UUID
        status: Current status
        message: Human-readable message
        extra_data: Additional data to include
    """
    try:
        import json
        import redis

        r = redis.from_url(settings.redis_url)

        notification = {
            "type": "generation_update",
            "generation_id": generation_id,
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **extra_data,
        }

        # Publish to channel specific to this generation
        channel = f"generation:{generation_id}"
        r.publish(channel, json.dumps(notification))

        logger.debug(f"Published notification to {channel}: {status}")

    except Exception as e:
        # Don't fail the task if notification fails
        logger.warning(f"Failed to send notification: {e}")
