import app.database as db


class FriendRepository:
    @staticmethod
    async def send_request(sender_id: int, receiver_id: int):
        return await db.pool.fetchrow(
            """INSERT INTO friend_requests (sender_id, receiver_id)
               VALUES ($1, $2)
               ON CONFLICT (sender_id, receiver_id) DO NOTHING
               RETURNING *""",
            sender_id, receiver_id,
        )

    @staticmethod
    async def get_request_between(user1_id: int, user2_id: int):
        return await db.pool.fetchrow(
            """SELECT * FROM friend_requests
               WHERE (sender_id = $1 AND receiver_id = $2)
                  OR (sender_id = $2 AND receiver_id = $1)""",
            user1_id, user2_id,
        )

    @staticmethod
    async def accept_request(request_id: int, receiver_id: int) -> bool:
        result = await db.pool.execute(
            """UPDATE friend_requests SET status = 'accepted'
               WHERE id = $1 AND receiver_id = $2 AND status = 'pending'""",
            request_id, receiver_id,
        )
        return result == "UPDATE 1"

    @staticmethod
    async def reject_request(request_id: int, receiver_id: int):
        await db.pool.execute(
            """UPDATE friend_requests SET status = 'rejected'
               WHERE id = $1 AND receiver_id = $2""",
            request_id, receiver_id,
        )

    @staticmethod
    async def remove_friend(user_id: int, friend_id: int):
        await db.pool.execute(
            """DELETE FROM friend_requests
               WHERE ((sender_id = $1 AND receiver_id = $2)
                   OR (sender_id = $2 AND receiver_id = $1))
                 AND status = 'accepted'""",
            user_id, friend_id,
        )

    @staticmethod
    async def get_friends(user_id: int):
        return await db.pool.fetch(
            """SELECT u.id, u.username, u.display_name, u.avatar_url
               FROM friend_requests fr
               JOIN users u ON u.id = CASE
                   WHEN fr.sender_id = $1 THEN fr.receiver_id
                   ELSE fr.sender_id
               END
               WHERE (fr.sender_id = $1 OR fr.receiver_id = $1)
                 AND fr.status = 'accepted'
               ORDER BY u.username""",
            user_id,
        )

    @staticmethod
    async def get_pending_requests(user_id: int):
        return await db.pool.fetch(
            """SELECT fr.id, fr.sender_id,
                      u.username AS sender_username,
                      u.display_name AS sender_display_name,
                      fr.created_at
               FROM friend_requests fr
               JOIN users u ON u.id = fr.sender_id
               WHERE fr.receiver_id = $1 AND fr.status = 'pending'
               ORDER BY fr.created_at DESC""",
            user_id,
        )
