from abc import ABC, abstractmethod
from pathlib import Path


class FileStorage(ABC):
    @abstractmethod
    async def save(self, content: bytes, stored_name: str) -> Path:
        """
        Сохранение файла на диск.
        """
        pass

    @abstractmethod
    async def delete(self, stored_name: str) -> None:
        """
        Удаление файла с диска.
        """
        pass

    @abstractmethod
    def get_path(self, stored_name: str) -> Path:
        """
        Получение абсолютного пути к файлу.
        """
        pass

    @abstractmethod
    async def file_exists(self, stored_name: str) -> bool:
        """
        Проверка существования файла на диске.
        """
        pass

    @abstractmethod
    async def read_text_metadata(self, path: Path) -> dict:
        """
        Извлечение метаданных из текстового файла.
        """
        pass

    @abstractmethod
    async def read_binary_metadata(self, path: Path, mime_type: str) -> dict:
        """
        Извлечение метаданных из бинарного файла.
        """
        pass