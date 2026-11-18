import sqlite3

DB_PATH = "file:/app/data/taskflow.db?mode=ro"

def check_database():
    # 1. 以只读模式连接当前业务数据库
    connection = sqlite3.connect(DB_PATH, uri=True)
    try:
        # 2. 检查数据库完整性
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]
        print("integrity_check:", integrity)

        if integrity != "ok":
            raise RuntimeError("当前数据库完整性检查失败")

        # 3. 获取所有数据表
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = ?
            ORDER BY name
            """,
            ("table",),
        ).fetchall()

        print("\n当前数据库数据统计：")

        # 4. 逐张表统计记录数量
        for (table_name,) in tables:
            safe_name = table_name.replace('"', '""')
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{safe_name}"'
            ).fetchone()[0]
            print(f"{table_name}: {count} 条")
    finally:
        # 5. 关闭数据库连接
        connection.close()

if __name__ == "__main__":
    check_database()