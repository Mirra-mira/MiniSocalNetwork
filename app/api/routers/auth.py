from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.core.responses import standard_response
from app.schemas.user import PasswordReset, Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    created_user = await AuthService.register_user(user)
    return standard_response(True, created_user.dict(), "Đăng ký thành công")


@router.post("/login", response_model=dict)
async def login(credentials: UserLogin):
    token_data = await AuthService.authenticate_user(credentials)
    return standard_response(True, token_data.dict(), "Đăng nhập thành công")


@router.get("/me", response_model=dict)
async def me(current_user: UserRead = Depends(get_current_user)):
    return standard_response(True, current_user.dict(), "Thông tin người dùng hiện tại")


@router.post("/reset-password", response_model=dict)
async def reset_password(data: PasswordReset):
    await AuthService.reset_password(data)
    return standard_response(True, {}, "Đặt lại mật khẩu thành công")
