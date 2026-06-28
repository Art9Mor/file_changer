from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Alert as AlertEntity
from src.domain.entities import StoredFile as FileEntity
from src.domain.interfaces.alert_repository import AlertRepository
from src.domain.interfaces.file_repository import FileRepository
from src.models import Alert, StoredFile


class FileRepositoryImpl(FileRepository):
    def __init__(self, session: AsyncSession):
        """
        Инициализация с сессией БД.
        """
        self.session = session

    async def list_files_paginated(self, skip: int, limit: int) -> tuple[list[FileEntity], int]:
        """
        Получение файлов с пагинацией.
        """
        total_sq = select(func.count()).select_from(StoredFile).scalar_subquery()
        stmt = (
            select(StoredFile, total_sq.label('total'))
            .order_by(StoredFile.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        if not rows:
            cnt = await self.session.execute(select(func.count()).select_from(StoredFile))
            return [], cnt.scalar_one()
        return [self._to_entity(row[0]) for row in rows], int(rows[0][1])

    async def get_file(self, file_id: str) -> FileEntity | None:
        """
        Получение файла по ID.
        """
        model = await self.session.get(StoredFile, file_id)
        if model is None:
            return None
        return self._to_entity(model) # type: ignore

    async def create_file(self, file: FileEntity) -> FileEntity:
        """
        Создание записи файла.
        """
        model = StoredFile(
            id=file.id,
            title=file.title,
            original_name=file.original_name,
            stored_name=file.stored_name,
            mime_type=file.mime_type,
            size=file.size,
            processing_status=file.processing_status,
            scan_status=file.scan_status,
            scan_details=file.scan_details,
            metadata_json=file.metadata_json,
            requires_attention=file.requires_attention,
            created_at=file.created_at,
            updated_at=file.updated_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update_file(self, file: FileEntity) -> FileEntity:
        """
        Обновление записи файла.
        """
        model = await self.session.get(StoredFile, file.id)
        if model is None:
            return file
        model.title = file.title
        model.processing_status = file.processing_status
        model.scan_status = file.scan_status
        model.scan_details = file.scan_details
        model.metadata_json = file.metadata_json
        model.requires_attention = file.requires_attention
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model) # type: ignore

    async def delete_file(self, file_id: str) -> None:
        """
        Удаление записи файла из БД.
        """
        model = await self.session.get(StoredFile, file_id)
        if model is not None:
            await self.session.delete(model)
            await self.session.commit()

    def _to_entity(self, model: StoredFile) -> FileEntity:
        """
        Преобразование ORM модели в сущность.
        """
        return FileEntity(
            id=model.id,
            title=model.title,
            original_name=model.original_name,
            stored_name=model.stored_name,
            mime_type=model.mime_type,
            size=model.size,
            processing_status=model.processing_status,
            scan_status=model.scan_status,
            scan_details=model.scan_details,
            metadata_json=model.metadata_json,
            requires_attention=model.requires_attention,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class AlertRepositoryImpl(AlertRepository):
    def __init__(self, session: AsyncSession):
        """
        Инициализация с сессией БД.
        """
        self.session = session

    async def list_alerts_paginated(self, skip: int, limit: int) -> tuple[list[AlertEntity], int]:
        """
        Получение алертов с пагинацией.
        """
        total_sq = select(func.count()).select_from(Alert).scalar_subquery()
        stmt = select(Alert, total_sq.label('total')).order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        rows = result.all()
        if not rows:
            cnt = await self.session.execute(select(func.count()).select_from(Alert))
            return [], cnt.scalar_one()
        return [self._to_entity(row[0]) for row in rows], int(rows[0][1])

    async def create_alert(self, alert: AlertEntity) -> AlertEntity:
        """
        Создание записи алерта.
        """
        model = Alert(
            file_id=alert.file_id,
            level=alert.level,
            message=alert.message,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: Alert) -> AlertEntity:
        """
        Преобразование ORM модели в сущность.
        """
        return AlertEntity(
            id=model.id,
            file_id=model.file_id,
            level=model.level,
            message=model.message,
            created_at=model.created_at,
        )