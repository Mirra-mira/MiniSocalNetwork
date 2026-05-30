import app.database as db


class UserRepository:
    @staticmethod
    async def get_by_username(username: str):
        return await db.pool.fetchrow(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = $1",
            username,
        )

    @staticmethod
    async def get_by_id(user_id: int):
        return await db.pool.fetchrow(
            "SELECT id, username, created_at FROM users WHERE id = $1",
            user_id,
        )

    @staticmethod
    async def create_user(username: str, password_hash: str):
        return await db.pool.fetchrow(
            "INSERT INTO users (username, password_hash) VALUES ($1, $2) RETURNING id, username, created_at",
            username,
            password_hash,
        )

    @staticmethod
    async def update_password(username: str, password_hash: str) -> bool:
        result = await db.pool.execute(
            "UPDATE users SET password_hash = $1 WHERE username = $2",
            password_hash,
            username,
        )
        return result == "UPDATE 1"
