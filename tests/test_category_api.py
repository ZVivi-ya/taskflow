def test_category_crud_endpoints(client, auth_headers):
    created_response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "工作", "description": "工作分类"},
    )

    assert created_response.status_code == 201
    created = created_response.json()
    assert created["name"] == "工作"
    assert created["description"] == "工作分类"
    assert created["owner_id"] > 0
    category_id = created["id"]

    list_response = client.get(
        "/api/v1/categories",
        headers=auth_headers,
    )
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [category_id]

    get_response = client.get(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == category_id

    update_response = client.patch(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
        json={"name": "学习", "description": None},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "学习"
    assert update_response.json()["description"] is None

    delete_response = client.delete(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    assert missing_response.status_code == 404
    assert missing_response.json()["data"]["error_code"] == "CATEGORY_NOT_FOUND"


def test_category_api_request_validation(client, auth_headers):
    missing_name = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"description": "缺少名称"},
    )
    empty_name = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": ""},
    )
    long_name = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "x" * 51},
    )

    assert missing_name.status_code == 422
    assert missing_name.json()["message"] == "Request validation failed"
    assert empty_name.status_code == 422
    assert long_name.status_code == 422


def test_category_api_rejects_duplicate_name(client, auth_headers):
    payload = {"name": "重名分类"}
    first = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json=payload,
    )
    duplicate = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json=payload,
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["data"]["error_code"] == (
        "CATEGORY_NAME_ALREADY_EXISTS"
    )


def test_category_api_update_errors(client, auth_headers):
    created = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "待更新"},
    )
    category_id = created.json()["id"]

    empty_update = client.patch(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
        json={},
    )
    null_name = client.patch(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
        json={"name": None},
    )
    missing_category = client.patch(
        "/api/v1/categories/999999",
        headers=auth_headers,
        json={"description": "不会创建"},
    )

    assert empty_update.status_code == 400
    assert empty_update.json()["data"]["error_code"] == "EMPTY_CATEGORY_UPDATE"
    assert null_name.status_code == 422
    assert null_name.json()["data"]["error_code"] == "INVALID_CATEGORY_UPDATE"
    assert missing_category.status_code == 404


def test_category_api_requires_valid_authentication(client):
    unauthenticated = client.get("/api/v1/categories")
    invalid_token = client.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert unauthenticated.status_code == 401
    assert invalid_token.status_code == 401


def test_user_cannot_read_update_or_delete_another_users_category(
    client,
    auth_headers,
):
    alice_category = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Alice 私有分类"},
    )
    assert alice_category.status_code == 201
    category_id = alice_category.json()["id"]

    bob_registration = client.post(
        "/api/v1/register",
        json={
            "username": "category_bob",
            "nickname": "Bob",
            "email": "category_bob@example.com",
            "password": "password123",
        },
    )
    assert bob_registration.status_code == 201
    bob_login = client.post(
        "/api/v1/login",
        json={
            "email": "category_bob@example.com",
            "password": "password123",
        },
    )
    assert bob_login.status_code == 200
    bob_headers = {
        "Authorization": f"Bearer {bob_login.json()['access_token']}"
    }

    bob_list = client.get("/api/v1/categories", headers=bob_headers)
    bob_get = client.get(
        f"/api/v1/categories/{category_id}",
        headers=bob_headers,
    )
    bob_update = client.patch(
        f"/api/v1/categories/{category_id}",
        headers=bob_headers,
        json={"name": "Bob 修改后的分类"},
    )
    bob_delete = client.delete(
        f"/api/v1/categories/{category_id}",
        headers=bob_headers,
    )

    assert bob_list.status_code == 200
    assert bob_list.json() == []
    assert bob_get.status_code == 404
    assert bob_update.status_code == 404
    assert bob_delete.status_code == 404

    alice_get = client.get(
        f"/api/v1/categories/{category_id}",
        headers=auth_headers,
    )
    assert alice_get.status_code == 200
    assert alice_get.json()["name"] == "Alice 私有分类"
