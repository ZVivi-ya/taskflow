#任务模块测试会覆盖 CRUD 和用户数据隔离

def test_create_task(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "学习 Pytest",
            "description": "完成 TaskFlow 自动化测试",
            "status": "todo",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "学习 Pytest"
    assert data["description"] == "完成 TaskFlow 自动化测试"
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert "id" in data
    assert "owner_id" in data


def test_get_tasks(client, auth_headers):
    # 先创建一条任务
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "测试任务列表",
        },
    )

    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "测试任务列表"


def test_get_task(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "测试任务详情",
        },
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "测试任务详情"


def test_update_task(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "修改前的任务",
        },
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={
            "title": "修改后的任务",
            "status": "in_progress",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "修改后的任务"
    assert data["status"] == "in_progress"


def test_delete_task(client, auth_headers):
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "准备删除的任务",
        },
    )

    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    # 删除后再次查询，应该找不到
    get_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
    )

    assert get_response.status_code == 404


def test_task_access_requires_login(client):
    response = client.get("/api/v1/tasks")

    assert response.status_code == 401


def test_user_cannot_access_another_users_task(
    client,
    auth_headers,
):
    # 用户 Alice 创建任务
    create_response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Alice 的私人任务",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    # 注册另一个用户 Bob
    register_response = client.post(
        "/api/v1/register",
        json={
            "username": "bob_test",
            "nickname": "Bob",
            "email": "bob_test@example.com",
            "password": "password123",
        },
    )

    assert register_response.status_code == 201

    # Bob 登录
    login_response = client.post(
        "/api/v1/login",
        json={
            "email": "bob_test@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    bob_headers = {
        "Authorization": (
            f"Bearer {login_response.json()['access_token']}"
        )
    }

    # Bob 尝试查询 Alice 的任务
    get_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers=bob_headers,
    )

    assert get_response.status_code == 404

    # Bob 尝试修改 Alice 的任务
    update_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=bob_headers,
        json={
            "title": "Bob 尝试修改 Alice 的任务",
        },
    )

    assert update_response.status_code == 404

    # Bob 尝试删除 Alice 的任务
    delete_response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers=bob_headers,
    )

    assert delete_response.status_code == 404