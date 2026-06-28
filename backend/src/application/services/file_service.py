from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EmptyFileError, FileTooLargeError, ResourceNotFound
from src.domain.constants import MAX_UPLOAD_BYTES
from src.domain.entities import StoredFile
from src.infrastructure.persistence.repositories import FileRepositoryImpl
from src.infrastructure.storage.file_storage import FileStorageImpl


class FileService:
    def __init__(self):
        """
        Инициализация сервиса.
        """
        self._file_storage = FileStorageImpl()

    @staticmethod
    async def list_files_paginated(skip: int, limit: int, db: AsyncSession) -> tuple[list[StoredFile], int]:
        """
        Получение файлов с пагинацией.
        """
        logger.debug(f'Получение файлов с пагинацией skip={skip} limit={limit}')
        repo = FileRepositoryImpl(db)
        items, total = await repo.list_files_paginated(skip, limit)
        logger.debug(f'Получено файлов: {len(items)} из {total}')
        return items, total

    @staticmethod
    async def get_file(file_id: str, db: AsyncSession) -> StoredFile:
        """
        Получение файла по ID.
        """
        logger.debug(f'Получение файла: {file_id}')
        repo = FileRepositoryImpl(db)
        file_item = await repo.get_file(file_id)
        if not file_item:
            logger.warning(f'Файл не найден: {file_id}')
            raise ResourceNotFound('file')
        return file_item

    async def create_file(
        self,
        db: AsyncSession,
        *,
        title: str,
        original_filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> StoredFile:
        """
        Создание нового файла и сохранение на диск.
        """
        logger.info(f'Загрузка файла: \'{original_filename}\' (название: \'{title}\')')
        if not content:
            logger.warning(f'Попытка загрузить пустой файл: \'{original_filename}\'')
            raise EmptyFileError()
        if len(content) > MAX_UPLOAD_BYTES:
            logger.warning(f'Файл слишком большой: {len(content)} байт (макс: {MAX_UPLOAD_BYTES})')
            raise FileTooLargeError(MAX_UPLOAD_BYTES)

        file_id = str(uuid4())
        suffix = Path(original_filename or '').suffix
        stored_name = f'{file_id}{suffix}'
        mime_type = content_type or self._file_storage.guess_mime_type(stored_name)

        await self._file_storage.save(content, stored_name)

        now = datetime.now(timezone.utc)
        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=original_filename or stored_name,
            stored_name=stored_name,
            mime_type=mime_type,
            size=len(content),
            processing_status='uploaded',
            scan_status=None,
            scan_details=None,
            metadata_json=None,
            requires_attention=False,
            created_at=now,
            updated_at=now,
        )

        repo = FileRepositoryImpl(db)
        created_file = await repo.create_file(file_item)
        logger.info(f'Файл создан успешно: \'{file_id}\' ({len(content)} байт)')
        return created_file

    @staticmethod
    async def update_file(file_id: str, title: str, db: AsyncSession) -> StoredFile:
        """
        Обновление названия файла.
        """
        logger.debug(f'Обновление файла: \'{file_id}\', новое название: \'{title}\'')
        repo = FileRepositoryImpl(db)
        file_item = await repo.get_file(file_id)
        if not file_item:
            logger.warning(f'Не удалось обновить: файл не найден: \'{file_id}\'')
            raise ResourceNotFound('file')
        file_item.title = title
        file_item.updated_at = datetime.now(timezone.utc)
        updated = await repo.update_file(file_item)
        logger.info(f'Файл обновлён: \'{file_id}\'')
        return updated

    async def delete_file(self, file_id: str, db: AsyncSession) -> None:
        """
        Удаление файла и его записи из БД.
        """
        logger.info(f'Удаление файла: \'{file_id}\'')
        repo = FileRepositoryImpl(db)
        file_item = await repo.get_file(file_id)
        if not file_item:
            logger.warning(f'Не удалось удалить: файл не найден: \'{file_id}\'')
            raise ResourceNotFound('file')
        await self._file_storage.delete(file_item.stored_name)
        await repo.delete_file(file_id)
        logger.info(f'Файл удалён успешно: \'{file_id}\'')

    async def get_file_for_download(self, file_id: str, db: AsyncSession) -> tuple[StoredFile, Path]:
        """
        Файл и путь на диске для отдачи клиенту.
        """
        logger.debug(f'Получение пути файла: \'{file_id}\'')
        file_item = await self.get_file(file_id, db)
        stored_path = self._file_storage.get_path(file_item.stored_name)
        if not await self._file_storage.file_exists(file_item.stored_name):
            logger.error(f'Файл не найден на диске: \'{stored_path}\'')
            raise ResourceNotFound('stored_blob')
        return file_item, stored_path

    @staticmethod
    async def scan_file(file_id: str, db: AsyncSession) -> None:
        """
        Сканирование файла на подозрительные признаки.
        """
        logger.info(f'Начало проверки угроз для файла: {file_id}')
        repo = FileRepositoryImpl(db)
        file_item = await repo.get_file(file_id)
        if not file_item:
            logger.error(f'Файл не найден для сканирования: {file_id}')
            return

        file_item.processing_status = 'processing'
        reasons: list[str] = []
        extension = Path(file_item.original_name).suffix.lower()

        logger.debug(f'Проверка файла: {file_id}, расширение: {extension}, размер: {file_item.size}')

        if extension in {'.exe', '.bat', '.cmd', '.sh', '.js'}:
            logger.warning(f'Обнаружено подозрительное расширение: {extension} для файла {file_id}')
            reasons.append(f'подозрительное расширение {extension}')

        if file_item.size > MAX_UPLOAD_BYTES:
            logger.warning(f'Файл слишком большой: {file_item.size} байт для файла {file_id}')
            reasons.append('файл больше 10 МБ')

        if extension == '.pdf' and file_item.mime_type not in {'application/pdf', 'application/octet-stream'}:
            logger.warning(f'Несоответствие mime-типа PDF: {file_item.mime_type} для файла {file_id}')
            reasons.append('расширение pdf не соответствует mime-типу')

        file_item.scan_status = 'suspicious' if reasons else 'clean'
        file_item.scan_details = ', '.join(reasons) if reasons else 'угроз не найдено'
        file_item.requires_attention = bool(reasons)
        file_item.updated_at = datetime.now(timezone.utc)
        await repo.update_file(file_item)
        logger.info(f'Проверка угроз завершена для файла: {file_id}, статус: {file_item.scan_status}')

    async def extract_file_metadata(self, file_id: str, db: AsyncSession) -> None:
        """
        Извлечение метаданных файла.
        """
        logger.info(f'Начало извлечения метаданных для файла: {file_id}')
        repo = FileRepositoryImpl(db)
        file_item = await repo.get_file(file_id)
        if not file_item:
            logger.error(f'Файл не найден для извлечения метаданных: {file_id}')
            return

        stored_path = self._file_storage.get_path(file_item.stored_name)
        if not await self._file_storage.file_exists(file_item.stored_name):
            logger.error(f'Файловый объект не найден: {stored_path}')
            file_item.processing_status = 'failed'
            file_item.scan_status = file_item.scan_status or 'failed'
            file_item.scan_details = 'файл не найден на диске при извлечении метаданных'
            file_item.updated_at = datetime.now(timezone.utc)
            await repo.update_file(file_item)
            return

        metadata = {
            'extension': Path(file_item.original_name).suffix.lower(),
            'size_bytes': file_item.size,
            'mime_type': file_item.mime_type,
        }

        logger.debug(f'Извлечение метаданных для {file_id}, mime_type: {file_item.mime_type}')

        if file_item.mime_type.startswith('text/'):
            logger.debug(f'Чтение текстового файла: {file_id}')
            text_metadata = await self._file_storage.read_text_metadata(stored_path)
            metadata.update(text_metadata)
            logger.debug(f'Текстовый файл {file_id}: {metadata["line_count"]} строк, {metadata["char_count"]} символов')
        elif file_item.mime_type == 'application/pdf':
            logger.debug(f'Чтение PDF-файла: {file_id}')
            binary_metadata = await self._file_storage.read_binary_metadata(stored_path, file_item.mime_type)
            metadata.update(binary_metadata)
            logger.debug(f'PDF-файл {file_id}: ~{metadata["approx_page_count"]} страниц')

        file_item.metadata_json = metadata
        file_item.processing_status = 'processed'
        file_item.updated_at = datetime.now(timezone.utc)
        await repo.update_file(file_item)
        logger.info(f'Извлечение метаданных завершено для файла: {file_id}')