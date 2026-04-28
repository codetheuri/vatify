from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, List, Optional, Type

T = TypeVar("T")
R = TypeVar("R")

class BaseService(Generic[T, R]):
    repo: Type[R] = None

    def __init__(self, session: AsyncSession):
        self.session = session
        if self.repo:
            self.repository = self.repo(session)

    async def commit(self):
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise HTTPException(400, detail=str(e))

    async def create(self, data: dict) -> T:
        instance = self.repository.model(**data)
        await self.repository.add(instance)
        await self.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: int, data: dict) -> T:
        instance = await self.repository.get(id)
        if not instance:
            raise HTTPException(404, detail=f"{self.repository.model.__name__} not found")
        await self.repository.update(instance, data)
        await self.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.repository.get(id)
        if not instance:
            raise HTTPException(404, detail=f"{self.repository.model.__name__} not found")
        await self.repository.delete(instance)
        await self.commit()
        return True

    async def get(self, id: int) -> T:
        instance = await self.repository.get(id)
        if not instance:
            raise HTTPException(404, detail=f"{self.repository.model.__name__} not found")
        return instance

    async def list(self, filters: dict = None) -> List[T]:
        return await self.repository.list(filters)
