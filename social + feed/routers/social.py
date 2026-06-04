from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.core.responses import standard_response
from app.schemas.social import CommentCreate
from app.schemas.user import UserRead
from app.services.social_service import SocialService

router = APIRouter(tags=["social"])

@router.post("/posts/{post_id}/like", response_model=dict)
async def toggle_like(
    post_id: int,
    current_user: UserRead = Depends(get_current_user),
):
    """Like hoặc unlike bài viết (toggle)."""
    result = await SocialService.toggle_like(post_id, current_user.id)
    action = "Đã thích" if result.liked else "Đã bỏ thích"
    return standard_response(True, result.dict(), action)


@router.post("/posts/{post_id}/comments", response_model=dict)
async def create_comment(
    post_id: int,
    body: CommentCreate,
    current_user: UserRead = Depends(get_current_user),
):
    comment = await SocialService.create_comment(
        post_id, current_user.id, body, current_user.username
    )
    return standard_response(True, comment.dict(), "Bình luận thành công")


@router.get("/posts/{post_id}/comments", response_model=dict)
async def get_comments(
    post_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    comments = await SocialService.get_comments(post_id, limit, offset)
    return standard_response(True, comments, "Danh sách bình luận")


@router.delete("/comments/{comment_id}", response_model=dict)
async def delete_comment(
    comment_id: int,
    current_user: UserRead = Depends(get_current_user),
):
    await SocialService.delete_comment(comment_id, current_user.id)
    return standard_response(True, None, "Đã xóa bình luận")


@router.post("/users/{user_id}/follow", response_model=dict)
async def follow_user(
    user_id: int,
    current_user: UserRead = Depends(get_current_user),
):

    result = await SocialService.follow_user(current_user.id, user_id)
    return standard_response(True, result.dict(), "Đã follow")


@router.delete("/users/{user_id}/follow", response_model=dict)
async def unfollow_user(
    user_id: int,
    current_user: UserRead = Depends(get_current_user),
):
    result = await SocialService.unfollow_user(current_user.id, user_id)
    return standard_response(True, result.dict(), "Đã unfollow")

@router.get("/users/{user_id}/follow", response_model=dict)
async def get_follow_counts(user_id: int):
    result = await SocialService.get_follow_counts(user_id)
    return standard_response(True, result.dict(), "Thống kê follow")
