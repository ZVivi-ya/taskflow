import asyncio

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from starlette.requests import Request
from starlette.responses import Response

from app.db.session import engine as application_engine
from app.middleware.request_logging import request_logging_middleware


def test_application_database_engine_hides_sql_parameters():
    assert application_engine.hide_parameters is True


def test_sqlalchemy_integrity_error_redacts_bound_parameter_values():
    secret_value = "sensitive-password-value"
    test_engine = create_engine("sqlite://", hide_parameters=True)
    try:
        with test_engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE credentials (value TEXT UNIQUE)")
            )
            connection.execute(
                text("INSERT INTO credentials (value) VALUES (:value)"),
                {"value": secret_value},
            )

        with pytest.raises(IntegrityError) as exc_info:
            with test_engine.begin() as connection:
                connection.execute(
                    text("INSERT INTO credentials (value) VALUES (:value)"),
                    {"value": secret_value},
                )

        assert secret_value not in str(exc_info.value)
        assert "[SQL parameters hidden due to hide_parameters=True]" in str(
            exc_info.value
        )
    finally:
        test_engine.dispose()


def test_request_logging_does_not_log_credentials_or_request_body(caplog):
    authorization = "Bearer sensitive-access-token"
    cookie = "session=sensitive-cookie"
    password = "sensitive-request-password"
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/login",
        "raw_path": b"/api/v1/login",
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"authorization", authorization.encode()),
            (b"cookie", cookie.encode()),
            (b"content-type", b"application/json"),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    async def receive():
        return {
            "type": "http.request",
            "body": f'{{"password":"{password}"}}'.encode(),
            "more_body": False,
        }

    request = Request(scope, receive=receive)

    async def call_next(_request):
        return Response(status_code=200)

    caplog.set_level("INFO", logger="app.middleware.request_logging")
    asyncio.run(request_logging_middleware(request, call_next))

    assert authorization not in caplog.text
    assert cookie not in caplog.text
    assert password not in caplog.text
