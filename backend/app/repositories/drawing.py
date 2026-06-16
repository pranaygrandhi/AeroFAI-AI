from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import Optional, List
from datetime import datetime

from ..models.drawing import Drawing, Characteristic, Balloon, DrawingRevision, DrawingPage
from .base import BaseRepository


class DrawingRepository(BaseRepository[Drawing]):
    """Repository for Drawing model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Drawing, db)

    async def get_by_part_number(self, part_number: str) -> Optional[Drawing]:
        """Get drawing by part number."""
        query = select(Drawing).where(Drawing.part_number == part_number)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_drawings(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Drawing]:
        """Get all drawings for a user."""
        query = (
            select(Drawing)
            .where(Drawing.user_id == user_id)
            .order_by(desc(Drawing.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_drawing_with_characteristics(self, drawing_id: int) -> Optional[Drawing]:
        """Get drawing with all characteristics loaded."""
        query = select(Drawing).where(Drawing.id == drawing_id)
        result = await self.db.execute(query)
        drawing = result.scalars().first()
        
        if drawing:
            # Load characteristics
            await self.db.refresh(drawing, ["characteristics", "balloons", "pages"])
        
        return drawing


class CharacteristicRepository(BaseRepository[Characteristic]):
    """Repository for Characteristic model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Characteristic, db)

    async def get_by_drawing(self, drawing_id: int) -> List[Characteristic]:
        """Get all characteristics for a drawing."""
        query = select(Characteristic).where(Characteristic.drawing_id == drawing_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_balloon_number(
        self, drawing_id: int, balloon_no: int
    ) -> Optional[Characteristic]:
        """Get characteristic by balloon number."""
        query = select(Characteristic).where(
            and_(
                Characteristic.drawing_id == drawing_id,
                Characteristic.balloon_no == balloon_no,
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_status(self, drawing_id: int, status: str) -> List[Characteristic]:
        """Get characteristics by status."""
        query = select(Characteristic).where(
            and_(Characteristic.drawing_id == drawing_id, Characteristic.status == status)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count_by_status(self, drawing_id: int, status: str) -> int:
        """Count characteristics by status."""
        query = select(Characteristic).where(
            and_(Characteristic.drawing_id == drawing_id, Characteristic.status == status)
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def bulk_update_characteristics(
        self, drawing_id: int, characteristics: List[dict]
    ) -> List[Characteristic]:
        """Bulk update characteristics."""
        result = []
        for char_data in characteristics:
            char_id = char_data.get("id")
            if char_id:
                char = await self.update(char_id, char_data)
                if char:
                    result.append(char)
            else:
                char = await self.create(char_data)
                result.append(char)
        return result


class BalloonRepository(BaseRepository[Balloon]):
    """Repository for Balloon model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Balloon, db)

    async def get_by_drawing(self, drawing_id: int) -> List[Balloon]:
        """Get all balloons for a drawing."""
        query = select(Balloon).where(Balloon.drawing_id == drawing_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_page(self, drawing_id: int, page_number: int) -> List[Balloon]:
        """Get balloons on a specific page."""
        query = select(Balloon).where(
            and_(Balloon.drawing_id == drawing_id, Balloon.page_number == page_number)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_next_balloon_number(self, drawing_id: int) -> int:
        """Get the next available balloon number."""
        query = select(Balloon).where(Balloon.drawing_id == drawing_id)
        result = await self.db.execute(query)
        balloons = result.scalars().all()
        
        if not balloons:
            return 1
        
        max_number = max([b.balloon_number for b in balloons])
        return max_number + 1


class DrawingPageRepository(BaseRepository[DrawingPage]):
    """Repository for DrawingPage model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(DrawingPage, db)

    async def get_by_drawing(self, drawing_id: int) -> List[DrawingPage]:
        """Get all pages for a drawing."""
        query = (
            select(DrawingPage)
            .where(DrawingPage.drawing_id == drawing_id)
            .order_by(DrawingPage.page_number)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_page(self, drawing_id: int, page_number: int) -> Optional[DrawingPage]:
        """Get a specific page."""
        query = select(DrawingPage).where(
            and_(
                DrawingPage.drawing_id == drawing_id,
                DrawingPage.page_number == page_number,
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()


class DrawingRevisionRepository(BaseRepository[DrawingRevision]):
    """Repository for DrawingRevision model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(DrawingRevision, db)

    async def get_by_drawing(self, drawing_id: int) -> List[DrawingRevision]:
        """Get all revisions for a drawing."""
        query = (
            select(DrawingRevision)
            .where(DrawingRevision.drawing_id == drawing_id)
            .order_by(desc(DrawingRevision.created_at))
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_latest_revision(self, drawing_id: int) -> Optional[DrawingRevision]:
        """Get the latest revision."""
        query = (
            select(DrawingRevision)
            .where(DrawingRevision.drawing_id == drawing_id)
            .order_by(desc(DrawingRevision.created_at))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalars().first()
