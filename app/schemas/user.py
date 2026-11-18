from pydantic import BaseModel,ConfigDict,EmailStr,Field

class UserCreate(BaseModel):
    username:str=Field(min_length=3,max_length=50)
    nickname:str | None=Field(default=None,max_length=30)
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)

'''
from_attributes=True:
它允许 Pydantic 从 Python 对象的属性中读取数据，而不只是从字典读取数据

在output里面加入一个新字段，必须确保SQLAlchemy的User ORM Model中也存在nickname字段
'''
class UserOutput(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    username:str
    nickname:str | None
    email:EmailStr

#定义用户登录时需要提交的数据
class UserLogin(BaseModel):
    email:EmailStr
    password:str

#定义登录成功后服务器返回的数据
class Token(BaseModel):
    access_token:str
    token_type:str="bearer"