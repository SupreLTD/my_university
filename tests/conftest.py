from typing import Generator, Any
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
import settings
from main import app
import os
import asyncio
from db.session import get_db
import asyncpg

test_engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
test_async_session = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

CLEAN_TABlES = [
    'users',
]


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def run_migrations():
    os.system('alembic init migrations')
    os.system('alembic revision --autogenerate -m "test running migrations"')
    os.system('alembic upgrade heads')


@pytest.fixture(scope='session')
async def async_session_test():
    engine = create_async_engine(settings.TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope='function', autouse=True)
async def clean_tables(async_session_test):
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABlES:
                await session.execute(f"""TRUNCATE TABLer{table_for_cleaning};""")


@pytest.fixture(scope='function')
async def client() -> Generator[TestClient, Any, None]:
    async def _get_test_db():
        try:
            yield test_async_session()
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope='session')
async def asyncpg_pool():
    pool = await asyncpg.create_pool("".join(settings.TEST_DATABASE_URL.split("+asyncpg")))
    yield pool
    pool.close()


@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user_from_database_by_uuid(user_id: str):
        async with asyncpg_pool.acquire() as conn:
            return await conn.fetch("""SELECT * FROM users WHERE user_id = $1;""", user_id)

    return get_user_from_database_by_uuid
