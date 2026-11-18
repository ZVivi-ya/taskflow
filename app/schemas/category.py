from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """创建分类时的请求数据。"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="分类名称",
    )

    description: str | None = Field(
        default=None,
        description="分类描述",
    )


class CategoryUpdate(BaseModel):
    """更新分类时的请求数据。"""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="分类名称",
    )

    description: str | None = Field(
        default=None,
        description="分类描述",
    )


class CategoryOutput(BaseModel):
    """分类接口的响应数据。"""

    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)