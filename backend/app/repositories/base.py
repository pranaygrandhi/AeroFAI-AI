# Repository base class for database operations
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Generic, List, Optional, Type, Any
from sqlalchemy import select, update, delete
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository class for common CRUD operations."""

    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj: dict) -> T:
        """Create a new record."""
        db_obj = self.model(**obj)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def get(self, id: Any) -> Optional[T]:
        """Get a record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, id: Any, obj: dict) -> Optional[T]:
        """Update a record."""
        query = update(self.model).where(self.model.id == id).values(**obj)
        await self.db.execute(query)
        return await self.get(id)

    async def delete(self, id: Any) -> bool:
        """Delete a record."""
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.rowcount > 0

    async def count(self, **filters) -> int:
        """Count records matching filters."""
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(select(func.count()).select_from(query.froms[0]))
        return result.scalar() or 0
