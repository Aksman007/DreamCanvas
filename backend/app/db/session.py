# app/db/session.py

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from app.config import settings


# ============== Engine Configuration ==============


def create_engine() -> AsyncEngine:
    """
    Create and configure the async database engine.
    """
    engine = create_async_engine(
        settings.database_url,
        echo=settings.db_echo,  # Log SQL queries if True
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,  # Check connection health before using
        # Use NullPool for testing to avoid connection issues
        # poolclass=NullPool if settings.environment == "testing" else None
    )
    return engine


# Create global engine instance
engine = create_engine()


# ============== Session Factory ==============

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,
    autoflush=False,
)


# ============== Session Context Manager ==============


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    Handles commit/rollback and cleanup.

    Usage:
        async with get_session() as session:
            # do database operations
            pass
    """
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# ============== Engine Lifecycle ==============


async def init_db() -> None:
    """
    Initialize database connection.
    Call on application startup.
    """
    # Test the connection
    async with engine.begin() as conn:
        # You could run initial setup here
        pass


async def close_db() -> None:
    """
    Close database connections.
    Call on application shutdown.
    """
    await engine.dispose()


# ============== Utility Functions ==============


async def check_db_connection() -> bool:
    """
    Check if database is accessible.
    Returns True if connection is successful.
    """
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
