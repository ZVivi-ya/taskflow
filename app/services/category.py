'''
Service 是本次分类模块的核心。
它负责：
- 创建分类。
- 查询分类。
- 修改分类。
- 删除分类。
- 检查用户是否有权访问分类。
- 检查更新内容是否合法。
- 管理事务。
- 将数据库唯一约束冲突转换为 HTTP 409。
'''
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories import category as category_repository
from app.schemas.category import CategoryCreate, CategoryUpdate

from app.core.exceptions import (
    CategoryNotFoundError,
    CategoryNameAlreadyExistsError,
    EmptyCategoryUpdateError,
    InvalidCategoryUpdateError,
)


def _is_category_name_conflict(
    db: Session,
    exc: IntegrityError,
    *,
    owner_id: int,
    name: str,
    category_id: int | None = None,
) -> bool:
    if getattr(exc.orig, "sqlite_errorname", None) != "SQLITE_CONSTRAINT_UNIQUE":
        return False

    statement = select(Category.id).where(
        Category.owner_id == owner_id,
        Category.name == name,
    )
    if category_id is not None:
        statement = statement.where(Category.id != category_id)

    return db.scalar(statement) is not None


def create_category(
    db: Session,
    *,
    payload: CategoryCreate,
    owner_id: int,
):
    """创建分类。"""

    try:
        category = category_repository.create(
            db,
            owner_id=owner_id,
            name=payload.name,
            description=payload.description,
        )

        db.commit()
        db.refresh(category)

        return category

    except IntegrityError as exc:
        db.rollback()

        if _is_category_name_conflict(
            db,
            exc,
            owner_id=owner_id,
            name=payload.name,
        ):
            raise CategoryNameAlreadyExistsError(
                "分类名称已存在"
            ) from exc
        raise

    except Exception:
        db.rollback()
        raise


def get_categories(
    db: Session,
    *,
    owner_id: int,
):
    """获取当前用户的分类列表。"""

    return category_repository.get_all(
        db,
        owner_id=owner_id,
    )


def get_category(
    db: Session,
    *,
    category_id: int,
    owner_id: int,
):
    """获取当前用户的指定分类。"""

    category = category_repository.get_by_id(
        db,
        category_id=category_id,
        owner_id=owner_id,
    )

    if category is None:
        raise CategoryNotFoundError("分类不存在")

    return category


def update_category(
    db: Session,
    *,
    category_id: int,
    payload: CategoryUpdate,
    owner_id: int,
):
    """更新当前用户的指定分类。"""

    category = get_category(
        db,
        category_id=category_id,
        owner_id=owner_id,
    )

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise EmptyCategoryUpdateError(
            "至少需要提供一个需要更新的字段"
        )

    if "name" in update_data and update_data["name"] is None:
        raise InvalidCategoryUpdateError(
            "分类名称不能为空"
        )

    try:
        category = category_repository.update(
            db,
            category=category,
            update_data=update_data,
        )

        db.commit()
        db.refresh(category)

        return category

    except IntegrityError as exc:
        db.rollback()

        name = update_data.get("name")
        if isinstance(name, str) and _is_category_name_conflict(
            db,
            exc,
            owner_id=owner_id,
            name=name,
            category_id=category_id,
        ):
            raise CategoryNameAlreadyExistsError(
                "分类名称已存在"
            ) from exc
        raise

    except Exception:
        db.rollback()
        raise


def delete_category(
    db: Session,
    *,
    category_id: int,
    owner_id: int,
) -> None:
    """删除当前用户的指定分类。"""

    category = get_category(
        db,
        category_id=category_id,
        owner_id=owner_id,
    )

    try:
        category_repository.delete(
            db,
            category=category,
        )

        db.commit()

    except Exception:
        db.rollback()
        raise