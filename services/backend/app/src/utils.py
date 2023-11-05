from functools import lru_cache

from datetime import datetime

class Singleton(object):
    _instances = {}

    @lru_cache(maxsize=1)
    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]


some_datetime = datetime(year=2023, month=7, day=16, hour=7, minute=9, second=12, microsecond=666)
some_earlier_datetime = datetime(year=2022, month=4, day=9, hour=1, minute=2, second=12, microsecond=345)
