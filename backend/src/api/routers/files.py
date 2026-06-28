from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.application.exceptions import EmptyFileError, FileTooLargeError, ResourceNotFound
from src.application.services.file_service import FileService
from src.database import get_db
from src.schemas import FileItem, FileUpdate, PaginatedFiles
from src.tasks.celery_tasks import scan_file_for_threats

router = APIRouter(prefix='/files', tags=['files'])


def get_file_service() -> FileService:
    """
    Получение экземпляра сервиса файлов.
    """
    return FileService()


@router.get('', response_model=PaginatedFiles)
async def list_files_view(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение всех файлов с пагинацией.
    """

    logger.debug(f'GET /files вызван (skip={skip}, limit={limit})')
    service = get_file_service()
    items, total = await service.list_files_paginated(skip, limit, db)
    return {'items': items, 'total': total, 'skip': skip, 'limit': limit}


@router.post('', response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Загрузка нового файла.
    """

    logger.info(f'POST /files: загрузка \'{file.filename}\' с названием \'{title}\'')
    content = await file.read()
    service = get_file_service()
    try:
        file_item = await service.create_file(
            db,
            title=title,
            original_filename=file.filename,
            content_type=file.content_type,
            content=content,
        )
    except EmptyFileError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File is empty') from None
    except FileTooLargeError as exc:
        mb = exc.max_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f'File size exceeds {mb} MB limit',
        ) from None
    logger.debug(f'Планирование сканирования файла: \'{file_item.id}\'')
    scan_file_for_threats.delay(file_item.id)
    return file_item


@router.get('/{file_id}', response_model=FileItem)
async def get_file_view(file_id: str, db: AsyncSession = Depends(get_db)):
    """
    Получение файла по ID.
    """

    logger.debug(f'GET /files/{file_id} вызван')
    service = get_file_service()
    try:
        return await service.get_file(file_id, db)
    except ResourceNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found') from None


@router.patch('/{file_id}', response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление названия файла.
    """

    logger.debug(f'PATCH /files/{file_id}: обновление названия на \'{payload.title}\'')
    service = get_file_service()
    try:
        return await service.update_file(file_id, payload.title, db)
    except ResourceNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found') from None


@router.get('/{file_id}/download')
async def download_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """
    Скачивание файла по ID.
    """

    logger.info(f'GET /files/{file_id}/download: запрос скачивания')
    service = get_file_service()
    try:
        file_item, stored_path = await service.get_file_for_download(file_id, db)
    except ResourceNotFound as exc:
        detail = 'Stored file not found' if exc.resource == 'stored_blob' else 'File not found'
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from None
    logger.debug(f'Отправка файла: \'{file_item.original_name}\'')
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete('/{file_id}', status_code=204)
async def delete_file_view(file_id: str, db: AsyncSession = Depends(get_db)):
    """
    Удаление файла по ID.
    """

    logger.warning(f'DELETE /files/{file_id}: запрос на удаление')
    service = get_file_service()
    try:
        await service.delete_file(file_id, db)
    except ResourceNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found') from None