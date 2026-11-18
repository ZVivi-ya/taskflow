# 使用 Python 3.12 官方轻量镜像作为基础环境
FROM python:3.12-slim

# 设置容器内的工作目录
WORKDIR /app

# 将依赖清单复制到容器中
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将项目代码复制到容器中
COPY . .

# 创建固定 UID/GID 的非 root 运行用户，并准备运行时写目录
RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/app/logs /app/data \
    && chmod -R a=rX /app \
    && chown -R appuser:appuser /app/app/logs \
    && find /app/app/logs -type d -exec chmod 0750 {} + \
    && find /app/app/logs -type f -exec chmod 0640 {} + \
    && chown appuser:appuser /app/data \
    && chmod 0750 /app/data

# 声明应用使用的容器端口
EXPOSE 8000

# 切换到非 root 用户
USER appuser

# 启动 FastAPI 服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
