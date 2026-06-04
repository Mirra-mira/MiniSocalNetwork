from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FriendRead(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class FriendRequestRead(BaseModel):
    id: int
    sender_id: int
    sender_username: str
    sender_display_name: Optional[str] = None
    created_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class MessageRead(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime
