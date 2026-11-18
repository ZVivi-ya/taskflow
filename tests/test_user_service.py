from app.schemas.user import UserCreate
from app.services.user_service import login_user, register_user


def test_register_and_login_user(db_session):
    payload = UserCreate(
        username="service_demo",
        nickname="Service Demo",
        email="service_demo@example.com",
        password="password123",
    )

    user = register_user(db_session, payload)
    login_result = login_user(
        db_session,
        email=payload.email,
        password=payload.password,
    )

    assert user.id is not None
    assert user.username == payload.username
    assert login_result["user"].id == user.id
    assert login_result["access_token"]
    assert login_result["token_type"] == "bearer"
