import os

TEST_DB_SUFFIX = '_test'
DATABASE_NAME: str  = os.environ.get('DATABASE_NAME')
os.environ['DATABASE_NAME'] = f"{DATABASE_NAME}{TEST_DB_SUFFIX}"
