# Быстрый старт

## Настройка

1. Установите зависимости:
```bash
cd backend
pip install -e ".[dev]"
```

2. Установите pre-commit хуки (рекомендуется):
```bash
pre-commit install
```

## Запуск сервера разработки

```bash
uvicorn src.app:app --host 0.0.0.0 --reload --port 8000
```

API будет доступно по адресу `http://localhost:8000/docs` (Swagger UI).

## Проверка качества кода

### Перед коммитом (автоматически через pre-commit):

```bash
# Проверка ruff
ruff check src/

# Форматирование ruff
ruff format src/

# Запуск всех pre-commit хуков
pre-commit run --all-files
```

## Логирование

Логи настраиваются автоматически при старте приложения:
- **Консоль**: уровень `DEBUG` с цветами
- **Файл**: уровень `INFO` в `backend/logs/app.log`

Логи вращаются при 500 МБ и хранятся 10 дней.

## Архитектура бэкенда

```
src/
├── __init__.py          # настройка логирования
├── app.py               # маршруты FastAPI
├── service.py           # бизнес-логика
├── repositories.py      # доступ к базе данных
├── models.py            # ORM-модели SQLAlchemy
├── schemas.py           # Pydantic-схемы
├── database.py          # настройки базы данных
└── tasks.py             # задачи Celery
```

## Переменные окружения

Требуются для Docker и локальной разработки. См. файл `.env.dev` в корне проекта.

## Тестирование эндпоинтов

Используйте Swagger UI по адресу `http://localhost:8000/docs` или:

```bash
# Загрузить файл
curl -X POST "http://localhost:8000/files" \
  -H "accept: application/json" \
  -F "title=My Document" \
  -F "file=@path/to/file.pdf"

# Получить список файлов
curl "http://localhost:8000/files"

# Получить список алертов
curl "http://localhost:8000/alerts"
```
