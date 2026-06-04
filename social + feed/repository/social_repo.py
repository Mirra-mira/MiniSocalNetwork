import app.database as database


class SocialRepository:

    @staticmethod
    async def add_like(post_id: int, user_id: int):
        query = """
        INSERT INTO likes (post_id, user_id)
        VALUES ($1, $2)
        ON CONFLICT (post_id, user_id) DO NOTHING
        RETURNING *
        """
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, post_id, user_id)

    @staticmethod
    async def remove_like(post_id: int, user_id: int) -> str:
        query = """
        DELETE FROM likes
        WHERE post_id = $1 AND user_id = $2
        """
        async with database.pool.acquire() as conn:
            return await conn.execute(query, post_id, user_id)

    @staticmethod
    async def get_like(post_id: int, user_id: int):
        query = """
        SELECT * FROM likes
        WHERE post_id = $1 AND user_id = $2
        """
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, post_id, user_id)

    @staticmethod
    async def count_likes(post_id: int) -> int:
        query = """
        SELECT COUNT(*) AS cnt FROM likes
        WHERE post_id = $1
        """
        async with database.pool.acquire() as conn:
            row = await conn.fetchrow(query, post_id)
            return row["cnt"] if row else 0


    @staticmethod
    async def create_comment(post_id: int, user_id: int, content: str):
        query = """
        INSERT INTO comments (post_id, user_id, content)
        VALUES ($1, $2, $3)
        RETURNING *
        """
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, post_id, user_id, content)

    @staticmethod
    async def get_comments_by_post(post_id: int, limit: int = 50, offset: int = 0):
        query = """
        SELECT c.id, c.post_id, c.user_id, u.username, c.content, c.created_at
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.post_id = $1
        ORDER BY c.created_at ASC
        LIMIT $2 OFFSET $3
        """
        async with database.pool.acquire() as conn:
            return await conn.fetch(query, post_id, limit, offset)

    @staticmethod
    async def delete_comment(comment_id: int, user_id: int) -> str:
        query = """
        DELETE FROM comments
        WHERE id = $1 AND user_id = $2
        """
        async with database.pool.acquire() as conn:
            return await conn.execute(query, comment_id, user_id)


    @staticmethod
    async def add_follow(follower_id: int, followee_id: int):
        query = """
        INSERT INTO follows (follower_id, followee_id)
        VALUES ($1, $2)
        ON CONFLICT (follower_id, followee_id) DO NOTHING
        RETURNING *
        """
        async with database.pool.acquire() as conn:
            return await conn.fetchrow(query, follower_id, followee_id)

    @staticmethod
    async def remove_follow(follower_id: int, followee_id: int) -> str:
        query = """
        DELETE FROM follows
        WHERE follower_id = $1 AND followee_id = $2
        """
        async with database.pool.acquire() as conn:
            return await conn.execute(query, follower_id, followee_id)

    @staticmethod
    async def is_following(follower_id: int, followee_id: int) -> bool:
        query = """
        SELECT 1 FROM follows
        WHERE follower_id = $1 AND followee_id = $2
        """
        async with database.pool.acquire() as conn:
            row = await conn.fetchrow(query, follower_id, followee_id)
            return row is not None

    @staticmethod
    async def count_followers(user_id: int) -> int:
        query = """
        SELECT COUNT(*) AS cnt FROM follows
        WHERE followee_id = $1
        """
        async with database.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
            return row["cnt"] if row else 0

    @staticmethod
    async def count_following(user_id: int) -> int:
        query = """
        SELECT COUNT(*) AS cnt FROM follows
        WHERE follower_id = $1
        """
        async with database.pool.acquire() as conn:
            row = await conn.fetchrow(query, user_id)
            return row["cnt"] if row else 0


    @staticmethod
    async def get_feed_posts(user_id: int, limit: int = 20, offset: int = 0):
        query = """
        SELECT
            p.id,
            p.user_id,
            u.username,
            p.content,
            p.created_at,
            COALESCE(lk.like_count, 0)    AS like_count,
            COALESCE(cm.comment_count, 0)  AS comment_count
        FROM posts p
        JOIN follows f ON f.followee_id = p.user_id
        JOIN users  u ON u.id = p.user_id
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS like_count
            FROM likes
            GROUP BY post_id
        ) lk ON lk.post_id = p.id
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS comment_count
            FROM comments
            GROUP BY post_id
        ) cm ON cm.post_id = p.id
        WHERE f.follower_id = $1
        ORDER BY p.created_at DESC
        LIMIT $2 OFFSET $3
        """
        async with database.pool.acquire() as conn:
            return await conn.fetch(query, user_id, limit, offset)
