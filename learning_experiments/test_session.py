from app.db.session import engine,SessionLocal

db=SessionLocal()

print("Engine:",engine)
print("Session:",db)

#close Session
db.close()

print("Session 已关闭")