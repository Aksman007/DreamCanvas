"""
User Service - Business logic for user operations.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID | str) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User's UUID (can be string or UUID)

        Returns:
            User if found, None otherwise
        """
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None

        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: User's email

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created User object

        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing_user = await self.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user = User(
            email=user_data.email.lower(),
            hashed_password=hash_password(user_data.password),
            display_name=user_data.display_name,
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Created new user: {user.email}")
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        """
        Authenticate user with email and password.

        Args:
            email: User's email
            password: Plain text password

        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_by_email(email)

        if user is None:
            logger.warning(f"Authentication failed: user not found - {email}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {email}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password - {email}")
            return None

        logger.info(f"User authenticated: {email}")
        return user

    async def update(self, user: User, user_data: UserUpdate) -> User:
        """
        Update user profile.

        Args:
            user: User to update
            user_data: Update data

        Returns:
            Updated User object
        """
        update_data = user_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Updated user: {user.email}")
        return user

    async def update_password(self, user: User, current_password: str, new_password: str) -> bool:
        """
        Update user's password.

        Args:
            user: User to update
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True if successful, False if current password is wrong
        """
        if not verify_password(current_password, user.hashed_password):
            return False

        user.hashed_password = hash_password(new_password)
        await self.db.commit()

        logger.info(f"Password updated for user: {user.email}")
        return True

    async def deactivate(self, user: User) -> User:
        """Deactivate a user account."""
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Deactivated user: {user.email}")
        return user

    async def activate(self, user: User) -> User:
        """Activate a user account."""
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Activated user: {user.email}")
        return user


async def get_user_service(db: AsyncSession) -> UserService:
    """Factory function to create UserService instance."""
    return UserService(db)
