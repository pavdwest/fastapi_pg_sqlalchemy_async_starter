from typing import List

from fastapi import APIRouter, status, HTTPException
from inflection import pluralize
from sqlalchemy.exc import IntegrityError

from src.database.exceptions import raise_known
from src.modules.book.models import Book
from src.validators import Bulk
from src.modules.book.validators import (
    BookCreate,
    BookGet,
    BookUpdate,
    BookUpdateWithPayload
)


ModelClass = Book
CreateClass = BookCreate
GetClass = BookGet
UpdateClass = BookUpdate


router = APIRouter(
    tags=[ModelClass.__tablename_friendly__],
    prefix=f"/{ModelClass.__tablename__}",
)


@router.post(
    '',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Create one {ModelClass.__name__} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def create_one(item: CreateClass) -> GetClass:
    try:
        res = await ModelClass(**item.__dict__).save()
        return GetClass.model_validate(res)
    except IntegrityError as e:
        raise_known(e)


@router.patch(
    '/{id}',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Update a specific {ModelClass.__name__} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def update_one(id: int, item: UpdateClass) -> GetClass:
    db_item = await ModelClass.get_by_id(id=id)

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with id={id} not found."
        )

    res = await ModelClass.update_by_id(id=id, data=item)
    return GetClass.model_validate(res)


@router.patch(
    '/',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Update a specific {ModelClass.__name__} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def update_one_by_payload(item: BookUpdateWithPayload) -> GetClass:
    db_item = await ModelClass.get_by_id(id=item.id)

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with id={id} not found."
        )

    res = await ModelClass.update_by_id(id=item.id, data=item)
    return GetClass.model_validate(res)


@router.put(
    '',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Create or update one {ModelClass.__name__} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def create_or_update_one(item: CreateClass) -> GetClass:
    try:
        res = await ModelClass.upsert(data=item)
        return GetClass.model_validate(res)
    except IntegrityError as e:
        raise_known(e)


@router.delete(
    '/{id}',
    response_model=Bulk,
    status_code=status.HTTP_200_OK,
    summary=f"Delete a specific {ModelClass.__name__} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def delete_one(id: int) -> Bulk:
    db_item = await ModelClass.get_by_id(id=id)

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with id={id} not found."
        )

    res = await ModelClass.delete_by_id(id=id)
    return Bulk(
        message=f'Deleted one {ModelClass.__name__} from the database.',
        count=1,
        ids=[id],
    )


@router.get(
    '/{id}',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Get a {ModelClass.__name__} stored in the database by its ID.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_by_id(id: int) -> GetClass:
    item = await ModelClass.get_by_id(id=id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with id={id} not found."
        )

    return GetClass.model_validate(item.__dict__)


@router.delete(
    '',
    response_model=Bulk,
    status_code=status.HTTP_200_OK,
    summary=f"Delete all {pluralize(ModelClass.__name__)} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def delete_all() -> Bulk:
    res =  await ModelClass.delete_all()
    return Bulk(
        message=f'Deleted all {pluralize(ModelClass.__name__)} in the database.',
        count=len(res),
        ids=res
    )


@router.get(
    '',
    response_model=List[GetClass],
    status_code=status.HTTP_200_OK,
    summary=f"Get all {pluralize(ModelClass.__name__)} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_all() -> List[GetClass]:
    return [GetClass.model_validate(item) for item in await Book.fetch_all()]


@router.post(
    '/bulk',
    response_model=Bulk,
    status_code=status.HTTP_200_OK,
    summary=f"Create one {ModelClass.__name__} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def create_many(items: List[CreateClass]) -> Bulk:
    try:
        res = await ModelClass.create_many(data=items)
        return Bulk(
            message=f'Created multiple {pluralize(ModelClass.__name__)} in the database.',
            count=len(res),
            ids=res
        )
    except IntegrityError as e:
        raise_known(e)


@router.put(
    '/bulk',
    response_model=Bulk,
    status_code=status.HTTP_200_OK,
    summary=f"Create or update many {pluralize(ModelClass.__name__)} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def create_or_update_many(items: List[UpdateClass]) -> Bulk:
    try:
        res = await ModelClass.upsert_many(data=items, apply_none_values=False)
        return Bulk(
            message=f'Created or updated multiple {pluralize(ModelClass.__name__)} in the database.',
            count=len(res),
            ids=res
        )
    except IntegrityError as e:
        raise_known(e)
