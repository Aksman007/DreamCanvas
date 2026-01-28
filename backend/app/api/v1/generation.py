"""
Generation Router - Image generation endpoints.

Endpoints:
    POST /generate - Create and process a new image generation
    GET /generate/{id} - Get generation status/result
    DELETE /generate/{id} - Delete a generation
"""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

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
    status_code=status.HTTP_201_CREATED,
    summary="Generate an image",
    description="Create a new AI-generated image from a text prompt.",
    responses={
        201: {"description": "Generation completed"},
        400: {"description": "Invalid request or generation failed"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def create_generation(
    request: GenerationRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> GenerationResponse:
    """
    Generate an AI image from a text prompt.

    **Workflow:**
    1. Optionally enhance prompt with Claude AI
    2. Generate image with DALL-E or Stability AI
    3. Upload to storage
    4. Return result with image URLs

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

    # Process the generation
    generation = await service.process_generation(
        generation=generation,
        enhance_prompt=request.enhance_prompt,
    )

    # Check if generation failed
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
    description="Get the status and result of a generation.",
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
    - Status (pending, processing, completed, failed)
    - Original and enhanced prompts
    - Image URL and thumbnail URL (if completed)
    - Error message (if failed)

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

    await service.delete_generation(generation)

    return SuccessResponse(message="Generation deleted successfully")
