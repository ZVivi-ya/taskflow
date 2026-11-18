import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserOutput


def test_user_create_valid_data():
    payload = UserCreate(
        username="alice",
        nickname=None,
        email="alice@example.com",
        password="12345678",
    )

    assert payload.username == "alice"
    assert payload.email == "alice@example.com"


def test_user_create_invalid_data():
    with pytest.raises(ValidationError):
        UserCreate(
            username="ab",
            email="not-an-email",
            password="123",
        )


def test_user_output_from_orm_object():
    class FakeUser:
        id = 1
        username = "alice"
        nickname = None
        email = "alice@example.com"
        password_hash = "some_hash"

    user_output = UserOutput.model_validate(FakeUser())

    assert user_output.id == 1
    assert user_output.username == "alice"
    assert user_output.nickname is None
    assert user_output.email == "alice@example.com"

    # 确认密码哈希没有出现在响应数据中
    assert "password_hash" not in user_output.model_dump()