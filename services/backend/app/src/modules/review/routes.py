from typing import List, Dict

from fastapi import APIRouter, status, HTTPException
from inflection import pluralize

from src.versions import ApiVersion
from src.database.exceptions import raise_known
from src.modules.review.models import Review
from src.validators import Bulk
from src.modules.review.validators import (
    ReviewCreate,
    ReviewGet,
    ReviewUpdate,
    ReviewUpdateWithId
)


ModelClass = Review
CreateClass = ReviewCreate
GetClass = ReviewGet
UpdateClass = ReviewUpdate


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
        raise_known(e)


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
async def update_one_with_id(item: ReviewUpdateWithId) -> GetClass:
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
        raise_known(e)


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
    return [GetClass.model_validate(item) for item in await Review.read_all()]


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
        raise_known(e)


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
        raise_known(e)


@router.post(
    '/test/seed_data',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary=f"Seed mock {pluralize(ModelClass.__name__)} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def seed_data(n: int = 100000) -> Dict:
    import time
    import asyncio

    # Prep test
    await ModelClass.delete_all()
    s = time.monotonic()
    batch_size = 10000
    orms = []
    tasks = []

    for i in range(n):
        orms.append(
            CreateClass(
                name=f"Review {i}",
                author=f"Author {i}",
                identifier=f"ISBN-{i}",
                release_year=2000 + i
            )
        )
        if len(orms) == batch_size or i == n - 1:
            # res = await ModelClass.create_many(items=orms)
            tasks.append(ModelClass.create_many(items=orms))
            orms = []

    await asyncio.gather(*tasks)
    print(time.monotonic() - s)
    return {
        'message': 'Done'
    }


@router.get(
    '/test/retrieve_data',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    summary=f"Retrieve {pluralize(ModelClass.__name__)} from the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def performance_test() -> Dict:
    import time

    # Raw fetch
    s = time.monotonic()
    res = await Review.read_all()  # 10.190340717992513 for 1 mil, Calc: 0.4833592210052302
    # res = await Review.popo_read_all() # 2.038523224997334 for 1 mil, Calc: 68.26654115399288
    print(f"Fetch: {time.monotonic() - s}")

    # Sum all release years
    s = time.monotonic()
    ry = sum([item.release_year for item in res])
    print(f"Calc: res={ry} took {time.monotonic() - s}")
    return {
        'message': 'Done'
    }
