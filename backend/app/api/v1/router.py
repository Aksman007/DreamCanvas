"""
API v1 Router

Aggregates all v1 API routes.
"""

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, OptionalUser, TokenDep
from app.core.security import create_token_pair, hash_password, verify_password

# Create main API router
api_router = APIRouter()


# ==================== API Root ====================


@api_router.get(
    "/",
    summary="API v1 Root",
)
async def api_v1_root():
    """API v1 root endpoint."""
    return {
        "message": "DreamCanvas API v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "generate": "/api/v1/generate",
            "chat": "/api/v1/chat",
            "gallery": "/api/v1/gallery",
        },
    }


# ==================== Test Auth Endpoints ====================


@api_router.post(
    "/test/token",
    summary="Generate test token",
    tags=["Testing"],
)
async def generate_test_token(user_id: str = "test-user-123"):
    """
    Generate a test JWT token pair.

    FOR DEVELOPMENT/TESTING ONLY.
    """
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
    """
    Test endpoint that requires authentication.

    Use the access_token from /test/token in the Authorization header:
    Authorization: Bearer <access_token>
    """
    return {
        "message": "You are authenticated!",
        "user_id": current_user.id,
        "email": current_user.email,
    }


@api_router.get(
    "/test/optional-auth",
    summary="Test optional auth endpoint",
    tags=["Testing"],
)
async def test_optional_auth(user: OptionalUser):
    """
    Test endpoint that works with or without authentication.
    """
    if user:
        return {
            "authenticated": True,
            "user_id": user.id,
        }
    return {
        "authenticated": False,
        "message": "Anonymous access",
    }


@api_router.post(
    "/test/password",
    summary="Test password hashing",
    tags=["Testing"],
)
async def test_password_hashing(password: str = "testpassword123"):
    """
    Test password hashing and verification.

    FOR DEVELOPMENT/TESTING ONLY.
    """
    hashed = hash_password(password)
    is_valid = verify_password(password, hashed)

    return {
        "original": password,
        "hashed": hashed,
        "verification": is_valid,
    }


# ==================== Include Sub-Routers (TODO: Phase 5) ====================

# from app.api.v1 import auth, generation, conversation, gallery
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
