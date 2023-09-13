from __future__ import annotations
from ast import Dict
from functools import lru_cache
from typing import List
from typing_extensions import Self
from datetime import datetime

from sqlalchemy import BigInteger, Insert
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
from inflection import titleize, pluralize, underscore

from src.database.service import DatabaseService
from src.validators import AppValidator


class IdMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    @classmethod
    async def get_by_id(cls, id: int) -> Self:
        async with DatabaseService.get().async_session() as session:
            q = select(cls.get_model_class()).where(cls.get_model_class().id == id)
            res = await session.execute(q)
            return res.scalars().first()


class TimestampsMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class IdentifierMixin:
    identifier: Mapped[str] = mapped_column(unique=True)

    @classmethod
    async def get_by_identifier(cls, identifier: str) -> Self:
        async with DatabaseService.get().async_session() as session:
            q = select(cls.get_model_class()).where(cls.get_model_class().identifier == identifier)
            res = await session.execute(q)
            return res.scalars().first()


class NameMixin:
    name: Mapped[str] = mapped_column()


class DescriptionMixin:
    identifier: Mapped[str] = mapped_column()


class AppModel(DeclarativeBase, IdMixin, TimestampsMixin):
    @declared_attr
    @lru_cache(maxsize=1)
    def __tablename__(cls):
        return underscore(cls.__name__)

    @classmethod
    @lru_cache(maxsize=1)
    def get_model_class(cls):
        return get_class_by_table(cls, cls.__table__)

    @declared_attr
    @lru_cache(maxsize=1)
    def __tablename_friendly__(cls):
        return pluralize(titleize(cls.__tablename__))

    @classmethod
    @lru_cache(maxsize=1)
    def get_unique_fields(cls):
        return [
            c.name for c in cls.get_model_class().__table__.columns if c.unique
        ]

    @classmethod
    @lru_cache(maxsize=1)
    def get_settable_fields(cls):
        return [
            c.name for c in cls.get_model_class().__table__.columns if c.name not in ['id', 'created_at', 'updated_at']
        ]

    @classmethod
    async def init_orm(cls):
        async with DatabaseService.get().async_engine.begin() as conn:
            # logger.warning("Creating tables...")
            # await conn.run_sync(cls.metadata.drop_all)
            # await conn.run_sync(cls.metadata.create_all)
            pass

    @classmethod
    async def get_count(cls) -> int:
        async with DatabaseService.get().async_session() as session:
            q = select(func.count(cls.get_model_class().id))
            res = await session.execute(q)
            return res.scalar()

    @classmethod
    async def fetch_all(cls) -> List[Self]:
        async with DatabaseService.get().async_session() as session:
            q = select(cls.get_model_class())
            res = await session.execute(q)
            return [r for r in res.scalars()]

    @classmethod
    async def delete_by_id(cls, id: int) -> int:
        async with DatabaseService.get().async_session() as session:
            q = delete(cls.get_model_class()).where(cls.get_model_class().id == id)
            res = await session.execute(q)
            await session.commit()
            return id

    @classmethod
    async def delete_all(cls) -> List[int]:
        async with DatabaseService.get().async_session() as session:
            q = delete(cls.get_model_class()).returning(cls.get_model_class().id)
            res = await session.execute(q)
            await session.commit()
            return res.scalars().all()

    @classmethod
    async def update_by_id(cls, id: int, data: AppValidator, apply_none_values: bool = False) -> Self:
        async with DatabaseService.get().async_session() as session:
            async with session.begin():
                q = update(cls.get_model_class())
                res = await session.execute(
                    q,
                    [
                        {
                            'id': id,
                            **data.to_dict(remove_none_values=not apply_none_values)
                        }
                    ]
                )
                await session.commit()
                return await cls.get_by_id(id=id)

    @classmethod
    async def create_many(cls, data: List[AppValidator]) -> List[int]:
        async with DatabaseService.get().async_session() as session:
            async with session.begin():
                q = insert(cls.get_model_class()).returning(cls.get_model_class().id)
                res = await session.execute(q, [d.to_dict() for d in data])
                await session.commit()
                return res.scalars().all()

    @classmethod
    @lru_cache(maxsize=1)
    def get_on_conflict_fields(cls) -> List[str]:
        return [f for f in cls.get_settable_fields() if f not in cls.get_unique_fields()]

    @classmethod
    def get_on_conflict_params(cls, q: Insert) -> Dict:
        return { f: q.excluded[f] for f in cls.get_on_conflict_fields() }

    @classmethod
    async def upsert(cls, data: AppValidator, apply_none_values: bool = False) -> Self:
        async with DatabaseService.get().async_session() as session:
            async with session.begin():
                q = upsert(cls.get_model_class())
                q = q.on_conflict_do_update(
                    index_elements=cls.get_unique_fields(),
                    set_=cls.get_on_conflict_params(q=q)
                )
                q = q.returning(cls.get_model_class().id)
                res = await session.execute(q, data.to_dict())
                await session.commit()
                return await cls.get_by_id(id=res.scalar())

    @classmethod
    async def upsert_many(cls, data: List[AppValidator], apply_none_values: bool = False) -> List[int]:
        async with DatabaseService.get().async_session() as session:
            async with session.begin():
                q = upsert(cls.get_model_class())
                set_ = [item.to_dict(remove_keys=cls.get_unique_fields(), remove_none_values=not apply_none_values) for item in data]
                q = q.on_conflict_do_update(
                    index_elements=cls.get_unique_fields(),
                    set_=cls.get_on_conflict_params(q=q),
                )
                q = q.returning(cls.get_model_class().id)
                res = await session.execute(q, [item.to_dict(remove_none_values=not apply_none_values) for item in data])
                await session.commit()
                return res.scalars().all()

    async def save(self) -> Self:
        async with DatabaseService.get().async_session() as session:
            async with session.begin():
                session.add(self)
                return self
