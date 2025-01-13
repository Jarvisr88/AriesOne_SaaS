"""
Alembic Environment Module

This module configures the Alembic environment for database migrations.
"""
import asyncio
from logging.config import fileConfig
import os
from typing import List

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import all models to ensure they're known to SQLAlchemy
from ability.models.database.ability_models import *
from cmn.models.database.cmn_models import *
from common.models.database.base import Base
from common.models.database.error_models import *
from common.models.database.file_models import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    """Get database URL from environment."""
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ariesone")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

def include_name(name: str, type_: str, parent_names: List[str]) -> bool:
    """Filter objects included in migrations."""
    if type_ == "table":
        # Include all tables
        return True
    return False

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations in online mode."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=include_name
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    config_section = config.get_section(config.config_ini_section)
    url = get_url()
    config_section["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())
