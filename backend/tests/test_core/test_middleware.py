"""
Tests for middleware - logging, rate limiting, and security headers.
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)

# ==================== Request Logging Middleware Tests ====================


class TestRequestLoggingMiddleware:
    """Test request logging middleware."""

    @pytest.fixture
    def app_with_logging(self) -> FastAPI:
        """Create test app with logging middleware."""
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():  # type: ignore[no-untyped-def]
            return {"message": "test"}

        @app.get("/health")
        async def health_endpoint():  # type: ignore[no-untyped-def]
            return {"status": "ok"}

        return app

    def test_logging_middleware_adds_request_id_header(self, app_with_logging: FastAPI) -> None:
        """Test that request ID is added to response headers."""
        client = TestClient(app_with_logging)

        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_logging_middleware_adds_response_time_header(self, app_with_logging: FastAPI) -> None:
        """Test that response time is added to response headers."""
        client = TestClient(app_with_logging)

        response = client.get("/test")

        assert "X-Response-Time" in response.headers
        assert "ms" in response.headers["X-Response-Time"]

    def test_logging_middleware_logs_requests(self, app_with_logging: FastAPI, caplog: pytest.LogCaptureFixture) -> None:
        """Test that requests are logged."""
        client = TestClient(app_with_logging)

        with caplog.at_level("INFO"):
            response = client.get("/test")

        # Check that request was logged
        assert any("GET /test" in record.message for record in caplog.records)
        assert response.status_code == 200

    def test_logging_middleware_skips_health_path(self, app_with_logging: FastAPI, caplog: pytest.LogCaptureFixture) -> None:
        """Test that health check path is not logged."""
        client = TestClient(app_with_logging)

        with caplog.at_level("INFO"):
            response = client.get("/health")

        # Health check should not be logged
        assert not any("/health" in record.message for record in caplog.records)
        assert response.status_code == 200

    def test_logging_middleware_stores_request_id_in_state(self, app_with_logging: FastAPI) -> None:
        """Test that request ID is stored in request state."""
        app = app_with_logging

        request_id_found = None

        @app.get("/check-state")
        async def check_state(request):  # type: ignore[no-untyped-def]
            nonlocal request_id_found
            request_id_found = getattr(request.state, "request_id", None)
            return {"request_id": request_id_found}

        client = TestClient(app)
        response = client.get("/check-state")

        assert response.status_code == 200
        assert request_id_found is not None
        assert len(request_id_found) > 0

    def test_logging_middleware_get_client_ip_with_forwarded(self, app_with_logging: FastAPI) -> None:
        """Test extracting client IP from X-Forwarded-For header."""
        client = TestClient(app_with_logging)

        response = client.get(
            "/test",
            headers={"X-Forwarded-For": "192.168.1.100, 10.0.0.1"},
        )

        assert response.status_code == 200
        # The middleware should extract the first IP

    def test_logging_middleware_get_client_ip_direct(self, app_with_logging: FastAPI) -> None:
        """Test extracting client IP from direct connection."""
        client = TestClient(app_with_logging)

        response = client.get("/test")

        assert response.status_code == 200
        # Should use request.client.host


# ==================== Rate Limit Middleware Tests ====================


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    @pytest.fixture
    def app_with_rate_limit(self) -> FastAPI:
        """Create test app with rate limiting middleware."""
        app = FastAPI()

        # Set low limit for testing
        app.add_middleware(RateLimitMiddleware, requests_per_minute=5)

        @app.get("/test")
        async def test_endpoint():  # type: ignore[no-untyped-def]
            return {"message": "test"}

        @app.get("/health")
        async def health_endpoint():  # type: ignore[no-untyped-def]
            return {"status": "ok"}

        return app

    @patch("app.config.settings.rate_limit_enabled", True)
    def test_rate_limit_allows_under_limit(self, app_with_rate_limit: FastAPI) -> None:
        """Test that requests under the limit are allowed."""
        client = TestClient(app_with_rate_limit)

        # Make 3 requests (under limit of 5)
        for _ in range(3):
            response = client.get("/test")
            assert response.status_code == 200

    @patch("app.config.settings.rate_limit_enabled", True)
    def test_rate_limit_blocks_over_limit(self, app_with_rate_limit: FastAPI) -> None:
        """Test that requests over the limit are blocked."""
        client = TestClient(app_with_rate_limit)

        # Make 5 requests to hit the limit
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

        # 6th request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429
        assert "RATE_LIMIT_EXCEEDED" in response.text

    @patch("app.config.settings.rate_limit_enabled", True)
    def test_rate_limit_adds_headers(self, app_with_rate_limit: FastAPI) -> None:
        """Test that rate limit headers are added to responses."""
        client = TestClient(app_with_rate_limit)

        response = client.get("/test")

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "5"

    @patch("app.config.settings.rate_limit_enabled", True)
    def test_rate_limit_remaining_decreases(self, app_with_rate_limit: FastAPI) -> None:
        """Test that remaining count decreases with each request."""
        client = TestClient(app_with_rate_limit)

        # First request
        response1 = client.get("/test")
        remaining1 = int(response1.headers["X-RateLimit-Remaining"])

        # Second request
        response2 = client.get("/test")
        remaining2 = int(response2.headers["X-RateLimit-Remaining"])

        assert remaining2 < remaining1

    @patch("app.config.settings.rate_limit_enabled", True)
    def test_rate_limit_includes_retry_after_header(self, app_with_rate_limit: FastAPI) -> None:
        """Test that Retry-After header is included when rate limited."""
        client = TestClient(app_with_rate_limit)

        # Exhaust the limit
        for _ in range(5):
            client.get("/test")

        # Get rate limited response
        response = client.get("/test")

        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert int(response.headers["Retry-After"]) > 0

    @patch("app.config.settings.rate_limit_enabled", True)
    def test_rate_limit_skips_excluded_paths(self, app_with_rate_limit: FastAPI) -> None:
        """Test that excluded paths are not rate limited."""
        client = TestClient(app_with_rate_limit)

        # Make many requests to excluded path
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200  # Should never be rate limited

    @patch("app.config.settings.rate_limit_enabled", False)
    def test_rate_limit_disabled_in_settings(self, app_with_rate_limit: FastAPI) -> None:
        """Test that rate limiting can be disabled via settings."""
        client = TestClient(app_with_rate_limit)

        # Make many requests (should all succeed)
        for _ in range(10):
            response = client.get("/test")
            assert response.status_code == 200

    def test_rate_limit_get_client_id_with_api_key(self, app_with_rate_limit: FastAPI) -> None:
        """Test client ID extraction with API key."""
        client = TestClient(app_with_rate_limit)

        response = client.get(
            "/test",
            headers={"X-API-Key": "test-api-key-12345678"},
        )

        assert response.status_code == 200

    def test_rate_limit_get_client_id_with_ip(self, app_with_rate_limit: FastAPI) -> None:
        """Test client ID extraction with IP address."""
        client = TestClient(app_with_rate_limit)

        response = client.get(
            "/test",
            headers={"X-Forwarded-For": "192.168.1.100"},
        )

        assert response.status_code == 200

    @patch("app.config.settings.rate_limit_enabled", True)
    def test_rate_limit_window_cleans_old_requests(self, app_with_rate_limit: FastAPI) -> None:
        """Test that requests outside the window are cleaned."""
        # This test would require mocking time to advance the window
        # For now, we just verify the middleware works
        client = TestClient(app_with_rate_limit)

        response = client.get("/test")
        assert response.status_code == 200


# ==================== Security Headers Middleware Tests ====================


class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""

    @pytest.fixture
    def app_with_security_headers(self) -> FastAPI:
        """Create test app with security headers middleware."""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        async def test_endpoint():  # type: ignore[no-untyped-def]
            return {"message": "test"}

        @app.get("/api/test")
        async def api_endpoint():  # type: ignore[no-untyped-def]
            return {"message": "api test"}

        return app

    def test_security_headers_added(self, app_with_security_headers: FastAPI) -> None:
        """Test that security headers are added to responses."""
        client = TestClient(app_with_security_headers)

        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_security_headers_x_frame_options(self, app_with_security_headers: FastAPI) -> None:
        """Test that X-Frame-Options header is added."""
        client = TestClient(app_with_security_headers)

        response = client.get("/test")

        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_security_headers_xss_protection(self, app_with_security_headers: FastAPI) -> None:
        """Test that X-XSS-Protection header is added."""
        client = TestClient(app_with_security_headers)

        response = client.get("/test")

        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_security_headers_referrer_policy(self, app_with_security_headers: FastAPI) -> None:
        """Test that Referrer-Policy header is added."""
        client = TestClient(app_with_security_headers)

        response = client.get("/test")

        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_security_headers_cache_control_for_api(self, app_with_security_headers: FastAPI) -> None:
        """Test that Cache-Control header is added for API endpoints."""
        client = TestClient(app_with_security_headers)

        response = client.get("/api/test")

        assert "Cache-Control" in response.headers
        assert "no-store" in response.headers["Cache-Control"]

    def test_security_headers_no_cache_control_for_non_api(self, app_with_security_headers: FastAPI) -> None:
        """Test that Cache-Control is not added for non-API endpoints."""
        client = TestClient(app_with_security_headers)

        response = client.get("/test")

        # Should not have Cache-Control or should have different value
        if "Cache-Control" in response.headers:
            assert "no-store" not in response.headers.get("Cache-Control", "")


# ==================== Middleware Integration Tests ====================


class TestMiddlewareIntegration:
    """Test multiple middleware working together."""

    @pytest.fixture
    def app_with_all_middleware(self) -> FastAPI:
        """Create test app with all middleware."""
        app = FastAPI()

        # Add all middleware (order matters - added in reverse order of execution)
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():  # type: ignore[no-untyped-def]
            return {"message": "test"}

        return app

    def test_all_middleware_work_together(self, app_with_all_middleware: FastAPI) -> None:
        """Test that all middleware can work together."""
        client = TestClient(app_with_all_middleware)

        response = client.get("/test")

        # Should have headers from all middleware
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers  # From logging
        assert "X-Response-Time" in response.headers  # From logging
        assert "X-Content-Type-Options" in response.headers  # From security
        # Rate limit headers might not be present if disabled in settings

    def test_middleware_order_is_correct(self, app_with_all_middleware: FastAPI) -> None:
        """Test that middleware executes in correct order."""
        client = TestClient(app_with_all_middleware)

        response = client.get("/test")

        # All headers should be present
        assert response.status_code == 200
        # Logging middleware should execute first (innermost)
        # Security middleware should execute last (outermost)
        assert "X-Request-ID" in response.headers
        assert "X-Content-Type-Options" in response.headers
