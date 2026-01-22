"""
Middleware Module

Custom middleware for request processing.
"""

import logging
import time
import uuid
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and outgoing responses.

    Features:
        - Generates unique request ID for tracing
        - Logs request method, path, and client IP
        - Measures and logs response time
        - Adds X-Request-ID and X-Response-Time headers
    """

    # Paths to skip logging (reduce noise)
    SKIP_PATHS = {"/health", "/favicon.ico"}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        # Skip logging for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]

        # Store request ID in state for access in route handlers
        request.state.request_id = request_id

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Log request start
        start_time = time.perf_counter()
        logger.info(f"[{request_id}] → {request.method} {request.url.path} (client: {client_ip})")

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            duration = time.perf_counter() - start_time
            logger.exception(
                f"[{request_id}] ✗ {request.method} {request.url.path} "
                f"failed after {duration:.3f}s: {e}"
            )
            raise

        # Calculate duration
        duration = time.perf_counter() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log response
        status_emoji = "✓" if response.status_code < 400 else "✗"
        logger.info(
            f"[{request_id}] {status_emoji} {request.method} {request.url.path} "
            f"→ {response.status_code} ({duration_ms}ms)"
        )

        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies."""
        # Check for forwarded header (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Get first IP in chain (original client)
            return forwarded.split(",")[0].strip()

        # Direct connection
        if request.client:
            return request.client.host

        return "unknown"


# ============================================================================
# RATE LIMITING MIDDLEWARE
# ============================================================================


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.

    Uses sliding window algorithm to track requests per client.

    Note: For production, use Redis-based rate limiting for:
        - Persistence across restarts
        - Distributed rate limiting across multiple instances

    Configuration:
        - requests_per_minute: Max requests allowed per minute
        - Excluded paths: /health, /docs, /redoc, /openapi.json
    """

    # Paths excluded from rate limiting
    EXCLUDED_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/"}

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
    ) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Store: {client_id: [timestamp1, timestamp2, ...]}
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Skip if rate limiting is disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        now = time.time()
        window_start = now - 60  # 1 minute window

        # Clean old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.requests_per_minute:
            # Calculate retry-after
            oldest_request = min(self.requests[client_id])
            retry_after = int(oldest_request + 60 - now) + 1

            logger.warning(
                f"Rate limit exceeded for {client_id}: "
                f"{len(self.requests[client_id])}/{self.requests_per_minute} requests"
            )

            return Response(
                content=f'{{"error": "RATE_LIMIT_EXCEEDED", "message": "Too many requests", "retry_after": {retry_after}}}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(retry_after)},
            )

        # Record this request
        self.requests[client_id].append(now)

        # Add rate limit headers to response
        response = await call_next(request)

        remaining = self.requests_per_minute - len(self.requests[client_id])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier.

        Priority:
            1. Authenticated user ID (from token)
            2. API key
            3. Client IP address
        """
        # Check for user ID in request state (set by auth middleware)
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"

        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key[:16]}"  # Only use first 16 chars

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        if request.client:
            return f"ip:{request.client.host}"

        return "ip:unknown"

    def reset_client(self, client_id: str) -> None:
        """Reset rate limit for a specific client (for testing)."""
        if client_id in self.requests:
            del self.requests[client_id]

    def get_client_stats(self, client_id: str) -> dict:
        """Get rate limit stats for a client (for debugging)."""
        now = time.time()
        window_start = now - 60

        requests = [r for r in self.requests.get(client_id, []) if r > window_start]

        return {
            "client_id": client_id,
            "requests_in_window": len(requests),
            "limit": self.requests_per_minute,
            "remaining": self.requests_per_minute - len(requests),
        }


# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Headers added:
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - X-XSS-Protection: 1; mode=block
        - Referrer-Policy: strict-origin-when-cross-origin
        - Cache-Control: no-store (for API responses)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Prevent caching of API responses
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, max-age=0"

        return response
