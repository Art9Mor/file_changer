import mimetypes
import os
from pathlib import Path
from typing import Optional

import aiofiles
from loguru import logger

from src.domain.interfaces.file_storage import FileStorage

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent.parent
STORAGE_DIR = BACKEND_ROOT / "storage" / "files"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class FileStorageImpl(FileStorage):
    async def save(self, content: bytes, stored_name: str) -> Path:
        """
        Сохранение файла на диск.
        """
        path = self.get_path(stored_name)
        async with aiofiles.open(path, 'wb') as f:
            await f.write(content)
        logger.debug(f'Файл сохранен: {path}')
        return path

    async def delete(self, stored_name: str) -> None:
        """
        Удаление файла с диска.
        """
        path = self.get_path(stored_name)
        if path.exists():
            os.remove(str(path))
            logger.debug(f'Файл удален: {path}')

    def get_path(self, stored_name: str) -> Path:
        """
        Получение абсолютного пути к файлу.
        """
        return STORAGE_DIR / stored_name

    async def file_exists(self, stored_name: str) -> bool:
        """
        Проверка существования файла на диске.
        """
        return self.get_path(stored_name).exists()

    async def read_text_metadata(self, path: Path) -> dict:
        """
        Извлечение метаданных из текстового файла.
        """
        line_count = 0
        char_count = 0
        async with aiofiles.open(path, 'r', encoding='utf-8', errors='ignore') as f:
            async for line in f:
                line_count += 1
                char_count += len(line)
        return {
            'line_count': line_count,
            'char_count': char_count,
        }

    async def read_binary_metadata(self, path: Path, mime_type: str) -> dict:
        """
        Извлечение метаданных из бинарного файла.
        """
        if mime_type == 'application/pdf':
            page_count = 0
            chunk_size = 8192
            async with aiofiles.open(path, 'rb') as f:
                chunk = await f.read(chunk_size)
                while chunk:
                    page_count += chunk.count(b'/Type /Page')
                    chunk = await f.read(chunk_size)
            return {'approx_page_count': max(page_count, 1)}
        return {}

    @staticmethod
    def guess_mime_type(stored_name: str) -> str:
        """
        Определение MIME-типа по расширению файла.
        """
        mime_type: Optional[str] = mimetypes.guess_type(stored_name)[0]  # type: ignore
        return mime_type if mime_type is not None else 'application/octet-stream'