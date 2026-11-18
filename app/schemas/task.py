from pydantic import BaseModel,ConfigDict,Field
from datetime import datetime
from typing import Literal

class TaskCreate(BaseModel):
    title:str=Field(min_length=1,max_length=100)
    description:str|None=None
    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: Literal["low", "medium", "high"] = "medium"
    due_at: datetime | None = None

#修改任务时使用
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    status: Literal["todo", "in_progress", "done"] | None = None
    priority: Literal["low", "medium", "high"] | None = None
    due_at: datetime | None = None

#返回任务时使用
'''
from_attributes=True 告诉 Pydantic：
当我把一个对象转换为当前 Schema 时，
可以从这个对象的属性中读取数据，
而不只是从字典中读取数据。
'''
class TaskOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    status: Literal["todo", "in_progress", "done"]
    priority: Literal["low", "medium", "high"]
    due_at: datetime | None
    owner_id: int
    created_at: datetime
    updated_at: datetime