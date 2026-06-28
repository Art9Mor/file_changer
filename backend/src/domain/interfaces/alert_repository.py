from abc import ABC, abstractmethod

from src.domain.entities import Alert


class AlertRepository(ABC):
    @abstractmethod
    async def list_alerts_paginated(self, skip: int, limit: int) -> tuple[list[Alert], int]:
        """
        Получение алертов с пагинацией.
        """
        pass

    @abstractmethod
    async def create_alert(self, alert: Alert) -> Alert:
        """
        Создание записи алерта.
        """
        pass