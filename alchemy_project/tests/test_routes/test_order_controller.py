from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

import pytest
from litestar.di import Provide
from litestar.status_codes import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT)
from litestar.testing import create_test_client
from order_controller import OrderController
from order_service import OrderService
from polyfactory.factories.pydantic_factory import ModelFactory
from schemas import OrderCreate, OrderItemBase, OrderResponse, OrderUpdate


class OrderCreateFactory(ModelFactory[OrderCreate]):
    __model__ = OrderCreate


class OrderUpdateFactory(ModelFactory[OrderUpdate]):
    __model__ = OrderUpdate


class OrderResponseFactory(ModelFactory[OrderResponse]):
    __model__ = OrderResponse


class OrderItemBaseFactory(ModelFactory[OrderItemBase]):
    __model__ = OrderItemBase


@pytest.fixture()
def order_create():
    return OrderCreateFactory.build()


@pytest.fixture()
def order_update():
    return OrderUpdateFactory.build()


@pytest.fixture()
def order_response():
    return OrderResponseFactory.build()


@pytest.fixture()
def order_item_base():
    return OrderItemBaseFactory.build()


class MockOrderService(OrderService):
    def __init__(self):
        super().__init__(repository=Mock())

        self._mock_get_by_id = Mock()
        self._mock_get_by_user_id = Mock()
        self._mock_get_by_filter = Mock()
        self._mock_get_total_count = Mock()
        self._mock_create = Mock()
        self._mock_update = Mock()
        self._mock_delete = Mock()
        self._mock_validate_order_items = Mock()

    async def get_by_id(self, order_id: UUID, include_relations: bool = True):
        return self._mock_get_by_id(order_id, include_relations)

    async def get_by_user_id(self, user_id: UUID, count: int = 10, page: int = 1):
        return self._mock_get_by_user_id(user_id, count, page)

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs):
        return self._mock_get_by_filter(count, page, **kwargs)

    async def get_total_count(self, **kwargs):
        return self._mock_get_total_count(**kwargs)

    async def create(self, order_data: OrderCreate):
        return self._mock_create(order_data)

    async def update(self, order_id: UUID, order_data: OrderUpdate):
        return self._mock_update(order_id, order_data)

    async def delete(self, order_id: UUID):
        return self._mock_delete(order_id)

    async def validate_order_items(self, items: list):
        return self._mock_validate_order_items(items)


@pytest.mark.asyncio
async def test_get_order_by_id(order_response: OrderResponse):
    mock_service = MockOrderService()

    mock_service._mock_get_by_id.return_value = order_response

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.get(f"/orders/get_order/{order_response.id}")
        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == str(order_response.id)


@pytest.mark.asyncio
async def test_get_order_by_id_not_found():
    from uuid import uuid4

    mock_service = MockOrderService()

    from litestar.exceptions import NotFoundException

    mock_service._mock_get_by_id.side_effect = NotFoundException(
        detail="Order not found"
    )

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.get(f"/orders/get_order/{uuid4()}")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_orders_by_user_id(order_response: OrderResponse):
    mock_service = MockOrderService()

    mock_service._mock_get_by_user_id.return_value = [order_response]
    mock_service._mock_get_total_count.return_value = 1

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.get(
            f"/orders/get_user_orders/{order_response.user_id}?count=10&page=1"
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["orders"]) == 1
        assert data["orders"][0]["id"] == str(order_response.id)
        assert data["user_id"] == str(order_response.user_id)


@pytest.mark.asyncio
async def test_get_all_orders(order_response: OrderResponse):
    mock_service = MockOrderService()

    mock_service._mock_get_by_filter.return_value = [order_response]
    mock_service._mock_get_total_count.return_value = 1

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.get("/orders/get_all_orders?count=10&page=1")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["orders"]) == 1
        assert data["page"] == 1
        assert data["count"] == 10


@pytest.mark.asyncio
async def test_get_all_orders_with_filters(order_response: OrderResponse):
    mock_service = MockOrderService()

    mock_service._mock_get_by_filter.return_value = [order_response]
    mock_service._mock_get_total_count.return_value = 1

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.get(
            f"/orders/get_all_orders?"
            "count=5&page=2&"
            f"user_id={order_response.user_id}&"
            "status=pending&"
            "min_amount=10&"
            "max_amount=1000&"
            "created_after=2024-01-01T00:00:00&"
            "created_before=2024-12-31T23:59:59"
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["filters"]["user_id"] == str(order_response.user_id)
        assert data["filters"]["status"] == "pending"
        assert data["filters"]["min_amount"] == 10.0
        assert data["filters"]["max_amount"] == 1000.0


@pytest.mark.asyncio
async def test_create_order(order_create: OrderCreate, order_response: OrderResponse):
    mock_service = MockOrderService()

    mock_service._mock_validate_order_items.return_value = True
    mock_service._mock_create.return_value = order_response

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        request_data = order_create.model_dump()
        request_data["user_id"] = str(request_data["user_id"])
        request_data["delivery_address_id"] = str(request_data["delivery_address_id"])
        for item in request_data["items"]:
            item["product_id"] = str(item["product_id"])

        response = client.post("/orders/create_order", json=request_data)
        assert response.status_code == HTTP_201_CREATED
        assert response.json()["id"] == str(order_response.id)


@pytest.mark.asyncio
async def test_create_order_validation_error(order_create: OrderCreate):
    mock_service = MockOrderService()

    from litestar.exceptions import ValidationException

    mock_service._mock_validate_order_items.side_effect = ValidationException(
        detail="Order must contain at least one item"
    )

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        request_data = order_create.model_dump()
        request_data["user_id"] = str(request_data["user_id"])
        request_data["delivery_address_id"] = str(request_data["delivery_address_id"])
        for item in request_data["items"]:
            item["product_id"] = str(item["product_id"])

        response = client.post("/orders/create_order", json=request_data)
        assert response.status_code == 400
        assert "item" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_order(order_response: OrderResponse, order_update: OrderUpdate):
    mock_service = MockOrderService()

    mock_service._mock_update.return_value = order_response

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.put(
            f"/orders/update_order/{order_response.id}", json=order_update.model_dump()
        )
        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == str(order_response.id)


@pytest.mark.asyncio
async def test_update_order_not_found(order_update: OrderUpdate):
    from uuid import uuid4

    mock_service = MockOrderService()

    from litestar.exceptions import NotFoundException

    mock_service._mock_update.side_effect = NotFoundException(detail="Order not found")

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.put(
            f"/orders/update_order/{uuid4()}", json=order_update.model_dump()
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_order(order_response: OrderResponse):
    mock_service = MockOrderService()

    mock_service._mock_delete.return_value = None

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.delete(f"/orders/delete_order/{order_response.id}")
        assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_order_not_found():
    from uuid import uuid4

    mock_service = MockOrderService()

    from litestar.exceptions import NotFoundException

    mock_service._mock_delete.side_effect = NotFoundException(detail="Order not found")

    with create_test_client(
        route_handlers=[OrderController],
        dependencies={
            "order_service": Provide(lambda: mock_service, sync_to_thread=False)
        },
    ) as client:
        response = client.delete(f"/orders/delete_order/{uuid4()}")
        assert response.status_code == 404
