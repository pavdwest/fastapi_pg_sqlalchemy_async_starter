from typing import List

from fastapi import APIRouter, status, HTTPException
from inflection import pluralize
from sqlalchemy.exc import IntegrityError

from src.database.exceptions import raise_known
from src.modules.book.models import Book
from src.modules.book.validators import BookCreate, BookGet, BookDelete


ModelClass = Book
CreateClass = BookCreate
GetClass = BookGet
DeleteClass = BookDelete

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


@router.get(
    "/{id}",
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


@router.get(
    '',
    response_model=List[GetClass],
    status_code=status.HTTP_200_OK,
    summary=f"Get all {pluralize(ModelClass.__name__)} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_all() -> List[GetClass]:
    return [GetClass.model_validate(item) for item in await Book.fetch_all()]


@router.delete(
    '',
    response_model=DeleteClass,
    status_code=status.HTTP_200_OK,
    summary=f"Delete all {pluralize(ModelClass.__name__)} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def delete_all() -> DeleteClass:
    res =  await ModelClass.delete_all()
    return DeleteClass(
        message=f'Deleted all {pluralize(ModelClass.__name__)} in the database.',
        count=res,
    )
