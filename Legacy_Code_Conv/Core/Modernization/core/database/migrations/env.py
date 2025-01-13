"""
Alembic Environment Configuration
Version: 1.0.0
Last Updated: 2025-01-10
"""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from ...utils.config import get_settings
from ..base import Base

settings = get_settings()

# Alembic Config object
config = context.config

# Interpret the config file for logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

# Database URL
def get_url():
    """Get database URL from settings."""
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations in a transaction."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations asynchronously."""
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
