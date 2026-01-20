# app/core/middleware.py

import time
import uuid
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and outgoing responses.
    Adds request ID for tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Add request ID to state for access in routes
        request.state.request_id = request_id

        # Log incoming request
        start_time = time.perf_counter()

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"[{request_id}] Request failed with exception")
            raise

        # Calculate duration
        duration = time.perf_counter() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log response
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({duration_ms}ms)",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    For production, use Redis-based rate limiting.
    """

    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client identifier (IP or user ID from token)
        client_id = self._get_client_id(request)

        # Check rate limit
        now = time.time()
        window_start = now - 60  # 1 minute window

        # Get requests in current window
        if client_id not in self.requests:
            self.requests[client_id] = []

        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"},
            )

        # Record this request
        self.requests[client_id].append(now)

        return await call_next(request)

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Try to get user ID from token (if authenticated)
        # For now, use IP address
        if request.client:
            return request.client.host
        return "unknown"


class CORSDebugMiddleware(BaseHTTPMiddleware):
    """
    Debug middleware to log CORS-related information.
    Only use in development.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if settings.debug:
            origin = request.headers.get("origin", "No origin")
            logger.debug(f"CORS Request from: {origin}")

        return await call_next(request)
