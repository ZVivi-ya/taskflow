import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint


logger = logging.getLogger(__name__)


async def request_logging_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:

    # 1. 生成当前请求的唯一 ID
    request_id = str(uuid.uuid4())

    # 2. 将 Request ID 保存到 request.state
    request.state.request_id = request_id

    # 3. 记录请求开始时间
    start_time = time.perf_counter()

    # 4. 获取请求基本信息
    method = request.method
    path = request.url.path

    # 5. 获取客户端 IP
    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    logger.info(
        "请求进入 | request_id=%s | method=%s | path=%s | client_ip=%s",
        request_id,
        method,
        path,
        client_ip,
    )
    logger.info("[Request Logging Middleware] 请求进入")
    try:
        # 6. 将请求交给后续 FastAPI 处理流程
        response = await call_next(request)
        logger.info("[Request Logging Middleware] 收到下游响应")
    except Exception:
        # 7. 记录未预期异常
        elapsed_time = time.perf_counter() - start_time

        logger.exception(
            "请求异常 | request_id=%s | method=%s | path=%s | "
            "client_ip=%s | elapsed=%.3fs",
            request_id,
            method,
            path,
            client_ip,
            elapsed_time,
        )

        # 继续抛出异常，交给外层异常处理机制
        raise

    # 8. 计算请求耗时
    elapsed_time = time.perf_counter() - start_time

    # 9. 给响应添加 Request ID
    response.headers["X-Request-ID"] = request_id

    # 10. 记录响应信息
    logger.info(
        "请求完成 | request_id=%s | method=%s | path=%s | "
        "status_code=%s | elapsed=%.3fs",
        request_id,
        method,
        path,
        response.status_code,
        elapsed_time,
    )

    # 11. 返回响应
    return response