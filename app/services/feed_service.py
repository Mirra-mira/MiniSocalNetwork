# Service tầng Business cho module Feed (Người 3)
# Xây dựng news feed từ bài viết của những người user follow.
from app.repositories.social_repo import SocialRepository
from app.schemas.social import FeedPostRead


class FeedService:
    """Business logic cho News Feed."""

    @staticmethod
    async def get_feed(
        user_id: int, limit: int = 20, offset: int = 0
    ) -> list[FeedPostRead]:
        """Lấy bài đăng của những người mà user đang follow,
        sắp xếp theo thời gian mới nhất (newest first)."""
        rows = await SocialRepository.get_feed_posts(user_id, limit, offset)
        return [
            FeedPostRead(
                id=r["id"],
                user_id=r["user_id"],
                username=r["username"],
                display_name=r["display_name"],
                avatar_url=r["avatar_url"],
                content=r["content"],
                created_at=r["created_at"],
                like_count=r["like_count"],
                comment_count=r["comment_count"],
                user_liked=r["user_liked"],
            )
            for r in rows
        ]
