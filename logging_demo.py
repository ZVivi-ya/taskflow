import logging

# 1. 配置日志系统
logging.basicConfig(
    level=logging.DEBUG, #表示最低输出级别是 INFO
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# 2. 输出不同级别的日志
logging.debug("这是一条 DEBUG 日志")
logging.info("用户登录成功")
logging.warning("用户连续登录失败")
logging.error("数据库查询失败")
logging.critical("数据库服务无法连接")