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

## API интеграция

Файл `src/app/api.ts` содержит функции для работы с бэкендом:

- `fetchFiles()` — получить список всех файлов
- `fetchAlerts()` — получить список всех алертов
- `uploadFile(title, file)` — загрузить новый файл
- `deleteFile(fileId)` — удалить файл
- `updateFile(fileId, title)` — обновить название файла
- `downloadFile(fileId)` — скачать файл

## Компоненты

### FileTable
Таблица с отображением загруженных файлов с действиями: скачивание, переименование, удаление.

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


This will build the project as a standalone app inside the Docker image.

## Deploying to Google Cloud Run

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) so you can use `gcloud` on the command line.
1. Run `gcloud auth login` to log in to your account.
1. [Create a new project](https://cloud.google.com/run/docs/quickstarts/build-and-deploy) in Google Cloud Run (e.g. `nextjs-docker`). Ensure billing is turned on.
1. Build your container image using Cloud Build: `gcloud builds submit --tag gcr.io/PROJECT-ID/helloworld --project PROJECT-ID`. This will also enable Cloud Build for your project.
1. Deploy to Cloud Run: `gcloud run deploy --image gcr.io/PROJECT-ID/helloworld --project PROJECT-ID --platform managed --allow-unauthenticated`. Choose a region of your choice.

   - You will be prompted for the service name: press Enter to accept the default name, `helloworld`.
   - You will be prompted for [region](https://cloud.google.com/run/docs/quickstarts/build-and-deploy#follow-cloud-run): select the region of your choice, for example `us-central1`.

## Running Locally

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
bun run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `pages/index.js`. The page auto-updates as you edit the file.

[API routes](https://nextjs.org/docs/api-routes/introduction) can be accessed on [http://localhost:3000/api/hello](http://localhost:3000/api/hello). This endpoint can be edited in `pages/api/hello.js`.

The `pages/api` directory is mapped to `/api/*`. Files in this directory are treated as [API routes](https://nextjs.org/docs/api-routes/introduction) instead of React pages.
