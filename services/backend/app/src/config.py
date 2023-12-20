# Don't move this file into another directory! Relative app folders are determined from it!
import os


# Project
PROJECT_NAME = os.environ.get('PROJECT_NAME')

# Project folders
APP_SRC_FOLDER_ABS = os.path.dirname(os.path.realpath(__file__))

# Database
DATABASE_HOST: str            = os.environ.get('DATABASE_HOST')
DATABASE_PORT: int            = os.environ.get('DATABASE_PORT')
DATABASE_USERNAME: str        = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD: str        = os.environ.get('DATABASE_PASSWORD')
DATABASE_NAME: str            = os.environ.get('DATABASE_NAME')
DATABASE_URL_SYNC: str        = f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
DATABASE_URL_ASYNC: str       = f"postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Routes
READ_ALL_LIMIT_DEFAULT: int   = int(os.environ.get('GET_ITEM_COUNT_DEFAULT', 100))
READ_ALL_LIMIT_MAX: int       = int(os.environ.get('GET_ITEM_COUNT_MAX', 200))

# Redis
REDIS_HOST: str               = os.environ.get('REDIS_HOST')
REDIS_PORT: str               = os.environ.get('REDIS_PORT')
REDIS_PASSWORD: str           = os.environ.get('REDIS_PASSWORD')
