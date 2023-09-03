import os

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient


# Config env vars - append _test to the db name
DATABASE_NAME: str  = os.environ.get('DATABASE_NAME')
os.environ['DATABASE_NAME'] = f"{DATABASE_NAME}_test"


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def client():
    # Lazy import to ensure env vars are set
    from src.main import app
    from src.database.service import DatabaseService

    # Drop the db before each run - will be recreated if it doesn't exist
    DatabaseService.drop_db()

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url='http://test') as c:
            yield c
