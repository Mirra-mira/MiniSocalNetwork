from app.core.exceptions import AppException
from app.core.security import create_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.user import Token, UserCreate, UserLogin, UserRead


class AuthService:
    @staticmethod
    async def register_user(user_create: UserCreate) -> UserRead:
        existing = await UserRepository.get_by_username(user_create.username)
        if existing is not None:
            raise AppException(status_code=400, detail="Tên người dùng đã tồn tại")

        password_hash = hash_password(user_create.password)
        record = await UserRepository.create_user(user_create.username, password_hash)
        return UserRead(**record)

    @staticmethod
    async def authenticate_user(user_login: UserLogin) -> Token:
        user = await UserRepository.get_by_username(user_login.username)
        if user is None or not verify_password(user_login.password, user["password_hash"]):
            raise AppException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không đúng")

        token = create_token(str(user["id"]))
        return Token(access_token=token)

    @staticmethod
    async def get_current_user(user_id: int) -> UserRead | None:
        record = await UserRepository.get_by_id(user_id)
        if record is None:
            return None
        return UserRead(**record)
