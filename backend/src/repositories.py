"""
Слой репозиториев для работы с БД.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert, StoredFile


class FileRepository:
    """
    Репозиторий файлов.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация с сессией БД.
        """
        self.session = session

    async def list_files(self) -> list[StoredFile]:
        """
        Получение всех файлов в порядке убывания даты.
        """
        result = await self.session.execute(select(StoredFile).order_by(StoredFile.created_at.desc()))
        return list(result.scalars().all())

    async def get_file(self, file_id: str) -> StoredFile | None:
        """
        Получение файла по ID.
        """
        return await self.session.get(StoredFile, file_id)

    async def create_file(self, file: StoredFile) -> StoredFile:
        """
        Создание записи файла.
        """
        self.session.add(file)
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def update_file(self, file: StoredFile) -> StoredFile:
        """
        Обновление записи файла.
        """
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def delete_file(self, file: StoredFile) -> None:
        """
        Удаление записи файла из БД.
        """
        await self.session.delete(file)
        await self.session.commit()


class AlertRepository:
    """
    Репозиторий алертов.
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация с сессией БД.
        """
        self.session = session

    async def list_alerts(self) -> list[Alert]:
        """
        Получение всех алертов в порядке убывания даты.
        """
        result = await self.session.execute(select(Alert).order_by(Alert.created_at.desc()))
        return list(result.scalars().all())

    async def create_alert(self, alert: Alert) -> Alert:
        """
        Создание записи алерта.
        """
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert