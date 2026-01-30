"""Database Module - Database configuration, session management, and initialization."""

from app.db.base import Base, BaseModel, SoftDeleteMixin, SoftDeleteModel, TimestampMixin, UUIDMixin
from app.db.session import (
    async_session_maker,
    check_db_connection,
    close_db,
    engine,
    get_db,
    get_session,
    init_db,
)
from app.db.sync_session import SyncSessionLocal, get_sync_session, sync_engine

__all__ = [
    # Base
    "Base",
    "BaseModel",
    "SoftDeleteModel",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UUIDMixin",
    # Async Session
    "async_session_maker",
    "check_db_connection",
    "close_db",
    "engine",
    "get_db",
    "get_session",
    "init_db",
    # Sync Session (for Celery)
    "get_sync_session",
    "SyncSessionLocal",
    "sync_engine",
]
