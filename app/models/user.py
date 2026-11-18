from sqlalchemy import String
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.category import Category
class User(Base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(primary_key=True)
    #用户名：字符串，最多 50 个字符，不能重复
    username:Mapped[str]=mapped_column(String(50),unique=True,nullable=False)
    #新字段，且它在数据库可空的
    nickname:Mapped[str | None]=mapped_column(String(30),nullable=True)
    #邮箱：字符串，最多 100 个字符，不能重复
    email:Mapped[str]=mapped_column(String(100),unique=True,nullable=False)
    #密码哈希值：不能为 NULL
    password_hash:Mapped[str]=mapped_column(String(255),nullable=False)
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    categories: Mapped[list["Category"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )