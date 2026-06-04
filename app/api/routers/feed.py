from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user
from app.core.responses import standard_response
from app.schemas.user import UserRead
from app.services.feed_service import FeedService

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=dict)
async def get_feed(
    current_user: UserRead = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    posts = await FeedService.get_feed(current_user.id, limit, offset)
    return standard_response(
        True,
        [p.dict() for p in posts],
        "News feed",
    )
