from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_DATABASE = (PROJECT_ROOT / "taskflow.db").resolve()
EXPECTED_TABLES = {
    "users",
    "tasks",
    "categories",
    "task_categories",
}


def _column_map(inspector, table_name):
    return {
        column["name"]: (
            str(column["type"]).upper(),
            column["nullable"],
            column["default"],
        )
        for column in inspector.get_columns(table_name)
    }


def _migration_config(database_url=None):
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option(
        "script_location",
        str(PROJECT_ROOT / "migrations"),
    )
    if database_url is not None:
        config.set_main_option(
            "sqlalchemy.url",
            database_url.replace("%", "%%"),
        )
    return config


def test_upgrade_head_creates_complete_schema_in_temporary_database(
    tmp_path,
    monkeypatch,
):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    database_path = (tmp_path / "migration_test.db").resolve()
    assert database_path != DEVELOPMENT_DATABASE

    database_url = URL.create(
        "sqlite",
        database=str(database_path),
    ).render_as_string(hide_password=False)
    config = _migration_config(database_url)

    command.upgrade(config, "20261104")

    base_engine = create_engine(database_url)
    try:
        with base_engine.connect() as connection:
            base_inspector = inspect(connection)
            assert {"users", "tasks", "alembic_version"} <= set(
                base_inspector.get_table_names()
            )
            assert not {"categories", "task_categories"} & set(
                base_inspector.get_table_names()
            )
            task_owner_fk = next(
                foreign_key
                for foreign_key in base_inspector.get_foreign_keys("tasks")
                if foreign_key["constrained_columns"] == ["owner_id"]
            )
            assert task_owner_fk["name"] == "fk_tasks_owner_id_users"
            base_task_fk = connection.exec_driver_sql(
                "PRAGMA foreign_key_list('tasks')"
            ).one()
            assert base_task_fk[6] == "NO ACTION"
    finally:
        base_engine.dispose()

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            tables = set(inspector.get_table_names())
            assert tables == EXPECTED_TABLES | {"alembic_version"}

            assert _column_map(inspector, "users") == {
                "id": ("INTEGER", False, None),
                "username": ("VARCHAR(50)", False, None),
                "nickname": ("VARCHAR(30)", True, None),
                "email": ("VARCHAR(100)", False, None),
                "password_hash": ("VARCHAR(255)", False, None),
            }
            user_primary_key = inspector.get_pk_constraint("users")
            assert user_primary_key["constrained_columns"] == ["id"]
            user_uniques = {
                tuple(constraint["column_names"])
                for constraint in inspector.get_unique_constraints("users")
            }
            assert user_uniques == {("username",), ("email",)}

            task_columns = _column_map(inspector, "tasks")
            assert task_columns == {
                "id": ("INTEGER", False, None),
                "title": ("VARCHAR(100)", False, None),
                "description": ("TEXT", True, None),
                "status": ("VARCHAR(20)", False, None),
                "priority": ("VARCHAR(20)", False, None),
                "due_at": ("DATETIME", True, None),
                "owner_id": ("INTEGER", False, None),
                "created_at": ("DATETIME", False, "CURRENT_TIMESTAMP"),
                "updated_at": ("DATETIME", False, "CURRENT_TIMESTAMP"),
            }
            task_primary_key = inspector.get_pk_constraint("tasks")
            assert task_primary_key["constrained_columns"] == ["id"]
            task_owner_fk = next(
                foreign_key
                for foreign_key in inspector.get_foreign_keys("tasks")
                if foreign_key["constrained_columns"] == ["owner_id"]
            )
            assert task_owner_fk["name"] == "fk_tasks_owner_id_users"
            assert task_owner_fk["referred_table"] == "users"
            assert task_owner_fk["referred_columns"] == ["id"]
            assert task_owner_fk["options"]["ondelete"] == "CASCADE"
            task_indexes = {
                (index["name"], tuple(index["column_names"]), index["unique"])
                for index in inspector.get_indexes("tasks")
            }
            assert ("ix_tasks_owner_id", ("owner_id",), False) in task_indexes

            category_columns = _column_map(inspector, "categories")
            assert category_columns == {
                "id": ("INTEGER", False, None),
                "name": ("VARCHAR(50)", False, None),
                "description": ("TEXT", True, None),
                "owner_id": ("INTEGER", False, None),
                "created_at": ("DATETIME", False, "CURRENT_TIMESTAMP"),
                "updated_at": ("DATETIME", False, "CURRENT_TIMESTAMP"),
            }
            category_primary_key = inspector.get_pk_constraint("categories")
            assert category_primary_key["constrained_columns"] == ["id"]
            category_uniques = {
                tuple(constraint["column_names"])
                for constraint in inspector.get_unique_constraints("categories")
            }
            assert ("owner_id", "name") in category_uniques
            category_owner_fk = next(
                foreign_key
                for foreign_key in inspector.get_foreign_keys("categories")
                if foreign_key["constrained_columns"] == ["owner_id"]
            )
            assert category_owner_fk["referred_table"] == "users"
            assert category_owner_fk["referred_columns"] == ["id"]
            assert category_owner_fk["options"]["ondelete"] == "CASCADE"
            assert category_owner_fk["name"] == "fk_categories_owner_id_users"

            association_columns = _column_map(inspector, "task_categories")
            assert association_columns == {
                "task_id": ("INTEGER", False, None),
                "category_id": ("INTEGER", False, None),
            }
            association_primary_key = inspector.get_pk_constraint(
                "task_categories"
            )
            assert association_primary_key["constrained_columns"] == [
                "task_id",
                "category_id",
            ]
            association_fks = {
                (
                    tuple(foreign_key["constrained_columns"]),
                    foreign_key["referred_table"],
                    tuple(foreign_key["referred_columns"]),
                    foreign_key["options"]["ondelete"],
                )
                for foreign_key in inspector.get_foreign_keys("task_categories")
            }
            assert association_fks == {
                (("task_id",), "tasks", ("id",), "CASCADE"),
                (("category_id",), "categories", ("id",), "CASCADE"),
            }
            association_fk_names = {
                foreign_key["name"]
                for foreign_key in inspector.get_foreign_keys(
                    "task_categories"
                )
            }
            assert association_fk_names == {
                "fk_task_categories_task_id_tasks",
                "fk_task_categories_category_id_categories",
            }
            association_indexes = {
                (index["name"], tuple(index["column_names"]), index["unique"])
                for index in inspector.get_indexes("task_categories")
            }
            assert (
                "ix_task_categories_category_id",
                ("category_id",),
                False,
            ) in association_indexes

            version = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            assert version == "5370c94fd036"
            assert connection.exec_driver_sql(
                "PRAGMA foreign_key_check"
            ).all() == []
    finally:
        engine.dispose()


def test_database_url_environment_variable_takes_precedence(
    tmp_path,
    monkeypatch,
):
    environment_database_path = (tmp_path / "environment.db").resolve()
    config_database_path = (tmp_path / "config.db").resolve()
    environment_url = URL.create(
        "sqlite",
        database=str(environment_database_path),
    ).render_as_string(hide_password=False)
    config_url = URL.create(
        "sqlite",
        database=str(config_database_path),
    ).render_as_string(hide_password=False)
    monkeypatch.setenv("DATABASE_URL", environment_url)

    command.upgrade(_migration_config(config_url), "head")

    assert environment_database_path.exists()
    assert not config_database_path.exists()
    engine = create_engine(environment_url)
    try:
        with engine.connect() as connection:
            assert set(inspect(connection).get_table_names()) == (
                EXPECTED_TABLES | {"alembic_version"}
            )
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    ("database_url", "message"),
    [
        (None, "explicit sqlalchemy.url"),
        ("driver://user:password@localhost/dbname", "template URL"),
        (
            URL.create(
                "sqlite",
                database=str(DEVELOPMENT_DATABASE),
            ).render_as_string(hide_password=False),
            "development taskflow.db",
        ),
    ],
)
def test_migration_refuses_missing_template_or_development_database(
    database_url,
    message,
    monkeypatch,
):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    config = _migration_config(database_url)

    with pytest.raises(RuntimeError, match=message):
        command.upgrade(config, "head")
