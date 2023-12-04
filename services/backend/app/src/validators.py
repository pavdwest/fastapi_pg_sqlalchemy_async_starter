from typing import List

from pydantic import BaseModel

from src.utils import ToDictMixin


class AppValidator(BaseModel, ToDictMixin):
    pass


class ReadValidator(AppValidator):
    pass


class CreateValidator(AppValidator):
    pass


class UpdateValidator(AppValidator):
    pass


class UpdateWithIdValidator(AppValidator):
    pass


class Bulk(AppValidator):
    message: str
    count: int
    ids: List[int]
