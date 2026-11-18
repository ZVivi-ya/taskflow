from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.hello import router as hello_router
from app.api.db_check import router as db_check_router
from app.api.router import api_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.users import router as users_router
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import setup_logging
from app.middleware.request_logging import request_logging_middleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import CORS_ORIGINS, DEBUG
from app.middleware.security_headers import security_headers_middleware

setup_logging()

app=FastAPI(
    title="TaskFlow API",
    description="个人任务与学习计划管理系统",
    version="1.0.0",
    debug=DEBUG,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(request_logging_middleware)
app.middleware("http")(security_headers_middleware)


register_exception_handlers(app)



app.include_router(
    health_router,
    prefix="/api/v1",
    tags=["健康检查"]
)

app.include_router(
    hello_router,
    prefix="/api/v1",
    tags=["欢迎"]
)

app.include_router(
    db_check_router,
    prefix="/api/v1",
    tags=["数据库测试"]
)

app.include_router(
    api_router,
    prefix="/api/v1"
)

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    tasks_router,
    prefix="/api/v1",
)
