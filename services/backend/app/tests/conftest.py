################################
### THIS MUST BE AT THE TOP! ###
################################
import os
TEST_DB_SUFFIX = '_test'
DATABASE_NAME: str  = os.environ.get('DATABASE_NAME')
os.environ['DATABASE_NAME'] = f"{DATABASE_NAME}{TEST_DB_SUFFIX}"
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
    # Assert we've set the test environment variable
    assert os.environ.get('DATABASE_NAME')[-len(TEST_DB_SUFFIX):] == TEST_DB_SUFFIX

    # Drop db
    assert DatabaseService.drop_db(db_name_suffix_check=TEST_DB_SUFFIX)

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
