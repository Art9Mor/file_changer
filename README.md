# File Changer

MVP файлообменника: загрузка файлов, фоновая проверка на подозрительные признаки, лента алертов. Стек: **FastAPI** (Python), **Next.js** (React), **PostgreSQL**, **Redis**, **Celery**.

## Требования

- Docker и Docker Compose (для контейнерного запуска)
- Либо локально: Python 3.14+, Node.js 20+, PostgreSQL и Redis

## Переменные окружения

Скопируйте пример в корень репозитория:

```bash
cp .env.dev.example .env.dev
```

Заполните значения для PostgreSQL, Redis и при необходимости `API_KEY`. Запросы к API требуют заголовок `X-API-Key`, совпадающий с `API_KEY`.

Для фронтенда в браузере при деплое задайте `NEXT_PUBLIC_API_URL` и `NEXT_PUBLIC_API_KEY` (см. `frontend/src/lib/config/publicEnv.ts`).

## Запуск в Docker

```bash
docker compose -f docker-compose.dev.yml up -d build
```

После старта контейнеров примените миграции:

```bash
docker exec -it backend alembic upgrade head
```

Убедитесь, что worker Celery запущен (сервис `backend-worker` в compose).

## Локальная разработка

**Бэкенд**

```bash
cd backend
pip install -e ".[dev]"
uvicorn src.app:app --host 0.0.0.0 --reload --port 8000
```

**Worker**

```bash
cd backend
celery -A src.tasks.celery_app worker -l info
```

**Фронтенд**

```bash
cd frontend
npm install
npm run dev
```

## Адреса

- UI: [http://localhost:3000](http://localhost:3000) — дублирующий маршрут: [http://localhost:3000/test](http://localhost:3000/test)
- OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)

С хоста PostgreSQL в compose доступен на порту **5433** (внутри сети контейнеров — `backend-db:5432`).

Дополнительно: `backend/DEVELOPMENT.md`, `backend/QUICKSTART.md`.
