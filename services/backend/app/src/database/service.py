from __future__ import annotations
from enum import Enum
import os
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, Session
# from sqlalchemy_utils import database_exists, create_database, drop_database
import sqlalchemy_utils

from src.logging.service import logger
from src import config


class Adapters(str, Enum):
    ASYNC = 'asyncpg'
    SYNC = 'psycopg2'


# TODO: Proper singleton
class DatabaseService:
    def __init__(self) -> None:
        # Sync
        self.SHARED_DATABASE_URL_SYNC = self.__class__.get_db_url(
            database_host=config.SHARED_DATABASE_HOST,
            database_port=config.SHARED_DATABASE_PORT,
            database_username=config.SHARED_DATABASE_USERNAME,
            database_password=config.SHARED_DATABASE_PASSWORD,
            database_name=config.SHARED_DATABASE_NAME,
            adapter=Adapters.SYNC,
        )
        # Shared DB
        self.create_db(self.SHARED_DATABASE_URL_SYNC)

        # Async
        self.SHARED_DATABASE_URL_ASYNC = self.__class__.get_db_url(
            database_host=config.SHARED_DATABASE_HOST,
            database_port=config.SHARED_DATABASE_PORT,
            database_username=config.SHARED_DATABASE_USERNAME,
            database_password=config.SHARED_DATABASE_PASSWORD,
            database_name=config.SHARED_DATABASE_NAME,
            adapter=Adapters.ASYNC,
        )
        self.SHARED_ENGINE = create_async_engine(
            url=self.SHARED_DATABASE_URL_ASYNC,
            echo=True,
        )

    # def get_tenant_engine(self, tenant_id: str) -> AsyncEngine:
    #     return create_async_engine(
    #         url=self.__class__.get_db_url(
    #             database_host=TENANT_DATABASE_HOST,
    #             database_port=TENANT_DATABASE_PORT,
    #             database_username=TENANT_DATABASE_USERNAME,
    #             database_password=TENANT_DATABASE_PASSWORD,
    #             database_name=f"{SHARED_DATABASE_NAME}_{tenant_id}",
    #         ),
    #         echo=True,
    #     )

        # Create engines
    @asynccontextmanager
    async def get_session():
        try:
            async_session = async_session_generator()

            async with async_session() as session:
                yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

    @classmethod
    def get_db_url(
        cls,
        database_host: str,
        database_port: str,
        database_username: str,
        database_password: str,
        database_name: str,
        adapter: str = Adapters.ASYNC,
    ) -> str:
        return f"postgresql+{adapter}://{database_username}:{database_password}@{database_host}:{database_port}/{database_name}"

    @classmethod
    def create_db(cls, url: str) -> bool:
        if not sqlalchemy_utils.database_exists(url):
            logger.warning(f"Creating database: {url}...")
            sqlalchemy_utils.create_database(url)
            # logger.warning('Running migrations as database was just created...')
            # cls.run_migrations()

            # TODO: Add some more detailed error handling if this borks
            if not sqlalchemy_utils.database_exists(url):
                raise Exception('COULD NOT CREATE DATABASE!')
            else:
                logger.warning('Database created.')
        else:
            logger.info(f"Database '{url}' already exists. Nothing to do.")
