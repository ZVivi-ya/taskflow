from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.task import Task

def create_task(db: Session, task_data: dict, owner_id: int) -> Task:
    task = Task(**task_data, owner_id=owner_id)
    db.add(task)
    db.flush()
    return task

# 查询当前用户的所有任务
def get_tasks_by_owner(db:Session,owner_id:int,)->list[Task]:
    statement=(
        select(Task)
        .where(Task.owner_id==owner_id)
        .order_by(Task.created_at.desc())
    )
    return list(db.scalars(statement).all())

# 根据任务 ID 查询当前用户的任务
def get_task_by_id(db: Session,task_id: int,owner_id: int,) -> Task | None:
    statement = select(Task).where(
        Task.id == task_id,
        Task.owner_id == owner_id,
    )
    return db.scalars(statement).first()

# 修改任务
def update_task(
    db: Session,
    task: Task,
    update_data: dict,
) -> Task:
    for key, value in update_data.items():
        setattr(task, key, value)

    db.flush()
    return task

# 删除任务
def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.flush()