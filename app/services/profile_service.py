from app.core.exceptions import AppException
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserProfileRead, UserProfileUpdate, UserRead


class ProfileService:
    @staticmethod
    async def get_profile(username: str, viewer_id: int | None = None) -> UserProfileRead:
        row = await UserRepository.get_profile(username, viewer_id)
        if row is None:
            raise AppException(status_code=404, detail="Nguoi dung khong ton tai")
        return UserProfileRead(**dict(row))

    @staticmethod
    async def get_user_posts(username: str, limit: int = 20, offset: int = 0, viewer_id: int | None = None):
        row = await UserRepository.get_by_username(username)
        if row is None:
            raise AppException(status_code=404, detail="Nguoi dung khong ton tai")
        rows = await UserRepository.get_posts_by_user_id(row["id"], limit, offset, viewer_id)
        return [dict(r) for r in rows]

    @staticmethod
    async def update_profile(user_id: int, data: UserProfileUpdate) -> UserRead:
        row = await UserRepository.update_profile(user_id, data.display_name, None)
        return UserRead(**dict(row))

    @staticmethod
    async def update_avatar(user_id: int, avatar_url: str) -> UserRead:
        row = await UserRepository.update_profile(user_id, None, avatar_url)
        return UserRead(**dict(row))
