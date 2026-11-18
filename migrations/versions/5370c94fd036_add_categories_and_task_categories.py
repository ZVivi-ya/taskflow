"""add categories and task categories

Revision ID: 5370c94fd036
Revises:
Create Date: 2026-11-03 10:10:14.553780

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.db.base import Base


# revision identifiers, used by Alembic.
revision: str = "5370c94fd036"
down_revision: Union[str, Sequence[str], None] = "20261104"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. 修改 tasks 表的 owner_id 外键。
    # 原来的 SQLite 外键没有名称，因此通过命名约定
    # 为反射得到的外键生成名称。
    with op.batch_alter_table(
        "tasks",
        naming_convention=Base.metadata.naming_convention,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_tasks_owner_id_users",
            type_="foreignkey",
        )

        batch_op.create_foreign_key(
            "fk_tasks_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # 2. 创建 categories 表。
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name="fk_categories_owner_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_categories",
        ),
        sa.UniqueConstraint(
            "owner_id",
            "name",
            name="uq_categories_owner_name",
        ),
    )

    # 3. 创建 task_categories 关联表。
    op.create_table(
        "task_categories",
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name="fk_task_categories_category_id_categories",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name="fk_task_categories_task_id_tasks",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "task_id",
            "category_id",
            name="pk_task_categories",
        ),
    )

    # 4. 创建 category_id 索引。
    op.create_index(
        "ix_task_categories_category_id",
        "task_categories",
        ["category_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 1. 先删除关联表，解除它对 tasks 和 categories 的引用。
    op.drop_table("task_categories")

    # 2. 删除分类表。
    op.drop_table("categories")

    # 3. 将 tasks 的外键恢复为原来的 NO ACTION。
    with op.batch_alter_table(
        "tasks",
        naming_convention=Base.metadata.naming_convention,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_tasks_owner_id_users",
            type_="foreignkey",
        )

        batch_op.create_foreign_key(
            "fk_tasks_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="NO ACTION",
        )