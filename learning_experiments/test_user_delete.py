from app.db.session import SessionLocal
from app.repositories.user_repository import(
    get_by_email,
    delete
)

db=SessionLocal()

try:
    email="repository_demo@example.com"
    user=get_by_email(db,email)

    if user is None:
        print("用户不存在，无需删除。")
    else:
        print("准备删除用户：", user.username)
        delete(db,user)
        db.commit()
        print("用户删除成功！")
        # 再次查询，验证是否删除
        deleted_user = get_by_email(db, email)
        print("删除后查询结果：", deleted_user)
except Exception as e:
    db.rollback()
    print("删除失败：", e)