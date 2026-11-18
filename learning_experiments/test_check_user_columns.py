from sqlalchemy import inspect
from app.db.session import engine

inspector=inspect(engine)
columns=inspector.get_columns("users")
print("users 表当前字段：")
for column in columns:
    print(column["name"],column["type"])