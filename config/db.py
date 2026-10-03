from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from config.settings import settings

engine = create_async_engine(url=settings.db_url, echo=True)


async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_session)]
