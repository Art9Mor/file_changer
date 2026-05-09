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
├── app.py               # re-export для uvicorn
├── main.py              # create_app(), сборка API
├── api/                 # роутеры и deps
├── application/         # сценарии использования
├── domain/              # константы домена
├── infrastructure/      # репозитории, storage
├── repositories.py      # реэкспорт репозиториев
├── models.py
├── schemas.py
├── database.py
├── config.py
└── tasks.py
```

## Переменные окружения

Требуются для Docker и локальной разработки. См. файл `.env.dev` в корне проекта.

## Тестирование эндпоинтов

Используйте Swagger UI по адресу `http://localhost:8000/docs` или:

Подставьте свой ключ, если меняли `API_KEY` в `.env.dev`:

```bash
# Загрузить файл
curl -X POST "http://localhost:8000/files" \
  -H "accept: application/json" \
  -H "X-API-Key: test-key-dev" \
  -F "title=My Document" \
  -F "file=@path/to/file.pdf"

# Получить список файлов
curl "http://localhost:8000/files" -H "X-API-Key: test-key-dev"

# Получить список алертов
curl "http://localhost:8000/alerts" -H "X-API-Key: test-key-dev"
```
