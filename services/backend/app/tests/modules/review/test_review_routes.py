from fastapi import status
import pytest
from httpx import AsyncClient
from datetime import datetime

from src.versions import ApiVersion
from src.modules.book.models import Book
from src.modules.critic.models import Critic
from src.modules.review.models import Review


ModelClass = Review
route_base = f"{ApiVersion.V1}/{ModelClass.__tablename__}"
get_model_member_count = 8
bulk_response_member_count = 3


# @pytest.fixture()
async def new_book() -> Book:
    next_item_id = await Book.get_count() + 1
    return await Book(
        **{
            'identifier': f"book {next_item_id} identifier",
            'name': f"book {next_item_id} name",
            'author': f"book {next_item_id} author",
            'release_year': 2040 + next_item_id,
        }
    ).save()


# @pytest.fixture()
async def new_critic() -> Critic:
    next_item_id = await Critic.get_count() + 1
    return await Critic(
        **{
            'username': f"critic {next_item_id} username",
            'bio': f"critic {next_item_id} bio",
            'name': f"critic {next_item_id} name",
        }
    ).save()


# @pytest.fixture()
async def new_item() -> Review:
    book = await new_book()
    critic = await new_critic()

    return await Review(
        **{
            'title': f"Critic {critic.id}'s review of Book {book.id} title",
            'critic_id': critic.id,
            'book_id': book.id,
            'rating': 4,
            'body': f"Critic {critic.id}'s review of Book {book.id} body",
        }
    ).save()


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


# @pytest.mark.anyio
# async def test_update_one_with_only_mandatory_fields(client: AsyncClient):
#     item = await Review(
#         **{
#             'username': 'ultimate_worryer1987',
#             'bio': 'I like to read books and write reviews',
#             'name': 'Booker DeDimwitte',
#         }
#     ).save()
#     response = await client.patch(
#         f"{route_base}/{item.id}",
#         json={
#             'username': 'ultimate_worryer1988',
#         }
#     )
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == get_model_member_count
#     assert data['id'] > 0
#     assert data['username'] == 'ultimate_worryer1988'
#     assert data['bio'] == 'I like to read books and write reviews'
#     assert data['name'] == 'Booker DeDimwitte'
#     assert datetime.fromisoformat(data['created_at']) == item.created_at
#     assert datetime.fromisoformat(data['updated_at']) > item.updated_at
#     assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


# @pytest.mark.anyio
# async def test_update_one_with_payload_with_all_fields(client: AsyncClient):
#     item = await Review(
#         **{
#             'username': 'ultimate_worryer1989',
#             'bio': 'I like to read books and write reviews',
#             'name': 'Booker DeDimwitte',
#         }
#     ).save()

#     response = await client.patch(
#         f"{route_base}/{item.id}",
#         json={
#             'id': item.id,
#             'username': 'ultimate_worryer1990',
#             'bio': 'I like to read books and write reviews for a living',
#             'name': 'Booker DeDimwittebrood',
#         }
#     )
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == get_model_member_count
#     assert data['id'] > 0
#     assert data['username'] == 'ultimate_worryer1990'
#     assert data['bio'] == 'I like to read books and write reviews for a living'
#     assert data['name'] == 'Booker DeDimwittebrood'
#     assert datetime.fromisoformat(data['created_at']) == item.created_at
#     assert datetime.fromisoformat(data['updated_at']) > item.updated_at
#     assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


# @pytest.mark.anyio
# async def test_update_one_by_payload_with_only_mandatory_fields(client: AsyncClient):
#     item = await Review(
#         **{
#             'username': 'ultimate_worryer1991',
#             'bio': 'I like to read books and write reviews',
#             'name': 'Booker DeDimwitte',
#         }
#     ).save()
#     response = await client.patch(
#         f"{route_base}/{item.id}",
#         json={
#             'id': item.id,
#             'username': 'ultimate_worryer1992',
#         }
#     )
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == get_model_member_count
#     assert data['id'] > 0
#     assert data['username'] == 'ultimate_worryer1992'
#     assert data['bio'] == 'I like to read books and write reviews'
#     assert data['name'] == 'Booker DeDimwitte'
#     assert datetime.fromisoformat(data['created_at']) == item.created_at
#     assert datetime.fromisoformat(data['updated_at']) > item.updated_at
#     assert datetime.fromisoformat(data['updated_at']) > datetime.fromisoformat(data['created_at'])


# @pytest.mark.anyio
# async def test_delete_one(client: AsyncClient):
#     item = await Review(
#         **{
#             'username': 'ultimate_worryer1993',
#             'bio': 'I like to read books and write reviews',
#             'name': 'Booker DeDimwitte',
#         }
#     ).save()
#     item_count = await Review.get_count()
#     response = await client.delete(
#         f"{route_base}/{item.id}"
#     )
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == bulk_response_member_count
#     assert data['count'] == 1
#     assert data['message'] == f'Deleted one Review from the database.'
#     assert data['ids'] == [item.id]
#     assert (await Review.get_count()) == (item_count - 1)


# @pytest.mark.anyio
# async def test_create_bulk(client: AsyncClient):
#     # Get count before
#     item_count = await Review.get_count()

#     # Create items
#     response = await client.post(
#         f"{route_base}/bulk",
#         json=[
#                 # With all fields
#                 {
#                     'username': 'ultimate_worryer1994',
#                     'bio': 'I like to read books and write reviews',
#                     'name': 'Booker DeDimwitte',
#                 },
#                 # With only mandatory fields
#                 {
#                     'username': 'ultimate_worryer1995',
#                 }
#         ]
#     )

#     # Assert response
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == bulk_response_member_count
#     assert data['count'] == 2
#     assert data['message'] == f'Created multiple Reviews in the database.'
#     assert (await Review.get_count()) == (item_count + 2)

#     # Assert values
#     item1 = await Review.read_by_id(id=data['ids'][0])
#     assert item1.username == 'ultimate_worryer1994'
#     assert item1.bio == 'I like to read books and write reviews'
#     assert item1.name == 'Booker DeDimwitte'
#     assert item1.created_at is not None
#     assert item1.updated_at is not None

#     item2 = await Review.read_by_id(id=data['ids'][1])
#     assert item2.username == 'ultimate_worryer1995'
#     assert item2.bio is None
#     assert item2.name is None
#     assert item2.created_at is not None
#     assert item2.updated_at is not None


# @pytest.mark.anyio
# async def test_create_if_not_exists(client: AsyncClient):
#     username = 'ultimate_worryer1996'
#     db_item = await ModelClass.get_by_username(username)
#     assert db_item is None

#     # Create items
#     response = await client.put(
#         route_base,
#         json={
#                 'username': username,
#                 'bio': 'I like to read books and write reviews',
#                 'name': 'Booker DeDimwitte',
#         }
#     )

#     # Assert response
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == get_model_member_count
#     assert data['id'] > 0
#     assert data['username'] == username
#     assert data['bio'] == 'I like to read books and write reviews'
#     assert data['name'] == 'Booker DeDimwitte'
#     assert data['created_at'] is not None
#     assert data['updated_at'] is not None


# @pytest.mark.anyio
# async def test_update_if_exists(client: AsyncClient):
#     # Create item
#     item = await ModelClass(
#         **{
#             'username': 'ultimate_worryer1997',
#             'bio': 'I like to read books and write reviews',
#             'name': 'Booker DeDimwitte',
#         }
#     ).save()

#     # Update item
#     response = await client.put(
#         route_base,
#         json={
#                 'username': 'ultimate_worryer1997',
#                 'bio': 'I like to read books and write reviews for a living dead',
#                 'name': 'Booker DeDimwittebroodmes',
#         }
#     )

#     # Assert response
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == get_model_member_count
#     assert data['id'] == item.id
#     assert data['username'] == 'ultimate_worryer1997'
#     assert data['bio'] == 'I like to read books and write reviews for a living dead'
#     assert data['name'] == 'Booker DeDimwittebroodmes'
#     assert data['created_at'] is not None
#     assert data['updated_at'] is not None


# @pytest.mark.anyio
# async def test_upsert_bulk(client: AsyncClient):
#     # Get count before
#     item_count = await ModelClass.get_count()

#     # Create items
#     response = await client.put(
#         f"{route_base}/bulk",
#         json=[
#                 # With all fields
#                 {
#                     'username': 'ultimate_worryer1998',
#                     'bio': 'I like to read books and write reviews',
#                     'name': 'Booker DeDimwitte',
#                 },
#                 # With only mandatory fields
#                 {
#                     'username': 'ultimate_worryer1999',
#                 }
#         ]
#     )

#     # Assert response
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == bulk_response_member_count
#     assert data['count'] == 2
#     assert data['message'] == f'Created or updated multiple Reviews in the database.'
#     assert len(data['ids']) == 2
#     assert (await ModelClass.get_count()) == (item_count + 2)

#     # Assert values
#     item1 = await ModelClass.read_by_id(id=data['ids'][0])
#     assert item1.username == 'ultimate_worryer1998'
#     assert item1.bio == 'I like to read books and write reviews'
#     assert item1.name == 'Booker DeDimwitte'
#     assert item1.created_at is not None
#     assert item1.updated_at is not None

#     item2 = await ModelClass.read_by_id(id=data['ids'][1])
#     assert item2.username == 'ultimate_worryer1999'
#     assert item2.bio is None
#     assert item2.name is None
#     assert item2.created_at is not None
#     assert item2.updated_at is not None

#     item_count_pre_update = await ModelClass.get_count()

#     # Update items
#     response = await client.put(
#         f"{route_base}/bulk",
#         json=[
#                 # With all fields
#                 {
#                     'username': 'ultimate_worryer1998',
#                     'bio': 'I like to read books and write reviews in sql',
#                     'name': 'Booker DeDimwitteveel',
#                 },
#                 # With only mandatory fields
#                 {
#                     'username': 'ultimate_worryer1999',
#                 }
#         ]
#     )

#     # Assert response
#     assert response.status_code == status.HTTP_200_OK, response.text
#     data = response.json()
#     assert len(data) == bulk_response_member_count
#     assert data['count'] == 2
#     assert data['message'] == f'Created or updated multiple Reviews in the database.'
#     assert len(data['ids']) == 2
#     assert (await ModelClass.get_count()) == item_count_pre_update

#     # Assert values
#     item3 = await ModelClass.read_by_id(id=data['ids'][0])
#     assert item3.id == item1.id
#     assert item3.username == 'ultimate_worryer1998'
#     assert item3.bio == 'I like to read books and write reviews in sql'
#     assert item3.name == 'Booker DeDimwitteveel'
#     assert item3.created_at is not None
#     assert item3.updated_at is not None

#     item4 = await ModelClass.read_by_id(id=data['ids'][1])
#     assert item4.id == item2.id
#     assert item4.username == 'ultimate_worryer1999'
#     assert item4.bio is None
#     assert item4.name is None
#     assert item4.created_at is not None
#     assert item4.updated_at is not None


# @pytest.mark.anyio
# async def test_read_all_full(client: AsyncClient):
#     # Create two items
#     item_second_last = await Review(
#         **{
#             'username': 'ultimate_worryer2003',
#             'bio': 'I like to read books and write wrongs',
#             'name': 'DeBooker DeDimwitte',
#         }
#     ).save()

#     item_last = await Review(
#         **{
#             'username': 'ultimate_worryer2004',
#             'bio': 'I like to write books and read wrongs',
#             'name': 'DeBooker DeDimwittelemetry',
#         }
#     ).save()

#     # Get from route
#     response = await client.get(
#         route_base
#     )
#     assert response.status_code == status.HTTP_200_OK, response.text
#     all_items_route = response.json()
#     all_items_route.sort(key=lambda x: x['id'])

#     # Get directly from db
#     all_items_db = await Review.read_all()
#     all_items_db.sort(key=lambda x: x.id)

#     # assert all_items_route == all_items_db
#     for i in range(len(all_items_route)):
#         assert all_items_route[i]['id'] == all_items_db[i].id
#         assert all_items_route[i]['username'] == all_items_db[i].username
#         assert all_items_route[i]['bio'] == all_items_db[i].bio
#         assert all_items_route[i]['name'] == all_items_db[i].name
#         assert all_items_route[i]['created_at'] == all_items_db[i].created_at.isoformat()
#         assert all_items_route[i]['updated_at'] == all_items_db[i].updated_at.isoformat()

#     # Verify the last two items retrieved from the route are the ones created at the start of the test
#     # Get second last item idx in all_items_route
#     second_last_idx = len(all_items_route) - 2
#     assert all_items_route[second_last_idx]['id'] == item_second_last.id
#     assert all_items_route[second_last_idx]['username'] == item_second_last.username
#     assert all_items_route[second_last_idx]['bio'] == item_second_last.bio
#     assert all_items_route[second_last_idx]['name'] == item_second_last.name
#     assert all_items_route[second_last_idx]['created_at'] == item_second_last.created_at.isoformat()
#     assert all_items_route[second_last_idx]['updated_at'] == item_second_last.updated_at.isoformat()

#     last_idx = len(all_items_route) - 1
#     assert all_items_route[last_idx]['id'] == item_last.id
#     assert all_items_route[last_idx]['username'] == item_last.username
#     assert all_items_route[last_idx]['bio'] == item_last.bio
#     assert all_items_route[last_idx]['name'] == item_last.name
#     assert all_items_route[last_idx]['created_at'] == item_last.created_at.isoformat()
#     assert all_items_route[last_idx]['updated_at'] == item_last.updated_at.isoformat()
