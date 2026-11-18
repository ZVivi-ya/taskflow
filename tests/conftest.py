import pytest

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models import User, Task, Category, TaskCategory


@pytest.fixture
def test_engine(tmp_path):
    """
    为当前测试创建独立的 SQLite 数据库。
    tmp_path 是 Pytest 提供的临时目录。
    """

    database_file = tmp_path / "test_taskflow.db"

    test_database_url = f"sqlite:///{database_file.as_posix()}"

    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )

    # 测试数据库也必须启用 SQLite 外键约束
    @event.listens_for(engine, "connect")
    def enable_test_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # 创建测试数据库中的所有业务表
    Base.metadata.create_all(bind=engine)

    yield engine

    # 测试结束后释放数据库连接
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """
    提供直接访问测试数据库的 Session。
    主要用于测试数据准备和结果验证。
    """

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_engine):
    """
    创建 TestClient，并将 FastAPI 的 get_db
    替换为使用测试数据库的版本。
    """

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    # 保存原有依赖覆盖配置，避免影响其他测试或应用状态
    original_overrides = app.dependency_overrides.copy()

    # 替换数据库依赖
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # 恢复原有依赖覆盖配置
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)

@pytest.fixture
def test_user(client):
    """
    通过注册接口创建一个测试用户。
    """
    user_data = {
        "username": "alice_test",
        "nickname": "Alice",
        "email": "alice_test@example.com",
        "password": "password123",
    }

    response = client.post(
        "/api/v1/register",
        json=user_data,
    )

    assert response.status_code == 201

    # 返回用户信息，同时保留登录需要的密码
    return {
        **response.json(),
        "password": user_data["password"],
    }


@pytest.fixture
def auth_headers(client, test_user):
    """
    使用测试用户登录，取得 JWT。
    后续测试通过 Authorization 请求头携带 Token。
    """
    response = client.post(
        "/api/v1/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def category_owners(db_session):
    owners = (
        User(
            username="category_owner_a",
            nickname="Owner A",
            email="category_owner_a@example.com",
            password_hash="test-hash-a",
        ),
        User(
            username="category_owner_b",
            nickname="Owner B",
            email="category_owner_b@example.com",
            password_hash="test-hash-b",
        ),
    )
    db_session.add_all(owners)
    db_session.flush()
    return owners