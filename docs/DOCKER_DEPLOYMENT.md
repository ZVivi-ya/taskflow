# Docker 部署说明

## 环境选择

Compose 要求显式设置 `APP_ENV` 为 `development` 或 `production`。
本地开发可从 `.env.example` 开始，复制为 `.env` 后使用开发配置。

生产环境应使用单独保管的环境文件，例如 `.env.production`，至少配置：

```text
APP_ENV=production
TASKFLOW_VOLUME_NAME=taskflow_data_production
ALLOW_SQLITE_IN_PRODUCTION=true
DEBUG=false
JWT_SECRET_KEY=<独立生成的强随机密钥>
CORS_ORIGINS=<正式 HTTPS 前端来源>
LOG_LEVEL=INFO
```

不要在生产环境使用 `.env.example` 中的 JWT 示例值。启动时通过
`docker compose --env-file .env.production up -d --build` 指定生产配置。
Compose 保留现有 external Volume 名称 `taskflow_data` 作为默认值；
建议开发和生产分别设置不同的 `TASKFLOW_VOLUME_NAME`。

Compose 将数据库固定为容器内的 `/app/data/taskflow.db`，并挂载所选的
external named volume。`.env.example` 中的 `DATABASE_URL` 是本地开发用；
Compose 不使用它。

## SQLite Volume 保护

容器删除或重建不会删除 external Volume；重新启动时必须继续使用原有
Volume。External Volume 必须先存在。首次创建开发 Volume（只会创建，不会
清理已有卷）：

```powershell
docker volume create taskflow_data
docker volume inspect taskflow_data
```

生产环境使用独立卷时，先创建与生产配置相同名称的卷，例如：

```powershell
docker volume create taskflow_data_production
docker volume inspect taskflow_data_production
```

使用已有 Volume 前先检查并确认其名称和用途。不要为了排查问题而创建替代
数据库或切换到空卷。容器启动命令会先对配置的数据库执行
`alembic upgrade head`，成功后才启动 Uvicorn。

日常部署或重建容器时不要使用 `docker compose down -v`、
`docker volume rm` 或 `docker volume prune`。这些操作可能移除持久化数据。
计划进行存储变更前，应通过 SQLite 一致性备份流程备份数据库。
