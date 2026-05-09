"""
Добавить индексы для оптимизации запросов.

Revision ID: 0001
Revises: 0d6439d2e79f
Create Date: 2026-05-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = '0d6439d2e79f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Добавить индексы.
    """
    # Индекс на created_at в таблице files для сортировки
    op.create_index('ix_files_created_at', 'files', ['created_at'], unique=False)

    # Индекс на file_id в таблице alerts для быстрого поиска алертов по файлу
    op.create_index('ix_alerts_file_id', 'alerts', ['file_id'], unique=False)

    # Индекс на created_at в таблице alerts для сортировки
    op.create_index('ix_alerts_created_at', 'alerts', ['created_at'], unique=False)


def downgrade() -> None:
    """
    Удалить индексы.
    """
    op.drop_index('ix_alerts_created_at', table_name='alerts')
    op.drop_index('ix_alerts_file_id', table_name='alerts')
    op.drop_index('ix_files_created_at', table_name='files')
