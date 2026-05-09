"""
Точка входа FastAPI и определение маршрутов.
"""

import src  # noqa: F401 - Initialize logging configuration
from fastapi import FastAPI, HTTPException
from fastapi import File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger
from starlette import status

from src.schemas import AlertItem, FileItem, FileUpdate
from src.service import create_file, delete_file, get_file, list_alerts, list_files, update_file, STORAGE_DIR
from src.tasks import scan_file_for_threats

app = FastAPI(title="File Manager API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info('Приложение FastAPI инициализировано')


@app.get("/files", response_model=list[FileItem])
async def list_files_view():
    """
    Получение всех файлов с метаданными.
    """

    logger.debug('GET /files вызван')
    return await list_files()


@app.get("/alerts", response_model=list[AlertItem])
async def list_alerts_view():
    """
    Получение всех алертов.
    """

    logger.debug('GET /alerts вызван')
    return await list_alerts()


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
