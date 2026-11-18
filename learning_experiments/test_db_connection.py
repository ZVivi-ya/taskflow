from sqlalchemy import create_engine, text

# 1. 定义数据库地址
DATABASE_URL = "sqlite:///./taskflow.db"

# 2. 创建 Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. 获取数据库连接并执行 SQL
with engine.connect() as connection:

    # 执行一条最简单的 SQL 查询
    result = connection.execute(text("SELECT 1"))

    # 获取查询结果
    value = result.scalar()

    print("数据库连接成功！")
    print("SQL 查询结果：", value)

# 4. with 代码块结束后，连接会被释放回连接池