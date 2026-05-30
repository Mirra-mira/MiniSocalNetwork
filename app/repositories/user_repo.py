from app.database import pool


class UserRepository:
    @staticmethod
    async def get_by_username(username: str):
        if pool is None:
            return None
        return await pool.fetchrow(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = $1",
            username,
        )

    @staticmethod
    async def get_by_id(user_id: int):
        if pool is None:
            return None
        return await pool.fetchrow(
            "SELECT id, username, created_at FROM users WHERE id = $1",
            user_id,
        )

    @staticmethod
    async def create_user(username: str, password_hash: str):
        if pool is None:
            return None
        return await pool.fetchrow(
            "INSERT INTO users (username, password_hash) VALUES ($1, $2) RETURNING id, username, created_at",
            username,
            password_hash,
        )
