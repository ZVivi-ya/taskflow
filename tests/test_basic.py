import pytest


@pytest.fixture
def database():
    print("\n创建数据库连接")

    db = "数据库连接对象"

    yield db

    print("\n关闭数据库连接")


def test_database(database):
    assert database == "数据库连接对象"