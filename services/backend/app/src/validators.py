from typing import Dict
from pydantic import BaseModel


class AppValidator(BaseModel):
    pass


class DeleteAll(AppValidator):
    message: str
    count: int
