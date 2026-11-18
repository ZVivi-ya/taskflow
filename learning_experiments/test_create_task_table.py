from app.db.base import Base
from app.db.session import engine

from app.models.user import User
from app.models.task import Task

Base.metadata.create_all(bind=engine)
print("数据表创建完成")