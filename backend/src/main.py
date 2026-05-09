import src  # noqa: F401 - Initialize logging configuration
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.deps import verify_api_key
from src.api.routers import alerts, files


def create_app() -> FastAPI:
    """
    Фабрика приложения (удобно для тестов и альтернативных конфигураций).
    """

    application = FastAPI(
        title='File Manager API',
        version='1.0.0',
        dependencies=[Depends(verify_api_key)],
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            'http://localhost:3000',
            'http://127.0.0.1:3000',
        ],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    application.include_router(files.router)
    application.include_router(alerts.router)
    logger.info('Приложение FastAPI собрано (роутеры подключены)')
    return application


app = create_app()
