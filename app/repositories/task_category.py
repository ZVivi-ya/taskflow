from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.category import Category
from app.models.task_category import TaskCategory


def get_owned_task(
    db: Session,
    *,
    task_id: int,
    owner_id: int,
) -> Task | None:
    """查询属于指定用户的任务。"""

    statement = select(Task).where(
        Task.id == task_id,
        Task.owner_id == owner_id,
    )

    return db.scalar(statement)


def get_owned_category(
    db: Session,
    *,
    category_id: int,
    owner_id: int,
) -> Category | None:
    """查询属于指定用户的分类。"""

    statement = select(Category).where(
        Category.id == category_id,
        Category.owner_id == owner_id,
    )

    return db.scalar(statement)


def get_link(
    db: Session,
    *,
    task_id: int,
    category_id: int,
) -> TaskCategory | None:
    """查询指定任务和分类之间是否已经存在关联。"""

    statement = select(TaskCategory).where(
        TaskCategory.task_id == task_id,
        TaskCategory.category_id == category_id,
    )

    return db.scalar(statement)


def get_categories_by_task(
    db: Session,
    *,
    task_id: int,
    owner_id: int,
) -> list[Category]:
    """查询任务关联的分类。"""

    statement = (
        select(Category)
        .join(
            TaskCategory,
            TaskCategory.category_id == Category.id,
        )
        .where(
            TaskCategory.task_id == task_id,
            Category.owner_id == owner_id,
        )
        .order_by(Category.id)
    )

    return list(db.scalars(statement).all())


def create_link(
    db: Session,
    *,
    task_id: int,
    category_id: int,
) -> TaskCategory:
    """创建任务与分类之间的关联。"""

    link = TaskCategory(
        task_id=task_id,
        category_id=category_id,
    )

    db.add(link)
    db.flush()

    return link


def delete_link(
    db: Session,
    *,
    link: TaskCategory,
) -> None:
    """删除任务与分类之间的关联。"""

    db.delete(link)
    db.flush()