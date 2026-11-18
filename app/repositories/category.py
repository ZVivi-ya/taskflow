from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def create(
    db: Session,
    *,
    owner_id: int,
    name: str,
    description: str | None = None,
) -> Category:
    """创建分类对象。"""

    category = Category(
        owner_id=owner_id,
        name=name,
        description=description,
    )

    db.add(category)
    db.flush()

    return category


def get_by_id(
    db: Session,
    *,
    category_id: int,
    owner_id: int,
) -> Category | None:
    """根据分类 ID 和用户 ID 查询分类。"""

    statement = select(Category).where(
        Category.id == category_id,
        Category.owner_id == owner_id,
    )

    return db.scalar(statement)


def get_all(
    db: Session,
    *,
    owner_id: int,
) -> list[Category]:
    """查询当前用户的全部分类。"""

    statement = (
        select(Category)
        .where(Category.owner_id == owner_id)
        .order_by(Category.created_at.desc(), Category.id.desc())
    )

    return list(db.scalars(statement).all())


def update(
    db: Session,
    *,
    category: Category,
    update_data: dict,
) -> Category:
    """更新分类对象。"""

    for field, value in update_data.items():
        setattr(category, field, value)

    db.flush()

    return category


def delete(
    db: Session,
    *,
    category: Category,
) -> None:
    """删除分类对象。"""

    db.delete(category)
    db.flush()