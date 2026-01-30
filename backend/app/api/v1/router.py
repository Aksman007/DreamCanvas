"""
API v1 Router - Aggregates all v1 API routes.
"""

from fastapi import APIRouter

from app.api.v1 import auth, chat, gallery, generation, websocket
from app.core.dependencies import CurrentUser, OptionalUser
from app.core.security import create_token_pair

# Create main API router
api_router = APIRouter()


# ==================== Include Sub-Routers ====================

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    generation.router,
    prefix="/generate",
    tags=["Image Generation"],
)

api_router.include_router(
    gallery.router,
    prefix="/gallery",
    tags=["Gallery"],
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"],
)


# ==================== API Root ====================


@api_router.get(
    "/",
    summary="API v1 Root",
    tags=["API Info"],
)
async def api_v1_root():
    """API v1 root endpoint - lists available endpoints."""
    return {
        "message": "DreamCanvas API v1",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/login",
                "refresh": "POST /api/v1/auth/refresh",
                "me": "GET /api/v1/auth/me",
                "update_profile": "PATCH /api/v1/auth/me",
            },
            "generate": {
                "create": "POST /api/v1/generate",
                "get": "GET /api/v1/generate/{id}",
                "status": "GET /api/v1/generate/{id}/status",
                "delete": "DELETE /api/v1/generate/{id}",
            },
            "gallery": {
                "list": "GET /api/v1/gallery",
            },
            "chat": {
                "chat": "POST /api/v1/chat",
                "enhance": "POST /api/v1/chat/enhance",
            },
            "websocket": {
                "generations": "WS /api/v1/ws/generations?token=JWT_TOKEN",
            },
        },
    }


# ==================== Test Endpoints ====================


@api_router.post(
    "/test/token",
    summary="Generate test token",
    tags=["Testing"],
)
async def generate_test_token(user_id: str = "test-user-123"):
    """Generate a test JWT token pair. FOR DEVELOPMENT ONLY."""
    tokens = create_token_pair(subject=user_id)
    return {
        "message": "Test tokens generated",
        "user_id": user_id,
        "tokens": tokens.model_dump(),
    }


@api_router.get(
    "/test/protected",
    summary="Test protected endpoint",
    tags=["Testing"],
)
async def test_protected_endpoint(current_user: CurrentUser):
    """Test endpoint that requires authentication."""
    return {
        "message": "You are authenticated!",
        "user_id": str(current_user.id),
        "email": current_user.email,
    }


@api_router.get(
    "/test/optional-auth",
    summary="Test optional auth endpoint",
    tags=["Testing"],
)
async def test_optional_auth(user: OptionalUser):
    """Test endpoint that works with or without authentication."""
    if user:
        return {"authenticated": True, "user_id": str(user.id), "email": user.email}
    return {"authenticated": False, "message": "Anonymous access"}
