# Taskflow 数据库备份与恢复说明
## 1. 文档目的
本文档说明 Taskflow 项目当前 SQLite 数据库的备份、
备份文件验证和恢复演练流程。
目标：
- 降低数据库文件损坏或误操作造成的数据丢失风险。
- 能够生成独立的数据库备份文件。
- 能够验证备份文件是否有效。
- 能够通过备份文件进行恢复演练。
- 明确正式数据库恢复时需要注意的风险。

本文档记录的是当前项目已经实现并验证的能力。
尚未实现的自动化备份和生产环境一键恢复，不视为已完成。

---
## 2. 当前数据库环境
| 项目 | 当前配置 |
|---|---|
| 数据库类型 | SQLite |
| 数据库文件 | taskflow.db |
| 容器名称 | taskflow-api |
| Compose 服务名 | api |
| 容器内数据库路径 | /app/data/taskflow.db |
| 数据库 URL | sqlite:////app/data/taskflow.db |
| Docker Volume | taskflow_data |
| Volume 挂载路径 | /app/data |
| SQLite journal_mode | delete |
数据库文件位于 Docker Volume 中，而不是仅保存在容器可写层。
因此，即使容器被删除并重新创建，只要保留原来的
taskflow_data Volume，并将其重新挂载到 /app/data，
数据库文件就可以继续使用。
注意：
不要在没有确认备份有效的情况下删除 Docker Volume。
尤其不要随意执行：
    docker compose down -v
该命令可能删除 Compose 管理的命名 Volume，
导致数据库持久化数据丢失。

---

## 3. 数据库备份方案
### 3.1 为什么使用 SQLite Backup API
当前项目使用 SQLite。
备份时使用 Python 标准库 sqlite3 提供的 Backup API，
而不是简单地直接复制正在使用的数据库文件。
Backup API 可以在数据库连接仍然打开的情况下，
生成一致性的数据库备份。
当前备份脚本：
    scripts/backup_db.py

### 3.2 备份过程

当前备份脚本采用以下流程：
1. 连接当前数据库。
2. 使用 SQLite Backup API 生成临时备份文件。
3. 对临时备份文件执行 integrity_check。
4. 只有完整性检查通过，才将临时文件替换为正式备份文件。
5. 输出备份文件路径。

临时文件通过检查后才成为正式备份文件，
可以避免将未验证的临时结果直接作为有效备份。

### 3.3 执行备份
先确认容器正在运行：
    docker compose ps

将备份脚本复制到容器：
    docker cp .\scripts\backup_db.py taskflow-api:/tmp/backup_db.py

执行备份脚本：
    docker exec taskflow-api python /tmp/backup_db.py

脚本成功执行后，会输出备份文件路径。
本次实际备份输出：
    /tmp/taskflow_20261110_044308.db

### 3.4 将备份复制到 Windows 宿主机
在项目根目录创建备份目录（如果尚不存在）：
    New-Item -ItemType Directory -Force .\backups

将容器内的备份文件复制到宿主机：
    docker cp taskflow-api:/tmp/taskflow_20261110_044308.db .\backups\

本次实际备份文件：
    backups/taskflow_20261110_044308.db

文件大小：
    53248 bytes

备份文件应保存在容器之外，避免容器删除时备份文件一并丢失。
---

## 4. 备份文件验证
备份成功不代表备份文件一定可以正常使用，
因此还需要独立验证备份文件。

当前验证脚本：
    scripts/verify_backup.py

执行：
    python .\scripts\verify_backup.py

验证内容包括：
- 能否正常打开备份数据库。
- SQLite integrity_check 是否返回 ok。
- 能否读取数据库表结构。

本次实际验证结果：
    integrity_check: ok
    tables:
     - alembic_version
     - categories
     - task_categories
     - tasks
     - users
验证结果：通过。

---

## 5. 恢复演练
### 5.1 恢复演练的目的
恢复演练用于验证备份文件不仅能够被打开，
还能够实际生成一个可用的数据库。
本次演练不会覆盖正在使用的正式数据库。

### 5.2 恢复演练方式

当前恢复演练脚本：
    scripts/restore_test.py

脚本从备份文件读取数据，
使用 SQLite Backup API 生成独立的恢复数据库。

本次恢复数据库位置：
    backups/restore_test/taskflow_restored.db

### 5.3 恢复验证

恢复完成后，对恢复数据库执行完整性检查，
并比较原备份与恢复数据库中的表记录数量。
本次实际验证结果：
    恢复操作：成功
    恢复数据库完整性：ok
    原备份中的数据：
      alembic_version: 1 条
      categories: 3 条
      task_categories: 1 条
      tasks: 7 条
      users: 3 条

    恢复数据库中的数据：
      alembic_version: 1 条
      categories: 3 条
      task_categories: 1 条
      tasks: 7 条
      users: 3 条
    恢复验证：通过

本次恢复演练证明：
备份文件可以被读取，并能够生成数据一致的独立恢复数据库。
注意：
这属于隔离环境中的恢复演练，
不代表已经实现正式数据库的一键恢复功能。

---
## 6. 正式恢复时的安全要求
当前项目已经完成独立数据库恢复演练，
但尚未实现自动替换生产数据库的恢复脚本。

未来执行正式恢复时，应遵循以下原则：
1. 先停止应用写入，避免恢复期间数据库仍被修改。
2. 确认备份文件来源、时间和完整性。
3. 保留当前数据库文件副本，不直接覆盖原文件。
4. 在独立位置完成恢复和完整性验证。
5. 确认恢复结果后，再按照受控流程替换正式数据库。
6. 启动应用并检查健康状态和核心业务接口。
7. 保留恢复前后的记录，便于问题追踪。

不要在应用仍然使用数据库时直接覆盖
/app/data/taskflow.db。

不要将未经验证的备份文件直接作为正式数据库使用。

---

## 7. 备份文件管理

当前备份目录：
    backups/

建议的备份管理策略：
| 备份类型 | 建议保留数量 |
|---|---:|
| 每日备份 | 最近 7 份 |
| 每周备份 | 最近 4 份 |
| 每月备份 | 最近 3 份 |

以上是建议策略，不代表当前已经配置自动备份或自动清理。
当前阶段采用手动备份和人工验证。
后续可以考虑：
- 定时执行备份脚本。
- 自动验证备份完整性。
- 按保留策略清理过期备份。
- 将重要备份复制到独立存储位置。
- 定期执行恢复演练。

在自动清理机制经过验证之前，不要编写自动删除备份文件的任务。

---

## 8. 当前完成情况
| 项目 | 状态 |
|---|---|
| SQLite Backup API 备份脚本 | 已完成 |
| 备份文件生成 | 已完成 |
| 备份复制到宿主机 | 已完成 |
| 备份文件完整性验证 | 已完成 |
| 独立恢复演练 | 已完成 |
| 恢复后数据一致性验证 | 已完成 |
| 自动定时备份 | 未实现 |
| 自动备份清理 | 未实现 |
| 生产环境一键恢复 | 未实现 |
| 异地备份 | 未实现 |
本次数据库备份与恢复核心流程已通过验证。

后续需要结合部署与运维文档，
补充健康检查失败、Alembic 迁移失败、
容器异常退出等故障排查说明。