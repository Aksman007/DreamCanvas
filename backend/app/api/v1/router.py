"""
API v1 Router

Aggregates all v1 API routes.
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()


# ==================== API Root ====================


@api_router.get(
    "/",
    summary="API v1 Root",
    description="Returns available API v1 endpoints",
)
async def api_v1_root():
    """
    API v1 root endpoint.

    Lists all available endpoint groups.
    """
    return {
        "message": "DreamCanvas API v1",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth - Authentication (TODO)",
            "generate": "/api/v1/generate - Image Generation (TODO)",
            "chat": "/api/v1/chat - Claude Conversation (TODO)",
            "gallery": "/api/v1/gallery - User Gallery (TODO)",
            "storyboard": "/api/v1/storyboard - Storyboards (TODO)",
        },
    }


# ==================== Include Sub-Routers (TODO: Phase 5) ====================

# from app.api.v1 import auth, generation, conversation, gallery, storyboard
#
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
# api_router.include_router(conversation.router, prefix="/chat", tags=["Conversation"])
# api_router.include_router(gallery.router, prefix="/gallery", tags=["Gallery"])
# api_router.include_router(storyboard.router, prefix="/storyboard", tags=["Storyboard"])
