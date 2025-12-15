from uuid import UUID
from typing import List
from order_repository import OrderRepository
from schemas import OrderCreate, OrderUpdate, OrderResponse, OrderItemBase
from litestar.exceptions import NotFoundException, ValidationException


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    async def get_by_id(self, order_id: UUID, include_relations: bool = True) -> OrderResponse:
        """Получить заказ по ID"""
        order = await self.repository.get_by_id(order_id, include_relations)
        if not order:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")
        return OrderResponse.model_validate(order)

    async def get_by_user_id(
            self,
            user_id: UUID,
            count: int = 10,
            page: int = 1
    ) -> List[OrderResponse]:
        """Получить заказы пользователя"""
        orders = await self.repository.get_by_user_id(user_id, count, page)
        return [OrderResponse.model_validate(order) for order in orders]

    async def get_by_filter(
            self,
            count: int = 10,
            page: int = 1,
            **kwargs
    ) -> List[OrderResponse]:
        """Получить заказы с фильтрацией"""
        orders = await self.repository.get_by_filter(count=count, page=page, **kwargs)
        return [OrderResponse.model_validate(order) for order in orders]

    async def get_total_count(self, **kwargs) -> int:
        """Получить общее количество заказов"""
        return await self.repository.get_total_count(**kwargs)

    async def create(self, order_data: OrderCreate) -> OrderResponse:
        """Создать новый заказ"""
        order = await self.repository.create(order_data)
        return OrderResponse.model_validate(order)

    async def update(self, order_id: UUID, order_data: OrderUpdate) -> OrderResponse:
        """Обновить заказ"""
        order = await self.repository.update(order_id, order_data)
        if not order:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")
        return OrderResponse.model_validate(order)

    async def delete(self, order_id: UUID) -> None:
        """Удалить заказ"""
        success = await self.repository.delete(order_id)
        if not success:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")

    async def validate_order_items(self, items: List[OrderItemBase]) -> bool:
        """Валидация товаров в заказе"""
        if not items:
            raise ValidationException(detail="Order must contain at least one item")

        return True