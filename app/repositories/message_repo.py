import app.database as db


class MessageRepository:
    @staticmethod
    async def create_message(sender_id: int, receiver_id: int, content: str):
        return await db.pool.fetchrow(
            """INSERT INTO messages (sender_id, receiver_id, content)
               VALUES ($1, $2, $3) RETURNING *""",
            sender_id, receiver_id, content,
        )

    @staticmethod
    async def get_messages(user1_id: int, user2_id: int, limit: int = 50):
        return await db.pool.fetch(
            """SELECT id, sender_id, receiver_id, content, created_at
               FROM messages
               WHERE (sender_id = $1 AND receiver_id = $2)
                  OR (sender_id = $2 AND receiver_id = $1)
               ORDER BY created_at DESC
               LIMIT $3""",
            user1_id, user2_id, limit,
        )

    @staticmethod
    async def get_new_messages(user1_id: int, user2_id: int, after_id: int):
        return await db.pool.fetch(
            """SELECT id, sender_id, receiver_id, content, created_at
               FROM messages
               WHERE ((sender_id = $1 AND receiver_id = $2)
                   OR (sender_id = $2 AND receiver_id = $1))
                 AND id > $3
               ORDER BY created_at ASC""",
            user1_id, user2_id, after_id,
        )
