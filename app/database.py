import asyncpg
from app.config import settings

pool: asyncpg.Pool | None = None


async def connect_db() -> None:
    global pool
    pool = await asyncpg.create_pool(settings.DATABASE_URL, ssl="require")


async def disconnect_db() -> None:
    global pool
    if pool is not None:
        await pool.close()
