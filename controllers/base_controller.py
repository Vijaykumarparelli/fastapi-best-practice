from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select


class BaseController:
    def __init__(self, session: AsyncSession, model: SQLModel):
        self.session = session
        self.model = model

    async def _get(self, id: UUID):
        return await self.session.get(self.model, id)

    async def _add(self, entity: SQLModel):
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def _get_by(self, **filters: Any):
        statement = select(self.model).filter_by(**filters)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def _get_all(self, **filters: Any):
        statement = select(self.model).filter_by(**filters)
        return (await self.session.execute(statement)).scalars().all()
