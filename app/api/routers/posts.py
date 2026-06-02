from fastapi import APIRouter
from fastapi import Depends

from app.api.deps import get_current_user
from app.schemas.user import UserRead
from app.schemas.post import PostCreate
from app.services.post_service import PostService

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.post("")
async def create_post(
    request: PostCreate,
    current_user: UserRead = Depends(
        get_current_user
    )
):

    return await PostService.create_post(
        current_user.id,
        request.content
    )


@router.get("/{post_id}")
async def get_post(
    post_id: int
):

    return await PostService.get_post(
        post_id
    )


@router.delete("/{post_id}")
async def delete_post(
    post_id: int
):

    return await PostService.delete_post(
        post_id
    )
