from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
import jwt

from app.db.session import get_db
from app.core.security import decode_access_token
from app.repositories import user_repository

bearer_scheme=HTTPBearer() # 告诉FastAPI：这个接口使用Bearer Token认证，客户端需要在请求头中携带Token

'''
把客户端提交的Token转换成一个真正的数据库用户对象步骤：
1.HTTPBearer提取Token
2.decode_access_token()验证Token
3.读取sub，得到用户ID
4.Repository查询数据库
5.返回User ORM对象
'''
def get_current_user(
    credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme),
    db:Session=Depends(get_db)
):
    token=credentials.credentials
    try:
        payload=decode_access_token(token)
        user_id=int(payload["sub"])
    except(jwt.InvalidTokenError,KeyError,TypeError,ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的 Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user=user_repository.get_by_id(db,user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate":"Bearer"}
        )
    return user