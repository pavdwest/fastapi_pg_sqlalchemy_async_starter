from typing import Type

from src.models import AppModel


class AppRoute:
    model: Type[AppModel]
    create: Type[AppModel]
    get: Type[AppModel]
    update: Type[AppModel]
    update_with_id: Type[AppModel]
    bulk: Type[AppModel]

    def __init__(self, model: Type[AppModel]):
        self.model = model
        self.create = generate_route_class(name=f'{model.__name__}Create')
        self.get = generate_route_class(name=f'{model.__name__}Get')
        self.update = generate_route_class(name=f'{model.__name__}Update')
        self.update_with_id = generate_route_class(name=f'{model.__name__}UpdateWithId')
        self.bulk = generate_route_class(name=f'{model.__name__}Bulk')

    def get_all(self):
        pass

    def get_by_id(self):
        pass

    def create_one(self):
        pass

    def update_one(self):
        pass

    def update_one_by_id(self):
        pass

    def delete_one(self):
        pass

    def delete_one_by_id(self):
        pass

    def delete_all(self):
        pass


def generate_route_class(name: str):
    klass = type(name, (object,), {})

    def test(self):
        print('test')

    klass.test = test
    return klass
