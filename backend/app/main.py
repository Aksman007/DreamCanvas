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
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.core.exceptions import DreamCanvasException
from app.core.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from app.api.v1.router import api_router

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
    """
    # ===== Startup =====
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info(f"🌐 API Prefix: {settings.api_v1_prefix}")
    logger.info("=" * 60)

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


# ==================== Middleware (Order Matters!) ====================

# 1. Security Headers (outermost - runs first on response)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate Limiting
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
    )

# 3. Request Logging
app.add_middleware(RequestLoggingMiddleware)

# 4. CORS (innermost - runs last on response)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ==================== Exception Handlers ====================


@app.exception_handler(DreamCanvasException)
async def dreamcanvas_exception_handler(
    request: Request,
    exc: DreamCanvasException,
) -> JSONResponse:
    """
    Handle custom DreamCanvas exceptions.

    Converts exceptions to proper JSON responses with status codes.
    """
    logger.warning(
        f"DreamCanvas exception: {exc.error_code} - {exc.message}",
        extra={"details": exc.details},
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Provides detailed error information for invalid requests.
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": errors},
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.

    In development: Shows detailed error information
    In production: Shows generic error message
    """
    # Log the full exception
    logger.exception(f"Unhandled exception: {exc}")

    # In development, show details
    if settings.is_development:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_ERROR",
                "message": str(exc),
                "type": exc.__class__.__name__,
            },
        )

    # In production, hide details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
        },
    )


# ==================== Include API Router ====================

app.include_router(api_router, prefix=settings.api_v1_prefix)


# ==================== Root Endpoints ====================


@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
)
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


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
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


# ==================== Run with Uvicorn ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.is_development,
        log_level=settings.log_level.lower(),
    )
