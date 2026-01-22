"""
DreamCanvas API - Main Application Entry Point

This module creates and configures the FastAPI application.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

# ==================== Logging Configuration ====================

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format,
)
logger = logging.getLogger(__name__)


# ==================== Lifespan Events ====================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    - Startup: Initialize connections (DB, Redis, etc.)
    - Shutdown: Close connections gracefully
    """
    # ===== Startup =====
    logger.info("=" * 50)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("=" * 50)

    # TODO: Initialize database connection (Phase 3)
    # TODO: Initialize Redis connection (Phase 6)

    logger.info("✅ Application startup complete")

    yield  # Application runs here

    # ===== Shutdown =====
    logger.info("Shutting down application...")

    # TODO: Close database connection (Phase 3)
    # TODO: Close Redis connection (Phase 6)

    logger.info("✅ Application shutdown complete")


# ==================== Create FastAPI Application ====================

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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ==================== Exception Handlers ====================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.

    In development: Shows detailed error information
    In production: Shows generic error message
    """
    logger.exception(f"Unhandled exception: {exc}")

    if settings.is_development:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "type": exc.__class__.__name__,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ==================== Routes ====================


@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Returns basic API information",
)
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API name, version, and documentation URL
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.docs_enabled else "Disabled",
        "health": "/health",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns the health status of the API and its dependencies",
)
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.

    Checks:
        - API status
        - Database connection (TODO: Phase 3)
        - Redis connection (TODO: Phase 6)

    Returns:
        dict: Health status of all components
    """
    # TODO: Add actual health checks in later phases
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {
            "api": "healthy",
            "database": "not_configured",  # TODO: Phase 3
            "redis": "not_configured",  # TODO: Phase 6
        },
    }

    return health_status


@app.get(
    "/info",
    tags=["Info"],
    summary="API Information",
    description="Returns detailed API configuration (development only)",
)
async def api_info():
    """
    Returns API configuration information.

    Only available in development mode for security.

    Returns:
        dict: API configuration details
    """
    if not settings.is_development:
        return {"detail": "Not available in production"}

    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "api_prefix": settings.api_v1_prefix,
        "cors_origins": settings.cors_origins,
        "docs_enabled": settings.docs_enabled,
        "rate_limit_enabled": settings.rate_limit_enabled,
        "rate_limit_per_minute": settings.rate_limit_per_minute,
    }


# ==================== API Router (TODO: Phase 5) ====================

from app.api.v1.router import api_router

app.include_router(api_router, prefix=settings.api_v1_prefix)


# ==================== Run with Uvicorn ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower(),
    )
