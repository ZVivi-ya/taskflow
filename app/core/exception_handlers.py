
# app/core/exception_handlers.py

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """
    注册 TaskFlow 全局异常处理器。
    """

    # 1. 处理自定义业务异常
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": exc.status_code,
                "message": exc.message,
                "data": {
                    "error_code": exc.error_code
                },
            },
        )

    # 2. 处理 FastAPI / Starlette HTTPException
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": exc.status_code,
                "message": str(exc.detail),
                "data": None,
            },
            headers=exc.headers,
        )

    # 3. 处理请求参数校验异常
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        details = [
            {
                "location": error["loc"],
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "code": 422,
                "message": "Request validation failed",
                "data": details,
            },
        )

    # 4. 处理未预期异常
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "发生未处理异常，method=%s，path=%s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": 500,
                "message": "Internal server error",
                "data": None,
            },
        )
