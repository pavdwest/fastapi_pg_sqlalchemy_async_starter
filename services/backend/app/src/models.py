from __future__ import annotations
from functools import lru_cache
from typing import List
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import select, delete
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy_utils import get_class_by_table
from inflection import titleize, pluralize, underscore

from src.logging.service import logger
from src.database.service import DatabaseService


class IdMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    @classmethod
    async def get_by_id(cls, id: int) -> AppModel:
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
    async def get_by_identifier(cls, identifier: str) -> AppModel:
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
    async def init_orm(cls):
        async with DatabaseService.get().async_engine.begin() as conn:
            logger.warning("Creating tables...")
            # await conn.run_sync(cls.metadata.drop_all)
            # await conn.run_sync(cls.metadata.create_all)

    @classmethod
    async def get_count(cls) -> int:
        async with DatabaseService.get().async_session() as session:
            q = select(func.count(cls.get_model_class().id))
            res = await session.execute(q)
            return res.scalar()

    @classmethod
    async def fetch_all(cls) -> List[AppModel]:
        async with DatabaseService.get().async_session() as session:
            q = select(cls.get_model_class())
            res = await session.execute(q)
            return [r for r in res.scalars()]

    @classmethod
    async def delete_all(cls):
        async with DatabaseService.get().async_session() as session:
            q = delete(cls.get_model_class())
            res = await session.execute(q)
            await session.commit()
            return res.rowcount

    async def save(self):
        async with DatabaseService.get().async_session() as session:
            async with session.begin():
                session.add(self)
                return self
