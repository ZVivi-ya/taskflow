from sqlalchemy import inspect

from app.db.session import engine


# 创建数据库结构检查器
inspector = inspect(engine)

# 获取数据库中真实存在的表名
table_names = inspector.get_table_names()

print("数据库中实际存在的表：", table_names)

# 查看 users 表的字段
columns = inspector.get_columns("users")

print("\nusers 表的字段：")

for column in columns:
    print(
        "字段名称：", column["name"],
        "| 类型：", column["type"],
        "| 是否允许 NULL：", column["nullable"]
    )