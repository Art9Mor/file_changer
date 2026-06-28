import asyncio
import os

from celery import Celery
from loguru import logger

from src.application.services.alert_service import AlertService
from src.application.services.file_service import FileService
from src.database import async_session_maker

REDIS_URL = os.environ.get('REDIS_URL', os.environ.get('CELERY_BROKER_URL', 'redis://backend-redis:6379/0'))

celery_app = Celery('file_tasks', broker=REDIS_URL, backend=REDIS_URL)

logger.info(f'Celery приложение инициализировано с брокером: {REDIS_URL}')


async def _process_file_scan(file_id: str) -> None:
    """
    Обработка сканирования файла.
    """
    async with async_session_maker() as session:
        service = FileService()
        await service.scan_file(file_id, session)


async def _process_file_metadata(file_id: str) -> None:
    """
    Обработка извлечения метаданных файла.
    """
    async with async_session_maker() as session:
        service = FileService()
        await service.extract_file_metadata(file_id, session)


async def _process_file_alert(file_id: str) -> None:
    """
    Обработка создания алерта для файла.
    """
    async with async_session_maker() as session:
        service = AlertService()
        await service.create_alert_from_file_processing(file_id, session)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def scan_file_for_threats(self, file_id: str) -> None:
    """
    Celery задача: сканирование файла на угрозы.
    """
    logger.debug(f'Celery задача запущена: scan_file_for_threats({file_id})')
    asyncio.run(_process_file_scan(file_id))


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def extract_file_metadata(self, file_id: str) -> None:
    """
    Celery задача: извлечение метаданных файла.
    """
    logger.debug(f'Celery задача запущена: extract_file_metadata({file_id})')
    asyncio.run(_process_file_metadata(file_id))


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def send_file_alert(self, file_id: str) -> None:
    """
    Celery задача: отправка алерта о файле.
    """
    logger.debug(f'Celery задача запущена: send_file_alert({file_id})')
    asyncio.run(_process_file_alert(file_id))