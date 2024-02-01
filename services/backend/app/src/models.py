from __future__ import annotations
import asyncio
from functools import lru_cache
from typing import Any, Dict, List, Optional, Type, Tuple, Union
from typing_extensions import Self
from datetime import datetime
import uuid

from sqlalchemy import BigInteger, Insert, text, UniqueConstraint
from sqlalchemy import select, delete, update, insert
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy_utils import get_class_by_table
from inflection import titleize, pluralize, underscore, camelize

from src.logging.service import logger
from src.config import SHARED_SCHEMA_NAME, TENANT_SCHEMA_NAME
from src.utils import ToDictMixin
from src.database.service import DatabaseService
from src.validators import AppValidator


@lru_cache()
def get_unique_constraint_name(
    model_name: Any = None,
    *field_names: Any,
) -> str:
    # I know this isn't very SQLike but it will allow programmatically identifying it, e.g. 'uc_Review_CriticId_BookId'
    return f"uc_{model_name}_{'_'.join([camelize(c) for c in field_names])}"


@lru_cache()
def generate_unique_constraint(
    *field_names: Any,
    model_name: Any = None,
    name: str = None,
) -> UniqueConstraint:
    # Given model name = 'Review', and field_names = ['critic_id', 'book_id'], produces 'uc_Review_CriticId_BookId'.
    # Bizarre that we need to use camelize here, but titleize drops the 'id' and produces 'Critic' from 'critic_id'.
    # camelize produces 'CriticId'.
    if name is None:
        name = get_unique_constraint_name(model_name, *field_names)

    return UniqueConstraint(
        *field_names,
        name=name,
    )


class IdMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    @classmethod
    async def read_by_id(
        cls,
        id: int,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> Union[None, Self]:
        async with DatabaseService.async_session(schema_name) as session:
            q = select(cls.get_model_class()).where(cls.get_model_class().id == id)
            res = await session.execute(q)
            return res.scalars().first()


class AuditTimestampsMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class TimestampMixin:
    timestamp: Mapped[datetime] = mapped_column()


class IdentifierMixin:
    identifier: Mapped[str] = mapped_column(unique=True)

    @classmethod
    async def read_by_identifier(
        cls,
        identifier: str,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> Self:
        async with DatabaseService.async_session(schema_name) as session:
            q = select(cls.get_model_class()).where(cls.get_model_class().identifier == identifier)
            res = await session.execute(q)
            return res.scalars().first()


class GUIDMixin:
    guid: Mapped[uuid.uuid4] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)


class NameMixin:
    name: Mapped[Optional[str]] = mapped_column(nullable=True)


class DescriptionMixin:
    name: Mapped[Optional[str]] = mapped_column(nullable=True)


class SharedModelMixin:
    __table_args__ = { 'schema': SHARED_SCHEMA_NAME }


class TenantModelMixin:
    __table_args__ = { 'schema': TENANT_SCHEMA_NAME }


class AppModel(DeclarativeBase, IdMixin, AuditTimestampsMixin, ToDictMixin):
    @declared_attr
    @lru_cache(maxsize=1)
    def __tablename__(cls) -> str:
        """Get name of the table this model is mapped to.
        Essentially, just underscore the class name.
        This can be used in raw queries.

        Returns:
            str: Name of the table this model is mapped to.
        """
        return underscore(cls.__name__)

    @classmethod
    @lru_cache(maxsize=1)
    def get_model_class(cls) -> Type[AppModel]:
        """Gets a reference to the model class we're currently in

        Returns:
            Type[AppModel]: Class reference derived from AppModel
        """
        return get_class_by_table(cls, cls.__table__)

    @declared_attr
    @lru_cache(maxsize=1)
    def __tablename_friendly__(cls):
        """Get a human-readable tablename. Essentially, just pluralize and titleize the __tablename__.

        Returns:
            _type_: _description_
        """
        return pluralize(titleize(cls.__tablename__))

    @classmethod
    @lru_cache(maxsize=1)
    def get_unique_fieldnames(cls) -> List[str]:
        return [
            c.name for c in cls.get_model_class().__table__.columns if c.unique
        ]

    @classmethod
    @lru_cache(maxsize=1)
    def get_unique_constraint_names(cls) -> List[str]:
        return [c.name for c in cls.get_model_class().__table__.constraints if isinstance(c, UniqueConstraint)]

    # TODO: Use reflection instead of hardcoding this
    @classmethod
    @lru_cache(maxsize=1)
    def get_system_fieldnames(cls) -> List[str]:
        """Get a list of fieldnames that are controlled by the system.
        This includes fields such as id, created_at, updated_at, etc.

        Returns:
            List[str]: List of fieldnames controlled by the system.
        """
        return ['id', 'created_at', 'updated_at']

    @classmethod
    @lru_cache(maxsize=1)
    def get_settable_fieldnames(cls) -> List[str]:
        """Get a list of fieldnames that can be set by the user.
        This excludes fields such as id, created_at, updated_at, etc.

        Returns:
            List[str]: List of fieldnames controlled by the user.
        """
        # TODO: use a mixin property
        return [
            c.name for c in cls.get_model_class().__table__.columns if c.name not in cls.get_system_fieldnames()
        ]

    @classmethod
    @lru_cache(maxsize=1)
    def get_field_types(cls, fields: Tuple[str, ...]) -> Dict[str, Any]:
        field_types = {}
        for field in fields:
            field_types[field] = getattr(cls.get_model_class(), field).type.python_type
        return field_types

    @classmethod
    async def init_orm(cls):
        pass
        # async with DatabaseService.async_session(schema_name) as conn:
        #     # logger.warning("Creating tables...")
        #     # await conn.run_sync(cls.metaitem.drop_all)
        #     # await conn.run_sync(cls.metaitem.create_all)
        #     pass

    @classmethod
    async def get_mock_instance(
        cls,
        schema_name: str = SHARED_SCHEMA_NAME,
        idx: int = None,
    ) -> Self:
        if idx is None:
            idx = await cls.get_max_id(schema_name=schema_name) + 1

        payload = {}
        settable_field_types = cls.get_field_types(fields=tuple(cls.get_settable_fieldnames()))

        for f in settable_field_types:
            if settable_field_types[f] == str:
                payload[f] = f"{f} {idx}"
            elif settable_field_types[f] == int:
                payload[f] = idx
            elif settable_field_types[f] == datetime:
                payload[f] = datetime.utcnow()

        return await cls.get_model_class()(**payload)

    @classmethod
    async def get_mock_instances(
        cls,
        count: int = 100,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> List[Self]:
        idx = await cls.get_max_id(schema_name=schema_name) + 1
        tasks = [
            cls.get_mock_instance(
                schema_name=schema_name,
                idx=idx+i
            ) for i in range(count)
        ]
        return await asyncio.gather(*tasks)

    @classmethod
    async def seed_multiple(
        cls,
        count: int = 100,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> List[Self]:
        items = await cls.get_mock_instances(count=count, schema_name=schema_name)
        return await cls.create_many(items, schema_name)

    @classmethod
    async def seed_one(
        cls,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> Self:
        idx = await cls.get_max_id() + 1
        return await cls.get_mock_instance(idx=idx).save(schema_name=schema_name)

    @classmethod
    async def get_max_id(
        cls,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> int:
        async with DatabaseService.async_session(schema_name) as session:
            q = select(func.max(cls.get_model_class().id))
            res = await session.execute(q)
            return res.scalar() or 0

    @classmethod
    async def get_count(
        cls,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> int:
        async with DatabaseService.async_session(schema_name) as session:
            q = select(func.count(cls.get_model_class().id))
            res = await session.execute(q)
            return res.scalar()

    # TODO: Find best way to do List[Self]
    @classmethod
    async def create_one(
        cls,
        item: AppValidator | Dict,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> Self:
        id = None
        async with DatabaseService.async_session(schema_name) as session:
            q = insert(cls.get_model_class()).returning(cls.get_model_class().id)
            res = await session.execute(q, item if isinstance(item, dict) else item.to_dict())
            await session.commit()
            items = res.scalars().all()
            if len(items) > 0:
                id = items[0]

        if id is not None:
            return await cls.read_by_id(id, schema_name=schema_name)
        else:
            return None

    # TODO: Add metadata to the response
    @classmethod
    async def read_all(
        cls,
        schema_name = SHARED_SCHEMA_NAME,
        offset: int = None,
        limit: int = None,
    ) -> List[Self]:
        async with DatabaseService.async_session(schema_name) as session:
            logger.error(f"Reading all {schema_name}...")
            q = select(cls.get_model_class())

            if offset is not None:
                q = q.offset(offset)
            if limit is not None:
                q = q.limit(limit)

            logger.error(text(str(q)))
            res = await session.execute(q)
            all = res.scalars().all()
            # meta = {
            #     "offset": offset,
            #     "limit": limit,
            #     "total": len(all)
            # }
            # return {
            #     'meta': meta,
            #     'data': all,
            # }
            return all

    @classmethod
    async def popo_read_all(cls, schema_name = SHARED_SCHEMA_NAME) -> List[Dict]:
        """Gets all objects from the database as plain old python objects.

        Returns:
            List[Dict]: List of dicts composed of plain old python objects
        """
        async with DatabaseService.async_session(schema_name) as session:
            q = select(cls.get_model_class())
            res = await session.execute(text(str(q)))
            # return [row for row in res]
            return res

    @classmethod
    async def delete_by_id(cls, id: int, schema_name = SHARED_SCHEMA_NAME) -> int:
        async with DatabaseService.async_session(schema_name) as session:
            q = delete(cls.get_model_class()).where(cls.get_model_class().id == id)
            await session.execute(q)
            return id

    @classmethod
    async def delete_all(cls, schema_name = SHARED_SCHEMA_NAME,) -> List[int]:
        async with DatabaseService.async_session(schema_name) as session:
            q = delete(cls.get_model_class()).returning(cls.get_model_class().id)
            res = await session.execute(q)
            await session.commit()
            return res.scalars().all()

    @classmethod
    async def update_by_id(
        cls,
        id: int,
        item: AppValidator,
        schema_name = SHARED_SCHEMA_NAME,
        apply_none_values: bool = False,
    ) -> Self:
        async with DatabaseService.async_session(schema_name) as session:
            q = update(cls.get_model_class())
            await session.execute(
                q,
                [
                    {
                        'id': id,
                        **item.to_dict(keep_none_values=apply_none_values)
                    }
                ]
            )
            await session.commit()
            return await cls.read_by_id(id=id, schema_name=schema_name)

    # TODO: Find best way to do List[Self]
    @classmethod
    async def create_many(
        cls,
        items: List[AppValidator] | List[Self],
        schema_name = SHARED_SCHEMA_NAME,
    ) -> List[int]:
        async with DatabaseService.async_session(schema_name) as session:
            q = insert(cls.get_model_class()).returning(cls.get_model_class().id)
            res = await session.execute(q, [d.to_dict() for d in items])
            await session.commit()
            return res.scalars().all()

    @classmethod
    @lru_cache(maxsize=1)
    def get_on_conflict_fields(cls) -> List[str]:
        """Gets a list of fieldnames that should be used in the ON CONFLICT clause of an upsert query.

        Returns:
            List[str]: List of fieldnames to update during upsert.
        """
        return [f for f in cls.get_settable_fieldnames() if f not in cls.get_unique_fieldnames()]

    @classmethod
    def get_on_conflict_params(cls, q: Insert) -> Dict:
        """Injections for the ON CONFLICT clause of an upsert query.

        Args:
            q (Insert): the working insert statement

        Returns:
            Dict: A dict with the on_conflict params injected
        """
        return { f: q.excluded[f] for f in cls.get_on_conflict_fields() }

    @classmethod
    async def upsert(
        cls,
        item: AppValidator,
        schema_name = SHARED_SCHEMA_NAME,
        apply_none_values: bool = False
    ) -> Self:
        async with DatabaseService.async_session(schema_name) as session:
            q = upsert(cls.get_model_class())

            ucn = cls.get_unique_constraint_names()
            ucf = cls.get_unique_fieldnames()

            # TODO: Ensure this is the desired behaviour
            if len(ucf) > 0:
                q = q.on_conflict_do_update(
                    index_elements=cls.get_unique_fieldnames(),
                    set_=cls.get_on_conflict_params(q=q)
                )
            elif len(ucn) > 0:
                q = q.on_conflict_do_update(
                    constraint=ucn[0],      # TODO: Handle multiple unique constraints?
                    set_=cls.get_on_conflict_params(q=q)
                )

            q = q.returning(cls.get_model_class().id)
            res = await session.execute(q, item.to_dict())
            await session.commit()
            return await cls.read_by_id(id=res.scalar(), schema_name=schema_name)

    @classmethod
    async def upsert_many(
        cls,
        items: List[AppValidator],
        schema_name = SHARED_SCHEMA_NAME,
        apply_none_values: bool = False,
    ) -> List[int]:
        async with DatabaseService.async_session(schema_name) as session:
            q = upsert(cls.get_model_class())

            ucn = cls.get_unique_constraint_names()
            ucf = cls.get_unique_fieldnames()

            # TODO: Ensure this is the desired behaviour. This allows only the following:
            # If there are any fields marked as unique, use those to uniquely identify the record.
            # If there are no fields marked as unique, use the first unique constraint.
            if len(ucf) > 0:
                q = q.on_conflict_do_update(
                    index_elements=cls.get_unique_fieldnames(),
                    set_=cls.get_on_conflict_params(q=q)
                )
            elif len(ucn) > 0:
                q = q.on_conflict_do_update(
                    constraint=ucn[0],      # TODO: Handle multiple unique constraints?
                    set_=cls.get_on_conflict_params(q=q)
                )
            q = q.returning(cls.get_model_class().id)
            res = await session.execute(q, [item.to_dict(keep_none_values=apply_none_values) for item in items])
            await session.commit()
            return res.scalars().all()

    async def save(self, schema_name: str = SHARED_SCHEMA_NAME) -> Self:
        async with DatabaseService.async_session(schema_name) as session:
            session.add(self)
            return self
