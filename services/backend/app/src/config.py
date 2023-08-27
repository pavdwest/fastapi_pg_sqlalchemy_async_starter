# Don't move this file into another directory! Relative app folders are determined from it!
import os


# Project
PROJECT_NAME = os.environ.get('PROJECT_NAME')

# Project folders
APP_SRC_FOLDER_ABS = os.path.dirname(os.path.realpath(__file__))

# Redis
REDIS_HOST     = os.environ.get('REDIS')
REDIS_PORT     = os.environ.get('REDIS_PORT')
REDIS_USERNAME = os.environ.get('REDIS_USERNAME')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

# Database
DATABASE_HOST: str      = os.environ.get('DATABASE_HOST')
DATABASE_PORT: int      = os.environ.get('DATABASE_PORT')
DATABASE_USERNAME: str  = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD: str  = os.environ.get('DATABASE_PASSWORD')
DATABASE_NAME: str      = os.environ.get('DATABASE_NAME')
DATABASE_URL_SYNC: str  = f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
DATABASE_URL_ASYNC: str = f"postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
