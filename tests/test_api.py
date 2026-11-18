from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.main import app

def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "TaskFlow API is running",
    }


def test_readiness_check_succeeds_when_database_query_succeeds(client):
    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ready"}


def test_readiness_check_returns_503_without_database_error_details(client):
    class FailingSession:
        def execute(self, statement):
            raise OperationalError(
                str(statement),
                {},
                RuntimeError("sensitive database details"),
            )

    def override_get_db():
        yield FailingSession()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json() == {
        "status": "error",
        "database": "unavailable",
    }
    assert "sensitive database details" not in response.text


def test_test_database_tables(test_engine):
    inspector = inspect(test_engine)

    tables = inspector.get_table_names()

    assert "users" in tables
    assert "tasks" in tables
    assert "categories" in tables
    assert "task_categories" in tables


def test_database_foreign_keys_enabled(test_engine):
    with test_engine.connect() as connection:
        result = connection.exec_driver_sql(
            "PRAGMA foreign_keys"
        ).scalar()

    assert result == 1

from app.db.session import engine


def test_test_database_is_separate_from_development(test_engine):
    test_database_path = test_engine.url.database
    development_database_path = engine.url.database

    assert test_database_path != development_database_path