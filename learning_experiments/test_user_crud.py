from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User


db = SessionLocal()

try:
    # =========================
    # 1. Create：创建用户
    # =========================
    user = User(
        username="crud_full_demo",
        email="crud_full_demo@example.com",
        password_hash="demo_hash"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print("\n===== CREATE =====")
    print("用户 ID：", user.id)
    print("用户名：", user.username)

    # =========================
    # 2. Read：查询用户
    # =========================
    user = db.scalar(
        select(User).where(
            User.username == "crud_full_demo"
        )
    )

    print("\n===== READ =====")

    if user:
        print("查询成功：", user.username)
        print("邮箱：", user.email)

    # =========================
    # 3. Update：修改用户
    # =========================

    if user:
        user.email = "updated@example.com"

        db.commit()
        db.refresh(user)

        print("\n===== UPDATE =====")
        print("修改后的邮箱：", user.email)

    # =========================
    # 4. Delete：删除用户
    # =========================
    if user:
        db.delete(user)
        db.commit()

        print("\n===== DELETE =====")
        print("用户删除成功")

    # =========================
    # 5. 验证删除结果
    # =========================
    result = db.scalar(
        select(User).where(
            User.username == "crud_full_demo"
        )
    )

    print("\n===== VERIFY =====")
    print("删除后查询结果：", result)

except Exception as e:
    db.rollback()
    print("数据库操作发生异常：", e)

finally:
    db.close()
    print("\nSession 已关闭")