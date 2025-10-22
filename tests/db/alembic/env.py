from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

metadata = MetaData()

audit_entries = Table(
    "audit_entries",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tool_id", String, nullable=False),
    Column("action", String, nullable=False),
    Column("actor", String, nullable=False),
    Column("timestamp", DateTime, nullable=False),
)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
