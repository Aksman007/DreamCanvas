"""Dependencies Module - FastAPI dependency injection."""

import logging
from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.security import TokenPayload, verify_token
from app.db.session import get_db as get_db_session
from app.models.user import User

logger = logging.getLogger(__name__)


# ==================== Settings ====================
SettingsDep = Annotated[Settings, Depends(get_settings)]


# ==================== Database ====================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    async for session in get_db_session():
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db)]


# ==================== Authentication ====================
bearer_scheme = HTTPBearer(auto_error=False)


async def get_token_from_header(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    """Extract JWT token from Authorization header."""
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
    """Validate and decode the current access token."""
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


TokenDep = Annotated[TokenPayload, Depends(get_current_token)]


# ==================== User Dependencies ====================
async def get_current_user(token: TokenDep, db: DBSession) -> User:
    """Get the current authenticated user from database."""
    try:
        # Convert string to UUID
        user_id = UUID(token.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: bad user ID format",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Get current user and verify they are a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return current_user


SuperUser = Annotated[User, Depends(get_current_active_superuser)]


# ==================== Optional Authentication ====================
async def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DBSession,
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials, token_type="access")
    if payload is None:
        return None

    try:
        user_id = UUID(payload.sub)
    except ValueError:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return None

    return user


OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]


# ==================== Pagination ====================
class PaginationParams:
    """Common pagination parameters."""

    def __init__(self, page: int = 1, page_size: int = 20, max_page_size: int = 100):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), max_page_size)
        self.offset = (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


async def get_pagination(page: int = 1, page_size: int = 20) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


Pagination = Annotated[PaginationParams, Depends(get_pagination)]
