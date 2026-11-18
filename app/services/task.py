'''
实现五个业务函数：
create_task：创建任务，并自动绑定当前用户
get_tasks：获取当前用户的任务列表
get_task：获取指定任务，并检查归属	
update_task：检查权限后修改任务
delete_task：检查权限后删除任务
'''

from sqlalchemy.orm import Session

from app.schemas.task import TaskCreate,TaskUpdate
from app.repositories.task import (
    create_task as create_task_repo,
    get_tasks_by_owner,
    get_task_by_id as get_task_by_id_repo,
    update_task as update_task_repo,
    delete_task as delete_task_repo
)
from app.core.exceptions import (
    TaskNotFoundError,
    InvalidTaskUpdateError,
    EmptyTaskUpdateError,
)

#创建任务
def create_task(
    db: Session,
    payload: TaskCreate,
    owner_id: int,
):
    try:
        # 1. 将 Pydantic Schema 转换成字典
        task_data = payload.model_dump()

        # 2. 调用 Repository 创建任务
        task = create_task_repo(
            db=db,
            task_data=task_data,
            owner_id=owner_id,
        )

        # 3. 提交事务
        db.commit()

        # 4. 重新从数据库加载对象
        db.refresh(task)

        # 5. 返回任务对象
        return task

    except Exception:
        # 发生异常，回滚当前事务
        db.rollback()
        raise

#获取当前用户的所有任务
def get_tasks(db:Session,owner_id:int):
    return get_tasks_by_owner(
        db=db,
        owner_id=owner_id
    )

#获取指定任务
def get_task(db:Session,task_id:int,owner_id:int):
    task=get_task_by_id_repo(
        db=db,
        task_id=task_id,
        owner_id=owner_id
    )

    '''
    原函数这里要处理两个任务
    1.判断任务是否存在
    2.负责决定HTTP应该返回404
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found"
        )

    为了将业务逻辑和Web框架解耦（分离）
    Service依赖业务规则
    FastAPI异常处理器依赖HTTP规则
    '''
    if task is None:
        raise TaskNotFoundError("Task not found")
    return task

#修改任务
def update_task(
    db: Session,
    task_id: int,
    owner_id: int,
    payload: TaskUpdate,
):
    try:
        # 1. 查询任务，并检查当前用户是否有权操作
        task = get_task(
            db=db,
            task_id=task_id,
            owner_id=owner_id,
        )

        # 2. 只提取客户端实际提交的字段
        update_data = payload.model_dump(exclude_unset=True)

        # 3. 检查不允许为 null 的字段
        for field in ("title", "status", "priority"):
            if field in update_data and update_data[field] is None:
                raise InvalidTaskUpdateError(
                    f"{field} cannot be null"
                )

        # 4. 检查是否为空更新
        if not update_data:
            raise EmptyTaskUpdateError(
                "No fields provided for update"
            )

        # 5. 调用 Repository 更新任务
        task = update_task_repo(
            db=db,
            task=task,
            update_data=update_data,
        )

        # 6. 提交事务
        db.commit()

        # 7. 刷新对象
        db.refresh(task)

        return task

    except Exception:
        db.rollback()
        raise

#删除任务
def delete_task(
    db: Session,
    task_id: int,
    owner_id: int,
):
    try:
        # 1. 查询任务并检查归属
        task = get_task(
            db=db,
            task_id=task_id,
            owner_id=owner_id,
        )

        # 2. 调用 Repository 删除任务
        delete_task_repo(
            db=db,
            task=task,
        )

        # 3. 提交事务
        db.commit()

    except Exception:
        # 4. 发生异常，回滚事务
        db.rollback()
        raise