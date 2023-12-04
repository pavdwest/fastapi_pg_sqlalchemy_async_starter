from src.modules.review.models import Review
from src.modules.review.validators import (
    ReviewCreate,
    ReviewGet,
    ReviewUpdate,
    ReviewUpdateWithId
)
from src.routes import generate_route_class


RouteClass = generate_route_class(
    ModelClass                 = Review,
    CreateValidatorClass       = ReviewCreate,
    ReadValidatorClass         = ReviewGet,
    UpdateValidatorClass       = ReviewUpdate,
    UpdateWithIdValidatorClass = ReviewUpdateWithId,
)
router = RouteClass()
