from fastapi import Header, HTTPException
from loguru import logger
from starlette import status

from src.config import get_settings


def verify_api_key(x_api_key: str | None = Header(None)) -> str:
    """
    Проверка API ключа.
    """
    expected = get_settings().api_key
    if not x_api_key or x_api_key != expected:
        logger.warning('Попытка доступа с неправильным API ключом')
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid API key')
    return x_api_key
