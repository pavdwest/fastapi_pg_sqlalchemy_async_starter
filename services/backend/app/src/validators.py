from typing import Dict, List
from pydantic import BaseModel


class AppValidator(BaseModel):
    def to_dict(
        self,
        remove_none_values: bool = False,
        remove_keys: List[str] = None,
    ) -> Dict:
        d = self.__dict__
        if remove_keys is not None:
            d = { k: v for k, v in d.items() if k not in remove_keys }

        return { k: v for k, v in d.items() if v is not None or not remove_none_values }


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
