from __future__ import annotations
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import AsyncIterator

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import (
    create_engine,
    text,
)
from sqlalchemy.schema import CreateSchema

from src.logging.service import logger
from src.config import (
    APP_SRC_FOLDER_ABS,
    IN_MAINTENANCE,
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_URL_SYNC,
    DATABASE_URL_ASYNC,
    SHARED_SCHEMA_NAME,
    TENANT_SCHEMA_NAME,
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
            DATABASE_URL_ASYNC,
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
    def get_schema_context(cls, schema_name: str = SHARED_SCHEMA_NAME) -> None:
        options = {}
        if schema_name == SHARED_SCHEMA_NAME:
            options['schema_translate_map'] = { 'tenant': None }
        else:
            options['schema_translate_map'] = { 'tenant': schema_name, 'shared': None }
        return options

    @classmethod
    @asynccontextmanager
    async def async_session(cls, schema_name: str = SHARED_SCHEMA_NAME) -> AsyncIterator[AsyncSession]:
        """Async Context Manager to create a session with a specific schema context that auto commits.
        Will lazy init db service if not already done.

        Args:
            schema_name (str): Database Schema Name for use with e.g. 'SELECT * FROM {schema_name}.some_table'

        Returns:
            AsyncSession: Async Session with the schema context set.

        Yields:
            Iterator[AsyncSession]: Async Session with the schema context set.
        """
        if IN_MAINTENANCE:
            logger.error("Request received during maintenance window.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service is currently under maintenance."
            )

        # Handle tenant switch
        session = cls.get()._async_session_maker()
        await session.connection(execution_options=cls.get_schema_context(schema_name))

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
        if not database_exists(url=DATABASE_URL_SYNC):
            logger.warning(f"Creating database: {DATABASE_NAME}...")
            create_database(url=DATABASE_URL_SYNC)
            logger.warning('Creating default schemas...')
            cls.create_schema(SHARED_SCHEMA_NAME)
            cls.create_schema(TENANT_SCHEMA_NAME)
            logger.warning('Default schemas created.')
            logger.warning('Creating functions...')
            cls.run_script_file(f"{APP_SRC_FOLDER_ABS}/database/scripts/create_function_clone_schema.sql")
            logger.warning('Functions created.')
            logger.warning('Running migrations as database was just created...')
            cls.run_migrations()

            # TODO: Add some more detailed error handling if this borks
            if not database_exists(url=DATABASE_URL_SYNC):
                raise Exception('COULD NOT CREATE DATABASE!')
            else:
                logger.warning('Database created.')
        else:
            logger.info(f"Database '{DATABASE_HOST}/{DATABASE_NAME}' already exists. Nothing to do.")

    @classmethod
    def create_schema(cls, schema_name: str) -> None:
        """
        Idempotent creation of a new blank schema with the provided name,
        which can then be accessed as e.g.

        ```
        select * from schema_name.some_table
        ```

        Args:
            schema_name (str): Schema name
        """
        sync_engine = create_engine(DATABASE_URL_SYNC)
        with sync_engine.begin() as conn:
            if not conn.dialect.has_schema(conn, schema_name):
                logger.warning(f"Creating schema: '{schema_name}'...")
                conn.execute(CreateSchema(schema_name))
                if not conn.dialect.has_schema(conn, schema_name):
                    logger.error(f"Could not create schema: '{schema_name}'.")
            else:
                logger.info(f"Schema '{schema_name}' already exists.")
        sync_engine.dispose()

    @classmethod
    def run_script_file(cls, path: str) -> None:
        """
        Runs a SQL script file against the database.

        Args:
            path (str): Path to the SQL script file.
        """
        sync_engine = create_engine(DATABASE_URL_SYNC)
        with sync_engine.begin() as conn:
            sql = open(path, 'r').read()
            conn.execute(text(sql))
        sync_engine.dispose()

    @classmethod
    def clone_db_schema(cls, source_schema_name: str, target_schema_name: str) -> None:
        """
        Clones the table definitions from one schema to another.
        If a table already exists in the target_schema, it will skip it.
        Does not clone any data. Idempotent.

        Args:
            source_schema_name (str): Schema to clone
            target_schema_name (str): Schema to clone into. Must exist already.
        """
        sync_engine = create_engine(DATABASE_URL_SYNC)
        with sync_engine.begin() as conn:
            logger.warning(f"Cloning schema '{source_schema_name}' to '{target_schema_name}...")
            sql = f"select public.clone_schema('{source_schema_name}', '{target_schema_name}');"
            clone_res = conn.execute(text(sql))
        logger.warning("Schema cloned.")
        sync_engine.dispose()

    # TODO: Do properly online with alembic
    @classmethod
    def run_migrations(cls):
        os.system('alembic upgrade head')

    @classmethod
    def drop_db(cls, db_name_suffix_check: str) -> bool:
        """Drops the active database - CAUTION!

        Args:
            db_name_check (str):

            Will only drop active db if suffix is this.
            E.g. if active db name is 'my_db_test', will drop active db if db_name_check = 'test'.
            Will not drop if db_name_check = 'db_tests'.

        Returns:
            bool: False if the name check fails and db was not dopped. True otherwise.
        """
        if database_exists(url=DATABASE_URL_SYNC):
            got = DATABASE_URL_SYNC[-len(db_name_suffix_check):]
            if got != db_name_suffix_check:
                logger.error(f"Failed name check! Looking for '{db_name_suffix_check}', got '{got}'. Aborting.")
                return False
            else:
                logger.warning(f"Dropping database: {DATABASE_NAME}...")
                drop_database(url=DATABASE_URL_SYNC)
                return True
        return True

    @classmethod
    async def shutdown(cls):
        if cls._instance is not None:
            if cls._instance._async_session_maker is not None:
                await cls._instance._async_session_maker.close_all()
            if cls._instance._async_engine is not None:
                await cls._instance._async_engine.dispose()
