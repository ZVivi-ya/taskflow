import logging

from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response


logger = logging.getLogger(__name__)


async def security_headers_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:

    logger.info(
        "[Security Middleware] 请求进入：%s",
        request.url.path,
    )

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    logger.info(
        "[Security Middleware] 响应返回：status=%s",
        response.status_code,
    )

    return response