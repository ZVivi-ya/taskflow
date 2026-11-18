import logging

# 1. 创建 Logger
logger = logging.getLogger("taskflow.demo")
logger.setLevel(logging.DEBUG)

# 2. 创建控制台 Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 3. 创建文件 Handler
file_handler = logging.FileHandler(
    "taskflow_demo.log",
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)

# 4. 创建 Formatter
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# 5. 将 Formatter 设置给两个 Handler
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 6. 将 Handler 添加到 Logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 7. 发送日志
logger.debug("这是一条 DEBUG 日志")
logger.info("用户登录成功")
logger.warning("用户连续登录失败")
logger.error("数据库查询失败")