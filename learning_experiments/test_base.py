from app.db.base import Base

print("Base 创建成功！")
print("Metadata 对象：", Base.metadata) #输出：Metadata 对象： MetaData()
print("当前登记的数据表：", Base.metadata.tables) #输出：当前登记的数据表： FacadeDict({})