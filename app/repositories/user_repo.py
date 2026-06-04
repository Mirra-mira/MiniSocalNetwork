import app.database as db


class UserRepository:
    @staticmethod
    async def get_by_username(username: str):
        return await db.pool.fetchrow(
            """SELECT id, username, display_name, avatar_url, password_hash, created_at
               FROM users WHERE username = $1""",
            username,
        )

    @staticmethod
    async def get_by_id(user_id: int):
        return await db.pool.fetchrow(
            """SELECT id, username, display_name, avatar_url, created_at
               FROM users WHERE id = $1""",
            user_id,
        )

    @staticmethod
    async def create_user(username: str, password_hash: str):
        return await db.pool.fetchrow(
            """INSERT INTO users (username, password_hash)
               VALUES ($1, $2)
               RETURNING id, username, display_name, avatar_url, created_at""",
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

    @staticmethod
    async def get_profile(username: str, viewer_id: int | None = None) -> dict | None:
        user = await db.pool.fetchrow(
            "SELECT id, username, display_name, avatar_url, created_at FROM users WHERE username = $1",
            username,
        )
        if user is None:
            return None

        followers = await db.pool.fetchval(
            "SELECT COUNT(*) FROM follows WHERE followee_id = $1", user["id"]
        )
        following = await db.pool.fetchval(
            "SELECT COUNT(*) FROM follows WHERE follower_id = $1", user["id"]
        )
        is_following = False
        if viewer_id is not None:
            is_following = bool(await db.pool.fetchval(
                "SELECT EXISTS(SELECT 1 FROM follows WHERE follower_id = $1 AND followee_id = $2)",
                viewer_id, user["id"],
            ))

        return {
            "id": user["id"],
            "username": user["username"],
            "display_name": user["display_name"],
            "avatar_url": user["avatar_url"],
            "created_at": user["created_at"],
            "followers": int(followers),
            "following": int(following),
            "is_following": is_following,
        }

    @staticmethod
    async def get_posts_by_user_id(user_id: int, limit: int = 20, offset: int = 0, viewer_id: int | None = None):
        return await db.pool.fetch(
            """SELECT
                p.id, p.user_id, p.content, p.created_at,
                COALESCE(lk.like_count, 0)    AS like_count,
                COALESCE(cm.comment_count, 0)  AS comment_count,
                EXISTS(
                    SELECT 1 FROM likes ul
                    WHERE ul.post_id = p.id AND ul.user_id = $4
                ) AS user_liked
               FROM posts p
               LEFT JOIN (
                   SELECT post_id, COUNT(*) AS like_count FROM likes GROUP BY post_id
               ) lk ON lk.post_id = p.id
               LEFT JOIN (
                   SELECT post_id, COUNT(*) AS comment_count FROM comments GROUP BY post_id
               ) cm ON cm.post_id = p.id
               WHERE p.user_id = $1
               ORDER BY p.created_at DESC
               LIMIT $2 OFFSET $3""",
            user_id,
            limit,
            offset,
            viewer_id,
        )

    @staticmethod
    async def search_users(query: str, exclude_id: int):
        return await db.pool.fetch(
            """SELECT id, username, display_name, avatar_url
               FROM users
               WHERE (username ILIKE $1 OR display_name ILIKE $1)
                 AND id != $2
               ORDER BY username
               LIMIT 10""",
            f"%{query}%",
            exclude_id,
        )

    @staticmethod
    async def update_profile(user_id: int, display_name: str | None, avatar_url: str | None):
        return await db.pool.fetchrow(
            """UPDATE users
               SET display_name = COALESCE($2, display_name),
                   avatar_url   = COALESCE($3, avatar_url)
               WHERE id = $1
               RETURNING id, username, display_name, avatar_url, created_at""",
            user_id,
            display_name,
            avatar_url,
        )
