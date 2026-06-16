from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_active_users(self, skip: int = 0, limit: int = 100):
        """Get all active users."""
        query = (
            select(User)
            .where(User.is_active == 1)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_password(self, user_id: int, hashed_password: str) -> Optional[User]:
        """Update user password."""
        return await self.update(user_id, {"hashed_password": hashed_password})

    async def deactivate(self, user_id: int) -> Optional[User]:
        """Deactivate a user."""
        return await self.update(user_id, {"is_active": 0})

    async def activate(self, user_id: int) -> Optional[User]:
        """Activate a user."""
        return await self.update(user_id, {"is_active": 1})
