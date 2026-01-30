"""
Generation Router - Image generation endpoints.

Endpoints:
    POST /generate - Create a new image generation (async or sync)
    GET /generate/{id} - Get generation status/result
    GET /generate/{id}/status - Get just the status (for polling)
    DELETE /generate/{id} - Delete a generation
"""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.config import settings
from app.core.dependencies import CurrentUser, DBSession
from app.models.generation import GenerationStatus
from app.schemas.common import SuccessResponse
from app.schemas.generation import GenerationRequest, GenerationResponse
from app.services.generation_service import GenerationService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=GenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate an image",
    description="Create a new AI-generated image from a text prompt.",
    responses={
        202: {"description": "Generation accepted (async) or completed (sync)"},
        400: {"description": "Invalid request"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def create_generation(
    request: GenerationRequest,
    current_user: CurrentUser,
    db: DBSession,
    sync: bool = Query(
        default=False,
        description="Run synchronously (wait for completion). Default is async.",
    ),
) -> GenerationResponse:
    """
    Generate an AI image from a text prompt.

    **Async Mode (default):**
    - Returns immediately with generation ID and status "pending"
    - Use WebSocket or polling to get updates
    - Connect to: `ws://localhost:8000/api/v1/ws/generations?token=YOUR_TOKEN`

    **Sync Mode (`?sync=true`):**
    - Waits for generation to complete
    - Returns with final result (image URLs or error)
    - May timeout for long generations

    **Parameters:**
    - `prompt`: Text description of the image (required)
    - `enhance_prompt`: Use Claude to improve the prompt (default: true)
    - `style`: Style preset (vivid, natural, anime, photorealistic)
    - `size`: Image dimensions (1024x1024, 1792x1024, 1024x1792)
    - `quality`: Quality setting (standard, hd)
    - `provider`: Image provider (dalle, stability)

    **Requires Authentication**
    """
    service = GenerationService(db)

    # Check rate limit
    is_allowed, error_msg = await service.check_rate_limit(current_user)
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg,
        )

    # Create generation record
    generation = await service.create_generation(
        user=current_user,
        request=request,
    )

    # Determine if we should run async or sync
    run_async = settings.generation_async and not sync

    if run_async:
        # Queue the task with Celery
        from app.tasks.generation_tasks import process_generation_task

        task = process_generation_task.delay(
            generation_id=str(generation.id),
            enhance_prompt=request.enhance_prompt,
        )

        # Store task ID in metadata
        generation.generation_metadata = {
            **generation.generation_metadata,
            "celery_task_id": task.id,
        }
        await db.commit()
        await db.refresh(generation)

        logger.info(f"Queued generation {generation.id} as task {task.id}")
    else:
        # Process synchronously
        generation = await service.process_generation(
            generation=generation,
            enhance_prompt=request.enhance_prompt,
        )

        if generation.status == GenerationStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=generation.error_message or "Generation failed",
            )

    return GenerationResponse.from_generation(generation)


@router.get(
    "/{generation_id}",
    response_model=GenerationResponse,
    summary="Get generation",
    description="Get the full details of a generation.",
    responses={
        200: {"description": "Generation found"},
        404: {"description": "Generation not found"},
    },
)
async def get_generation(
    generation_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> GenerationResponse:
    """
    Get a generation by ID.

    Returns the full generation details including:
    - Status (pending, processing, enhancing, generating, uploading, completed, failed)
    - Original and enhanced prompts
    - Image URL and thumbnail URL (if completed)
    - Error message (if failed)
    - Timing information

    **Requires Authentication** - Users can only access their own generations.
    """
    service = GenerationService(db)

    generation = await service.get_generation(
        generation_id=generation_id,
        user_id=current_user.id,
    )

    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found",
        )

    return GenerationResponse.from_generation(generation)


@router.get(
    "/{generation_id}/status",
    summary="Get generation status",
    description="Get just the status of a generation (for polling).",
    responses={
        200: {"description": "Status retrieved"},
        404: {"description": "Generation not found"},
    },
)
async def get_generation_status(
    generation_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """
    Get just the status of a generation.

    Lighter endpoint for polling. Returns:
    - `status`: Current status
    - `message`: Human-readable message
    - `image_url`: URL if completed
    - `error`: Error message if failed

    **Requires Authentication**
    """
    service = GenerationService(db)

    generation = await service.get_generation(
        generation_id=generation_id,
        user_id=current_user.id,
    )

    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found",
        )

    # Build status response
    response = {
        "generation_id": str(generation.id),
        "status": generation.status.value,
        "message": _get_status_message(generation.status),
    }

    if generation.status == GenerationStatus.COMPLETED:
        response["image_url"] = generation.image_url
        response["thumbnail_url"] = generation.thumbnail_url
    elif generation.status == GenerationStatus.FAILED:
        response["error"] = generation.error_message

    return response


@router.delete(
    "/{generation_id}",
    response_model=SuccessResponse,
    summary="Delete generation",
    description="Delete a generation and its associated image.",
    responses={
        200: {"description": "Generation deleted"},
        404: {"description": "Generation not found"},
    },
)
async def delete_generation(
    generation_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> SuccessResponse:
    """
    Delete a generation.

    This will:
    - Cancel the task if still processing
    - Delete the generation record from the database
    - Delete the associated image from storage

    **Requires Authentication** - Users can only delete their own generations.
    """
    service = GenerationService(db)

    generation = await service.get_generation(
        generation_id=generation_id,
        user_id=current_user.id,
    )

    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found",
        )

    # Cancel Celery task if still running
    task_id = generation.generation_metadata.get("celery_task_id")
    if task_id and generation.status in (
        GenerationStatus.PENDING,
        GenerationStatus.PROCESSING,
        GenerationStatus.ENHANCING,
        GenerationStatus.GENERATING,
        GenerationStatus.UPLOADING,
    ):
        from app.celery_app import celery_app

        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"Cancelled task {task_id} for generation {generation_id}")

    await service.delete_generation(generation)

    return SuccessResponse(message="Generation deleted successfully")


def _get_status_message(status: GenerationStatus) -> str:
    """Get human-readable message for status."""
    messages = {
        GenerationStatus.PENDING: "Waiting to start...",
        GenerationStatus.PROCESSING: "Starting generation...",
        GenerationStatus.ENHANCING: "Enhancing prompt with AI...",
        GenerationStatus.GENERATING: "Generating image...",
        GenerationStatus.UPLOADING: "Saving image...",
        GenerationStatus.COMPLETED: "Generation complete!",
        GenerationStatus.FAILED: "Generation failed",
    }
    return messages.get(status, "Unknown status")
