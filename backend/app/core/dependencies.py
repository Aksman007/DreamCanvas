"""
Dependencies Module

FastAPI dependency injection for common operations.
"""

import logging
from typing import Annotated
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.core.security import TokenPayload, verify_token
from app.core.exceptions import (
    InvalidTokenError,
    MissingTokenError,
    TokenExpiredError,
    AccountDeactivatedError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


# ============================================================================
# SETTINGS DEPENDENCY
# ============================================================================

SettingsDep = Annotated[Settings, Depends(get_settings)]


# ============================================================================
# DATABASE DEPENDENCY (Placeholder - Implemented in Phase 3)
# ============================================================================


# Placeholder type for now - will be replaced with actual AsyncSession
class DatabaseSession:
    """Placeholder for database session."""

    pass


async def get_db() -> AsyncGenerator[DatabaseSession, None]:
    """
    Dependency that provides a database session.

    Note: This is a placeholder. Actual implementation in Phase 3.

    Yields:
        AsyncSession: Database session
    """
    # TODO: Implement in Phase 3
    # async with async_session_maker() as session:
    #     try:
    #         yield session
    #         await session.commit()
    #     except Exception:
    #         await session.rollback()
    #         raise
    #     finally:
    #         await session.close()

    yield DatabaseSession()


DBSession = Annotated[DatabaseSession, Depends(get_db)]


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

# HTTP Bearer token scheme
# auto_error=False allows us to handle missing tokens ourselves
bearer_scheme = HTTPBearer(auto_error=False)


async def get_token_from_header(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    """
    Extract JWT token from Authorization header.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        JWT token string

    Raises:
        HTTPException: If no token provided
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


async def get_current_token(
    token: Annotated[str, Depends(get_token_from_header)],
) -> TokenPayload:
    """
    Validate and decode the current access token.

    Args:
        token: JWT token from Authorization header

    Returns:
        TokenPayload: Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# Type alias for token dependency
TokenDep = Annotated[TokenPayload, Depends(get_current_token)]


# ============================================================================
# USER DEPENDENCIES (Placeholder - Full implementation in Phase 3)
# ============================================================================


class UserPlaceholder:
    """
    Placeholder User class until models are implemented.

    Represents the current authenticated user.
    """

    def __init__(
        self,
        id: str,
        email: str = "user@example.com",
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> None:
        self.id = id
        self.email = email
        self.is_active = is_active
        self.is_superuser = is_superuser


async def get_current_user(
    token: TokenDep,
    db: DBSession,
) -> UserPlaceholder:
    """
    Get the current authenticated user.

    Args:
        token: Validated token payload
        db: Database session

    Returns:
        User: Current user object

    Raises:
        HTTPException: If user not found or deactivated

    Note: This is a placeholder. Full implementation in Phase 3.
    """
    # TODO: Implement actual user lookup in Phase 3
    # user = await db.get(User, token.sub)
    # if user is None:
    #     raise UserNotFoundError(token.sub)
    # if not user.is_active:
    #     raise AccountDeactivatedError()
    # return user

    # Placeholder implementation
    user = UserPlaceholder(
        id=token.sub,
        email="user@example.com",
        is_active=True,
        is_superuser=False,
    )

    return user


# Type alias for current user dependency
CurrentUser = Annotated[UserPlaceholder, Depends(get_current_user)]


async def get_current_active_superuser(
    current_user: CurrentUser,
) -> UserPlaceholder:
    """
    Get current user and verify they are a superuser.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )

    return current_user


# Type alias for superuser dependency
SuperUser = Annotated[UserPlaceholder, Depends(get_current_active_superuser)]


# ============================================================================
# OPTIONAL AUTHENTICATION
# ============================================================================


async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DBSession,
) -> UserPlaceholder | None:
    """
    Get current user if authenticated, None otherwise.

    Useful for endpoints that work for both authenticated and anonymous users.

    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session

    Returns:
        User if authenticated, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        return None

    # TODO: Implement actual user lookup in Phase 3
    return UserPlaceholder(
        id=payload.sub,
        email="user@example.com",
        is_active=True,
    )


# Type alias for optional user dependency
OptionalUser = Annotated[UserPlaceholder | None, Depends(get_optional_current_user)]


# ============================================================================
# REQUEST CONTEXT DEPENDENCIES
# ============================================================================


def get_request_id(request: Request) -> str:
    """
    Get the current request ID.

    Args:
        request: FastAPI request object

    Returns:
        Request ID string (set by RequestLoggingMiddleware)
    """
    return getattr(request.state, "request_id", "unknown")


RequestID = Annotated[str, Depends(get_request_id)]


# ============================================================================
# PAGINATION DEPENDENCIES
# ============================================================================


class PaginationParams:
    """Common pagination parameters."""

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
    ) -> None:
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


async def get_pagination(
    page: int = 1,
    page_size: int = 20,
) -> PaginationParams:
    """
    Dependency for pagination parameters.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page (max 100)

    Returns:
        PaginationParams object
    """
    return PaginationParams(page=page, page_size=page_size)


Pagination = Annotated[PaginationParams, Depends(get_pagination)]
