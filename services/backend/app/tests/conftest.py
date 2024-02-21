import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
import os

from tests.env import TEST_DB_SUFFIX    # MUST BE AT THE TOP!
from src.main import app
from src.database.service import DatabaseService
from src.tenant.models import Tenant
from src.tenant.validators import TenantCreate
from src.login.models import Login
from src.login.validators import LoginCreate


# Assert we've set the test environment variable
assert len(TEST_DB_SUFFIX) > 0
assert os.environ.get('DATABASE_NAME').endswith(TEST_DB_SUFFIX)
assert os.environ.get('DATABASE_NAME') != TEST_DB_SUFFIX

# Drop db
assert DatabaseService.drop_db(db_name_suffix_check=TEST_DB_SUFFIX)


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def client(login):
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url='http://test') as c:
            # Create token
            from src.auth import create_access_token, bearer_token_header
            access_token = create_access_token(login.identifier)
            access_header = bearer_token_header(access_token)
            c.headers = access_header
            c.login = login
            yield c


@pytest.fixture(scope='session')
async def login() -> Login:
    # Check if login already exists
    l = LoginCreate(
        identifier='test.user@test.com',
        password='secret_password',
    )
    ldb = await Login.read_by_identifier(l.identifier)
    if ldb is not None:
        return ldb

    # Create a user and tenant
    login = await Login.create_one(l)
    tenant = await Tenant.create_one(
        TenantCreate(
            identifier=login.identifier
        )
    )
    await tenant.provision()
    login.tenant_schema_name = tenant.schema_name
    login.verified = True
    return await login.save()
