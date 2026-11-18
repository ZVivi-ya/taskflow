import pytest

from app.core.config import load_settings


def test_development_settings_keep_sqlite_and_local_cors_defaults():
    settings = load_settings({"JWT_SECRET_KEY": "development-test-secret"})

    assert settings.app_env == "development"
    assert settings.database_url == "sqlite:///./taskflow.db"
    assert settings.allow_sqlite_in_production is False
    assert settings.debug is False
    assert settings.cors_origins == (
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    )
    assert settings.log_level == "DEBUG"


def test_production_settings_accept_explicit_safe_values():
    settings = load_settings(
        {
            "APP_ENV": "production",
            "DATABASE_URL": "postgresql://db.example/taskflow",
            "DEBUG": "false",
            "JWT_SECRET_KEY": "secure-production-secret-value-123456",
            "JWT_EXPIRE_MINUTES": "20",
            "CORS_ORIGINS": "https://app.example.com",
            "LOG_LEVEL": "INFO",
        }
    )

    assert settings.debug is False
    assert settings.database_url == "postgresql://db.example/taskflow"
    assert settings.cors_origins == ("https://app.example.com",)
    assert settings.jwt_expire_minutes == 20
    assert settings.log_level == "INFO"
    assert "secure-production-secret-value-123456" not in repr(settings)


def test_production_rejects_sqlite_by_default():
    with pytest.raises(RuntimeError, match="SQLite"):
        load_settings(
            {
                "APP_ENV": "production",
                "DATABASE_URL": "sqlite:////app/data/taskflow.db",
                "JWT_SECRET_KEY": "secure-production-secret-value-123456",
                "DEBUG": "false",
                "CORS_ORIGINS": "https://app.example.com",
                "LOG_LEVEL": "INFO",
            }
        )


def test_production_allows_sqlite_when_explicitly_enabled():
    settings = load_settings(
        {
            "APP_ENV": "production",
            "DATABASE_URL": "sqlite:////app/data/taskflow.db",
            "ALLOW_SQLITE_IN_PRODUCTION": "true",
            "JWT_SECRET_KEY": "secure-production-secret-value-123456",
            "DEBUG": "false",
            "CORS_ORIGINS": "https://app.example.com",
            "LOG_LEVEL": "INFO",
        }
    )

    assert settings.database_url == "sqlite:////app/data/taskflow.db"
    assert settings.allow_sqlite_in_production is True


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"JWT_SECRET_KEY": "short"}, "JWT_SECRET_KEY"),
        ({"DEBUG": "true"}, "DEBUG"),
        ({"CORS_ORIGINS": "*"}, "CORS_ORIGINS"),
        ({"CORS_ORIGINS": "http://localhost:3000"}, "non-local HTTPS"),
        ({"CORS_ORIGINS": "http://app.example.com"}, "non-local HTTPS"),
    ],
)
def test_sqlite_opt_in_does_not_bypass_other_production_checks(
    overrides,
    message,
):
    values = {
        "APP_ENV": "production",
        "DATABASE_URL": "sqlite:////app/data/taskflow.db",
        "ALLOW_SQLITE_IN_PRODUCTION": "true",
        "JWT_SECRET_KEY": "secure-production-secret-value-123456",
        "DEBUG": "false",
        "CORS_ORIGINS": "https://app.example.com",
        "LOG_LEVEL": "INFO",
        **overrides,
    }

    with pytest.raises(RuntimeError, match=message):
        load_settings(values)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({}, "DATABASE_URL"),
        ({"DATABASE_URL": "sqlite:///./taskflow.db"}, "SQLite"),
        (
            {
                "DATABASE_URL": "postgresql://db.example/taskflow",
                "JWT_SECRET_KEY": "short",
            },
            "JWT_SECRET_KEY",
        ),
        (
            {
                "DATABASE_URL": "postgresql://db.example/taskflow",
                "JWT_SECRET_KEY": "secure-production-secret-value-123456",
                "DEBUG": "true",
            },
            "DEBUG",
        ),
        (
            {
                "DATABASE_URL": "postgresql://db.example/taskflow",
                "JWT_SECRET_KEY": "secure-production-secret-value-123456",
                "CORS_ORIGINS": "*",
            },
            "CORS_ORIGINS",
        ),
        (
            {
                "DATABASE_URL": "postgresql://db.example/taskflow",
                "JWT_SECRET_KEY": "secure-production-secret-value-123456",
                "CORS_ORIGINS": "http://localhost:3000",
            },
            "non-local HTTPS",
        ),
        (
            {
                "DATABASE_URL": "postgresql://db.example/taskflow",
                "JWT_SECRET_KEY": "secure-production-secret-value-123456",
                "CORS_ORIGINS": "http://app.example.com",
            },
            "non-local HTTPS",
        ),
        (
            {
                "DATABASE_URL": "postgresql://db.example/taskflow",
                "JWT_SECRET_KEY": "secure-production-secret-value-123456",
                "LOG_LEVEL": "DEBUG",
            },
            "DEBUG logging",
        ),
    ],
)
def test_production_rejects_unsafe_or_missing_settings(overrides, message):
    values = {
        "APP_ENV": "production",
        "JWT_SECRET_KEY": "secure-production-secret-value-123456",
        "DEBUG": "false",
        "CORS_ORIGINS": "https://app.example.com",
        "LOG_LEVEL": "INFO",
        **overrides,
    }

    with pytest.raises(RuntimeError, match=message):
        load_settings(values)


@pytest.mark.parametrize("value", ["0", "false", "no", "off"])
def test_debug_accepts_false_spellings(value):
    settings = load_settings(
        {
            "JWT_SECRET_KEY": "development-test-secret",
            "DEBUG": value,
        }
    )

    assert settings.debug is False


def test_invalid_log_level_is_rejected():
    with pytest.raises(ValueError, match="LOG_LEVEL"):
        load_settings(
            {
                "JWT_SECRET_KEY": "development-test-secret",
                "LOG_LEVEL": "TRACE",
            }
        )
