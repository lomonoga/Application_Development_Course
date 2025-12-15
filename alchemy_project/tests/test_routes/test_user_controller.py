import pytest
from unittest.mock import Mock
from uuid import UUID
from polyfactory.factories.pydantic_factory import ModelFactory
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from litestar.di import Provide
from litestar.testing import create_test_client

from user_controller import UserController
from user_service import UserService
from schemas import UserCreate, UserUpdate, UserResponse


class UserCreateFactory(ModelFactory[UserCreate]):
    __model__ = UserCreate


class UserUpdateFactory(ModelFactory[UserUpdate]):
    __model__ = UserUpdate


class UserResponseFactory(ModelFactory[UserResponse]):
    __model__ = UserResponse


@pytest.fixture()
def user_create():
    return UserCreateFactory.build()


@pytest.fixture()
def user_update():
    return UserUpdateFactory.build()


@pytest.fixture()
def user_response():
    return UserResponseFactory.build()


class MockUserService(UserService):
    def __init__(self):
        super().__init__(user_repository=Mock())

        self._mock_get_by_id = Mock()
        self._mock_get_by_filter = Mock()
        self._mock_get_total_count = Mock()
        self._mock_create = Mock()
        self._mock_update = Mock()
        self._mock_delete = Mock()

    async def get_by_id(self, user_id: UUID):
        return self._mock_get_by_id(user_id)

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs):
        return self._mock_get_by_filter(count, page, **kwargs)

    async def get_total_count(self, **kwargs):
        return self._mock_get_total_count(**kwargs)

    async def create(self, user_data: UserCreate):
        return self._mock_create(user_data)

    async def update(self, user_id: UUID, user_data: UserUpdate):
        return self._mock_update(user_id, user_data)

    async def delete(self, user_id: UUID):
        return self._mock_delete(user_id)


@pytest.mark.asyncio
async def test_get_user_by_id(user_response: UserResponse):
    mock_service = MockUserService()

    user_obj = Mock()
    for key, value in user_response.model_dump().items():
        setattr(user_obj, key, value)

    mock_service._mock_get_by_id.return_value = user_obj

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get(f"/users/get_user/{user_response.id}")
        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == str(user_response.id)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    from uuid import uuid4

    mock_service = MockUserService()
    mock_service._mock_get_by_id.return_value = None

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get(f"/users/get_user/{uuid4()}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_all_users(user_response: UserResponse):
    mock_service = MockUserService()

    user_obj = Mock()
    for key, value in user_response.model_dump().items():
        setattr(user_obj, key, value)

    mock_service._mock_get_by_filter.return_value = [user_obj]
    mock_service._mock_get_total_count.return_value = 1

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get("/users/get_all_users?count=10&page=1")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["users"]) == 1
        assert data["users"][0]["id"] == str(user_response.id)


@pytest.mark.asyncio
async def test_get_all_users_default_pagination(user_response: UserResponse):
    mock_service = MockUserService()

    user_obj = Mock()
    for key, value in user_response.model_dump().items():
        setattr(user_obj, key, value)

    def verify_params(count, page, **kwargs):
        assert count == 10
        assert page == 1
        return [user_obj]

    mock_service._mock_get_by_filter.side_effect = verify_params
    mock_service._mock_get_total_count.return_value = 1

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get("/users/get_all_users")
        assert response.status_code == HTTP_200_OK


@pytest.mark.asyncio
async def test_create_user(user_create: UserCreate, user_response: UserResponse):
    mock_service = MockUserService()

    user_obj = Mock()
    for key, value in user_response.model_dump().items():
        setattr(user_obj, key, value)

    mock_service._mock_create.return_value = user_obj

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.post("/users/create_user", json=user_create.model_dump())
        assert response.status_code == HTTP_201_CREATED
        assert response.json()["username"] == user_response.username


@pytest.mark.asyncio
async def test_update_user(user_response: UserResponse, user_update: UserUpdate):
    mock_service = MockUserService()

    user_obj = Mock()
    for key, value in user_response.model_dump().items():
        setattr(user_obj, key, value)

    mock_service._mock_update.return_value = user_obj

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.put(
            f"/users/update_user/{user_response.id}",
            json=user_update.model_dump()
        )
        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == str(user_response.id)


@pytest.mark.asyncio
async def test_update_user_not_found(user_update: UserUpdate):
    from uuid import uuid4

    mock_service = MockUserService()
    mock_service._mock_update.return_value = None

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.put(f"/users/update_user/{uuid4()}", json=user_update.model_dump())
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(user_response: UserResponse):
    mock_service = MockUserService()

    user_obj = Mock()
    for key, value in user_response.model_dump().items():
        setattr(user_obj, key, value)

    mock_service._mock_get_by_id.return_value = user_obj
    mock_service._mock_delete.return_value = True

    with create_test_client(
            route_handlers=[UserController],
            dependencies={"user_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.delete(f"/users/delete_user/{user_response.id}")
        assert response.status_code == HTTP_204_NO_CONTENT
