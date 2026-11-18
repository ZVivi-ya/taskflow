#专门测试用户模块 

def test_register_user(client):
    response = client.post(
        "/api/v1/register",
        json={
            "username": "bob_test",
            "nickname": "Bob",
            "email": "bob_test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "bob_test"
    assert data["nickname"] == "Bob"
    assert data["email"] == "bob_test@example.com"

    # 不应该把密码返回给客户端
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_user(client, test_user):
    response = client.post(
        "/api/v1/register",
        json={
            "username": test_user["username"],
            "nickname": "Another Alice",
            "email": test_user["email"],
            "password": "password123",
        },
    )

    assert response.status_code == 409


def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/login",
        json={
            "email": test_user["email"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == 401


def test_get_me(client, auth_headers, test_user):
    response = client.get(
        "/api/v1/me",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_user["id"]
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]


def test_get_me_without_token(client):
    response = client.get("/api/v1/me")

    # HTTPBearer 默认会在缺少认证凭据时拒绝请求
    assert response.status_code == 401


def test_get_me_with_invalid_token(client):
    response = client.get(
        "/api/v1/me",
        headers={
            "Authorization": "Bearer invalid.token.value"
        },
    )

    assert response.status_code == 401