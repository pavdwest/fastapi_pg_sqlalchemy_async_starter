import os

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from src.main import app


# Config env vars
DATABASE_NAME: str  = os.environ.get('DATABASE_NAME')
os.environ['DATABASE_NAME'] = f"{DATABASE_NAME}_test"


@pytest.fixture(scope='session')
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope='session')
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url='http://test') as c:
            yield c
