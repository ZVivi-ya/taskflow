from sqlalchemy import text
from app.db.session import engine


with engine.connect() as connection:

    # 1. 检查 tasks 表的外键
    print("\n========== tasks 外键 ==========")

    foreign_keys = connection.execute(
        text("PRAGMA foreign_key_list(tasks)")
    ).fetchall()

    for foreign_key in foreign_keys:
        print(foreign_key)

    # 2. 检查 users 表的索引
    print("\n========== users 索引 ==========")

    indexes = connection.execute(
        text("PRAGMA index_list(users)")
    ).fetchall()

    for index in indexes:
        print(index)

    # 3. 检查 users 表的建表语句
    print("\n========== users 建表语句 ==========")

    users_sql = connection.execute(
        text("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table' AND name = 'users'
        """)
    ).scalar_one()

    print(users_sql)