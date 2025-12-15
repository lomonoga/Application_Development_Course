import pytest

from user_repository import UserRepository
from schemas import UserCreate, UserUpdate
from tables import User


class TestUserRepository:
    """Тесты для репозитория пользователей"""

    @pytest.mark.asyncio
    async def test_create_user(self, user_repository: UserRepository):
        """Тест создания пользователя"""
        user_data = UserCreate(
            email="test@example.com",
            username="john_doe",
            description="Test user description"
        )

        user = await user_repository.create(user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "john_doe"
        assert user.description == "Test user description"

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, user_repository: UserRepository):
        """Тест успешного получения пользователя по ID"""
        user_data = UserCreate(
            email="getbyid@example.com",
            username="getbyid_user",
            description="Test user"
        )
        created_user = await user_repository.create(user_data)

        found_user = await user_repository.get_by_id(created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "getbyid@example.com"
        assert found_user.username == "getbyid_user"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, user_repository: UserRepository):
        """Тест поиска несуществующего пользователя по ID"""
        import uuid
        random_id = uuid.uuid4()

        user = await user_repository.get_by_id(random_id)

        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_filter_basic(self, user_repository: UserRepository):
        """Тест получения пользователей с пагинацией"""

        for i in range(1, 6):
            user_data = UserCreate(
                email=f"filter{i}@example.com",
                username=f"user_filter{i}",
                description=f"User {i} for filter test"
            )
            await user_repository.create(user_data)

        users_page1 = await user_repository.get_by_filter(count=3, page=1)

        assert len(users_page1) == 3
        assert all(isinstance(user, User) for user in users_page1)

        users_page2 = await user_repository.get_by_filter(count=3, page=2)
        assert len(users_page2) >= 2

    @pytest.mark.asyncio
    async def test_get_by_filter_with_email_filter(self, user_repository: UserRepository):
        """Тест фильтрации по email"""
        user1_data = UserCreate(
            email="specific@example.com",
            username="specific_user",
            description="Specific user"
        )
        await user_repository.create(user1_data)

        user2_data = UserCreate(
            email="other@example.com",
            username="other_user",
            description="Other user"
        )
        await user_repository.create(user2_data)

        filtered_users = await user_repository.get_by_filter(
            count=10, page=1, email="specific@example.com"
        )

        assert len(filtered_users) >= 1
        assert filtered_users[0].email == "specific@example.com"
        assert filtered_users[0].username == "specific_user"

    @pytest.mark.asyncio
    async def test_get_by_filter_with_username_filter(self, user_repository: UserRepository):
        """Тест фильтрации по username"""
        user_data = UserCreate(
            email="filter_username@example.com",
            username="unique_filter_name",
            description="User for username filter"
        )
        await user_repository.create(user_data)

        filtered_users = await user_repository.get_by_filter(
            count=10, page=1, username="unique_filter_name"
        )

        assert len(filtered_users) >= 1
        assert filtered_users[0].username == "unique_filter_name"

    @pytest.mark.asyncio
    async def test_get_by_filter_invalid_filter(self, user_repository: UserRepository):
        """Тест с несуществующим полем фильтрации"""
        users = await user_repository.get_by_filter(
            count=10, page=1, nonexistent_field="value"
        )

        assert isinstance(users, list)

    @pytest.mark.asyncio
    async def test_get_total_count(self, user_repository: UserRepository):
        """Тест получения общего количества пользователей"""

        for i in range(1, 4):
            user_data = UserCreate(
                email=f"count{i}@example.com",
                username=f"user_count{i}",
                description=f"User {i} for count test"
            )
            await user_repository.create(user_data)

        total_count = await user_repository.get_total_count()

        assert total_count >= 3

    @pytest.mark.asyncio
    async def test_get_total_count_with_filter(self, user_repository: UserRepository):
        """Тест подсчета с фильтром"""

        user1_data = UserCreate(
            email="filtered_count@example.com",
            username="user_filtered",
            description="Filtered user"
        )
        await user_repository.create(user1_data)

        user2_data = UserCreate(
            email="other_count@example.com",
            username="user_other",
            description="Other user"
        )
        await user_repository.create(user2_data)

        filtered_count = await user_repository.get_total_count(
            email="filtered_count@example.com"
        )

        assert filtered_count >= 1

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_repository: UserRepository):
        """Тест успешного обновления пользователя"""

        user_data = UserCreate(
            email="update_test@example.com",
            username="update_user",
            description="Original description"
        )
        created_user = await user_repository.create(user_data)

        update_data = UserUpdate(description="Updated description")
        updated_user = await user_repository.update(created_user.id, update_data)

        assert updated_user is not None
        assert updated_user.id == created_user.id
        assert updated_user.description == "Updated description"
        assert updated_user.email == "update_test@example.com"
        assert updated_user.username == "update_user"

    @pytest.mark.asyncio
    async def test_update_user_partial(self, user_repository: UserRepository):
        """Тест частичного обновления (только одно поле)"""
        user_data = UserCreate(
            email="partial@example.com",
            username="partial_user",
            description="Original"
        )
        created_user = await user_repository.create(user_data)

        update_data = UserUpdate(email="new_email@example.com")
        updated_user = await user_repository.update(created_user.id, update_data)

        assert updated_user.email == "new_email@example.com"
        assert updated_user.username == "partial_user"
        assert updated_user.description == "Original"

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_repository: UserRepository):
        """Тест обновления несуществующего пользователя"""
        import uuid
        random_id = uuid.uuid4()

        update_data = UserUpdate(description="Should not update")
        result = await user_repository.update(random_id, update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_repository: UserRepository):
        """Тест успешного удаления пользователя"""
        user_data = UserCreate(
            email="delete@example.com",
            username="delete_user",
            description="Will be deleted"
        )
        created_user = await user_repository.create(user_data)

        deleted = await user_repository.delete(created_user.id)

        assert deleted is True

        found_user = await user_repository.get_by_id(created_user.id)
        assert found_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_repository: UserRepository):
        """Тест удаления несуществующего пользователя"""
        import uuid
        random_id = uuid.uuid4()

        deleted = await user_repository.delete(random_id)

        assert deleted is False

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, user_repository: UserRepository):
        """Тест получения пользователя по email"""
        user_data = UserCreate(
            email="unique_email@example.com",
            username="email_user",
            description="User for email test"
        )
        await user_repository.create(user_data)

        users = await user_repository.get_by_filter(
            count=1, page=1, email="unique_email@example.com"
        )

        assert len(users) >= 1
        assert users[0].email == "unique_email@example.com"

    @pytest.mark.asyncio
    async def test_full_crud_cycle(self, user_repository: UserRepository):
        """Полный тест цикла создания, чтения, обновления, удаления"""
        user_data = UserCreate(
            email="crud@example.com",
            username="crud_user",
            description="CRUD test user"
        )
        created_user = await user_repository.create(user_data)
        assert created_user.id is not None

        found_user = await user_repository.get_by_id(created_user.id)
        assert found_user.id == created_user.id

        update_data = UserUpdate(description="Updated via CRUD")
        updated_user = await user_repository.update(created_user.id, update_data)
        assert updated_user.description == "Updated via CRUD"

        deleted = await user_repository.delete(created_user.id)
        assert deleted is True

        deleted_user = await user_repository.get_by_id(created_user.id)
        assert deleted_user is None
