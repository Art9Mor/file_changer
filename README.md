# File Changer — MVP файлообменника

Простой проект для загрузки файлов, проверки их на подозрительный контент и отображения результатов обработки.

## Что это
- Название: **File Changer**
- Назначение: обмен файлами с бэкендом на FastAPI и фронтендом на Next.js
- Как работает: пользователь загружает файл, сервер сохраняет его, асинхронно проверяет на угрозы и создает алерты для администратора

## Установка зависимостей
```bash
cd backend
pip install -e ".[dev]"
```

## Переменные окружения
Скопируйте пример и заполните значения:
```bash
cp .env.dev.example .env.dev
```
Заполните `.env.dev` необходимыми значениями, прежде чем запускать приложение.

## Запуск через Docker
```bash
docker compose -f docker-compose.dev.yml up -d
```

После запуска контейнеров выполните миграции:
```bash
docker exec -it backend alembic upgrade head
```

## Запуск из терминала
### Бэкенд
```bash
cd backend
uvicorn src.app:app --host 0.0.0.0 --reload --port 8000
```

### Celery
Запустите worker Celery параллельно:
```bash
cd backend
celery -A src.tasks.celery_app worker -l info
```

### Фронтенд
```bash
cd frontend
npm install
npm run dev
```

## Открыть в браузере
- Фронтенд: `http://localhost:3000`
- Бэкенд: `http://localhost:8000`
- Документация OpenAPI: `http://localhost:8000/docs`


Для локальной разработки используйте `backend/DEVELOPMENT.md` и `backend/QUICKSTART.md`.
