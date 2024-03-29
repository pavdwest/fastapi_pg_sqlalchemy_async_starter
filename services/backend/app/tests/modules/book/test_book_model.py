import pytest

from httpx import AsyncClient

from src.login.models import Login
from src.modules.book.models import Book


@pytest.mark.anyio
async def test_create_one(client: AsyncClient, login: Login):
    """Test create one."""
    book = await Book(
        identifier='SomeIdentifier001',
        name='SomeName001',
        author='SomeAuthor001',
        release_year=1999,
    ).save(login.tenant_schema_name)

    assert book.id is not None
    assert book.identifier == 'SomeIdentifier001'
    assert book.name == 'SomeName001'
    assert book.author == 'SomeAuthor001'
    assert book.release_year == 1999
