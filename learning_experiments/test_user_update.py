from app.db.session import SessionLocal
from app.repositories.user_repository import(
    get_by_email,
    update_nickname
)
db=SessionLocal()
try:
    email="repository_demo@example.com"

    #查询用户
    user=get_by_email(db,email)

    if user is None:
        print("用户不存在")
    else:
        print("修改前昵称：",user.nickname)

        update_nickname(
            db,
            user,
            "Vivi"
        )

        db.commit()

        print("修改后昵称：", user.nickname)

        #再次查询，验证数据库中的数据
        '''
        db.expire_all()
        它会让当前Session中已经加载的ORM对象属性过期
        下一次读取属性时，SQLAlchemy会重新从数据库加载数据。
        '''
        db.expire_all()
        user=get_by_email(db,email)
        print("重新查询的昵称：", user.nickname)
except Exception as e:
    db.rollback()
    print("更新失败：",e)
finally:
    db.close()