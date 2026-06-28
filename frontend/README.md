# File Changer — Фронтенд

Интерфейс для File Changer MVP на базе Next.js 13+ (App Router) и React 18.

## Структура проекта

```
src/
├── app/
│   ├── layout.tsx          # Главный layout приложения
│   ├── page.tsx            # Главная страница с управлением файлами
│   ├── api.ts              # API клиент для работы с бэкендом
│   └── components/         # React компоненты
│       ├── FileTable.tsx    # Таблица загруженных файлов
│       ├── AlertTable.tsx   # Таблица алертов
│       └── UploadModal.tsx  # Модальное окно для загрузки файлов
```

## Технологии

- **Next.js 13+** — фреймворк React с App Router
- **React 18.2** — библиотека UI компонентов
- **TypeScript** — типизированный JavaScript
- **Bootstrap 5.3 + react-bootstrap** — CSS компоненты
- **fetch API** — HTTP запросы к бэкенду

## Установка

Сперва создайте .env.local и env.production с содержимым, как в файлах example (API_KEY назначается опционально).   

```bash
cd frontend
npm install
```

## Запуск

### Разработка
```bash
npm run dev
```

Приложение доступно на `http://localhost:3000`

### Production сборка
```bash
npm run build
npm start
```

## Слои и API

- **`src/lib/config/publicEnv.ts`** — базовый URL и ключ API (`NEXT_PUBLIC_*`)
- **`src/lib/api/`** — типы, HTTP-заголовки, клиенты `filesClient` и `alertsClient`
- **`src/features/file-manager/`** — хук `useFileManagerDashboard` и экран `FileManagerDashboard`

Ко всем запросам добавляется заголовок `X-API-Key` (в dev по умолчанию `test-key-dev`, на проде задайте `NEXT_PUBLIC_API_KEY`).

## Компоненты

### FileTable
Таблица с отображением загруженных файлов и кнопкой скачивания (запрос с `X-API-Key`).

### AlertTable
Таблица с алертами о проблемах при обработке файлов, цветные метки по уровню серьёзности.

### UploadModal
Модальное окно для выбора файла и ввода названия, с обработкой ошибок и состояния загрузки.

## Docker

```bash
docker build -t nextjs-docker .
docker run -p 3000:3000 nextjs-docker
```

Или использовать Bun:
```bash
docker build -f Dockerfile.bun -t nextjs-docker .
```
