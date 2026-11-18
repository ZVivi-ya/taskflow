from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.user import UserCreate
from app.repositories import user_repository
from app.core.security import (get_password_hash,verify_password,create_access_token)
from app.core.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    InvalidCredentialsError,
)

def register_user(db:Session,payload:UserCreate):
    existing_email=user_repository.get_by_email(db,payload.email)
    if existing_email is not None:
        raise EmailAlreadyExistsError("该邮件已经注册")
    existing_username=user_repository.get_by_name(db,payload.username)
    if existing_username is not None:
        raise UsernameAlreadyExistsError("该用户已经被使用")
    password_hash=get_password_hash(payload.password)
    try:
        user=user_repository.create(
            db,username=payload.username,
            nickname=payload.nickname,
            email=payload.email,
            password_hash=password_hash
        )
        db.commit()
        #重新从数据库加载用户数据
        db.refresh(user)
        return user
    except IntegrityError:
        # 1. 发生数据库约束冲突，先回滚
        db.rollback()

        # 2. 回滚后重新查询，判断具体是哪种唯一约束冲突
        existing_email = user_repository.get_by_email(
            db, payload.email
        )

        if existing_email is not None:
            raise EmailAlreadyExistsError("该邮件已经注册")

        existing_username = user_repository.get_by_name(
            db, payload.username
        )

        if existing_username is not None:
            raise UsernameAlreadyExistsError("该用户已经被使用")

        # 3. 如果不是已知的邮箱或用户名冲突，
        #    就保留原始数据库异常，不要错误地转换
        raise

    except Exception:
        db.rollback()
        raise
    
def login_user(db: Session, email: str, password: str):
    user = user_repository.get_by_email(db, email)

    if user is None:
        raise InvalidCredentialsError("邮箱或密码错误")

    password_is_valid = verify_password(
        password,
        user.password_hash,
    )

    if not password_is_valid:
        raise InvalidCredentialsError("邮箱或密码错误")

    access_token = create_access_token(user.id)

    return {
        "user": user,
        "access_token": access_token,
        "token_type": "bearer",
    }

