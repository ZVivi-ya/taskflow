from sqlalchemy import create_engine,event
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.core.config import DATABASE_URL
import time
import logging
'''
sqlite:使用SQLite
///:SQLite相对路径形式
./taskflow.db:当前工作目录下的数据库文件
'''

'''
check_same_thread=False 是 SQLite 在 FastAPI 多线程使用场景下常见的连接参数，
允许 SQLite 连接被不同线程使用
'''

engine=create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False},
    hide_parameters=True,
    echo=True,
)
logger = logging.getLogger("sql.performance")

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(
    conn,
    cursor,
    statement,
    parameters,
    context,
    executemany,
):
    context._query_start_time = time.perf_counter()

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(
    conn,
    cursor,
    statement,
    parameters,
    context,
    executemany,
):
    elapsed = time.perf_counter() - context._query_start_time
    logger.info(
        "[SQL Performance] 耗时：%.4f ms | SQL：%s",
        elapsed * 1000,
        statement,
    )

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
SessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

#get_db()职责是向外提供数据库Session
def get_db():
    db=SessionLocal()
    print("[DEBUG] get_db() 已经被调用")
    print("[DEBUG] 当前 Session 使用的 Engine：", db.get_bind())
    print("[DEBUG] 当前 Engine 的 echo：", db.get_bind().echo)
    try:
        yield db
    finally:
        db.close()