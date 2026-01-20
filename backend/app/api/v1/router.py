# app/api/v1/router.py

from fastapi import APIRouter

# Import route modules (create these files as needed)
# from app.api.v1 import auth, generation, conversation, gallery, storyboard

api_router = APIRouter()

# Include sub-routers
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
# api_router.include_router(conversation.router, prefix="/chat", tags=["Conversation"])
# api_router.include_router(gallery.router, prefix="/gallery", tags=["Gallery"])
# api_router.include_router(storyboard.router, prefix="/storyboard", tags=["Storyboard"])


@api_router.get("/")
async def api_root():
    """API v1 root endpoint."""
    return {
        "message": "DreamCanvas API v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "generate": "/api/v1/generate",
            "chat": "/api/v1/chat",
            "gallery": "/api/v1/gallery",
            "storyboard": "/api/v1/storyboard",
        },
    }
