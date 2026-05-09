from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.repositories import AlertRepository
from src.models import Alert


async def list_alerts(db: AsyncSession) -> list[Alert]:
    """
    Получение всех алертов.
    """

    logger.debug('Получение всех алертов')
    repo = AlertRepository(db)
    alerts = await repo.list_alerts()
    logger.debug(f'Получено алертов: {len(alerts)}')
    return alerts


async def list_alerts_paginated(skip: int, limit: int, db: AsyncSession) -> tuple[list[Alert], int]:
    """
    Получение алертов с пагинацией.
    """

    logger.debug(f'Получение алертов с пагинацией skip={skip} limit={limit}')
    repo = AlertRepository(db)
    items, total = await repo.list_alerts_paginated(skip=skip, limit=limit)
    logger.debug(f'Получено алертов: {len(items)} из {total}')
    return items, total
