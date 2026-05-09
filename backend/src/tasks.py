"""
Celery задачи для обработки файлов и сканирования угроз.
"""

import asyncio
import os
from pathlib import Path

import aiofiles
from celery import Celery
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.models import Alert
from src.repositories import AlertRepository, FileRepository
from src.service import STORAGE_DIR

REDIS_URL = os.environ.get('REDIS_URL', 'redis://backend-redis:6379/0')

celery_app = Celery('file_tasks', broker=REDIS_URL, backend=REDIS_URL)

logger.info(f'Celery приложение инициализировано с брокером: {REDIS_URL}')


def _get_db_session():
    """
    Создание фабрики сессий БД для задач Celery.
    """

    DB_URL = (
        f'postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}: '
        f'{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:'
        f'{os.environ.get("PGPORT")}/{os.environ.get("POSTGRES_DB")}'
    )
    engine = create_async_engine(DB_URL)
    return async_sessionmaker(engine, expire_on_commit=False)


async def _scan_file_for_threats(file_id: str) -> None:
    """
    Сканирование файла на подозрительные признаки.
    """

    logger.info(f'Начало проверки угроз для файла: {file_id}')
    async_session_maker = _get_db_session()

    async with async_session_maker() as session:
        repo = FileRepository(session)
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

        if file_item.size > 10 * 1024 * 1024:
            logger.warning(f'Файл слишком большой: {file_item.size} байт для файла {file_id}')
            reasons.append('файл больше 10 МБ')

        if extension == '.pdf' and file_item.mime_type not in {'application/pdf', 'application/octet-stream'}:
            logger.warning(f'Несоответствие mime-типа PDF: {file_item.mime_type} для файла {file_id}')
            reasons.append('расширение pdf не соответствует mime-типу')

        file_item.scan_status = 'suspicious' if reasons else 'clean'
        file_item.scan_details = ', '.join(reasons) if reasons else 'угроз не найдено'
        file_item.requires_attention = bool(reasons)
        await repo.update_file(file_item)
        logger.info(f'Проверка угроз завершена для файла: {file_id}, статус: {file_item.scan_status}')

    extract_file_metadata.delay(file_id)


async def _extract_file_metadata(file_id: str) -> None:
    """
    Извлечение метаданных файла.
    """

    logger.info(f'Начало извлечения метаданных для файла: {file_id}')
    async_session_maker = _get_db_session()

    async with async_session_maker() as session:
        repo = FileRepository(session)
        file_item = await repo.get_file(file_id)
        if not file_item:
            logger.error(f'Файл не найден для извлечения метаданных: {file_id}')
            return

        stored_path = STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            logger.error(f'Файловый объект не найден: {stored_path}')
            file_item.processing_status = 'failed'
            file_item.scan_status = file_item.scan_status or 'failed'
            file_item.scan_details = 'файл не найден на диске при извлечении метаданных'
            await repo.update_file(file_item)
            send_file_alert.delay(file_id)
            return

        metadata = {
            'extension': Path(file_item.original_name).suffix.lower(),
            'size_bytes': file_item.size,
            'mime_type': file_item.mime_type,
        }

        logger.debug(f'Извлечение метаданных для {file_id}, mime_type: {file_item.mime_type}')

        if file_item.mime_type.startswith('text/'):
            logger.debug(f'Чтение текстового файла: {file_id}')
            async with aiofiles.open(stored_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read()
            metadata['line_count'] = len(content.splitlines())
            metadata['char_count'] = len(content)
            logger.debug(f'Текстовый файл {file_id}: {metadata["line_count"]} строк, {metadata["char_count"]} символов')
        elif file_item.mime_type == 'application/pdf':
            logger.debug(f'Чтение PDF-файла: {file_id}')
            async with aiofiles.open(stored_path, 'rb') as f:
                content = await f.read()
            metadata['approx_page_count'] = max(content.count(b'/Type /Page'), 1)
            logger.debug(f'PDF-файл {file_id}: ~{metadata["approx_page_count"]} страниц')

        file_item.metadata_json = metadata
        file_item.processing_status = 'processed'
        await repo.update_file(file_item)
        logger.info(f'Извлечение метаданных завершено для файла: {file_id}')

    send_file_alert.delay(file_id)


async def _send_file_alert(file_id: str) -> None:
    """
    Отправка алерта по результатам обработки файла.
    """

    logger.info(f'Отправка алерта для файла: {file_id}')
    async_session_maker = _get_db_session()

    async with async_session_maker() as session:
        repo = FileRepository(session)
        file_item = await repo.get_file(file_id)
        if not file_item:
            logger.error(f'Файл не найден для алерта: {file_id}')
            return

        alert_repo = AlertRepository(session)
        if file_item.processing_status == 'failed':
            alert = Alert(file_id=file_id, level='critical', message='Ошибка обработки файла')
            logger.error(f'Создание критического алерта для {file_id}: ошибка обработки')
        elif file_item.requires_attention:
            alert = Alert(
                file_id=file_id,
                level='warning',
                message=f'Файл требует внимания: {file_item.scan_details}',
            )
            logger.warning(f'Создание предупреждающего алерта для {file_id}: {file_item.scan_details}')
        else:
            alert = Alert(file_id=file_id, level='info', message='Файл обработан успешно')
            logger.info(f'Файл {file_id} обработан успешно')

        await alert_repo.create_alert(alert)
        logger.debug(f'Алерт создан для файла: {file_id}')


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def scan_file_for_threats(self, file_id: str) -> None:
    """
    Celery задача: сканирование файла на угрозы.
    """

    logger.debug(f'Celery задача запущена: scan_file_for_threats({file_id})')
    asyncio.run(_scan_file_for_threats(file_id))


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def extract_file_metadata(self, file_id: str) -> None:
    """
    Celery задача: извлечение метаданных файла.
    """

    logger.debug(f'Celery задача запущена: extract_file_metadata({file_id})')
    asyncio.run(_extract_file_metadata(file_id))


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def send_file_alert(self, file_id: str) -> None:
    """
    Celery задача: отправка алерта о файле.
    """

    logger.debug(f'Celery задача запущена: send_file_alert({file_id})')
    asyncio.run(_send_file_alert(file_id))
