from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import task_category as task_category_repository

from app.core.exceptions import (
    TaskNotFoundError,
    CategoryNotFoundError,
    TaskCategoryLinkNotFoundError,
    TaskCategoryLinkConflictError,
)

def _validate_task_and_category(
    db: Session,
    *,
    task_id: int,
    category_id: int,
    owner_id: int,
) -> None:
    """检查任务和分类是否都属于当前用户。"""

    task = task_category_repository.get_owned_task(
        db,
        task_id=task_id,
        owner_id=owner_id,
    )

    if task is None:
        raise TaskNotFoundError("任务不存在")

    category = task_category_repository.get_owned_category(
        db,
        category_id=category_id,
        owner_id=owner_id,
    )

    if category is None:
        raise CategoryNotFoundError("分类不存在")


def add_category_to_task(
    db: Session,
    *,
    task_id: int,
    category_id: int,
    owner_id: int,
) -> None:
    """为当前用户的任务添加分类。"""

    _validate_task_and_category(
        db,
        task_id=task_id,
        category_id=category_id,
        owner_id=owner_id,
    )

    # 如果关联已经存在，直接返回。
    # PUT 操作具有幂等性，不重复插入关联记录。
    existing_link = task_category_repository.get_link(
        db,
        task_id=task_id,
        category_id=category_id,
    )

    if existing_link is not None:
        return

    try:
        task_category_repository.create_link(
            db,
            task_id=task_id,
            category_id=category_id,
        )

        db.commit()

    except IntegrityError as exc:
        db.rollback()

        raise TaskCategoryLinkConflictError(
            "任务与分类关联冲突"
        ) from exc

    except Exception:
        db.rollback()
        raise


def get_task_categories(
    db: Session,
    *,
    task_id: int,
    owner_id: int,
):
    """查询当前用户任务关联的分类列表。"""

    task = task_category_repository.get_owned_task(
        db,
        task_id=task_id,
        owner_id=owner_id,
    )

    if task is None:
        raise TaskNotFoundError("任务不存在")

    return task_category_repository.get_categories_by_task(
        db,
        task_id=task_id,
        owner_id=owner_id,
    )


def remove_category_from_task(
    db: Session,
    *,
    task_id: int,
    category_id: int,
    owner_id: int,
) -> None:
    """移除当前用户任务上的指定分类。"""

    _validate_task_and_category(
        db,
        task_id=task_id,
        category_id=category_id,
        owner_id=owner_id,
    )

    link = task_category_repository.get_link(
        db,
        task_id=task_id,
        category_id=category_id,
    )

    if link is None:
        raise TaskCategoryLinkNotFoundError("任务与分类的关联不存在")

    try:
        task_category_repository.delete_link(
            db,
            link=link,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise