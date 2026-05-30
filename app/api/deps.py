from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AppException
from app.core.security import decode_token
from app.services.auth_service import AuthService
from app.schemas.user import UserRead

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserRead:
    token = credentials.credentials
    user_id = decode_token(token)
    user = await AuthService.get_current_user(int(user_id))
    if user is None:
        raise AppException(status_code=401, detail="Người dùng không tồn tại")
    return user
