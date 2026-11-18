import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from app.db.base import Base
import app.models


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _migration_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        database_url = config.get_main_option("sqlalchemy.url")
    if not database_url or not database_url.strip():
        raise RuntimeError(
            "DATABASE_URL or an explicit sqlalchemy.url is required "
            "for migrations"
        )

    try:
        url = make_url(database_url)
    except Exception as exc:
        raise RuntimeError("Invalid migration database URL") from exc

    if (
        url.drivername.lower() in {"driver", "dialect", "dialect+driver"}
        or (url.database or "").lower()
        in {"dbname", "database", "your_database"}
        or any(marker in database_url.lower() for marker in ("<", ">", "{", "}"))
    ):
        raise RuntimeError(
            "A template URL cannot be used as the migration database"
        )

    if url.drivername.startswith("sqlite"):
        if not url.database:
            raise RuntimeError(
                "An explicit SQLite database path is required for migrations"
            )
        if url.database != ":memory:":
            database_path = Path(url.database)
            if not database_path.is_absolute():
                raise RuntimeError(
                    "SQLite migration database path must be absolute"
                )

            development_database = (
                Path(__file__).resolve().parents[1] / "taskflow.db"
            )
            if database_path.resolve() == development_database.resolve():
                raise RuntimeError(
                    "Migrations cannot target the development taskflow.db"
                )

    return database_url


database_url = _migration_database_url()

def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(database_url, poolclass=NullPool)

    if connectable.dialect.name == "sqlite":
        @event.listens_for(connectable, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                render_as_batch=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
