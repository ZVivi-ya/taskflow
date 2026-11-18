import sqlite3
from pathlib import Path

# 1. 指定需要验证的备份文件
backup_path = (
    Path(__file__).resolve().parent.parent
    / "backups"
    / "taskflow_20261110_044308.db"
)

# 2. 检查文件是否存在
if not backup_path.is_file():
    raise FileNotFoundError(
        f"备份文件不存在：{backup_path}"
    )

# 3. 以只读模式打开备份数据库
connection = sqlite3.connect(
    backup_path.as_uri() + "?mode=ro",
    uri=True,
)

try:
    # 4. 检查数据库完整性
    result = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    print("integrity_check:", result)

    # 5. 获取数据库中的所有表名
    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = ?
        ORDER BY name
        """,
        ("table",),
    ).fetchall()

    print("tables:")

    for table in tables:
        print(" -", table[0])

finally:
    # 6. 无论检查成功还是失败，都关闭连接
    connection.close()
