import logging
from pathlib import Path

from app.core.config import LOG_LEVEL


# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parents[1]

# 日志目录
LOG_DIR = BASE_DIR / "logs"

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging():
    log_level = getattr(logging, LOG_LEVEL)

    # 创建统一的日志格式
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(max(logging.INFO, log_level))
    console_handler.setFormatter(formatter)

    # 文件 Handler
    file_handler = logging.FileHandler(
        LOG_DIR / "taskflow.log",
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # 配置根 Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清理已有 Handler，避免重复输出
    root_logger.handlers.clear()

    # 添加两个 Handler
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)