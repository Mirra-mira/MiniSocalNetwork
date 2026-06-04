from app.core.exceptions import AppException
from app.repositories.social_repo import SocialRepository
from app.repositories.post_repo import PostRepository
from app.schemas.social import (
    CommentCreate,
    CommentRead,
    FollowCount,
    FollowStatus,
    LikeStatus,
)


class SocialService:

    @staticmethod
    async def toggle_like(post_id: int, user_id: int) -> LikeStatus:
        post = await PostRepository.get_post_by_id(post_id)
        if post is None:
            raise AppException(status_code=404, detail="Bài viết không tồn tại")

        existing = await SocialRepository.get_like(post_id, user_id)
        if existing is not None:
            await SocialRepository.remove_like(post_id, user_id)
            liked = False
        else:
            await SocialRepository.add_like(post_id, user_id)
            liked = True

        total = await SocialRepository.count_likes(post_id)
        return LikeStatus(liked=liked, total_likes=total)


    @staticmethod
    async def create_comment(
        post_id: int, user_id: int, data: CommentCreate, username: str
    ) -> CommentRead:
        post = await PostRepository.get_post_by_id(post_id)
        if post is None:
            raise AppException(status_code=404, detail="Bài viết không tồn tại")

        record = await SocialRepository.create_comment(
            post_id, user_id, data.content
        )
        return CommentRead(
            id=record["id"],
            post_id=record["post_id"],
            user_id=record["user_id"],
            username=username,
            content=record["content"],
            created_at=record["created_at"],
        )

    @staticmethod
    async def get_comments(post_id: int, limit: int = 50, offset: int = 0):
        post = await PostRepository.get_post_by_id(post_id)
        if post is None:
            raise AppException(status_code=404, detail="Bài viết không tồn tại")

        rows = await SocialRepository.get_comments_by_post(post_id, limit, offset)
        return [dict(r) for r in rows]

    @staticmethod
    async def delete_comment(comment_id: int, user_id: int) -> None:
        result = await SocialRepository.delete_comment(comment_id, user_id)
        if result == "DELETE 0":
            raise AppException(
                status_code=404,
                detail="Bình luận không tồn tại hoặc bạn không có quyền xóa",
            )


    @staticmethod
    async def follow_user(follower_id: int, followee_id: int) -> FollowStatus:
        if follower_id == followee_id:
            raise AppException(status_code=400, detail="Không thể follow chính mình")

        await SocialRepository.add_follow(follower_id, followee_id)
        return FollowStatus(following=True)

    @staticmethod
    async def unfollow_user(follower_id: int, followee_id: int) -> FollowStatus:
        if follower_id == followee_id:
            raise AppException(status_code=400, detail="Không thể unfollow chính mình")

        await SocialRepository.remove_follow(follower_id, followee_id)
        return FollowStatus(following=False)

    @staticmethod
    async def get_follow_counts(user_id: int) -> FollowCount:
        followers = await SocialRepository.count_followers(user_id)
        following = await SocialRepository.count_following(user_id)
        return FollowCount(
            user_id=user_id, followers=followers, following=following
        )
