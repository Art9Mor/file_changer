# Руководство по разработке бэкенда

## Установка

Установите зависимости для разработки:

```bash
pip install -e ".[dev]"
```

## Запуск

Запустите сервер разработки:

```bash
uvicorn src.app:app --host 0.0.0.0 --reload --port 8000
```

## Инструменты качества кода

### Ruff (линтинг и форматирование)

Проверка стиля кода:
```bash
ruff check src/
```

Автоисправление проблем:
```bash
ruff check --fix src/
```

Форматирование кода:
```bash
ruff format src/
```

Конфигурация находится в `ruff.toml`.

### Pre-commit хуки

Установите хуки один раз:
```bash
pre-commit install
```

Запустите хоки вручную:
```bash
pre-commit run --all-files
```

Конфигурация находится в `.pre-commit-config.yaml`.

## Логирование

Приложение использует `loguru` для структурированного логирования. Логи настраиваются автоматически при старте приложения.

Уровни логов:
- `DEBUG`: подробная информация для отладки (вызовы эндпоинтов, запросы)
- `INFO`: общая информация (загрузка файлов, завершение обработки)
- `WARNING`: предупреждения (подозрительные файлы, большие файлы)
- `ERROR`: ошибки (файл не найден, сбой обработки)

## Переменные окружения

Скопируйте `.env.dev.example` в `.env.dev`:
```bash
cp .env.dev.example .env.dev
```

Основные переменные (их читает `src/database.py` и приложение):
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `PGPORT` — сборка URL `postgresql+asyncpg://...` для SQLAlchemy и asyncpg
- `REDIS_URL` — брокер и backend Celery (если не задан, в worker можно использовать `CELERY_BROKER_URL`)
- `API_KEY` — значение заголовка `X-API-Key` для всех запросов к API

Пример для Docker см. в корневом `.env.dev.example`. Образ Postgres в compose слушает порт **5432** внутри сети контейнеров; с хоста БД доступна на **5433** (маппинг `5433:5432`).

## База данных

Выполните миграции:
```bash
alembic upgrade head
```

## Задачи Celery

Приложение использует Celery для асинхронной обработки задач. Задачи:
- `scan_file_for_threats`: проверка файла на угрозы
- `extract_file_metadata`: извлечение метаданных файла
- `send_file_alert`: отправка алертов

Запуск worker'а Celery:
```bash
celery -A src.tasks.celery_app worker -l info
```

## Архитектура

- `app.py` / `main.py`: точка входа и сборка приложения
- `api/`: HTTP-слой (зависимости, роутеры)
- `application/`: сценарии использования (use cases)
- `domain/`: доменные константы
- `infrastructure/`: репозитории, пути хранилища
- `repositories.py`: реэкспорт репозиториев (совместимость)
- `models.py`: ORM-модели SQLAlchemy
- `schemas.py`: Pydantic-схемы
- `database.py`: подключение к БД
- `tasks.py`: задачи Celery
- `config.py`: настройки из окружения
