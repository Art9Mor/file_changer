from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileItem(BaseModel):
    """
    Схема ответа файла с метаданными.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    original_name: str
    mime_type: str
    size: int
    processing_status: str
    scan_status: str | None
    scan_details: str | None
    metadata_json: dict | None
    requires_attention: bool
    created_at: datetime
    updated_at: datetime


class FileUpdate(BaseModel):
    """
    Схема для обновления файла.
    """

    title: str


class AlertItem(BaseModel):
    """
    Схема ответа алерта.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    file_id: str
    level: str
    message: str
    created_at: datetime


class PaginatedFiles(BaseModel):
    """
    Пагинированный ответ списка файлов.
    """

    items: list[FileItem]
    total: int
    skip: int
    limit: int


class PaginatedAlerts(BaseModel):
    """
    Пагинированный ответ списка алертов.
    """

    items: list[AlertItem]
    total: int
    skip: int
    limit: int
