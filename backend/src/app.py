"""
Точка входа FastAPI и определение маршрутов.
"""

import os
import src  # noqa: F401 - Initialize logging configuration
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi import File, Form, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger
from starlette import status

from src.schemas import AlertItem, FileItem, FileUpdate, PaginatedAlerts, PaginatedFiles
from src.service import (
    create_file,
    delete_file,
    get_file,
    list_alerts_paginated,
    list_files_paginated,
    update_file,
    STORAGE_DIR,
)
from src.tasks import scan_file_for_threats

# Получить API ключ из переменных окружения
API_KEY = os.environ.get('API_KEY', 'test-key-dev')


def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    Проверка API ключа.
    """
    if not x_api_key or x_api_key != API_KEY:
        logger.warning('Попытка доступа с неправильным API ключом')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid API key')
    return x_api_key


app = FastAPI(title='File Manager API', version='1.0.0', dependencies=[Depends(verify_api_key)])
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

logger.info('Приложение FastAPI инициализировано')


@app.get('/files', response_model=PaginatedFiles)
async def list_files_view(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    """
    Получение всех файлов с пагинацией.
    """

    logger.debug(f'GET /files вызван (skip={skip}, limit={limit})')
    items, total = await list_files_paginated(skip=skip, limit=limit)
    return {'items': items, 'total': total, 'skip': skip, 'limit': limit}


@app.get('/alerts', response_model=PaginatedAlerts)
async def list_alerts_view(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    """
    Получение всех алертов с пагинацией.
    """

    logger.debug(f'GET /alerts вызван (skip={skip}, limit={limit})')
    items, total = await list_alerts_paginated(skip=skip, limit=limit)
    return {'items': items, 'total': total, 'skip': skip, 'limit': limit}


@app.post("/files", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Загрузка нового файла.
    """

    logger.info(f'POST /files: загрузка \'{file.filename}\' с названием \'{title}\'')
    file_item = await create_file(title=title, upload_file=file)
    logger.debug(f'Планирование сканирования файла: \'{file_item.id}\'')
    scan_file_for_threats.delay(file_item.id)
    return file_item


@app.get("/files/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str):
    """
    Получение файла по ID.
    """

    logger.debug(f'GET /files/{file_id} вызван')
    return await get_file(file_id)


@app.patch("/files/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
):
    """
    Обновление названия файла.
    """

    logger.debug(f'PATCH /files/{file_id}: обновление названия на \'{payload.title}\'')
    return await update_file(file_id=file_id, title=payload.title)


@app.get("/files/{file_id}/download")
async def download_file(file_id: str):
    """
    Скачивание файла по ID.
    """

    logger.info(f'GET /files/{file_id}/download: запрос скачивания')
    file_item = await get_file(file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        logger.error(f'Файл не найден на диске: \'{stored_path}\'')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    logger.debug(f'Отправка файла: \'{file_item.original_name}\'')
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@app.delete("/files/{file_id}", status_code=204)
async def delete_file_view(file_id: str):
    """
    Удаление файла по ID.
    """

    logger.warning(f'DELETE /files/{file_id}: запрос на удаление')
    await delete_file(file_id)
