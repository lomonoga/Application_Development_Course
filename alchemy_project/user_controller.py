from uuid import UUID

from litestar import Controller, delete, get, post, put
from litestar.exceptions import NotFoundException
from litestar.params import Body, Parameter
from schemas import UserCreate, UserResponse, UsersResponse, UserUpdate
from user_service import UserService
from redis_client import get_redis_client


class UserController(Controller):
    path = "/users"
    tags = ["User Management"]

    USER_CACHE_TTL = 3600  # 1 час
    USERS_LIST_CACHE_TTL = 600  # 10 минут

    @get("/get_user/{user_id:uuid}")
    async def get_user_by_id(
        self, user_service: UserService, user_id: UUID
    ) -> UserResponse:
        """Get user by ID"""
        cache_key = f"user:{user_id}"
        redis_client = await get_redis_client()

        cached_user = await redis_client.get(cache_key)
        if cached_user:
            return UserResponse.model_validate_json(cached_user)

        user = await user_service.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        user_response = UserResponse.model_validate(user)
        await redis_client.setex(
            cache_key,
            self.USER_CACHE_TTL,
            user_response.model_dump_json()
        )

        return user_response

    @get("/get_all_users")
    async def get_all_users(
        self,
        user_service: UserService,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(gt=0, default=1),
    ) -> UsersResponse:
        """Get all users with pagination"""
        users = await user_service.get_by_filter(count=count, page=page)
        total_count = await user_service.get_total_count()

        return UsersResponse(
            users=[UserResponse.model_validate(user) for user in users],
            total_count=total_count,
        )

    @post("/create_user")
    async def create_user(
        self,
        user_service: UserService,
        data: UserCreate = Body(media_type="application/json"),
    ) -> UserResponse:
        """Create user"""
        user = await user_service.create(data)
        return UserResponse.model_validate(user)

    @delete("/delete_user/{user_id:uuid}")
    async def delete_user(self, user_service: UserService, user_id: UUID) -> None:
        """Delete user"""
        success = await user_service.delete(user_id)
        redis_client = await get_redis_client()
        if not success:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        await redis_client.delete(f"user:{user_id}")

    @put("/update_user/{user_id:uuid}")
    async def update_user(
        self,
        user_service: UserService,
        user_id: UUID,
        data: UserUpdate = Body(media_type="application/json"),
    ) -> UserResponse:
        """Update user"""
        redis_client = await get_redis_client()
        user = await user_service.update(user_id, data)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        user_response = UserResponse.model_validate(user)
        await redis_client.setex(
            f"user:{user_id}",
            self.USER_CACHE_TTL,
            user_response.model_dump_json()
        )

        return UserResponse.model_validate(user)
