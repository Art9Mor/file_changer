from abc import ABC, abstractmethod
from src.domain.entities import StoredFile


class FileRepository(ABC):
    @abstractmethod
    async def list_files_paginated(self, skip: int, limit: int) -> tuple[list[StoredFile], int]:
        """
        Получение файлов с пагинацией.
        """
        pass

    @abstractmethod
    async def get_file(self, file_id: str) -> StoredFile | None:
        """
        Получение файла по ID.
        """
        pass

    @abstractmethod
    async def create_file(self, file: StoredFile) -> StoredFile:
        """
        Создание записи файла.
        """
        pass

    @abstractmethod
    async def update_file(self, file: StoredFile) -> StoredFile:
        """
        Обновление записи файла.
        """
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> None:
        """
        Удаление записи файла из БД.
        """
        pass