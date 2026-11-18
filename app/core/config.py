import os
from dataclasses import dataclass, field
from typing import Mapping
from urllib.parse import urlsplit

from dotenv import load_dotenv


DEFAULT_CORS_ORIGINS = (
    "http://localhost:5500",
    "http://127.0.0.1:5500",
)
LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
ENVIRONMENTS = {"development", "test", "production"}
JWT_SECRET_PLACEHOLDERS = {
    "secret",
    "changeme",
    "change_me",
    "your_secret_key",
    "replace-with-a-random-secret",
}


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str
    allow_sqlite_in_production: bool
    debug: bool
    jwt_secret_key: str = field(repr=False)
    jwt_expire_minutes: int
    cors_origins: tuple[str, ...]
    log_level: str


def _parse_bool(name: str, value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _is_local_origin(origin: str) -> bool:
    hostname = urlsplit(origin).hostname
    return hostname in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def load_settings(environ: Mapping[str, str] | None = None) -> Settings:
    """从环境变量加载配置，并校验生产环境必须满足的安全条件。"""
    values = os.environ if environ is None else environ

    app_env = values.get("APP_ENV", "development").strip().lower()
    if app_env not in ENVIRONMENTS:
        raise ValueError(
            "APP_ENV must be development, test, or production"
        )

    database_url = values.get("DATABASE_URL", "").strip()
    if not database_url:
        if app_env == "production":
            raise RuntimeError(
                "DATABASE_URL must be explicitly set in production"
            )
        database_url = "sqlite:///./taskflow.db"

    allow_sqlite_in_production = _parse_bool(
        "ALLOW_SQLITE_IN_PRODUCTION",
        values.get("ALLOW_SQLITE_IN_PRODUCTION", "false"),
    )

    jwt_secret_key = values.get("JWT_SECRET_KEY", "").strip()
    if not jwt_secret_key:
        raise RuntimeError("JWT_SECRET_KEY must be configured")

    try:
        jwt_expire_minutes = int(values.get("JWT_EXPIRE_MINUTES", "30"))
    except ValueError as exc:
        raise ValueError("JWT_EXPIRE_MINUTES must be an integer") from exc
    if jwt_expire_minutes <= 0:
        raise ValueError("JWT_EXPIRE_MINUTES must be greater than zero")

    debug_value = values.get("DEBUG")
    debug = (
        _parse_bool("DEBUG", debug_value)
        if debug_value is not None
        else False
    )

    if "CORS_ORIGINS" in values:
        cors_origins = tuple(
            origin.strip()
            for origin in values["CORS_ORIGINS"].split(",")
            if origin.strip()
        )
    else:
        cors_origins = DEFAULT_CORS_ORIGINS

    log_level = values.get(
        "LOG_LEVEL",
        "DEBUG" if app_env == "development" else "INFO",
    ).strip().upper()
    if log_level not in LOG_LEVELS:
        raise ValueError(
            "LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL"
        )

    if app_env == "production":
        if (
            database_url.lower().startswith("sqlite")
            and not allow_sqlite_in_production
        ):
            raise RuntimeError(
                "SQLite is not allowed as the production DATABASE_URL"
            )
        if (
            len(jwt_secret_key) < 32
            or jwt_secret_key.lower() in JWT_SECRET_PLACEHOLDERS
            or any(
                marker in jwt_secret_key.lower()
                for marker in ("placeholder", "replace-me", "change-me")
            )
        ):
            raise RuntimeError(
                "Production JWT_SECRET_KEY must be a non-placeholder "
                "secret of at least 32 characters"
            )
        if debug:
            raise RuntimeError("DEBUG must be false in production")
        if not cors_origins or "*" in cors_origins:
            raise RuntimeError(
                "Production CORS_ORIGINS must be explicitly restricted"
            )
        if any(
            _is_local_origin(origin)
            or urlsplit(origin).scheme != "https"
            or not urlsplit(origin).hostname
            for origin in cors_origins
        ):
            raise RuntimeError(
                "Production CORS_ORIGINS must use non-local HTTPS origins"
            )
        if log_level == "DEBUG":
            raise RuntimeError("DEBUG logging is not allowed in production")

    return Settings(
        app_env=app_env,
        database_url=database_url,
        allow_sqlite_in_production=allow_sqlite_in_production,
        debug=debug,
        jwt_secret_key=jwt_secret_key,
        jwt_expire_minutes=jwt_expire_minutes,
        cors_origins=cors_origins,
        log_level=log_level,
    )


# 加载本地 .env；部署环境变量优先于文件值。
load_dotenv()
settings = load_settings()

APP_ENV = settings.app_env
DATABASE_URL = settings.database_url
ALLOW_SQLITE_IN_PRODUCTION = settings.allow_sqlite_in_production
DEBUG = settings.debug
JWT_SECRET_KEY = settings.jwt_secret_key
JWT_SECRET_MINUTES = settings.jwt_expire_minutes
CORS_ORIGINS = list(settings.cors_origins)
LOG_LEVEL = settings.log_level
