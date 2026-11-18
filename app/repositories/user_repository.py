from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User

# 根据Emial获取用户
def get_by_email(db:Session,email:str)->User | None:
    statement=select(User).where(User.email==email)
    user=db.scalar(statement) #scalar执行查询语句
    return user

# 根据ID获取用户
def get_by_id(db:Session,user_id:int)->User | None:
    statement=select(User).where(User.id==user_id)
    user=db.scalar(statement)
    return user

#根据username获取用户
def get_by_name(db:Session,username:str)->User|None:
    statement=select(User).where(User.username==username)
    user=db.scalar(statement)
    return user

# 实现创建用户
def create(db:Session,username:str,email:str,password_hash:str,nickname:str | None=None)->User:
    user=User(
        username=username,
        nickname=nickname,
        email=email,
        password_hash=password_hash
    )
    db.add(user)
    db.flush()
    return user

# 实现更新用户表
def update_nickname(db:Session,user:User,nickname:str|None)->User:
    user.nickname=nickname
    db.flush()
    return user

#删除用户表中数据
def delete(db:Session,user:User)->None:
    db.delete(user)
    db.flush()