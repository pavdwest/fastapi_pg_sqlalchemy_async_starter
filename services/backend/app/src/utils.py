from functools import lru_cache


class Singleton(object):
    _instances = {}

    @lru_cache(maxsize=1)
    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)
        return class_._instances[class_]
