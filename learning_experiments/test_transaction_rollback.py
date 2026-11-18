import uuid

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User
from app.models.task import Task
from app.repositories.task import create_task as create_task_repo


class SimulatedFailure(Exception):
    """用于模拟事务提交前发生异常。"""
    pass


# 1. 创建一个独立的数据库 Session
db = SessionLocal()

try:
    # 2. 找到一个已经注册的用户，作为任务所有者
    owner = db.scalar(select(User).limit(1))

    if owner is None:
        print("测试终止：数据库中没有用户，请先注册一个用户。")
        raise SystemExit

    # 3. 生成一个唯一任务标题，避免和已有数据冲突
    test_title = f"rollback_test_{uuid.uuid4().hex[:8]}"

    task_data = {
        "title": test_title,
        "description": "这是一个事务回滚测试",
        "status": "todo",
        "priority": "medium",
        "due_at": None,
    }

    try:
        # 4. 调用 Repository：添加任务并执行 flush
        task = create_task_repo(
            db=db,
            task_data=task_data,
            owner_id=owner.id,
        )

        print("1. 任务已经 flush，尚未 commit")
        print(f"   任务 ID：{task.id}")
        print(f"   任务标题：{task.title}")

        # 5. 人为制造异常，模拟业务执行过程中发生错误
        raise SimulatedFailure("模拟 commit 前发生异常")

    except SimulatedFailure as exc:
        print(f"2. 捕获模拟异常：{exc}")

        # 6. 回滚当前事务
        db.rollback()
        print("3. 已执行 rollback")

    finally:
        # 7. 关闭当前 Session
        db.close()

    # 8. 创建一个全新的 Session，检查数据库中是否存在这条任务
    check_db = SessionLocal()

    try:
        saved_task = check_db.scalar(
            select(Task).where(Task.title == test_title)
        )

        print(f"4. 新 Session 查询结果：{saved_task}")

        if saved_task is None:
            print("回滚测试通过：未提交的任务不存在。")
        else:
            print("回滚测试失败：任务仍然存在。")

    finally:
        check_db.close()

finally:
    # 如果前面提前退出或发生其他异常，也确保 Session 被关闭
    db.close()