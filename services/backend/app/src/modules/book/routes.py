from typing import List

from fastapi import APIRouter, status

from src.modules.book.models import Book
from src.modules.book.validators import BookCreate, BookGet


model_class = Book


router = APIRouter(
    tags=[model_class.__tablename_friendly__],
    prefix=f"/{model_class.__tablename__}",
)


@router.post(
    f"/create_one",
    response_model=BookGet,
    status_code=status.HTTP_200_OK,
    summary=f"Create one {model_class.__name__} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def create_one(item: BookCreate) -> BookGet:
    res = await Book(**dict(item)).create()
    return BookGet.model_validate(res)


@router.get(
    f"/get_all",
    response_model=List[BookGet],
    status_code=status.HTTP_200_OK,
    summary=f"Get all instances of {model_class.__name__} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_all() -> List[BookGet]:
    items = await Book.fetch_all()
    return [BookGet.model_validate(item) for item in items]
