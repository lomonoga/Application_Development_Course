import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime

from schemas import UserCreate, UserUpdate
from user_service import UserService


class TestUserService:
    @pytest.mark.asyncio
    async def test_get_by_id(self):
        mock_repo = AsyncMock()
        mock_user = Mock(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            description="Test description",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.get_by_id.return_value = mock_user

        service = UserService(user_repository=mock_repo)
        result = await service.get_by_id(mock_user.id)

        assert result.id == mock_user.id
        mock_repo.get_by_id.assert_called_once_with(mock_user.id)

    @pytest.mark.asyncio
    async def test_get_by_filter(self):
        mock_repo = AsyncMock()
        mock_users = [
            Mock(
                id=uuid4(),
                username="user1",
                email="user1@example.com",
                description="Desc1",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Mock(
                id=uuid4(),
                username="user2",
                email="user2@example.com",
                description="Desc2",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_repo.get_by_filter.return_value = mock_users

        service = UserService(user_repository=mock_repo)
        result = await service.get_by_filter(email="test@example.com", count=20, page=2)

        assert len(result) == 2
        mock_repo.get_by_filter.assert_called_once_with(20, 2, email="test@example.com")

    @pytest.mark.asyncio
    async def test_get_total_count(self):
        mock_repo = AsyncMock()
        mock_repo.get_total_count.return_value = 42

        service = UserService(user_repository=mock_repo)
        result = await service.get_total_count(is_active=True)

        assert result == 42
        mock_repo.get_total_count.assert_called_once_with(is_active=True)

    @pytest.mark.asyncio
    async def test_create(self):
        mock_repo = AsyncMock()
        mock_user = Mock(
            id=uuid4(),
            username="newuser",
            email="new@example.com",
            description="New user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.create.return_value = mock_user

        service = UserService(user_repository=mock_repo)
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            description="New user"
        )
        result = await service.create(user_data)

        assert result.username == "newuser"
        mock_repo.create.assert_called_once_with(user_data)

    @pytest.mark.asyncio
    async def test_update(self):
        mock_repo = AsyncMock()
        user_id = uuid4()
        mock_user = Mock(
            id=user_id,
            username="updated",
            email="updated@example.com",
            description="Updated",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repo.update.return_value = mock_user

        service = UserService(user_repository=mock_repo)
        user_data = UserUpdate(username="updated", description="Updated")
        result = await service.update(user_id, user_data)

        assert result.username == "updated"
        mock_repo.update.assert_called_once_with(user_id, user_data)

    @pytest.mark.asyncio
    async def test_delete(self):
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = True

        service = UserService(user_repository=mock_repo)
        user_id = uuid4()
        result = await service.delete(user_id)

        assert result is True
        mock_repo.delete.assert_called_once_with(user_id)