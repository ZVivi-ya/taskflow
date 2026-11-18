from app.db.base import Base
from app.db.session import engine
from app.models.user import User

Base.metadata.create_all(bind=engine)#create_all()，SQLAlchemy根据Metadata中的表结构生成建表SQL
print("数据库表创建完成！")
print("当前登记的数据表：", Base.metadata.tables.keys())
