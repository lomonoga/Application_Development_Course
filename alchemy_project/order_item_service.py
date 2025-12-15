from typing import List
from uuid import UUID

from litestar.exceptions import NotFoundException
from order_item_repository import OrderItemRepository
from schemas import OrderItemCreate, OrderItemResponse, OrderItemUpdate


class OrderItemService:
    def __init__(self, repository: OrderItemRepository):
        self.repository = repository

    async def get_by_order_id(self, order_id: UUID) -> List[OrderItemResponse]:
        """Получить товары в заказе"""
        order_items = await self.repository.get_by_order_id(order_id)
        return [OrderItemResponse.model_validate(item) for item in order_items]

    async def get_by_product_id(self, product_id: UUID) -> List[OrderItemResponse]:
        """Получить заказы, содержащие данный товар"""
        order_items = await self.repository.get_by_product_id(product_id)
        return [OrderItemResponse.model_validate(item) for item in order_items]

    async def create(self, order_item_data: OrderItemCreate) -> OrderItemResponse:
        """Создать товар в заказе"""
        order_item = await self.repository.create(order_item_data)
        return OrderItemResponse.model_validate(order_item)

    async def update(
        self, order_item_id: UUID, order_item_data: OrderItemUpdate
    ) -> OrderItemResponse:
        """Обновить товар в заказе"""
        order_item = await self.repository.update(order_item_id, order_item_data)
        if not order_item:
            raise NotFoundException(
                detail=f"Order item with ID {order_item_id} not found"
            )
        return OrderItemResponse.model_validate(order_item)

    async def delete(self, order_item_id: UUID) -> None:
        """Удалить товар из заказа"""
        success = await self.repository.delete(order_item_id)
        if not success:
            raise NotFoundException(
                detail=f"Order item with ID {order_item_id} not found"
            )

    async def update_quantity(
        self, order_item_id: UUID, quantity: int
    ) -> OrderItemResponse:
        """Обновить количество товара в заказе"""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        update_data = OrderItemUpdate(quantity=quantity)
        return await self.update(order_item_id, update_data)
