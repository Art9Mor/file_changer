from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Alert
from src.infrastructure.persistence.repositories import AlertRepositoryImpl, FileRepositoryImpl


class AlertService:
    def __init__(self):
        """
        Инициализация сервиса.
        """
        pass

    async def list_alerts_paginated(self, skip: int, limit: int, db: AsyncSession) -> tuple[list[Alert], int]:
        """
        Получение алертов с пагинацией.
        """
        logger.debug(f'Получение алертов с пагинацией skip={skip} limit={limit}')
        repo = AlertRepositoryImpl(db)
        items, total = await repo.list_alerts_paginated(skip, limit)
        logger.debug(f'Получено алертов: {len(items)} из {total}')
        return items, total

    async def create_alert_from_file_processing(self, file_id: str, db: AsyncSession) -> None:
        """
        Создание алерта по результатам обработки файла.
        """
        logger.info(f'Отправка алерта для файла: {file_id}')
        file_repo = FileRepositoryImpl(db)
        file_item = await file_repo.get_file(file_id)
        if not file_item:
            logger.error(f'Файл не найден для алерта: {file_id}')
            return

        if file_item.processing_status == 'failed':
            alert = Alert(
                id=None,
                file_id=file_id,
                level='critical',
                message='Ошибка обработки файла',
                created_at=None,
            )
            logger.error(f'Создание критического алерта для {file_id}: ошибка обработки')
        elif file_item.requires_attention:
            alert = Alert(
                id=None,
                file_id=file_id,
                level='warning',
                message=f'Файл требует внимания: {file_item.scan_details}',
                created_at=None,
            )
            logger.warning(f'Создание предупреждающего алерта для {file_id}: {file_item.scan_details}')
        else:
            alert = Alert(
                id=None,
                file_id=file_id,
                level='info',
                message='Файл обработан успешно',
                created_at=None,
            )
            logger.info(f'Файл {file_id} обработан успешно')

        alert_repo = AlertRepositoryImpl(db)
        await alert_repo.create_alert(alert)
        logger.debug(f'Алерт создан для файла: {file_id}')