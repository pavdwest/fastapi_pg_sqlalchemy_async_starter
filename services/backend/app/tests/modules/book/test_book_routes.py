from fastapi import status
import pytest
from httpx import AsyncClient
from datetime import datetime

from src.modules.book.models import Book


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


@pytest.mark.anyio
async def test_update_one_with_all_fields(client: AsyncClient):
    item = await Book(
        **{
            'identifier': '978-3-16-148410-2',
            'name': 'A Brief Horror Story of Time Part Three',
            'author': 'Stephen Hawk Kingpin',
            'release_year': 2041,
        }
    ).save()

    response = await client.patch(
        f"/book/{item.id}",
        json={
            'identifier': '978-3-16-148410-3',
            'name': 'A Brief Horror Story of Time Part 3',
            'author': 'Stephen Hawk Kingfisher',
            'release_year': 2039,
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['identifier'] == '978-3-16-148410-3'
    assert data['name'] == 'A Brief Horror Story of Time Part 3'
    assert data['author'] == 'Stephen Hawk Kingfisher'
    assert data['release_year'] == 2039
    assert datetime.fromisoformat(data['created_at']) == item.created_at
    assert datetime.fromisoformat(data['updated_at']) > item.updated_at
    assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


@pytest.mark.anyio
async def test_update_one_with_some_fields(client: AsyncClient):
    item = await Book(
        **{
            'identifier': '978-3-16-148410-4',
            'name': 'A Brief Horror Story of Time Part Four',
            'author': 'Stephen Hawk Kingpin',
            'release_year': 2041,
        }
    ).save()
    response = await client.patch(
        f"/book/{item.id}",
        json={
            'identifier': '978-3-16-148410-5',
            'name': 'A Brief Horror Story of Time Part 4',
            'author': 'Stephen Hawk Kingfisher',
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['identifier'] == '978-3-16-148410-5'
    assert data['name'] == 'A Brief Horror Story of Time Part 4'
    assert data['author'] == 'Stephen Hawk Kingfisher'
    assert data['release_year'] == 2041
    assert datetime.fromisoformat(data['created_at']) == item.created_at
    assert datetime.fromisoformat(data['updated_at']) > item.updated_at
    assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


@pytest.mark.anyio
async def test_delete_one(client: AsyncClient):
    item = await Book(
        **{
            'identifier': '978-3-16-148410-6',
            'name': 'A Brief Horror Story of Time Part 5',
            'author': 'Stephen Hawk Kingpin',
            'release_year': 2041,
        }
    ).save()
    item_count = await Book.get_count()
    response = await client.delete(
        f"/book/{item.id}"
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data['message'] == f'Deleted one Book from the database.'
    assert data['count'] == 1
    assert (await Book.get_count()) == (item_count - 1)
