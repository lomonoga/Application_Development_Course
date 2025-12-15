import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime

from order_service import OrderService
from schemas import OrderCreate, OrderItemBase, OrderUpdate


class TestOrderService:
    @pytest.mark.asyncio
    async def test_get_by_id(self):
        mock_repo = AsyncMock()
        mock_order = Mock(
            id=uuid4(),
            user_id=uuid4(),
            delivery_address_id=uuid4(),
            status="pending",
            total_amount=100.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            items=[]
        )
        mock_repo.get_by_id.return_value = mock_order

        service = OrderService(repository=mock_repo)
        result = await service.get_by_id(mock_order.id)

        assert result.id == mock_order.id
        mock_repo.get_by_id.assert_called_once_with(mock_order.id, True)

    @pytest.mark.asyncio
    async def test_get_by_user_id(self):
        mock_repo = AsyncMock()
        mock_orders = [
            Mock(
                id=uuid4(),
                user_id=uuid4(),
                delivery_address_id=uuid4(),
                status="pending",
                total_amount=100.0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                items=[]
            )
        ]
        mock_repo.get_by_user_id.return_value = mock_orders

        service = OrderService(repository=mock_repo)
        user_id = uuid4()
        result = await service.get_by_user_id(user_id, 10, 1)

        assert len(result) == 1
        mock_repo.get_by_user_id.assert_called_once_with(user_id, 10, 1)

    @pytest.mark.asyncio
    async def test_get_by_filter(self):
        mock_repo = AsyncMock()
        mock_orders = [
            Mock(
                id=uuid4(),
                user_id=uuid4(),
                delivery_address_id=uuid4(),
                status="completed",
                total_amount=200.0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                items=[]
            )
        ]
        mock_repo.get_by_filter.return_value = mock_orders

        service = OrderService(repository=mock_repo)
        result = await service.get_by_filter(status="completed", count=5, page=2)

        assert len(result) == 1
        mock_repo.get_by_filter.assert_called_once_with(count=5, page=2, status="completed")

    @pytest.mark.asyncio
    async def test_get_total_count(self):
        mock_repo = AsyncMock()
        mock_repo.get_total_count.return_value = 15

        service = OrderService(repository=mock_repo)
        result = await service.get_total_count(status="pending")

        assert result == 15
        mock_repo.get_total_count.assert_called_once_with(status="pending")

    @pytest.mark.asyncio
    async def test_create(self):
        mock_repo = AsyncMock()
        mock_order = Mock(
            id=uuid4(),
            user_id=uuid4(),
            delivery_address_id=uuid4(),
            status="pending",
            total_amount=150.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            items=[]
        )
        mock_repo.create.return_value = mock_order

        service = OrderService(repository=mock_repo)
        order_data = OrderCreate(
            user_id=uuid4(),
            delivery_address_id=uuid4(),
            items=[
                OrderItemBase(
                    product_id=uuid4(),
                    quantity=2,
                    unit_price=75.0
                )
            ]
        )
        result = await service.create(order_data)

        assert result.id == mock_order.id
        mock_repo.create.assert_called_once_with(order_data)

    @pytest.mark.asyncio
    async def test_update(self):
        mock_repo = AsyncMock()
        order_id = uuid4()
        mock_order = Mock(
            id=order_id,
            user_id=uuid4(),
            delivery_address_id=uuid4(),
            status="completed",
            total_amount=100.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            items=[]
        )
        mock_repo.update.return_value = mock_order

        service = OrderService(repository=mock_repo)
        order_data = OrderUpdate(status="completed")
        result = await service.update(order_id, order_data)

        assert result.status == "completed"
        mock_repo.update.assert_called_once_with(order_id, order_data)

    @pytest.mark.asyncio
    async def test_delete(self):
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = True

        service = OrderService(repository=mock_repo)
        order_id = uuid4()
        await service.delete(order_id)

        mock_repo.delete.assert_called_once_with(order_id)

    @pytest.mark.asyncio
    async def test_validate_order_items(self):
        service = OrderService(repository=AsyncMock())

        items = [
            OrderItemBase(
                product_id=uuid4(),
                quantity=1,
                unit_price=50.0
            )
        ]
        result = await service.validate_order_items(items)

        assert result is True