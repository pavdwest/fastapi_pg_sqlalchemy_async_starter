# Don't move this file into another directory! Relative app folders are determined from it!
import os


# Project
PROJECT_NAME = os.environ.get('PROJECT_NAME')

# Project folders
APP_SRC_FOLDER_ABS = os.path.dirname(os.path.realpath(__file__))

# Shared Database
SHARED_DATABASE_HOST: str      = os.environ.get('SHARED_DATABASE_HOST')
SHARED_DATABASE_PORT: int      = os.environ.get('SHARED_DATABASE_PORT')
SHARED_DATABASE_USERNAME: str  = os.environ.get('SHARED_DATABASE_USERNAME')
SHARED_DATABASE_PASSWORD: str  = os.environ.get('SHARED_DATABASE_PASSWORD')
SHARED_DATABASE_NAME: str      = os.environ.get('SHARED_DATABASE_NAME')
# SHARED_DATABASE_URL_SYNC: str  = f"postgresql+psycopg2://{SHARED_DATABASE_USERNAME}:{SHARED_DATABASE_PASSWORD}@{SHARED_DATABASE_HOST}:{SHARED_DATABASE_PORT}/{SHARED_DATABASE_NAME}"
# SHARED_DATABASE_URL_ASYNC: str = f"postgresql+asyncpg://{SHARED_DATABASE_USERNAME}:{SHARED_DATABASE_PASSWORD}@{SHARED_DATABASE_HOST}:{SHARED_DATABASE_PORT}/{SHARED_DATABASE_NAME}"

# Tenant Databases
TENANT_DATABASE_HOST: str      = os.environ.get('SHARED_DATABASE_HOST')
TENANT_DATABASE_PORT: int      = os.environ.get('SHARED_DATABASE_PORT')
TENANT_DATABASE_USERNAME: str  = os.environ.get('SHARED_DATABASE_USERNAME')
TENANT_DATABASE_PASSWORD: str  = os.environ.get('SHARED_DATABASE_PASSWORD')
# TENANT_DATABASE_URL_ASYNC: str = f"postgresql+asyncpg://{TENANT_DATABASE_USERNAME}:{TENANT_DATABASE_PASSWORD}@{TENANT_DATABASE_HOST}:{TENANT_DATABASE_PORT}/"

# Routes
READ_ALL_LIMIT_DEFAULT: int    = int(os.environ.get('GET_ITEM_COUNT_DEFAULT', 100))
READ_ALL_LIMIT_MAX: int        = int(os.environ.get('GET_ITEM_COUNT_MAX', 200))

# Redis
REDIS_HOST: str                = os.environ.get('REDIS_HOST')
REDIS_PORT: str                = os.environ.get('REDIS_PORT')
