"""
Слой бизнес-логики и операций с файлами.
"""

import mimetypes
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import Depends, HTTPException, UploadFile, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import Alert, StoredFile
from src.repositories import AlertRepository, FileRepository

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "files"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


async def list_files(db: AsyncSession = Depends(get_db)) -> list[StoredFile]:
    """
    Получение всех файлов.
    """

    logger.debug('Получение всех файлов')
    repo = FileRepository(db)
    files = await repo.list_files()
    logger.debug(f'Получено файлов: {len(files)}')
    return files


async def list_files_paginated(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)) -> tuple[list[StoredFile], int]:
    """
    Получение файлов с пагинацией.
    """

    logger.debug(f'Получение файлов с пагинацией skip={skip} limit={limit}')
    repo = FileRepository(db)
    items, total = await repo.list_files_paginated(skip=skip, limit=limit)
    logger.debug(f'Получено файлов: {len(items)} из {total}')
    return items, total


async def list_alerts(db: AsyncSession = Depends(get_db)) -> list[Alert]:
    """
    Получение всех алертов.
    """

    logger.debug('Получение всех алертов')
    repo = AlertRepository(db)
    alerts = await repo.list_alerts()
    logger.debug(f'Получено алертов: {len(alerts)}')
    return alerts


async def list_alerts_paginated(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)) -> tuple[list[Alert], int]:
    """
    Получение алертов с пагинацией.
    """

    logger.debug(f'Получение алертов с пагинацией skip={skip} limit={limit}')
    repo = AlertRepository(db)
    items, total = await repo.list_alerts_paginated(skip=skip, limit=limit)
    logger.debug(f'Получено алертов: {len(items)} из {total}')
    return items, total


async def get_file(file_id: str, db: AsyncSession = Depends(get_db)) -> StoredFile:
    """
    Получение файла по ID.
    """

    logger.debug(f'Получение файла: {file_id}')
    repo = FileRepository(db)
    file_item = await repo.get_file(file_id)
    if not file_item:
        logger.warning(f'Файл не найден: {file_id}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file_item


async def create_file(title: str, upload_file: UploadFile, db: AsyncSession = Depends(get_db)) -> StoredFile:
    """
    Создание нового файла и сохранение на диск.
    """

    logger.info(f'Загрузка файла: \'{upload_file.filename}\' (название: \'{title}\')')
    content = await upload_file.read()
    if not content:
        logger.warning(f'Попытка загрузить пустой файл: \'{upload_file.filename}\'')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    MAX_FILE_SIZE = 10 * 1024 * 1024
    if len(content) > MAX_FILE_SIZE:
        logger.warning(f'Файл слишком большой: {len(content)} байт (макс: {MAX_FILE_SIZE})')
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f'File size exceeds {MAX_FILE_SIZE // (1024 * 1024)} MB limit')
    file_id = str(uuid4())
    suffix = Path(upload_file.filename or "").suffix
    stored_name = f"{file_id}{suffix}"
    stored_path = STORAGE_DIR / stored_name

    logger.debug(f'Запись файла на диск: \'{stored_path}\'')
    async with aiofiles.open(stored_path, "wb") as f:
        await f.write(content)

    file_item = StoredFile(
        id=file_id,
        title=title,
        original_name=upload_file.filename or stored_name,
        stored_name=stored_name,
        mime_type=upload_file.content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
        size=len(content),
        processing_status="uploaded",
    )
    repo = FileRepository(db)
    created_file = await repo.create_file(file_item)
    logger.info(f'Файл создан успешно: \'{file_id}\' ({len(content)} байт)')
    return created_file


async def update_file(file_id: str, title: str, db: AsyncSession = Depends(get_db)) -> StoredFile:
    """
    Обновление названия файла.
    """

    logger.debug(f'Обновление файла: \'{file_id}\', новое название: \'{title}\'')
    repo = FileRepository(db)
    file_item = await repo.get_file(file_id)
    if not file_item:
        logger.warning(f'Не удалось обновить: файл не найден: \'{file_id}\'')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    file_item.title = title
    updated = await repo.update_file(file_item)
    logger.info(f'Файл обновлён: \'{file_id}\'')
    return updated


async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """
    Удаление файла и его записи из БД.
    """

    logger.info(f'Удаление файла: \'{file_id}\'')
    repo = FileRepository(db)
    file_item = await repo.get_file(file_id)
    if not file_item:
        logger.warning(f'Не удалось удалить: файл не найден: \'{file_id}\'')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    stored_path = STORAGE_DIR / file_item.stored_name
    if stored_path.exists():
        logger.debug(f'Удаление файла с диска: \'{stored_path}\'')
        await aiofiles.os.remove(str(stored_path))
    await repo.delete_file(file_item)
    logger.info(f'Файл удалён успешно: \'{file_id}\'')


async def get_file_path(file_id: str, db: AsyncSession = Depends(get_db)) -> tuple[StoredFile, Path]:
    """
    Получение файла и пути для скачивания.
    """

    logger.debug(f'Получение пути файла: \'{file_id}\'')
    file_item = await get_file(file_id, db)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        logger.error(f'Файл не найден на диске: \'{stored_path}\'')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return file_item, stored_path


async def create_alert(file_id: str, level: str, message: str, db: AsyncSession = Depends(get_db)) -> Alert:
    """
    Создание алерта для файла.
    """

    logger.info(f'Создание алерта для файла \'{file_id}\': [{level}] \'{message}\'')
    alert = Alert(file_id=file_id, level=level, message=message)
    repo = AlertRepository(db)
    return await repo.create_alert(alert)
