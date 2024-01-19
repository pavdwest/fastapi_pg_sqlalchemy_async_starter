import uuid
from functools import lru_cache
from typing import Type, List, Union
from types import MethodType

from sqlalchemy import Column, String
from sqlalchemy.orm import reconstructor

from src.logging.service import logger
from src.config import TENANT_SCHEMA_NAME
from src.database.service import DatabaseService
from src.models import AppModel, IdentifierMixin, SharedModelMixin


TENANT_SCHEMA_NAME_PREFIX = 'tenant_'


def generate_schema_name() -> str:
    """
    Generates a string of the form 'tenant_889a0da2_e5c7_461d_b1b2_b6f6828eea34'

    Returns:
        str: the result
    """
    return f"{TENANT_SCHEMA_NAME_PREFIX}{str(uuid.uuid4()).replace('-','_')}"


class CRUD:
    def test_func(self):
        print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZ')


class Tenant(AppModel, IdentifierMixin, SharedModelMixin):
    schema_name = Column(String, default=generate_schema_name)

    # # TODO: Is necessary?
    # @reconstructor
    # def init_on_load(self):
    #     self._CRUD = None

    async def provision(self):
        """Creates the required database schema for this tenant. Idempotent.
        """
        if self.schema_name is None:
            logger.error(f"Tenant {self.identifier} cannot be provisioned: No schema name specified!")
        else:
            # Create a new schema for the tenant
            DatabaseService.get().create_schema(schema_name=self.schema_name)

            # Create schema tables
            DatabaseService.get().clone_db_schema(source_schema_name=TENANT_SCHEMA_NAME, target_schema_name=self.schema_name)

    @classmethod
    @lru_cache()
    def schema_name_from_identifier(cls, identifier: str) -> str:
        return f"{TENANT_SCHEMA_NAME_PREFIX}{identifier}"

    @classmethod
    @lru_cache()
    def identifier_from_schema_name(cls, schema_name: str) -> str:
        return schema_name.removeprefix(TENANT_SCHEMA_NAME_PREFIX)

    # Crud accessor
    def CRUD(self, model_class: Type[AppModel]) -> CRUD:
        from src.logging.service import logger
        self._CRUD = CRUD()
        owner_instance = self

        # # Generate helpers
        # async def read_all(
        #     self,
        #     offset: int = None,
        #     limit: int = None,
        # ) -> List[model_class]:
        #     return await model_class.read_all(
        #         offset=offset,
        #         limit=limit,
        #         schema_name=owner_instance.schema_name,
        #     )
        # self._CRUD.read_all = MethodType(read_all, self._CRUD)


        # async def read_by_id(cls, id: int) -> Union[None, model_class]:
        #     return await model_class.read_by_id(
        #         id=id,
        #         schema_name=owner_instance.schema_name,
        #     )
        # self._CRUD.read_by_id = MethodType(read_by_id, self._CRUD)


        # async def read_by_identifier(cls, identifier: int) -> Union[None, model_class]:
        #     return await model_class.read_by_identifier(
        #         identifier=identifier,
        #         schema_name=owner_instance.schema_name,
        #     )
        # self._CRUD.read_by_identifier = MethodType(read_by_identifier, self._CRUD)

        return self._CRUD
