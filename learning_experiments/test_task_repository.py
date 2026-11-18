from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.task import (
    create_task,
    get_tasks_by_owner,
    get_task_by_id,
    update_task,
    delete_task,
)

db = SessionLocal()

try:
    user = db.query(User).first()

    if user is None:
        print("数据库中还没有用户，请先注册。")

    else:
        # 1. 创建任务
        task = create_task(
            db=db,
            task_data={
                "title": "Repository CRUD 测试",
                "description": "测试创建、查询、修改和删除",
                "status": "todo",
                "priority": "high",
            },
            owner_id=user.id,
        )

        print("1. 创建成功：", task.id, task.title)

        # 2. 查询单条任务
        found_task = get_task_by_id(
            db=db,
            task_id=task.id,
            owner_id=user.id,
        )

        print("2. 查询成功：", found_task.title)

        # 3. 修改任务
        updated_task = update_task(
            db=db,
            task=found_task,
            update_data={
                "status": "done",
            },
        )

        print("3. 修改成功：", updated_task.status)

        # 4. 删除任务
        delete_task(
            db=db,
            task=updated_task,
        )

        print("4. 删除成功")

        # 5. 再次查询，验证删除
        deleted_task = get_task_by_id(
            db=db,
            task_id=task.id,
            owner_id=user.id,
        )

        print("5. 删除后查询结果：", deleted_task)

finally:
    db.close()