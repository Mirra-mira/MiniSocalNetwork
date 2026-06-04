# Pydantic schemas cho module Social & Feed (Người 3)
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    username: str
    content: str
    created_at: datetime


class LikeRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime


class LikeStatus(BaseModel):
    liked: bool
    total_likes: int


class FollowStatus(BaseModel):
    following: bool


class FollowCount(BaseModel):
    user_id: int
    followers: int
    following: int

class FeedPostRead(BaseModel):
    id: int
    user_id: int
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    content: str
    created_at: datetime
    like_count: int
    comment_count: int
    user_liked: bool = False
