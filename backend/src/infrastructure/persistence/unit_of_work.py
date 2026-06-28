from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.repositories import AlertRepositoryImpl, FileRepositoryImpl


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        """
        Инициализация с сессией БД.
        """
        self.session = session
        self.file_repo = FileRepositoryImpl(session)
        self.alert_repo = AlertRepositoryImpl(session)

    async def commit(self) -> None:
        """
        Фиксация транзакции.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Откат транзакции.
        """
        await self.session.rollback()