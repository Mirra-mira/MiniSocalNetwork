# TODO: Bộ phận Post sẽ định nghĩa schema nhập/xuất tại đây.
from pydantic import BaseModel
from datetime import datetime


class PostCreate(BaseModel):
    content: str


class PostRead(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime