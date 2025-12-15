from litestar import Controller, get, post, put, delete
from litestar.params import Parameter, Body
from litestar.exceptions import NotFoundException
from uuid import UUID

from user_service import UserService
from schemas import UserCreate, UserUpdate, UserResponse, UsersResponse

class UserController(Controller):
    path = "/users"
    tags = ["User Management"]

    @get("/get_user/{user_id:uuid}")
    async def get_user_by_id(
            self,
            user_service: UserService,
            user_id: UUID
    ) -> UserResponse:
        """Get user by ID"""
        user = await user_service.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @get("/get_all_users")
    async def get_all_users(
            self,
            user_service: UserService,
            count: int = Parameter(gt=0, le=100, default=10),
            page: int = Parameter(gt=0, default=1)
    ) -> UsersResponse:
        """Get all users with pagination"""
        users = await user_service.get_by_filter(count=count, page=page)
        total_count = await user_service.get_total_count()

        return UsersResponse(
            users=[UserResponse.model_validate(user) for user in users],
            total_count=total_count
        )

    @post("/create_user")
    async def create_user(
            self,
            user_service: UserService,
            data: UserCreate = Body(media_type="application/json")
    ) -> UserResponse:
        """Create user"""
        user = await user_service.create(data)
        return UserResponse.model_validate(user)

    @delete("/delete_user/{user_id:uuid}")
    async def delete_user(
            self,
            user_service: UserService,
            user_id: UUID
    ) -> None:
        """Delete user"""
        success = await user_service.delete(user_id)
        if not success:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

    @put("/update_user/{user_id:uuid}")
    async def update_user(
            self,
            user_service: UserService,
            user_id: UUID,
            data: UserUpdate = Body(media_type="application/json")
    ) -> UserResponse:
        """Update user"""
        user = await user_service.update(user_id, data)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)
