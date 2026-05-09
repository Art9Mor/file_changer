"""
Настройка БД и управление сессиями.
"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DB_URL = (
    f"postgresql+asyncpg://{os.environ.get('POSTGRES_USER')}:"
    f"{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:"
    f"{os.environ.get('PGPORT')}/{os.environ.get('POSTGRES_DB')}"
)

engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """
    Получение сессии БД для async операций.
    """

    async with async_session_maker() as session:
        yield session