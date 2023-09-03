from fastapi import status
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_all_empty(client: AsyncClient):
    response = await client.get(
        '/book'
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data == []


@pytest.mark.anyio
async def test_create_one_with_all_fields(client: AsyncClient):
    response = await client.post(
        '/book',
        json={
            'identifier': '978-3-16-148410-0',
            'name': 'A Brief Horror Story of Time',
            'author': 'Stephen Hawk King',
            'release_year': 2035,
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['identifier'] == '978-3-16-148410-0'
    assert data['name'] == 'A Brief Horror Story of Time'
    assert data['author'] == 'Stephen Hawk King'
    assert data['release_year'] == 2035
    assert data['created_at'] is not None
    assert data['updated_at'] is not None


@pytest.mark.anyio
async def test_create_one_with_only_mandatory_fields(client: AsyncClient):
    response = await client.post(
        '/book',
        json={
            'identifier': '978-3-16-148410-1',
            'name': 'A Brief Horror Story of Time Part Deux',
            'author': 'Stephen Hawk King',
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['identifier'] == '978-3-16-148410-1'
    assert data['name'] == 'A Brief Horror Story of Time Part Deux'
    assert data['author'] == 'Stephen Hawk King'
    assert data['release_year'] is None
    assert data['created_at'] is not None
    assert data['updated_at'] is not None
