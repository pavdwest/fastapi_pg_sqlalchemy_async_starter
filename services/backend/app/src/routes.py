from typing import Type, List, Dict

from fastapi import APIRouter, status, HTTPException, Query
from inflection import pluralize

from src.logging.service import logger
from src.config import READ_ALL_LIMIT_DEFAULT, READ_ALL_LIMIT_MAX
from src.versions import ApiVersion
from src.database.exceptions import handle_exception
from src.models import AppModel
from src.validators import Bulk
from src.validators import (
    ReadValidator,
    CreateValidator,
    UpdateValidator,
    UpdateWithIdValidator,
)


def generate_route_class(
    ModelClass: Type[AppModel],
    ReadValidatorClass: Type[ReadValidator],
    CreateValidatorClass: Type[CreateValidator],
    UpdateValidatorClass: Type[UpdateValidator],
    UpdateWithIdValidatorClass: Type[UpdateWithIdValidator],
):
    # Basic setup
    klass = type(f"{ModelClass.__name__}Routes", (object,), {})
    router = APIRouter(
        tags=[ModelClass.__tablename_friendly__],
        prefix=f"{ApiVersion.V1}/{ModelClass.__tablename__}",
    )
    klass.router = router
    klass.ModelClass                 = ModelClass
    klass.ReadValidatorClass         = ReadValidatorClass
    klass.CreateValidatorClass       = CreateValidatorClass
    klass.UpdateValidatorClass       = UpdateValidatorClass
    klass.UpdateWithIdValidatorClass = UpdateWithIdValidatorClass


    # Endpoints
    @router.post(
        '',
        response_model=ReadValidatorClass,
        status_code=status.HTTP_200_OK,
        summary=f"Create one {ModelClass.__name__} in the database.",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def create_one(item: CreateValidatorClass) -> ReadValidatorClass:
        try:
            res = await ModelClass(**item.__dict__).save()
            # We use model_construct to ignore validations as this data is coming from the db and already validated
            return ReadValidatorClass.model_construct(**res.to_dict())
        except Exception as e:
            handle_exception(e)


    @router.patch(
        '/{id}',
        response_model=ReadValidatorClass,
        status_code=status.HTTP_200_OK,
        summary=f"Update a specific {ModelClass.__name__} stored in the database.",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def update_one(id: int, item: UpdateValidatorClass) -> ReadValidatorClass:
        db_item = await ModelClass.read_by_id(id=id)

        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object with id={id} not found."
            )

        res = await ModelClass.update_by_id(id=id, item=item)
        return ReadValidatorClass.model_construct(**res.to_dict())


    @router.patch(
        '',
        response_model=ReadValidatorClass,
        status_code=status.HTTP_200_OK,
        summary=f"Update a specific {ModelClass.__name__} stored in the database (`id` included in the payload).",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def update_one_with_id(item: UpdateWithIdValidatorClass) -> ReadValidatorClass:
        db_item = await ModelClass.read_by_id(id=item.id)

        if db_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object with id={id} not found."
            )

        res = await ModelClass.update_by_id(id=item.id, item=item)
        return ReadValidatorClass.model_construct(**res.to_dict())


    @router.put(
        '',
        response_model=ReadValidatorClass,
        status_code=status.HTTP_200_OK,
        summary=f"Create or update one {ModelClass.__name__} in the database.",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def upsert_one(item: CreateValidatorClass) -> ReadValidatorClass:
        try:
            res = await ModelClass.upsert(item=item)
            return ReadValidatorClass.model_construct(**res.to_dict())
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

        await ModelClass.delete_by_id(id=id)
        return Bulk(
            message=f'Deleted one {ModelClass.__name__} from the database.',
            count=1,
            ids=[id],
        )


    @router.get(
        '/{id}',
        response_model=ReadValidatorClass,
        status_code=status.HTTP_200_OK,
        summary=f"Get a {ModelClass.__name__} stored in the database by its ID.",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def read_by_id(id: int) -> ReadValidatorClass:
        item = await ModelClass.read_by_id(id=id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object with id={id} not found."
            )

        return ReadValidatorClass.model_construct(item.to_dict())


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
            # ids=res,
            ids=[-1],
        )


    @router.get(
        '',
        response_model=List[ReadValidatorClass],
        status_code=status.HTTP_200_OK,
        summary=f"Get all {pluralize(ModelClass.__name__)} stored in the database.",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def read_all(
        offset: int = Query(
            default=0,
            ge=0,
        ),
        limit: int = Query(
            default=READ_ALL_LIMIT_DEFAULT,
            ge=1,
            le=READ_ALL_LIMIT_MAX,
        ),
    ) -> List[ReadValidatorClass]:
        limit = min(limit, READ_ALL_LIMIT_MAX)
        return [ReadValidatorClass.model_construct(**item.to_dict()) for item in await ModelClass.read_all(offset=offset, limit=limit)]


    @router.post(
        '/bulk',
        response_model=Bulk,
        status_code=status.HTTP_200_OK,
        summary=f"Create multiple {pluralize(ModelClass.__name__)} in the database.",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def create_many(items: List[CreateValidatorClass]) -> Bulk:
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
    async def upsert_many(items: List[UpdateValidatorClass]) -> Bulk:
        try:
            res = await ModelClass.upsert_many(items=items, apply_none_values=False)
            return Bulk(
                message=f'Created or updated multiple {pluralize(ModelClass.__name__)} in the database.',
                count=len(res),
                ids=res
            )
        except Exception as e:
            handle_exception(e)


    @router.post(
        '/test/seed_data',
        response_model=Dict,
        status_code=status.HTTP_200_OK,
        summary=f"Seed mock {pluralize(ModelClass.__name__)} in the database.",
        description='Endpoint description. Will use the docstring if not provided.',
    )
    async def seed_data(n: int = 100000) -> Dict:
        import time
        s = time.monotonic()
        await ModelClass.seed_multiple(n)
        logger.warning(f"Took: {time.monotonic() - s} seconds")
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
        res = await ModelClass.read_all()  # 10.190340717992513 for 1 mil, Calc: 0.4833592210052302
        # res = await Book.popo_read_all() # 2.038523224997334 for 1 mil, Calc: 68.26654115399288
        logger.warning(f"Fetch: {time.monotonic() - s}")

        # Sum all release years
        s = time.monotonic()
        # ry = sum([item.release_year for item in res])
        ry = sum([ReadValidatorClass.model_validate(item).release_year for item in res])
        # ry = sum([ReadValidatorClass.model_construct(**item.to_dict()).release_year for item in res])

        logger.warning(f"Calc: res={ry} took {time.monotonic() - s}")
        return {
            'message': 'Done'
        }


    # Link functions to class - not sure it's necessary but could be useful
    setattr(klass, 'create_one',         create_one)
    setattr(klass, 'update_one',         update_one)
    setattr(klass, 'update_one_with_id', update_one_with_id)
    setattr(klass, 'upsert_one',         upsert_one)
    setattr(klass, 'delete_one',         delete_one)
    setattr(klass, 'read_by_id',         read_by_id)
    setattr(klass, 'delete_all',         delete_all)
    setattr(klass, 'read_all',           read_all)
    setattr(klass, 'create_many',        create_many)
    setattr(klass, 'upsert_many',        upsert_many)
    setattr(klass, 'seed_data',          seed_data)
    setattr(klass, 'performance_test',   performance_test)

    return klass
