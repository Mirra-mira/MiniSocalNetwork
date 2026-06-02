# TODO: Bộ phận Post sẽ triển khai service xử lý logic ở đây.
# Service không viết SQL trực tiếp, chỉ gọi repository.
from app.repositories.post_repo import PostRepository


class PostService:

    @staticmethod
    async def create_post(
        user_id: int,
        content: str
    ):

        if not content.strip():
            raise ValueError(
                "Content cannot be empty"
            )

        return await PostRepository.create_post(
            user_id,
            content
        )

    @staticmethod
    async def get_post(
        post_id: int
    ):

        post = await PostRepository.get_post_by_id(
            post_id
        )

        if post is None:
            raise ValueError(
                "Post not found"
            )

        return post

    @staticmethod
    async def delete_post(
        post_id: int
    ):

        post = await PostRepository.get_post_by_id(
            post_id
        )

        if post is None:
            raise ValueError(
                "Post not found"
            )

        await PostRepository.delete_post(
            post_id
        )

        return {
            "message": "Deleted successfully"
        }