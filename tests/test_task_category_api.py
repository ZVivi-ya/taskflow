def _create_task(client, headers, title="关联测试任务"):
    response = client.post(
        "/api/v1/tasks",
        headers=headers,
        json={"title": title},
    )
    assert response.status_code == 201
    return response.json()


def _create_category(client, headers, name="关联测试分类"):
    response = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()


def _register_and_login(client, *, username, email):
    registration = client.post(
        "/api/v1/register",
        json={
            "username": username,
            "nickname": username,
            "email": email,
            "password": "password123",
        },
    )
    assert registration.status_code == 201

    login = client.post(
        "/api/v1/login",
        json={"email": email, "password": "password123"},
    )
    assert login.status_code == 200
    return {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }


def test_add_and_list_task_categories(client, auth_headers):
    task = _create_task(client, auth_headers)
    first_category = _create_category(client, auth_headers, "优先")
    second_category = _create_category(client, auth_headers, "工作")

    add_first = client.put(
        f"/api/v1/tasks/{task['id']}/categories/{first_category['id']}",
        headers=auth_headers,
    )
    add_second = client.put(
        f"/api/v1/tasks/{task['id']}/categories/{second_category['id']}",
        headers=auth_headers,
    )

    assert add_first.status_code == 204
    assert add_first.content == b""
    assert add_second.status_code == 204

    listed = client.get(
        f"/api/v1/tasks/{task['id']}/categories",
        headers=auth_headers,
    )
    assert listed.status_code == 200
    assert [category["id"] for category in listed.json()] == [
        first_category["id"],
        second_category["id"],
    ]


def test_repeated_add_is_idempotent(client, auth_headers):
    task = _create_task(client, auth_headers)
    category = _create_category(client, auth_headers)
    url = f"/api/v1/tasks/{task['id']}/categories/{category['id']}"

    first_add = client.put(url, headers=auth_headers)
    repeated_add = client.put(url, headers=auth_headers)

    assert first_add.status_code == 204
    assert repeated_add.status_code == 204

    listed = client.get(
        f"/api/v1/tasks/{task['id']}/categories",
        headers=auth_headers,
    )
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [category["id"]]


def test_remove_task_category_and_reject_second_remove(
    client,
    auth_headers,
):
    task = _create_task(client, auth_headers)
    category = _create_category(client, auth_headers)
    association_url = (
        f"/api/v1/tasks/{task['id']}/categories/{category['id']}"
    )
    client.put(association_url, headers=auth_headers)

    removed = client.delete(association_url, headers=auth_headers)
    listed = client.get(
        f"/api/v1/tasks/{task['id']}/categories",
        headers=auth_headers,
    )
    removed_again = client.delete(association_url, headers=auth_headers)

    assert removed.status_code == 204
    assert removed.content == b""
    assert listed.status_code == 200
    assert listed.json() == []
    assert removed_again.status_code == 404
    assert removed_again.json()["data"]["error_code"] == (
        "TASK_CATEGORY_LINK_NOT_FOUND"
    )


def test_task_category_routes_return_404_for_missing_task(
    client,
    auth_headers,
):
    category = _create_category(client, auth_headers)

    get_categories = client.get(
        "/api/v1/tasks/999999/categories",
        headers=auth_headers,
    )
    add_category = client.put(
        f"/api/v1/tasks/999999/categories/{category['id']}",
        headers=auth_headers,
    )
    remove_category = client.delete(
        f"/api/v1/tasks/999999/categories/{category['id']}",
        headers=auth_headers,
    )

    for response in (get_categories, add_category, remove_category):
        assert response.status_code == 404
        assert response.json()["data"]["error_code"] == "TASK_NOT_FOUND"


def test_task_category_routes_return_404_for_missing_category(
    client,
    auth_headers,
):
    task = _create_task(client, auth_headers)

    add_category = client.put(
        f"/api/v1/tasks/{task['id']}/categories/999999",
        headers=auth_headers,
    )
    remove_category = client.delete(
        f"/api/v1/tasks/{task['id']}/categories/999999",
        headers=auth_headers,
    )

    for response in (add_category, remove_category):
        assert response.status_code == 404
        assert response.json()["data"]["error_code"] == "CATEGORY_NOT_FOUND"


def test_users_cannot_link_tasks_or_categories_owned_by_others(
    client,
    auth_headers,
):
    # 关联两端必须都属于当前用户；分别验证任务和分类的归属检查。
    alice_task = _create_task(client, auth_headers, "Alice 的任务")
    alice_category = _create_category(client, auth_headers, "Alice 的分类")
    bob_headers = _register_and_login(
        client,
        username="task_category_bob",
        email="task_category_bob@example.com",
    )
    bob_task = _create_task(client, bob_headers, "Bob 的任务")
    bob_category = _create_category(client, bob_headers, "Bob 的分类")

    bob_uses_alice_task = client.put(
        f"/api/v1/tasks/{alice_task['id']}/categories/{bob_category['id']}",
        headers=bob_headers,
    )
    bob_uses_alice_category = client.put(
        f"/api/v1/tasks/{bob_task['id']}/categories/{alice_category['id']}",
        headers=bob_headers,
    )
    bob_reads_alice_task_categories = client.get(
        f"/api/v1/tasks/{alice_task['id']}/categories",
        headers=bob_headers,
    )
    alice_uses_bob_category = client.put(
        f"/api/v1/tasks/{alice_task['id']}/categories/{bob_category['id']}",
        headers=auth_headers,
    )

    for response in (
        bob_uses_alice_task,
        bob_uses_alice_category,
        bob_reads_alice_task_categories,
        alice_uses_bob_category,
    ):
        assert response.status_code == 404

    # 前述越权请求不得造成关联记录，合法所有者仍可正常关联。
    alice_categories = client.get(
        f"/api/v1/tasks/{alice_task['id']}/categories",
        headers=auth_headers,
    )
    bob_categories = client.get(
        f"/api/v1/tasks/{bob_task['id']}/categories",
        headers=bob_headers,
    )
    assert alice_categories.status_code == 200
    assert alice_categories.json() == []
    assert bob_categories.status_code == 200
    assert bob_categories.json() == []

    valid_bob_link = client.put(
        f"/api/v1/tasks/{bob_task['id']}/categories/{bob_category['id']}",
        headers=bob_headers,
    )
    assert valid_bob_link.status_code == 204
    assert client.get(
        f"/api/v1/tasks/{bob_task['id']}/categories",
        headers=bob_headers,
    ).json()[0]["id"] == bob_category["id"]
