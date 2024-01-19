from src.modules.critic.models import Critic
from src.modules.critic.validators import (
    CriticCreate,
    CriticGet,
    CriticUpdate,
    CriticUpdateWithId
)
from src.routes import generate_route_class


RouteClass = generate_route_class(
    ModelClass                 = Critic,
    CreateValidatorClass       = CriticCreate,
    ReadValidatorClass         = CriticGet,
    UpdateValidatorClass       = CriticUpdate,
    UpdateWithIdValidatorClass = CriticUpdateWithId,
)
router = RouteClass().router
