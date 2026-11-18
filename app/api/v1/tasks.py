from fastapi import APIRouter,Depends,status,Response
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskUpdate,TaskCreate,TaskOutput
from app.services import task as task_service
from app.schemas.category import CategoryOutput
from app.services import task_category as task_category_service

import logging
logger=logging.getLogger(__name__)

router=APIRouter(prefix="/tasks",tags=["Tasks"],)

#创建任务
@router.post("",response_model=TaskOutput,status_code=status.HTTP_201_CREATED,)
def create_task(payload:TaskCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user),):
    task=task_service.create_task(
        db=db,
        payload=payload,
        owner_id=current_user.id
    )

    logging.info(
        "用户创建任务成功，user_id=%s，task_id=%s",
        current_user.id,
        task.id
    )

    return task

#查询当前用户的任务列表
@router.get("",response_model=list[TaskOutput],)
def get_tasks(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    return task_service.get_tasks(db=db,owner_id=current_user.id,)


#查询指定任务
@router.get("/{task_id}",response_model=TaskOutput)
def get_task(task_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user),):
    return task_service.get_task(db=db,task_id=task_id,owner_id=current_user.id,)
@router.get(
    "/{task_id}/categories",
    response_model=list[CategoryOutput],
)
def get_task_categories(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_category_service.get_task_categories(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
    )

@router.put(
    "/{task_id}/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def add_category_to_task(
    task_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_category_service.add_category_to_task(
        db=db,
        task_id=task_id,
        category_id=category_id,
        owner_id=current_user.id,
    )

    return None

#修改任务
@router.patch("/{task_id}",response_model=TaskOutput,)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.update_task(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
        payload=payload,
    )


# 5. 删除任务
@router.delete("/{task_id}",status_code=status.HTTP_204_NO_CONTENT,)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_service.delete_task(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete(
    "/{task_id}/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_category_from_task(
    task_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task_category_service.remove_category_from_task(
        db=db,
        task_id=task_id,
        category_id=category_id,
        owner_id=current_user.id,
    )

    return None