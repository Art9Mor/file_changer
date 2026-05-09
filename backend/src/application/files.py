import mimetypes
from pathlib import Path
from uuid import uuid4

import aiofiles
import aiofiles.os
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.exceptions import EmptyFileError, FileTooLargeError, ResourceNotFound
from src.domain.constants import MAX_UPLOAD_BYTES
from src.infrastructure.persistence.repositories import AlertRepository, FileRepository
from src.infrastructure.storage import stored_file_path
from src.models import Alert, StoredFile


async def list_files(db: AsyncSession) -> list[StoredFile]:
    """
    Получение всех файлов.
    """

    logger.debug('Получение всех файлов')
    repo = FileRepository(db)
    files = await repo.list_files()
    logger.debug(f'Получено файлов: {len(files)}')
    return files


async def list_files_paginated(skip: int, limit: int, db: AsyncSession) -> tuple[list[StoredFile], int]:
    """
    Получение файлов с пагинацией.
    """

    logger.debug(f'Получение файлов с пагинацией skip={skip} limit={limit}')
    repo = FileRepository(db)
    items, total = await repo.list_files_paginated(skip=skip, limit=limit)
    logger.debug(f'Получено файлов: {len(items)} из {total}')
    return items, total


async def get_file(file_id: str, db: AsyncSession) -> StoredFile:
    """
    Получение файла по ID.
    """

    logger.debug(f'Получение файла: {file_id}')
    repo = FileRepository(db)
    file_item = await repo.get_file(file_id)
    if not file_item:
        logger.warning(f'Файл не найден: {file_id}')
        raise ResourceNotFound('file')
    return file_item


async def create_file(
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
    path = stored_file_path(stored_name)

    logger.debug(f'Запись файла на диск: \'{path}\'')
    async with aiofiles.open(path, 'wb') as f:
        await f.write(content)

    file_item = StoredFile(
        id=file_id,
        title=title,
        original_name=original_filename or stored_name,
        stored_name=stored_name,
        mime_type=content_type or mimetypes.guess_type(stored_name)[0] or 'application/octet-stream',
        size=len(content),
        processing_status='uploaded',
    )
    repo = FileRepository(db)
    created_file = await repo.create_file(file_item)
    logger.info(f'Файл создан успешно: \'{file_id}\' ({len(content)} байт)')
    return created_file


async def update_file(file_id: str, title: str, db: AsyncSession) -> StoredFile:
    """
    Обновление названия файла.
    """

    logger.debug(f'Обновление файла: \'{file_id}\', новое название: \'{title}\'')
    repo = FileRepository(db)
    file_item = await repo.get_file(file_id)
    if not file_item:
        logger.warning(f'Не удалось обновить: файл не найден: \'{file_id}\'')
        raise ResourceNotFound('file')
    file_item.title = title
    updated = await repo.update_file(file_item)
    logger.info(f'Файл обновлён: \'{file_id}\'')
    return updated


async def delete_file(file_id: str, db: AsyncSession) -> None:
    """
    Удаление файла и его записи из БД.
    """

    logger.info(f'Удаление файла: \'{file_id}\'')
    repo = FileRepository(db)
    file_item = await repo.get_file(file_id)
    if not file_item:
        logger.warning(f'Не удалось удалить: файл не найден: \'{file_id}\'')
        raise ResourceNotFound('file')
    disk_path = stored_file_path(file_item.stored_name)
    if disk_path.exists():
        logger.debug(f'Удаление файла с диска: \'{disk_path}\'')
        await aiofiles.os.remove(str(disk_path))
    await repo.delete_file(file_item)
    logger.info(f'Файл удалён успешно: \'{file_id}\'')


async def get_file_for_download(file_id: str, db: AsyncSession) -> tuple[StoredFile, Path]:
    """
    Файл и путь на диске для отдачи клиенту.
    """

    logger.debug(f'Получение пути файла: \'{file_id}\'')
    file_item = await get_file(file_id, db)
    stored_path = stored_file_path(file_item.stored_name)
    if not stored_path.exists():
        logger.error(f'Файл не найден на диске: \'{stored_path}\'')
        raise ResourceNotFound('stored_blob')
    return file_item, stored_path


async def create_alert(file_id: str, level: str, message: str, db: AsyncSession) -> Alert:
    """
    Создание алерта для файла.
    """

    logger.info(f'Создание алерта для файла \'{file_id}\': [{level}] \'{message}\'')
    alert = Alert(file_id=file_id, level=level, message=message)
    alert_repo = AlertRepository(db)
    return await alert_repo.create_alert(alert)
