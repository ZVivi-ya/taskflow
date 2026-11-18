from sqlalchemy import inspect,text
from app.db.session import engine
inspector=inspect(engine)
columns=inspector.get_columns("users")
column_name=[column["name"] for column in columns]

if "nickname" not in column_name:
    with engine.begin() as connection:
        sql="""
        ALTER TABLE users
        ADD COLUMN nickname VARCHAR(30)
        """
        connection.execute(text(sql))
    print("nickname 字段添加成功！")
else:
    print("nickname 字段已经存在，无需重复添加。")