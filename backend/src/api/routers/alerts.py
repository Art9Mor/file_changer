from fastapi import APIRouter, Depends, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.application import alerts as alert_cases
from src.database import get_db
from src.schemas import PaginatedAlerts

router = APIRouter(prefix='/alerts', tags=['alerts'])


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
    items, total = await alert_cases.list_alerts_paginated(skip=skip, limit=limit, db=db)
    return {'items': items, 'total': total, 'skip': skip, 'limit': limit}
