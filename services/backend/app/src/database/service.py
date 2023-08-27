from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from src.logging.service import logger
from src.config import DATABASE_HOST, DATABASE_NAME, DATABASE_URL_SYNC, DATABASE_URL_ASYNC


class DatabaseService:
    def __init__(self) -> None:
        self.__class__.init_db()
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
    def create_db_if_not_exists(cls):
        if not database_exists(url=DATABASE_URL_SYNC):
            logger.warning(f"Creating database: {DATABASE_NAME}...")
            create_database(url=DATABASE_URL_SYNC)

            # TODO: Add some more detailed error handling if this borks
            if not database_exists(url=DATABASE_URL_SYNC):
                raise Exception(f"COULD NOT CREATE DATABASE!")
            else:
                logger.warning("Database created.")
        else:
            logger.info(f"Database '{DATABASE_HOST}/{DATABASE_NAME}' already exists. Nothing to do.")

    @classmethod
    def init_db(cls):
        cls.create_db_if_not_exists()

    async def shutdown(self):
        if self.async_engine is not None:
            await self.async_engine.dispose()


db: DatabaseService = DatabaseService()
