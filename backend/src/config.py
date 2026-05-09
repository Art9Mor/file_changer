import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class Settings:
    """
    Конфигурация API и интеграций.
    """

    api_key: str


@lru_cache
def get_settings() -> Settings:
    """
    Загрузка настроек один раз на процесс.
    """

    return Settings(api_key=os.environ.get('API_KEY', 'test-key-dev'))
