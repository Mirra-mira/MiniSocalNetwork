from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

from app.api.routers.auth import router as auth_router
from app.api.routers.feed import router as feed_router
from app.api.routers.friends import router as friends_router
from app.api.routers.posts import router as posts_router
from app.api.routers.profile import router as profile_router
from app.api.routers.social import router as social_router
from app.core.exceptions import register_exception_handlers
from app.database import connect_db, disconnect_db

app = FastAPI(title="Mini Social Network", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(posts_router)
app.include_router(feed_router)
app.include_router(social_router)
app.include_router(profile_router)
app.include_router(friends_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

register_exception_handlers(app)


@app.on_event("startup")
async def on_startup():
    await connect_db()
    os.makedirs(os.path.join("frontend", "uploads", "avatars"), exist_ok=True)


@app.on_event("shutdown")
async def on_shutdown():
    await disconnect_db()
