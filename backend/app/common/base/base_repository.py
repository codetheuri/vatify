from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Generic, TypeVar, Type, List, Optional

T = TypeVar("T")

class BaseRepository(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, filters: dict = None) -> List[T]:
        stmt = select(self.model)
        if filters:
            for key, value in filters.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add(self, instance: T) -> T:
        self.session.add(instance)
        return instance

    async def delete(self, instance: T) -> bool:
        await self.session.delete(instance)
        return True

    async def update(self, instance: T, data: dict) -> T:
        for key, value in data.items():
            setattr(instance, key, value)
        return instance

    async def list_paginated(self, filters: dict = None, page: int = 1, per_page: int = 10):
        from sqlalchemy import func
        stmt = select(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)
        
        # Count total using a subquery to correct handle filtered queries
        res_count = await self.session.execute(select(func.count()).select_from(stmt.subquery()))
        total = res_count.scalar() or 0
        
        # Order by newest (descending ID) and apply limit/offset
        offset = (page - 1) * per_page
        stmt = stmt.order_by(self.model.id.desc()).offset(offset).limit(per_page)
        
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        return items, total
