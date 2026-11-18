from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    result = db.execute(
        text("PRAGMA foreign_keys")
    ).scalar_one()

    print(f"SQLite foreign_keys 当前状态：{result}")

    if result == 1:
        print("外键约束已经启用")
    else:
        print("外键约束尚未启用")

finally:
    db.close()