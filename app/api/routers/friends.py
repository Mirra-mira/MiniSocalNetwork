from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.core.exceptions import AppException
from app.core.responses import standard_response
from app.repositories.friend_repo import FriendRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.friend import FriendRead, FriendRequestRead, MessageCreate, MessageRead
from app.schemas.user import UserRead

router = APIRouter(tags=["friends"])


# ── Friend requests ─────────────────────────────────────

@router.post("/friends/request/{user_id}", response_model=dict)
async def send_request(user_id: int, current_user: UserRead = Depends(get_current_user)):
    if user_id == current_user.id:
        raise AppException(status_code=400, detail="Khong the ket ban voi chinh minh")
    existing = await FriendRepository.get_request_between(current_user.id, user_id)
    if existing:
        raise AppException(status_code=400, detail="Loi moi da ton tai hoac da la ban be")
    await FriendRepository.send_request(current_user.id, user_id)
    return standard_response(True, {}, "Da gui loi moi ket ban")


@router.get("/friends/requests", response_model=dict)
async def get_requests(current_user: UserRead = Depends(get_current_user)):
    rows = await FriendRepository.get_pending_requests(current_user.id)
    return standard_response(True, [dict(r) for r in rows], "Loi moi ket ban")


@router.post("/friends/requests/{request_id}/accept", response_model=dict)
async def accept_request(request_id: int, current_user: UserRead = Depends(get_current_user)):
    ok = await FriendRepository.accept_request(request_id, current_user.id)
    if not ok:
        raise AppException(status_code=404, detail="Loi moi khong ton tai")
    return standard_response(True, {}, "Da chap nhan ket ban")


@router.post("/friends/requests/{request_id}/reject", response_model=dict)
async def reject_request(request_id: int, current_user: UserRead = Depends(get_current_user)):
    await FriendRepository.reject_request(request_id, current_user.id)
    return standard_response(True, {}, "Da tu choi")


@router.get("/friends", response_model=dict)
async def get_friends(current_user: UserRead = Depends(get_current_user)):
    rows = await FriendRepository.get_friends(current_user.id)
    return standard_response(True, [dict(r) for r in rows], "Danh sach ban be")


@router.delete("/friends/{user_id}", response_model=dict)
async def remove_friend(user_id: int, current_user: UserRead = Depends(get_current_user)):
    await FriendRepository.remove_friend(current_user.id, user_id)
    return standard_response(True, {}, "Da xoa ban be")


@router.get("/friends/{user_id}/status", response_model=dict)
async def friend_status(user_id: int, current_user: UserRead = Depends(get_current_user)):
    req = await FriendRepository.get_request_between(current_user.id, user_id)
    if req is None:
        return standard_response(True, {"status": "none", "request_id": None}, "")
    return standard_response(True, {
        "status": req["status"] if req["status"] == "accepted" else (
            "sent" if req["sender_id"] == current_user.id else "received"
        ),
        "request_id": req["id"],
    }, "")


# ── Messages ────────────────────────────────────────────

@router.post("/messages/{user_id}", response_model=dict)
async def send_message(
    user_id: int,
    body: MessageCreate,
    current_user: UserRead = Depends(get_current_user),
):
    req = await FriendRepository.get_request_between(current_user.id, user_id)
    if req is None or req["status"] != "accepted":
        raise AppException(status_code=403, detail="Chi co the nhan tin voi ban be")
    row = await MessageRepository.create_message(current_user.id, user_id, body.content)
    msg = MessageRead(**dict(row))
    return standard_response(True, msg.dict(), "Da gui")


@router.get("/messages/{user_id}", response_model=dict)
async def get_messages(
    user_id: int,
    after_id: int = Query(0, ge=0),
    current_user: UserRead = Depends(get_current_user),
):
    if after_id > 0:
        rows = await MessageRepository.get_new_messages(current_user.id, user_id, after_id)
        msgs = [MessageRead(**dict(r)).dict() for r in rows]
    else:
        rows = await MessageRepository.get_messages(current_user.id, user_id)
        msgs = list(reversed([MessageRead(**dict(r)).dict() for r in rows]))
    return standard_response(True, msgs, "Tin nhan")
