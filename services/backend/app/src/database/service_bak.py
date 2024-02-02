from __future__ import annotations
import os
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from src.logging.service import logger
from src.config import (
    SHARED_DATABASE_HOST,
    SHARED_DATABASE_NAME,
    SHARED_DATABASE_URL_SYNC,
    SHARED_DATABASE_URL_ASYNC,
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
        self._async_engine: AsyncEngine = create_async_engine(
            SHARED_DATABASE_URL_ASYNC,
            future=True,
            echo=True,
            # pool_size=50,
        )

        self._async_session_maker: AsyncSession = sessionmaker(
            self._async_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @classmethod
    @asynccontextmanager
    async def async_session(cls) -> AsyncSession:
        """Async Context Manager to create a session with a specific schema context that auto commits.
        Will lazy init db service if not already done.

        Args:
            schema_name (str): Database Schema Name for use with e.g. 'SELECT * FROM {schema_name}.some_table'

        Returns:
            AsyncSession: Async Session with the schema context set.

        Yields:
            Iterator[AsyncSession]: Async Session with the schema context set.
        """
        session = cls.get()._async_session_maker()
        # session.expire_on_commit = False

        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

    @classmethod
    def create_db(cls):
        if not database_exists(url=SHARED_DATABASE_URL_SYNC):
            logger.warning(f"Creating database: {SHARED_DATABASE_NAME}...")
            create_database(url=SHARED_DATABASE_URL_SYNC)
            logger.warning('Running migrations as database was just created...')
            cls.run_migrations()

            # TODO: Add some more detailed error handling if this borks
            if not database_exists(url=SHARED_DATABASE_URL_SYNC):
                raise Exception('COULD NOT CREATE DATABASE!')
            else:
                logger.warning('Database created.')
        else:
            logger.info(f"Database '{SHARED_DATABASE_HOST}/{SHARED_DATABASE_NAME}' already exists. Nothing to do.")

    # TODO: Do properly online with alembic
    @classmethod
    def run_migrations(cls):
        os.system('alembic upgrade head')

    @classmethod
    def drop_db(cls):
        if database_exists(url=SHARED_DATABASE_URL_SYNC):
            logger.warning(f"Dropping database: {SHARED_DATABASE_NAME}...")
            drop_database(url=SHARED_DATABASE_URL_SYNC)

    @classmethod
    async def shutdown(cls):
        if cls._instance is not None:
            if cls._instance._async_session_maker is not None:
                await cls._instance._async_session_maker.close_all()
            if cls._instance._async_engine is not None:
                await cls._instance._async_engine.dispose()
