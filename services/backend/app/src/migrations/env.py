import asyncio
from logging.config import fileConfig
from typing import List

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from src.config import DATABASE_URL_ASYNC, SHARED_SCHEMA_NAME, TENANT_SCHEMA_NAME
from src.models import AppModel
from src.helpers.models_includer import *


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL_ASYNC)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = AppModel.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def get_revision(connection: Connection, schema: str):
    alembic_table_exists = connection.execute(text(f"select exists (select from pg_tables where schemaname = '{schema}' and tablename = 'alembic_version')")).mappings().all()[0]['exists']
    revision = None
    if alembic_table_exists:
        revision_res = connection.execute(text(f'select version_num from {schema}.alembic_version')).mappings().all()
        if len(revision_res) > 0:
            revision = revision_res[0]['version_num']
    return revision


def set_revision(connection: Connection, schema: str, revision: str):
    connection.execute(text(f"update {schema}.alembic_version set version_num = '{revision}'"))


def execute_select(connection: Connection, query: str) -> List:
    return [r for r in connection.execute(text(query)).mappings().all()]


def table_exists(connection: Connection, schema: str, table: str) -> bool:
    return execute_select(
        connection=connection,
        query=f"select exists (select from pg_tables where schemaname = '{schema}' and tablename = '{table}')"
    )[0]['exists']


def do_run_migrations(connection: Connection) -> None:
    # TODO: Rethink how to deal with failed migrations
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction() as ctx:
        # Get current version num so we can reset for each tenant
        public_revision_pre = get_revision(connection=connection, schema='public')
        print(f"Current revision is '{public_revision_pre}'.")

        # Shared + Tenant model schema
        print('Running migrations for shared & tenant model schema...')
        context.run_migrations()

        public_revision_post = get_revision(connection=connection, schema='public')
        print(f"{SHARED_SCHEMA_NAME} and {TENANT_SCHEMA_NAME} migrated to revision {public_revision_post}.")

        # Getting tenants
        # TODO: Parallellise Migrations
        if table_exists(connection=connection, schema=SHARED_SCHEMA_NAME, table='tenant'):
            tenants = execute_select(connection=connection, query=f"select * from {SHARED_SCHEMA_NAME}.tenant")
            if len(tenants) > 0:
                set_revision(connection=connection, schema='public', revision=public_revision_pre)
                print('=====================================')
                print(f"Migrating {len(tenants)} tenant schemas...")
                print('=====================================')
                for i, tenant in enumerate(tenants):
                    junk_schema_name = 'junk'
                    tenant_schema_name = tenant['schema_name']
                    print('-------------------------------------')
                    print(f"Running migrations for specific tenant ({i + 1} of {len(tenants)}): '{tenant_schema_name}'")
                    print(f"Resetting revision to '{public_revision_pre}'...")
                    set_revision(connection=connection, schema='public', revision=public_revision_pre)

                    # This is a huge hack:
                    # It looks like you can't map a schema to None so we create a dummy junk schema
                    # to map the SHARED_SCHEMA_NAME into and we just drop it again after.
                    connection.execution_options(
                        schema_translate_map={
                            SHARED_SCHEMA_NAME: junk_schema_name,
                            TENANT_SCHEMA_NAME: tenant_schema_name,
                        }
                    )
                    print('Creating junk schema...')
                    connection.execute(text(f"create schema if not exists '{junk_schema_name}'"))
                    print('Running actual migrations...')
                    context.run_migrations()
                    print('Deleting junk schema...')
                    connection.execute(text(f"drop schema if exists '{junk_schema_name}' cascade"))
                    post_rev = get_revision(connection=connection, schema='public')
                    print(f"Tenant migrated to revision '{post_rev}'.")

        print('=====================================')
        public_revision_post_tenants = get_revision(connection=connection, schema='public')
        print(f"Final revision: '{public_revision_post_tenants}'")
        result = public_revision_post == public_revision_post_tenants
        print(f"Migration success?: {result}")
        print('=====================================')


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
