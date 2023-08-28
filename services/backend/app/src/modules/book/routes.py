from typing import List

from fastapi import APIRouter, status, HTTPException
from inflection import pluralize
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError

from src.modules.book.models import Book
from src.modules.book.validators import BookCreate, BookGet


ModelClass = Book
CreateClass = BookCreate
GetClass = BookGet

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
    res = await Book(**dict(item)).create()
    return GetClass.model_validate(res)


@router.get(
    "/{id}",
    response_model=List[GetClass],
    status_code=status.HTTP_200_OK,
    summary=f"Get a {ModelClass.__name__} stored in the database by its ID.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_by_id(id: int) -> List[GetClass]:
    item = await Book.get(id=id)
    return GetClass.model_validate(item)


@router.get(
    '',
    response_model=List[GetClass],
    status_code=status.HTTP_200_OK,
    summary=f"Get all {pluralize(ModelClass.__name__)} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_all() -> List[GetClass]:
    items = await Book.fetch_all()
    return [GetClass.model_validate(item) for item in items]
