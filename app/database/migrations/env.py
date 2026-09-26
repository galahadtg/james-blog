"""Alembic environment configuration.

This file tells Alembic:
  1. Where to find our database (from app.core.config)
  2. Which models to inspect for schema changes
  3. How to run migrations (offline/online)

Importing all models here is required for --autogenerate to detect changes.
"""

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to sys.path so Alembic can find our app package
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import our settings and models
from app.core.config import get_settings
from app.database.base import Base

# Import all models so Alembic can detect them for autogenerate
import app.models  # noqa: F401

# Alembic Config object
config = context.config

# Set the database URL from our application settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic to our models' metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL scripts, no DB connection).

    This is useful for reviewing the SQL that will be executed.
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


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
