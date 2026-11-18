import sqlite3
from pathlib import Path

# 1. 确定备份文件和恢复目标路径
PROJECT_DIR = Path(__file__).resolve().parent.parent
BACKUP_DB = (
    PROJECT_DIR
    / "backups"
    / "taskflow_20261110_044308.db"
)
RESTORE_DIR = PROJECT_DIR / "backups" / "restore_test"
RESTORED_DB = RESTORE_DIR / "taskflow_restored.db"

def get_table_info(connection):
    """获取数据库中的表名及每张表的记录数量。"""
    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = ?
        ORDER BY name
        """,
        ("table",),
    ).fetchall()

    result = {}

    for (table_name,) in tables:
        # 对表名中的双引号进行转义
        safe_name = table_name.replace('"', '""')

        count = connection.execute(
            f'SELECT COUNT(*) FROM "{safe_name}"'
        ).fetchone()[0]

        result[table_name] = count

    return result

def restore_database():
    # 2. 检查备份文件
    if not BACKUP_DB.is_file():
        raise FileNotFoundError(
            f"备份文件不存在：{BACKUP_DB}"
        )

    # 3. 创建独立的恢复测试目录
    RESTORE_DIR.mkdir(parents=True, exist_ok=True)

    # 4. 防止覆盖之前的恢复结果
    if RESTORED_DB.exists():
        raise FileExistsError(
            f"恢复目标已经存在，请先检查：{RESTORED_DB}"
        )

    source = None
    target = None

    try:
        # 5. 只读打开原始备份
        source = sqlite3.connect(
            BACKUP_DB.as_uri() + "?mode=ro",
            uri=True,
        )

        # 6. 创建新的恢复数据库
        target = sqlite3.connect(str(RESTORED_DB))

        # 7. 使用 SQLite Backup API 执行恢复
        source.backup(target)

        print("恢复操作：成功")

        # 8. 关闭连接
        target.close()
        target = None

        source.close()
        source = None

        # 9. 重新打开恢复后的数据库进行独立验证
        restored = sqlite3.connect(
            RESTORED_DB.as_uri() + "?mode=ro",
            uri=True,
        )

        try:
            integrity = restored.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

            print("恢复数据库完整性：", integrity)

            if integrity != "ok":
                raise RuntimeError("恢复数据库完整性检查失败")

            # 10. 对比备份与恢复数据库的表名和记录数量
            original = sqlite3.connect(
                BACKUP_DB.as_uri() + "?mode=ro",
                uri=True,
            )

            try:
                original_info = get_table_info(original)
                restored_info = get_table_info(restored)

                print("\n原备份中的数据：")
                for name, count in original_info.items():
                    print(f"  {name}: {count} 条")

                print("\n恢复数据库中的数据：")
                for name, count in restored_info.items():
                    print(f"  {name}: {count} 条")

                if original_info != restored_info:
                    raise RuntimeError(
                        "恢复前后的表结构或记录数量不一致"
                    )

                print("\n恢复验证：通过")

            finally:
                original.close()

        finally:
            restored.close()

        print("恢复文件：", RESTORED_DB)

    except Exception:
        if target is not None:
            target.close()
        if source is not None:
            source.close()
        # 仅清理本次创建的恢复测试文件
        RESTORED_DB.unlink(missing_ok=True)
        raise

if __name__ == "__main__":
    restore_database()
