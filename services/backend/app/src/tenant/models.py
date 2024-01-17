import uuid
from functools import lru_cache

from sqlalchemy import Column, String

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


class Tenant(AppModel, IdentifierMixin, SharedModelMixin):
    schema_name = Column(String, default=generate_schema_name)

    async def provision(self):
        if self.schema_name is not None:
            # Create a new schema for the tenant
            DatabaseService.get().create_schema(schema_name=self.schema_name)

            # Create schema tables
            DatabaseService.get().create_schema(source_schema_name=TENANT_SCHEMA_NAME, target_schema_name=self.schema_name)

    @classmethod
    @lru_cache()
    def schema_name_from_identifier(cls, identifier: str) -> str:
        return f"{TENANT_SCHEMA_NAME_PREFIX}{identifier}"

    @classmethod
    @lru_cache()
    def identifier_from_schema_name(cls, schema_name: str) -> str:
        return schema_name.removeprefix(TENANT_SCHEMA_NAME_PREFIX)
