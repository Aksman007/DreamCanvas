"""DreamCanvas API - Main Application Entry Point"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import DreamCanvasException
from app.core.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.db.init_db import init_db as initialize_database
from app.db.session import check_db_connection, close_db, init_db

# Logging
logging.basicConfig(level=getattr(logging, settings.log_level), format=settings.log_format)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info(f"🤖 Claude: {'✅' if settings.has_claude else '❌'}")
    logger.info(f"🎨 DALL-E: {'✅' if settings.has_dalle else '❌'}")
    logger.info(f"💾 Storage: {settings.storage_provider}")
    logger.info(f"⚡ Async generation: {'✅' if settings.generation_async else '❌'}")
    logger.info("=" * 60)

    # Initialize database
    await init_db()
    await initialize_database()

    # Create local storage directories
    if settings.storage_provider == "local":
        storage_path = Path(settings.local_storage_path)
        (storage_path / "images").mkdir(parents=True, exist_ok=True)
        (storage_path / "thumbnails").mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Local storage: {storage_path.absolute()}")

    # Initialize WebSocket manager
    from app.api.v1.websocket import startup_websocket_manager, shutdown_websocket_manager

    await startup_websocket_manager()

    logger.info("✅ Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down application...")
    await shutdown_websocket_manager()
    await close_db()
    logger.info("✅ Application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
    lifespan=lifespan,
)


# ==================== Middleware ====================
app.add_middleware(SecurityHeadersMiddleware)

if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ==================== Static Files (Local Storage) ====================
if settings.storage_provider == "local":
    storage_path = Path(settings.local_storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")


# ==================== Exception Handlers ====================
@app.exception_handler(DreamCanvasException)
async def dreamcanvas_exception_handler(
    request: Request, exc: DreamCanvasException
) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]} for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Validation failed",
            "details": {"errors": errors},
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception: {exc}")
    if settings.is_development:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_ERROR",
                "message": str(exc),
                "type": exc.__class__.__name__,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
    )


# ==================== Include API Router ====================
app.include_router(api_router, prefix=settings.api_v1_prefix)


# ==================== Root Endpoints ====================
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.docs_enabled else "Disabled",
        "health": "/health",
        "api": settings.api_v1_prefix,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    from app.db.session import check_db_connection
    from app.services.claude_service import get_claude_service
    from app.services.image_gen_service import get_image_gen_service

    db_healthy = await check_db_connection()

    # Check Redis
    redis_healthy = False
    try:
        import redis.asyncio as redis_client

        r = redis_client.from_url(settings.redis_url)
        await r.ping()
        redis_healthy = True
        await r.close()
    except Exception:
        pass

    # Check Celery (if workers are running)
    celery_healthy = False
    try:
        from app.celery_app import celery_app

        inspect = celery_app.control.inspect()
        if inspect.ping():
            celery_healthy = True
    except Exception:
        pass

    claude = get_claude_service()
    image_gen = get_image_gen_service()

    overall_status = "healthy" if (db_healthy and redis_healthy) else "degraded"

    return {
        "status": overall_status,
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {
            "api": "healthy",
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "celery": "healthy" if celery_healthy else "no_workers",
            "claude": "configured" if claude.is_available else "not_configured",
            "dalle": "configured" if image_gen.dalle.is_available else "not_configured",
            "storage": settings.storage_provider,
        },
        "features": {
            "async_generation": settings.generation_async,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
