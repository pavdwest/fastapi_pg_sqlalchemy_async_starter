from typing import List

from fastapi import APIRouter, status, HTTPException
from inflection import pluralize

from src.versions import ApiVersion
from src.database.exceptions import handle_exception
from src.modules.critic.models import Critic
from src.validators import Bulk
from src.modules.critic.validators import (
    CriticCreate,
    CriticGet,
    CriticUpdate,
    CriticUpdateWithId
)


ModelClass = Critic
CreateClass = CriticCreate
GetClass = CriticGet
UpdateClass = CriticUpdate


router = APIRouter(
    tags=[ModelClass.__tablename_friendly__],
    prefix=f"{ApiVersion.V1}/{ModelClass.__tablename__}",
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
    except Exception as e:
        handle_exception(e)


@router.patch(
    '/{id}',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Update a specific {ModelClass.__name__} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def update_one(id: int, item: UpdateClass) -> GetClass:
    db_item = await ModelClass.read_by_id(id=id)

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with id={id} not found."
        )

    res = await ModelClass.update_by_id(id=id, item=item)
    return GetClass.model_validate(res)


@router.patch(
    '',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Update a specific {ModelClass.__name__} stored in the database (`id` included in the payload).",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def update_one_with_id(item: CriticUpdateWithId) -> GetClass:
    db_item = await ModelClass.read_by_id(id=item.id)

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with id={id} not found."
        )

    res = await ModelClass.update_by_id(id=item.id, item=item)
    return GetClass.model_validate(res)


@router.put(
    '',
    response_model=GetClass,
    status_code=status.HTTP_200_OK,
    summary=f"Create or update one {ModelClass.__name__} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def upsert_one(item: CreateClass) -> GetClass:
    try:
        res = await ModelClass.upsert(item=item)
        return GetClass.model_validate(res)
    except Exception as e:
        handle_exception(e)


@router.delete(
    '/{id}',
    response_model=Bulk,
    status_code=status.HTTP_200_OK,
    summary=f"Delete a specific {ModelClass.__name__} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def delete_one(id: int) -> Bulk:
    db_item = await ModelClass.read_by_id(id=id)

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
async def read_by_id(id: int) -> GetClass:
    item = await ModelClass.read_by_id(id=id)

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
async def read_all() -> List[GetClass]:
    return [GetClass.model_validate(item) for item in await Critic.read_all()]


@router.post(
    '/bulk',
    response_model=Bulk,
    status_code=status.HTTP_200_OK,
    summary=f"Create multiple {pluralize(ModelClass.__name__)} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def create_many(items: List[CreateClass]) -> Bulk:
    try:
        res = await ModelClass.create_many(items=items)
        return Bulk(
            message=f'Created multiple {pluralize(ModelClass.__name__)} in the database.',
            count=len(res),
            ids=res
        )
    except Exception as e:
        handle_exception(e)


@router.put(
    '/bulk',
    response_model=Bulk,
    status_code=status.HTTP_200_OK,
    summary=f"Create or update many {pluralize(ModelClass.__name__)} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def upsert_many(items: List[UpdateClass]) -> Bulk:
    try:
        res = await ModelClass.upsert_many(items=items, apply_none_values=False)
        return Bulk(
            message=f'Created or updated multiple {pluralize(ModelClass.__name__)} in the database.',
            count=len(res),
            ids=res
        )
    except Exception as e:
        handle_exception(e)
