from fastapi import status
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_home(client: AsyncClient):
    response = await client.get(
        '/home'
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['message'] == 'Hello boils and ghouls'
