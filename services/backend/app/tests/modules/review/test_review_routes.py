from fastapi import status
import pytest
from httpx import AsyncClient
from datetime import datetime

from src.versions import ApiVersion
from src.login.models import Login
from src.modules.book.models import Book
from src.modules.critic.models import Critic
from src.modules.review.models import Review


ModelClass = Review
route_base = f"{ApiVersion.V1}/{ModelClass.__tablename__}"
get_model_member_count = 8
bulk_response_member_count = 3


# @pytest.fixture()
async def new_book(login: Login) -> Book:
    next_item_id = await Book.get_count(schema_name=login.tenant_schema_name) + 1
    return await Book(
        **{
            'identifier': f"book {next_item_id} identifier",
            'name': f"book {next_item_id} name",
            'author': f"book {next_item_id} author",
            'release_year': 2040 + next_item_id,
        }
    ).save(schema_name=login.tenant_schema_name)


# @pytest.fixture()
async def new_critic(login: Login) -> Critic:
    next_item_id = await Critic.get_count(schema_name=login.tenant_schema_name) + 1
    return await Critic(
        **{
            'username': f"critic {next_item_id} username",
            'bio': f"critic {next_item_id} bio",
            'name': f"critic {next_item_id} name",
        }
    ).save(schema_name=login.tenant_schema_name)


# @pytest.fixture()
async def new_item(login: Login) -> Review:
    book = await new_book(login)
    critic = await new_critic(login)

    return await Review(
        **{
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 4,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    ).save(schema_name=login.tenant_schema_name)


@pytest.mark.anyio
async def test_read_all_empty(client: AsyncClient):
    response = await client.get(
        route_base
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data == []


@pytest.mark.anyio
async def test_create_one_with_all_fields(
    client: AsyncClient,
):
    book = await new_book(client.login)
    critic = await new_critic(client.login)

    response = await client.post(
        route_base,
        json={
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 4,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['id'] > 0
    assert data['title'] == f"Critic {critic.id}'s review of Book {book.id} title"
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 4
    assert data['body'] == f"Critic {critic.id}'s review of Book {book.id} body"
    assert data['created_at'] is not None
    assert data['updated_at'] is not None


@pytest.mark.anyio
async def test_create_one_with_only_mandatory_fields(
    client: AsyncClient,
):
    book = await new_book()
    critic = await new_critic()

    response = await client.post(
        route_base,
        json={
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 4,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['id'] > 0
    assert data['title'] == f"Critic {critic.id}'s review of Book {book.id} title"
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 4
    assert data['body'] == f"Critic {critic.id}'s review of Book {book.id} body"
    assert data['created_at'] is not None
    assert data['updated_at'] is not None


@pytest.mark.anyio
async def test_update_one_with_all_fields(
    client: AsyncClient,
):
    book = await new_book()
    critic = await new_critic()
    item = await new_item()

    response = await client.patch(
        f"{route_base}/{item.id}",
        json={
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 4,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['title'] == f"Critic {critic.id}'s review of Book {book.id} title"
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 4
    assert data['body'] == f"Critic {critic.id}'s review of Book {book.id} body"
    assert datetime.fromisoformat(data['created_at']) == item.created_at
    assert datetime.fromisoformat(data['updated_at']) > item.updated_at
    assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


@pytest.mark.anyio
async def test_update_one_does_not_apply_none(client: AsyncClient):
    book = await new_book()
    critic = await new_critic()
    item = await new_item()

    response = await client.patch(
        f"{route_base}/{item.id}",
        json={
            'title': '',
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 3,
            'body': None,
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['title'] == ''
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 3
    assert data['body'] == item.body
    assert datetime.fromisoformat(data['created_at']) == item.created_at
    assert datetime.fromisoformat(data['updated_at']) > item.updated_at
    assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


@pytest.mark.anyio
async def test_update_one_with_only_mandatory_fields(client: AsyncClient):
    book = await new_book()
    critic = await new_critic()
    item = await new_item()

    response = await client.patch(
        f"{route_base}/{item.id}",
        json={
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 4,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['title'] == f"Critic {critic.id}'s review of Book {book.id} title"
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 4
    assert data['body'] == f"Critic {critic.id}'s review of Book {book.id} body"
    assert datetime.fromisoformat(data['created_at']) == item.created_at
    assert datetime.fromisoformat(data['updated_at']) > item.updated_at
    assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


@pytest.mark.anyio
async def test_update_one_with_payload_with_all_fields(client: AsyncClient):
    book = await new_book()
    critic = await new_critic()
    item = await new_item()

    response = await client.patch(
        f"{route_base}/{item.id}",
        json={
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 4,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['title'] == f"Critic {critic.id}'s review of Book {book.id} title"
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 4
    assert data['body'] == f"Critic {critic.id}'s review of Book {book.id} body"
    assert datetime.fromisoformat(data['created_at']) == item.created_at
    assert datetime.fromisoformat(data['updated_at']) > item.updated_at
    assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


@pytest.mark.anyio
async def test_update_one_by_payload_with_only_mandatory_fields(client: AsyncClient):
    book = await new_book()
    critic = await new_critic()
    item = await new_item()

    response = await client.patch(
        f"{route_base}",
        json={
            'id': item.id,
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 3,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['title'] == f"Critic {critic.id}'s review of Book {book.id} title"
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 3
    assert data['body'] == f"Critic {critic.id}'s review of Book {book.id} body"
    assert datetime.fromisoformat(data['created_at']) == item.created_at
    assert datetime.fromisoformat(data['updated_at']) > item.updated_at
    assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


@pytest.mark.anyio
async def test_delete_one(client: AsyncClient):
    item = await new_item()
    item_count = await Review.get_count(schema_name=client.login.tenant_schema_name)
    response = await client.delete(
        f"{route_base}/{item.id}"
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == bulk_response_member_count
    assert data['count'] == 1
    assert data['message'] == f'Deleted one Review from the database.'
    assert data['ids'] == [item.id]
    assert (await Review.get_count(schema_name=client.login.tenant_schema_name)) == (item_count - 1)


@pytest.mark.anyio
async def test_create_bulk(client: AsyncClient):
    book1 = await new_book()
    critic1 = await new_critic()
    book2 = await new_book()
    critic2 = await new_critic()

    # Get count before
    item_count = await Review.get_count(schema_name=client.login.tenant_schema_name)

    # Create items
    response = await client.post(
        f"{route_base}/bulk",
        json=[
                # With all fields
                {
                    'title': f"Critic {critic1.id}'s review of Book {book1.id} title",
                    'critic_id': critic1.id,
                    'book_id': book1.id,
                    'rating': 3,
                    'body': f"Critic {critic1.id}'s review of Book {book1.id} body",
                },
                # With only mandatory fields
                {
                    'title': f"Critic {critic2.id}'s review of Book {book2.id} title",
                    'critic_id': critic2.id,
                    'book_id': book2.id,
                    'rating': 3,
                    'body': f"Critic {critic2.id}'s review of Book {book2.id} body",
                }
        ]
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == bulk_response_member_count
    assert data['count'] == 2
    assert data['message'] == f'Created multiple Reviews in the database.'
    assert (await Review.get_count(schema_name=client.login.tenant_schema_name)) == (item_count + 2)

    # Assert values
    item1 = await Review.read_by_id(id=data['ids'][0])
    assert item1.title == f"Critic {critic1.id}'s review of Book {book1.id} title"
    assert item1.critic_id == critic1.id
    assert item1.book_id == book1.id
    assert item1.rating == 3
    assert item1.body == f"Critic {critic1.id}'s review of Book {book1.id} body"
    assert item1.created_at is not None
    assert item1.updated_at is not None

    item2 = await Review.read_by_id(id=data['ids'][1])
    assert item2.title == f"Critic {critic2.id}'s review of Book {book2.id} title"
    assert item2.critic_id == critic2.id
    assert item2.book_id == book2.id
    assert item2.rating == 3
    assert item2.body == f"Critic {critic2.id}'s review of Book {book2.id} body"
    assert item2.created_at is not None
    assert item2.updated_at is not None


@pytest.mark.anyio
async def test_create_if_not_exists(client: AsyncClient):
    book = await new_book()
    critic = await new_critic()

    # Create items
    response = await client.put(
        route_base,
        json={
                'title': f"Critic {critic.id}'s review of Book {book.id} title",
                'critic_id': critic.id,
                'book_id': book.id,
                'rating': 4,
                'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['id'] > 0
    assert data['title'] == f"Critic {critic.id}'s review of Book {book.id} title"
    assert data['critic_id'] == critic.id
    assert data['book_id'] == book.id
    assert data['rating'] == 4
    assert data['body'] == f"Critic {critic.id}'s review of Book {book.id} body"
    assert data['created_at'] is not None
    assert data['updated_at'] is not None


@pytest.mark.anyio
async def test_update_if_exists(client: AsyncClient):
    item = await new_item()

    # Update item
    response = await client.put(
        route_base,
        json={
                'title': f"Critic {item.critic_id}'s review of Book {item.book_id} title UPDATE",
                'critic_id': item.critic_id,
                'book_id': item.book_id,
                'rating': 5,
                'body': f"Critic {item.critic_id}'s review of Book {item.book_id} body UPDATE",
        }
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == get_model_member_count
    assert data['id'] == item.id
    assert data['title'] == f"Critic {item.critic_id}'s review of Book {item.book_id} title UPDATE"
    assert data['critic_id'] == item.critic_id
    assert data['book_id'] == item.book_id
    assert data['rating'] == 5
    assert data['body'] == f"Critic {item.critic_id}'s review of Book {item.book_id} body UPDATE"
    assert data['created_at'] is not None
    assert data['updated_at'] is not None


@pytest.mark.anyio
async def test_upsert_bulk(client: AsyncClient):
    book1 = await new_book()
    critic1 = await new_critic()
    book2 = await new_book()
    critic2 = await new_critic()

    # Get count before
    item_count = await ModelClass.get_count(schema_name=client.login.tenant_schema_name)

    # Create items
    response = await client.put(
        f"{route_base}/bulk",
        json=[
                # With all fields
                {
                    'title': f"Critic {critic1.id}'s review of Book {book1.id} title",
                    'critic_id': critic1.id,
                    'book_id': book1.id,
                    'rating': 3,
                    'body': f"Critic {critic1.id}'s review of Book {book1.id} body",
                },
                # With only mandatory fields
                {
                    'title': f"Critic {critic2.id}'s review of Book {book2.id} title",
                    'critic_id': critic2.id,
                    'book_id': book2.id,
                    'rating': 3,
                    'body': f"Critic {critic2.id}'s review of Book {book2.id} body",
                }
        ]
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == bulk_response_member_count
    assert data['count'] == 2
    assert data['message'] == f'Created or updated multiple Reviews in the database.'
    assert len(data['ids']) == 2
    assert (await ModelClass.get_count(schema_name=client.login.tenant_schema_name)) == (item_count + 2)

    # Assert values
    item1 = await ModelClass.read_by_id(id=data['ids'][0])
    assert item1.id == item1.id
    assert item1.title == f"Critic {item1.critic_id}'s review of Book {item1.book_id} title"
    assert item1.critic_id == item1.critic_id
    assert item1.book_id == item1.book_id
    assert item1.rating == 3
    assert item1.body == f"Critic {item1.critic_id}'s review of Book {item1.book_id} body"
    assert item1.created_at is not None
    assert item1.updated_at is not None

    item2 = await ModelClass.read_by_id(id=data['ids'][1])
    assert item2.id == item2.id
    assert item2.title == f"Critic {item2.critic_id}'s review of Book {item2.book_id} title"
    assert item2.critic_id == item2.critic_id
    assert item2.book_id == item2.book_id
    assert item2.rating == 3
    assert item2.body == f"Critic {item2.critic_id}'s review of Book {item2.book_id} body"
    assert item2.created_at is not None
    assert item2.updated_at is not None

    item_count_pre_update = await ModelClass.get_count(schema_name=client.login.tenant_schema_name)

    # Update items
    response = await client.put(
        f"{route_base}/bulk",
        json=[
                # With all fields
                {
                    'title': f"Critic {item1.critic_id}'s review of Book {item1.book_id} title UPDATE",
                    'critic_id': item1.critic_id,
                    'book_id': item1.book_id,
                    'rating': 1,
                    'body': f"Critic {item1.critic_id}'s review of Book {item1.book_id} body UPDATE",
                },
                # With only mandatory fields
                {
                    'title': f"Critic {item2.critic_id}'s review of Book {item2.book_id} title UPDATE",
                    'critic_id': item2.critic_id,
                    'book_id': item2.book_id,
                    'rating': 1,
                    'body': f"Critic {item2.critic_id}'s review of Book {item2.book_id} body UPDATE",
                }
        ]
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert len(data) == bulk_response_member_count
    assert data['count'] == 2
    assert data['message'] == f'Created or updated multiple Reviews in the database.'
    assert len(data['ids']) == 2
    assert (await ModelClass.get_count(schema_name=client.login.tenant_schema_name)) == item_count_pre_update

    # Assert values
    item1db = await ModelClass.read_by_id(id=data['ids'][0])
    assert item1db.id == item1.id
    assert item1db.title == f"Critic {item1.critic_id}'s review of Book {item1.book_id} title UPDATE"
    assert item1db.critic_id == item1.critic_id
    assert item1db.book_id == item1.book_id
    assert item1db.rating == 1
    assert item1db.body == f"Critic {item1.critic_id}'s review of Book {item1.book_id} body UPDATE"
    assert item1db.created_at is not None
    assert item1db.updated_at is not None

    item2db = await ModelClass.read_by_id(id=data['ids'][1])
    assert item2db.id == item2.id
    assert item2db.title == f"Critic {item2.critic_id}'s review of Book {item2.book_id} title UPDATE"
    assert item2db.critic_id == item2.critic_id
    assert item2db.book_id == item2.book_id
    assert item2db.rating == 1
    assert item2db.body == f"Critic {item2.critic_id}'s review of Book {item2.book_id} body UPDATE"
    assert item2db.created_at is not None
    assert item2db.updated_at is not None


@pytest.mark.anyio
async def test_read_all_full(client: AsyncClient):
    # Create two items
    item_second_last = await new_item()
    item_last = await new_item()

    # Get from route
    response = await client.get(
        route_base
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    all_items_route = response.json()
    all_items_route.sort(key=lambda x: x['id'])

    # Get directly from db
    all_items_db = await Review.read_all()
    all_items_db.sort(key=lambda x: x.id)

    # assert all_items_route == all_items_db
    for i in range(len(all_items_route)):
        assert all_items_route[i]['id'] == all_items_db[i].id
        assert all_items_route[i]['title'] == all_items_db[i].title
        assert all_items_route[i]['critic_id'] == all_items_db[i].critic_id
        assert all_items_route[i]['book_id'] == all_items_db[i].book_id
        assert all_items_route[i]['rating'] == all_items_db[i].rating
        assert all_items_route[i]['body'] == all_items_db[i].body
        assert all_items_route[i]['created_at'] == all_items_db[i].created_at.isoformat()
        assert all_items_route[i]['updated_at'] == all_items_db[i].updated_at.isoformat()

    # Verify the last two items retrieved from the route are the ones created at the start of the test
    # Get second last item idx in all_items_route
    second_last_idx = len(all_items_route) - 2
    assert all_items_route[second_last_idx]['id'] == item_second_last.id
    assert all_items_route[second_last_idx]['title'] == item_second_last.title
    assert all_items_route[second_last_idx]['critic_id'] == item_second_last.critic_id
    assert all_items_route[second_last_idx]['book_id'] == item_second_last.book_id
    assert all_items_route[second_last_idx]['rating'] == item_second_last.rating
    assert all_items_route[second_last_idx]['body'] == item_second_last.body
    assert all_items_route[second_last_idx]['created_at'] == item_second_last.created_at.isoformat()
    assert all_items_route[second_last_idx]['updated_at'] == item_second_last.updated_at.isoformat()

    last_idx = len(all_items_route) - 1
    assert all_items_route[last_idx]['id'] == item_last.id
    assert all_items_route[last_idx]['title'] == item_last.title
    assert all_items_route[last_idx]['critic_id'] == item_last.critic_id
    assert all_items_route[last_idx]['book_id'] == item_last.book_id
    assert all_items_route[last_idx]['rating'] == item_last.rating
    assert all_items_route[last_idx]['body'] == item_last.body
    assert all_items_route[last_idx]['created_at'] == item_last.created_at.isoformat()
    assert all_items_route[last_idx]['updated_at'] == item_last.updated_at.isoformat()
