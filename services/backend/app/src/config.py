# Don't move this file into another directory! Relative app folders are determined from it!
import os


# Project
PROJECT_NAME: str             = os.environ.get('PROJECT_NAME')

# Project folders
APP_SRC_FOLDER_ABS: str       = os.path.dirname(os.path.realpath(__file__))

# Maintenance
IN_MAINTENANCE: int           = False

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

# Auth
JWT_SECRET_KEY                = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY        = os.environ['JWT_REFRESH_SECRET_KEY']
ACCESS_TOKEN_EXPIRE_MINUTES   = 30
REFRESH_TOKEN_EXPIRE_MINUTES  = 60 * 24 * 7  # 7 days

# Multi-tenant
SHARED_SCHEMA_NAME: str       = 'shared'
TENANT_SCHEMA_NAME: str       = 'tenant'
