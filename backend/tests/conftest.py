import os

os.environ.setdefault('API_KEY', 'test-api-key-for-pytest')
os.environ.setdefault('POSTGRES_USER', 'pytest')
os.environ.setdefault('POSTGRES_PASSWORD', 'pytest')
os.environ.setdefault('POSTGRES_HOST', 'localhost')
os.environ.setdefault('PGPORT', '5432')
os.environ.setdefault('POSTGRES_DB', 'pytest')

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import src  # noqa: F401

from src.database import get_db
from src.main import create_app
from src.models import Base


@pytest.fixture(autouse=True)
def _noop_celery_scan(monkeypatch):
    monkeypatch.setattr(
        'src.api.routers.files.scan_file_for_threats.delay',
        lambda *args, **kwargs: None,
    )


@pytest.fixture(autouse=True)
def _isolated_storage(tmp_path, monkeypatch):
    storage = tmp_path / 'storage' / 'files'
    storage.mkdir(parents=True)
    monkeypatch.setattr('src.infrastructure.storage.STORAGE_DIR', storage)


@pytest_asyncio.fixture
async def test_engine(tmp_path):
    db_path = tmp_path / 'pytest.sqlite3'
    engine = create_async_engine(
        f'sqlite+aiosqlite:///{db_path}',
        connect_args={'check_same_thread': False},
    )

    @event.listens_for(engine.sync_engine, 'connect')
    def _sqlite_foreign_keys(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def app(test_engine):
    session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    application = create_app()

    async def override_get_db():
        async with session_maker() as session:
            yield session

    application.dependency_overrides[get_db] = override_get_db
    yield application
    application.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture
def api_headers():
    return {'X-API-Key': os.environ['API_KEY']}
