# TaskFlow

个人任务与学习计划管理系统的后端 API。项目基于 FastAPI 提供用户认证、个人任务和分类管理能力，并使用 SQLAlchemy 持久化数据、Alembic 管理数据库迁移。

## 项目功能（Features）

### 已实现

- 用户注册、登录和当前用户信息查询；密码使用 Argon2 哈希，登录后签发 JWT。
- 任务的创建、列表查询、详情查询、更新和删除；任务按用户隔离。
- 分类的创建、列表查询、详情查询、更新和删除；同一用户下分类名称唯一。
- 任务与分类的关联、查询和移除。
- 健康检查、数据库就绪检查，以及请求日志、请求 ID 和安全响应头中间件。
- Alembic 数据库迁移。
- SQLite 数据库备份、完整性验证和隔离的恢复演练脚本。
- Docker 镜像与 Docker Compose 部署配置；容器启动时先执行数据库迁移。

### 计划实现

- 自动定时备份、自动备份验证和按保留策略清理备份。
- 将备份复制到独立存储位置，并定期执行恢复演练。
- 生产数据库的一键恢复能力。

以上自动化备份与正式恢复能力目前尚未实现；现有备份和恢复脚本用于手动操作及独立恢复验证。

## 技术栈（Tech Stack）

- Python（Docker 镜像使用 Python 3.12）
- FastAPI、Uvicorn
- SQLAlchemy 2.x、Alembic
- SQLite（默认配置及当前 Compose 配置）
- Pydantic（请求与响应数据校验）
- pwdlib（Argon2 密码哈希）、PyJWT（JWT）
- pytest、HTTPX（测试）
- Docker、Docker Compose

## 项目结构（Project Structure）

```text
.
├── app/
│   ├── api/                 # API 路由、依赖和健康检查
│   │   └── v1/              # 用户、任务、分类及任务分类接口
│   ├── core/                # 配置、安全、日志和异常处理
│   ├── db/                  # SQLAlchemy 基础类与数据库会话
│   ├── middleware/          # 请求日志与安全响应头
│   ├── models/              # 用户、任务、分类及关联模型
│   ├── repositories/        # 数据访问层
│   ├── schemas/             # 请求与响应模型
│   └── services/            # 业务逻辑
├── migrations/              # Alembic 环境与迁移版本
├── scripts/                 # 数据库备份、验证、恢复演练等脚本
├── tests/                   # API、服务、配置、迁移等测试
├── docs/                    # Docker 部署及数据库备份/恢复说明
├── learning_experiments/    # 学习与数据库实验脚本
├── backups/                 # 本地备份及恢复演练数据
├── Dockerfile
├── compose.yaml
├── alembic.ini
└── requirements.txt
```

仓库根目录还包含演示脚本、日志和 SQLite 数据库文件；这些文件不属于应用启动所需的源码模块。

## 环境要求（Prerequisites）

- Docker Engine 与 Docker Compose 插件。
- 运行测试或在容器外操作时需要 Python；Dockerfile 使用 Python 3.12。
- 按 `.env.example` 提供应用配置。`JWT_SECRET_KEY` 必须设置；生产环境还要求显式配置数据库、非占位且至少 32 个字符的 JWT 密钥、受限的 HTTPS CORS 来源，以及关闭调试模式。

## 安装与运行（Installation & Usage）

### 使用 Docker Compose 启动

在项目根目录执行以下 PowerShell 命令：

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker volume create taskflow_data
docker compose up --build -d
docker compose ps
```

Compose 使用外部 Docker volume `taskflow_data` 保存 SQLite 数据；启动容器前会对数据库执行 `alembic upgrade head`，然后启动 Uvicorn。确认 `.env` 中的开发配置适用于本地环境；生产环境不要使用示例密钥，并应参考 [Docker 部署说明](docs/DOCKER_DEPLOYMENT.md) 配置专用环境文件和数据卷。Compose 当前固定使用 SQLite；生产环境如继续使用 SQLite，必须显式允许。

服务启动后可访问：

- Swagger UI：<http://localhost:8000/docs>
- 健康检查：<http://localhost:8000/api/v1/health>
- 数据库就绪检查：<http://localhost:8000/api/v1/health/ready>

API 路由前缀为 `/api/v1`。用户认证接口包括注册、登录和当前用户查询；任务与分类接口需要通过 Bearer JWT 进行认证。接口详情也可在 Swagger UI 中查看。

### 安装依赖并运行测试

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
python -m pip install -r requirements.txt
python -m pytest
```

测试使用独立的临时 SQLite 数据库。若 `.env` 已存在，请勿覆盖已有配置；确保至少配置了 `JWT_SECRET_KEY` 后再运行测试。

## 后续规划（Roadmap）

- 将手动数据库备份扩展为定时任务，并自动验证生成的备份。
- 设计并验证备份保留与清理策略。
- 增加异地或独立存储备份及定期恢复演练流程。
- 在受控流程下补充生产数据库恢复能力。

以上为现有备份与恢复文档中提出但尚未实现的事项。其他产品功能规划：待确认。
