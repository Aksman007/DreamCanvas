"""Database Initialization - Functions for initializing database tables and seed data."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

# Import directly from security module, not from core package
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import async_session_maker, engine
from app.models.user import User

logger = logging.getLogger(__name__)


async def create_tables() -> None:
    """Create all database tables. Use Alembic migrations in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created")


async def drop_tables() -> None:
    """Drop all database tables. WARNING: Deletes ALL data!"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("⚠️ All database tables dropped")


async def create_superuser(
    session: AsyncSession,
    email: str,
    password: str,
    display_name: str = "Admin",
) -> User | None:
    """Create a superuser account if it doesn't exist."""
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.info(f"Superuser {email} already exists")
        return None

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
    await session.refresh(user)

    logger.info(f"✅ Superuser {email} created")
    return user


async def seed_demo_users(session: AsyncSession) -> list[User]:
    """Seed database with demo users (development only)."""
    demo_users_data = [
        {"email": "demo@example.com", "password": "demopassword123", "display_name": "Demo User"},
        {
            "email": "artist@example.com",
            "password": "artistpassword123",
            "display_name": "Creative Artist",
        },
    ]

    created_users = []

    for user_data in demo_users_data:
        result = await session.execute(select(User).where(User.email == user_data["email"]))
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
        created_users.append(user)

    if created_users:
        await session.commit()
        logger.info(f"✅ Created {len(created_users)} demo users")

    return created_users


async def init_db() -> None:
    """Initialize database with tables and seed data."""
    logger.info("Initializing database...")

    if settings.is_development:
        await create_tables()

    async with async_session_maker() as session:
        await create_superuser(
            session,
            email="admin@dreamcanvas.app",
            password="adminpassword123",
            display_name="Admin",
        )

        if settings.is_development:
            await seed_demo_users(session)

    logger.info("✅ Database initialization complete")
