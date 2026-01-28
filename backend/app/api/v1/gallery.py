"""
Gallery Router - List user's generations.

Endpoints:
    GET /gallery - List user's generations with pagination
"""

import logging

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DBSession
from app.models.generation import GenerationStatus
from app.schemas.generation import GenerationListResponse, GenerationResponse
from app.services.generation_service import GenerationService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=GenerationListResponse,
    summary="List generations",
    description="Get a paginated list of the user's image generations.",
    responses={
        200: {"description": "Generations retrieved"},
    },
)
async def list_generations(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: GenerationStatus | None = Query(default=None, description="Filter by status"),
) -> GenerationListResponse:
    """
    List user's image generations.

    **Pagination:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)

    **Filtering:**
    - `status`: Filter by generation status (pending, processing, completed, failed)

    **Ordering:**
    - Results are ordered by creation date (newest first)

    **Requires Authentication**
    """
    service = GenerationService(db)

    generations, total = await service.list_generations(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status,
    )

    pages = (total + page_size - 1) // page_size

    return GenerationListResponse(
        items=[GenerationResponse.from_generation(g) for g in generations],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
