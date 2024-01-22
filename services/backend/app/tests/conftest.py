################################
### THIS MUST BE AT THE TOP! ###
################################
import os
DATABASE_NAME: str  = os.environ.get('DATABASE_NAME')
os.environ['DATABASE_NAME'] = f"{DATABASE_NAME}_test"
################################

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from src.main import app
from src.database.service import DatabaseService
from src.tenant.models import Tenant
from src.tenant.validators import TenantCreate
from src.login.models import Login
from src.login.models import Login
from src.login.validators import LoginCreate


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def client():
    assert os.environ.get('DATABASE_NAME') == 'project_database_test'

    # Drop & recreate db
    DatabaseService.drop_db()
    DatabaseService.get()

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url='http://test') as c:
            yield c


@pytest.fixture(scope='session')
async def login() -> Login:
    # Create a user and tenant
    login = await Login.create_one(
        LoginCreate(
            identifier='test.user@test.com',
            password='secret_password',
        )
    )
    tenant = await Tenant.create_one(
        TenantCreate(
            identifier=login.identifier
        )
    )
    await tenant.provision()
    login.tenant_schema_name = tenant.schema_name
    return await login.save()
