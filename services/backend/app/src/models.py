from __future__ import annotations
from functools import lru_cache
from re import L
from typing import Any, Dict, List, Optional, Type
from typing_extensions import Self
from datetime import datetime

from sqlalchemy import BigInteger, Insert, text, UniqueConstraint
from sqlalchemy import select, delete, update, insert
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy_utils import get_class_by_table
from inflection import titleize, pluralize, underscore, camelize

from src.database.service import DatabaseService
from src.validators import AppValidator


@lru_cache()
def generate_unique_constraint(
    *field_names: Any,
    model_name: Any = None,
    name: str = None,
):
    # Given model name = 'Review', and field_names = ['critic_id', 'book_id'], produces 'uc_Review_CriticId_BookId'.
    # Bizarre that we need to use camelize here, but titleize drops the 'id' and produces 'Critic' from 'critic_id'.
    # camelize produces 'CriticId'.
    if name is None:
        name = f"uc_{model_name}_{'_'.join([camelize(c) for c in field_names])}"

    return UniqueConstraint(
        *field_names,
        name=name,
    )


class IdMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    @classmethod
    async def read_by_id(cls, id: int) -> Self:
        async with DatabaseService.async_session() as session:
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
    async def read_by_identifier(cls, identifier: str) -> Self:
        async with DatabaseService.async_session() as session:
            q = select(cls.get_model_class()).where(cls.get_model_class().identifier == identifier)
            res = await session.execute(q)
            return res.scalars().first()


class NameMixin:
    name: Mapped[Optional[str]] = mapped_column(nullable=True)


class DescriptionMixin:
    name: Mapped[Optional[str]] = mapped_column(nullable=True)


class AppModel(DeclarativeBase, IdMixin, AuditTimestampsMixin):
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
    def get_settable_fieldnames(cls) -> List[str]:
        """Get a list of fieldnames that can be set by the user.
        This excludes fields such as id, created_at, updated_at, etc.

        Returns:
            List[str]: List of fieldnames controlled by the user.
        """
        # TODO: use a mixin property
        return [
            c.name for c in cls.get_model_class().__table__.columns if c.name not in ['id', 'created_at', 'updated_at']
        ]

    @classmethod
    async def init_orm(cls):
        # async with DatabaseService.get().async_engine.begin() as conn:
        async with DatabaseService.async_session() as conn:
            # logger.warning("Creating tables...")
            # await conn.run_sync(cls.metaitem.drop_all)
            # await conn.run_sync(cls.metaitem.create_all)
            pass

    @classmethod
    async def get_count(cls) -> int:
        async with DatabaseService.async_session() as session:
            q = select(func.count(cls.get_model_class().id))
            res = await session.execute(q)
            return res.scalar()

    # TODO: Add metadata to the response
    @classmethod
    async def read_all(
        cls,
        offset: int = None,
        limit: int = None,
    ) -> List[Self]:
        async with DatabaseService.async_session() as session:
            # Base query
            q = select(cls.get_model_class()).offset(0).limit(limit)

            # Apply offset and limit
            if offset is not None:
                q = q.offset(offset)

            if limit is not None:
                q = q.limit(limit)

            res = await session.execute(q)
            all = res.scalars().all()
            meta = {
                "offset": offset,
                "limit": limit,
                "total": len(all)
            }
            # return {
            #     'meta': meta,
            #     'data': all,
            # }
            return all

    @classmethod
    async def popo_read_all(cls) -> List[Dict]:
        """Gets all objects from the database as plain old python objects.

        Returns:
            List[Dict]: List of dicts composed of plain old python objects
        """
        async with DatabaseService.async_session() as session:
            q = select(cls.get_model_class())
            res = await session.execute(text(str(q)))
            # return [row for row in res]
            return res

    @classmethod
    async def delete_by_id(cls, id: int) -> int:
        async with DatabaseService.async_session() as session:
            q = delete(cls.get_model_class()).where(cls.get_model_class().id == id)
            res = await session.execute(q)
            # await session.commit()
            return id

    @classmethod
    async def delete_all(cls) -> List[int]:
        async with DatabaseService.async_session() as session:
            q = delete(cls.get_model_class()).returning(cls.get_model_class().id)
            res = await session.execute(q)
            await session.commit()
            return res.scalars().all()

    @classmethod
    async def update_by_id(cls, id: int, item: AppValidator, apply_none_values: bool = False) -> Self:
        async with DatabaseService.async_session() as session:
            q = update(cls.get_model_class())
            res = await session.execute(
                q,
                [
                    {
                        'id': id,
                        **item.to_dict(remove_none_values=not apply_none_values)
                    }
                ]
            )
            await session.commit()
            return await cls.read_by_id(id=id)

    @classmethod
    async def create_many(cls, items: List[AppValidator]) -> List[int]:
        async with DatabaseService.async_session() as session:
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
    async def upsert(cls, item: AppValidator, apply_none_values: bool = False) -> Self:
        async with DatabaseService.async_session() as session:
            q = upsert(cls.get_model_class())
            q = q.on_conflict_do_update(
                index_elements=cls.get_unique_fieldnames(),
                set_=cls.get_on_conflict_params(q=q)
            )
            q = q.returning(cls.get_model_class().id)
            res = await session.execute(q, item.to_dict())
            await session.commit()
            return await cls.read_by_id(id=res.scalar())

    @classmethod
    async def upsert_many(cls, items: List[AppValidator], apply_none_values: bool = False) -> List[int]:
        async with DatabaseService.async_session() as session:
            q = upsert(cls.get_model_class())
            q = q.on_conflict_do_update(
                index_elements=cls.get_unique_fieldnames(),
                set_=cls.get_on_conflict_params(q=q),
            )
            q = q.returning(cls.get_model_class().id)
            res = await session.execute(q, [item.to_dict(remove_none_values=not apply_none_values) for item in items])
            await session.commit()
            return res.scalars().all()

    async def save(self) -> Self:
        async with DatabaseService.async_session() as session:
            session.add(self)
            return self
