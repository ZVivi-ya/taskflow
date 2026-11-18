from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.category import Category

class TaskCategory(Base):
    __tablename__ = "task_categories"

    __table_args__ = (
        Index(
            "ix_task_categories_category_id",
            "category_id",
        ),
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    )

    task: Mapped["Task"] = relationship(
        back_populates="task_categories",
    )

    category: Mapped["Category"] = relationship(
        back_populates="task_categories",
    )