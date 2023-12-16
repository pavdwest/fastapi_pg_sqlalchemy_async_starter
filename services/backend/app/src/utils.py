from typing import Dict, List
from functools import lru_cache

from datetime import datetime

class Singleton(object):
    _instances = {}

    @lru_cache(maxsize=1)
    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]


class ToDictMixin:
    def to_dict(
        self,
        keep_none_values: bool = True,
        remove_keys: List[str] = None,
    ) -> Dict:
        # Early return
        if keep_none_values and remove_keys is None:
            return self.__dict__

        # Remove keys
        d = self.__dict__
        if remove_keys is not None:
            [d.pop(k) for k in remove_keys]

        return { k: v for k, v in d.items() if v is not None or keep_none_values }


some_datetime = datetime(year=2023, month=7, day=16, hour=7, minute=9, second=12, microsecond=666)
some_earlier_datetime = datetime(year=2022, month=4, day=9, hour=1, minute=2, second=12, microsecond=345)
