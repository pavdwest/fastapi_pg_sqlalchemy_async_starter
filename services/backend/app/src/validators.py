from typing import Dict, List
from pydantic import BaseModel


class AppValidator(BaseModel):
    pass


class DeleteBulk(AppValidator):
    message: str
    count: int
    ids: List[int]


class CreateBulk(AppValidator):
    message: str
    count: int
    ids: List[int]
