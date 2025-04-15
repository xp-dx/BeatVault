from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from . import database as _global_database


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with _global_database.async_session_maker() as session:
        yield session
