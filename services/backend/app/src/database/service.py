from __future__ import annotations
import os
from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from src.logging.service import logger
from src.config import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_URL_SYNC,
    DATABASE_URL_ASYNC,
)


# TODO: Proper singleton
class DatabaseService:
    _instance = None

    @classmethod
    @lru_cache(maxsize=1)
    def get(cls) -> DatabaseService:
        if cls._instance is None:
            cls._instance = DatabaseService()
        return cls._instance

    def __init__(self) -> None:
        __class__.create_db()
        self.async_engine: AsyncEngine = create_async_engine(
            DATABASE_URL_ASYNC,
            future=True,
            echo=True,
            pool_size=50,
        )

        self.async_session: AsyncSession = sessionmaker(
            self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    @classmethod
    def create_db(cls):
        if not database_exists(url=DATABASE_URL_SYNC):
            logger.warning(f"Creating database: {DATABASE_NAME}...")
            create_database(url=DATABASE_URL_SYNC)
            cls.run_migrations()

            # TODO: Add some more detailed error handling if this borks
            if not database_exists(url=DATABASE_URL_SYNC):
                raise Exception(f"COULD NOT CREATE DATABASE!")
            else:
                logger.warning('Database created.')
        else:
            logger.info(f"Database '{DATABASE_HOST}/{DATABASE_NAME}' already exists. Nothing to do.")

    @classmethod
    def run_migrations(cls):
        os.system('alembic upgrade head')

    @classmethod
    def drop_db(cls):
        if database_exists(url=DATABASE_URL_SYNC):
            logger.warning(f"Dropping database: {DATABASE_NAME}...")
            drop_database(url=DATABASE_URL_SYNC)

    async def shutdown(self):
        if self.async_engine is not None:
            await self.async_engine.dispose()
