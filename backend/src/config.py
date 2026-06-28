import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env.dev"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


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