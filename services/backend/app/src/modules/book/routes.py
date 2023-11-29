from src.modules.book.models import Book
from src.modules.book.validators import (
    BookCreate,
    BookGet,
    BookUpdate,
    BookUpdateWithId
)
from src.routes import generate_route_class


RouteClass = generate_route_class(
    ModelClass                 = Book,
    CreateValidatorClass       = BookCreate,
    ReadValidatorClass         = BookGet,
    UpdateValidatorClass       = BookUpdate,
    UpdateWithIdValidatorClass = BookUpdateWithId,
)
router = RouteClass()
