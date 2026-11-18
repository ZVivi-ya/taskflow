from pwdlib import PasswordHash
from datetime import datetime,timedelta,timezone
import jwt
from app.core.config import JWT_SECRET_KEY, JWT_SECRET_MINUTES
password_hash=PasswordHash.recommended()
def get_password_hash(password:str)->str:
    return password_hash.hash(password)

'''
plain_password：用户本次输入的原始密码。
hashed_password：数据库中存储的密码哈希。
'''
def verify_password(plain_password:str,hashed_password:str)->bool:
    return password_hash.verify(plain_password,hashed_password)

'''
以下是JWT签发函数
'''
def create_access_token(user_id:int)->str:
    '''为用户生成JWT访问令牌'''
    now=datetime.now(timezone.utc) #获取当前UTC时间
    '''
    sub:Subject，令牌代表的主体，这里是用户 ID
    iat:Issued At，签发时间
    exp:Expiration Time，过期时间
    '''
    payload={
        "sub":str(user_id),
        "iat":now,
        "exp":now+timedelta(minutes=JWT_SECRET_MINUTES)
    }

    #PyJWT根据Payload、密钥和算法生成Token
    token=jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256"
    )
    return token

def decode_access_token(token:str)->dict:
    payload=jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=["HS256"]
    )
    return payload