import os
import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, File

from app.api.deps import get_current_user
from app.core.responses import standard_response
from app.schemas.user import UserProfileUpdate, UserRead
from app.services.profile_service import ProfileService

router = APIRouter(tags=["profile"])

UPLOAD_DIR = os.path.join("frontend", "uploads", "avatars")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@router.get("/users/search", response_model=dict)
async def search_users(
    q: str = Query("", min_length=1, max_length=50),
    current_user: UserRead = Depends(get_current_user),
):
    from app.repositories.user_repo import UserRepository
    rows = await UserRepository.search_users(q, current_user.id)
    return standard_response(True, [dict(r) for r in rows], "")


@router.get("/users/{username}", response_model=dict)
async def get_profile(
    username: str,
    current_user: UserRead = Depends(get_current_user),
):
    profile = await ProfileService.get_profile(username, current_user.id)
    return standard_response(True, profile.dict(), "Profile")


@router.get("/users/{username}/posts", response_model=dict)
async def get_user_posts(
    username: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserRead = Depends(get_current_user),
):
    posts = await ProfileService.get_user_posts(username, limit, offset, current_user.id)
    return standard_response(True, posts, "Bai dang cua nguoi dung")


@router.put("/users/me", response_model=dict)
async def update_profile(
    data: UserProfileUpdate,
    current_user: UserRead = Depends(get_current_user),
):
    updated = await ProfileService.update_profile(current_user.id, data)
    return standard_response(True, updated.dict(), "Cap nhat thanh cong")


@router.post("/users/me/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserRead = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        from app.core.exceptions import AppException
        raise AppException(status_code=400, detail="Chi chap nhan jpg, png, gif, webp")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)

    avatar_url = f"/uploads/avatars/{filename}"
    updated = await ProfileService.update_avatar(current_user.id, avatar_url)
    return standard_response(True, updated.dict(), "Cap nhat anh dai dien thanh cong")
