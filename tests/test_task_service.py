import pytest

from app.services import task as task_service
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.exceptions import TaskNotFoundError


def test_create_task(db_session, test_user):
    task = task_service.create_task(
        db=db_session,
        payload=TaskCreate(
            title="Task Service测试",
            description="测试 Service 层",
            status="todo",
            priority="high",
        ),
        owner_id=test_user["id"],
    )

    assert task.id is not None
    assert task.title == "Task Service测试"
    assert task.owner_id == test_user["id"]


def test_get_tasks(db_session, test_user):
    task_service.create_task(
        db=db_session,
        payload=TaskCreate(
            title="Task列表测试",
            description="测试任务列表",
            priority="high",
        ),
        owner_id=test_user["id"],
    )

    tasks = task_service.get_tasks(
        db=db_session,
        owner_id=test_user["id"],
    )

    assert len(tasks) == 1
    assert tasks[0].title == "Task列表测试"


def test_get_task(db_session, test_user):
    task = task_service.create_task(
        db=db_session,
        payload=TaskCreate(
            title="Task详情测试",
            description="测试单条任务查询",
        ),
        owner_id=test_user["id"],
    )

    found_task = task_service.get_task(
        db=db_session,
        task_id=task.id,
        owner_id=test_user["id"],
    )

    assert found_task.id == task.id
    assert found_task.title == task.title


def test_update_task(db_session, test_user):
    task = task_service.create_task(
        db=db_session,
        payload=TaskCreate(title="修改前"),
        owner_id=test_user["id"],
    )

    updated_task = task_service.update_task(
        db=db_session,
        task_id=task.id,
        owner_id=test_user["id"],
        payload=TaskUpdate(status="done"),
    )

    assert updated_task.status == "done"


def test_delete_task(db_session, test_user):
    task = task_service.create_task(
        db=db_session,
        payload=TaskCreate(title="待删除任务"),
        owner_id=test_user["id"],
    )

    task_service.delete_task(
        db=db_session,
        task_id=task.id,
        owner_id=test_user["id"],
    )

    with pytest.raises(TaskNotFoundError):
        task_service.get_task(
            db=db_session,
            task_id=task.id,
            owner_id=test_user["id"],
        )