from typing import List
from uuid import UUID

from schemas import OrderItemCreate, OrderItemUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from tables import OrderItem


class OrderItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_order_id(self, order_id: UUID) -> List[OrderItem]:
        result = await self.session.execute(
            select(OrderItem)
            .options(joinedload(OrderItem.product))
            .where(OrderItem.order_id == order_id)
        )
        return list(result.scalars().all())

    async def get_by_product_id(self, product_id: UUID) -> List[OrderItem]:
        result = await self.session.execute(
            select(OrderItem).where(OrderItem.product_id == product_id)
        )
        return list(result.scalars().all())

    async def create(self, order_item_data: OrderItemCreate) -> OrderItem:
        order_item = OrderItem(
            order_id=order_item_data.order_id,
            product_id=order_item_data.product_id,
            quantity=order_item_data.quantity,
            unit_price=order_item_data.unit_price,
        )
        self.session.add(order_item)
        await self.session.commit()
        await self.session.refresh(order_item)
        return order_item

    async def update(
        self, order_item_id: UUID, order_item_data: OrderItemUpdate
    ) -> OrderItem:
        order_item = await self.session.get(OrderItem, order_item_id)
        if not order_item:
            return None

        update_data = order_item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order_item, field, value)

        await self.session.commit()
        await self.session.refresh(order_item)
        return order_item

    async def delete(self, order_item_id: UUID) -> bool:
        order_item = await self.session.get(OrderItem, order_item_id)
        if not order_item:
            return False

        await self.session.delete(order_item)
        await self.session.commit()
        return True
