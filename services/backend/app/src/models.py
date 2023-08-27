from __future__ import annotations
from functools import lru_cache
from typing import List
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.future import select
from inflection import titleize, pluralize, underscore
from sqlalchemy_utils import get_class_by_table
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr

from src.logging.service import logger
from src.database.service import db


class IdMixin:
    id =  Column(Integer, primary_key=True)


class TimestampsMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IdentifierMixin:
    identifier =  Column(String, primary_key=True)


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
        async with db.async_engine.begin() as conn:
            logger.warning('Creating tables...')
            # await conn.run_sync(cls.metadata.drop_all)
            # await conn.run_sync(cls.metadata.create_all)

    async def create(self):
        async with db.async_session() as session:
            async with session.begin():
                session.add(self)
                return self

    @classmethod
    async def fetch_all(cls) -> List[AppModel]:
        async with db.async_session() as session:
            q = select(cls.get_model_class())
            res = await session.execute(q)
            return [r for r in res.scalars()]
