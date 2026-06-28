from fastapi import APIRouter, Depends, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.alert_service import AlertService
from src.database import get_db
from src.schemas import PaginatedAlerts

router = APIRouter(prefix='/alerts', tags=['alerts'])


def get_alert_service() -> AlertService:
    """
    Получение экземпляра сервиса алертов.
    """
    return AlertService()


@router.get('', response_model=PaginatedAlerts)
async def list_alerts_view(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение всех алертов с пагинацией.
    """

    logger.debug(f'GET /alerts вызван (skip={skip}, limit={limit})')
    service = get_alert_service()
    items, total = await service.list_alerts_paginated(skip=skip, limit=limit, db=db)
    return {'items': items, 'total': total, 'skip': skip, 'limit': limit}