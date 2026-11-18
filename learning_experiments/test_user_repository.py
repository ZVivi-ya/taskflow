from app.db.session import SessionLocal
from app.repositories.user_repository import(
    create,
    get_by_email,
    get_by_id
)

db=SessionLocal()

try:
    email="repository_demo@example.com"
    user=get_by_email(db,email)
    if user is None:
        user=create(
            db,
            username="respository_demo",
            nickname="res-d",
            email=email,
            password_hash="demo_hash_value"
        )
        db.commit()
        print("用户创建成功！")
    else:
        print("用户已经存在，不重复创建。")

    # 4. 根据邮箱查询
    user = get_by_email(db, email)

    print("\n根据邮箱查询：")
    print("用户 ID：", user.id)
    print("用户名：", user.username)
    print("邮箱：", user.email)

    # 5. 根据 ID 查询
    user_by_id = get_by_id(db, user.id)

    print("\n根据 ID 查询：")
    print("用户名：", user_by_id.username)

except Exception as e:
    db.rollback()
    print("操作失败：", e)

finally:
    db.close()