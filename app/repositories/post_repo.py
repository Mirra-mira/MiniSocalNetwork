# TODO: Bộ phận Post sẽ triển khai repository truy vấn SQL thuần ở đây.
import app.database as database


class PostRepository:

    @staticmethod
    async def create_post(user_id: int, content: str):

        query = """
        INSERT INTO posts(user_id, content)
        VALUES($1, $2)
        RETURNING *
        """

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                query,
                user_id,
                content
            )

    @staticmethod
    async def get_post_by_id(post_id: int):

        query = """
        SELECT *
        FROM posts
        WHERE id = $1
        """

        async with database.pool.acquire() as conn:
            return await conn.fetchrow(
                query,
                post_id
            )

    @staticmethod
    async def delete_post(post_id: int):

        query = """
        DELETE FROM posts
        WHERE id = $1
        """

        async with database.pool.acquire() as conn:
            await conn.execute(
                query,
                post_id
            )