import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from src.main import app


@pytest.fixture(scope='session')
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope='session')
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url='http://test') as c:
            yield c
