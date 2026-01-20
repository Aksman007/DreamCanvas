# app/db/init_db.py

import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.session import engine, async_session_maker
from app.core.security import hash_password
from app.config import settings

logger = logging.getLogger(__name__)


async def create_tables() -> None:
    """
    Create all database tables.
    Note: In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def drop_tables() -> None:
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped")


async def create_superuser(
    session: AsyncSession, email: str, password: str, display_name: str = "Admin"
) -> None:
    """
    Create a superuser account if it doesn't exist.
    """
    from app.models.user import User
    from sqlalchemy import select

    # Check if user exists
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.info(f"Superuser {email} already exists")
        return

    # Create superuser
    user = User(
        email=email,
        hashed_password=hash_password(password),
        display_name=display_name,
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )

    session.add(user)
    await session.commit()
    logger.info(f"Superuser {email} created")


async def init_db() -> None:
    """
    Initialize database with required data.
    Called on application startup in development.
    """
    logger.info("Initializing database...")

    # Create tables (development only - use migrations in production)
    if settings.environment == "development":
        await create_tables()

    # Create default superuser
    async with async_session_maker() as session:
        await create_superuser(
            session,
            email="admin@dreamcanvas.app",
            password="admin123",  # Change in production!
            display_name="Admin",
        )

    logger.info("Database initialization complete")


async def seed_demo_data(session: AsyncSession) -> None:
    """
    Seed database with demo data for development/testing.
    """
    from app.models.user import User

    demo_users = [
        {
            "email": "demo@example.com",
            "password": "demo123",
            "display_name": "Demo User",
        },
        {
            "email": "artist@example.com",
            "password": "artist123",
            "display_name": "Creative Artist",
        },
    ]

    for user_data in demo_users:
        from sqlalchemy import select

        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        if result.scalar_one_or_none():
            continue

        user = User(
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            display_name=user_data["display_name"],
            is_active=True,
            is_verified=True,
        )
        session.add(user)

    await session.commit()
    logger.info("Demo data seeded")
