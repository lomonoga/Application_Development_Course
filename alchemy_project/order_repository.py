from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import List, Optional
from tables import Order, OrderItem, Product
from schemas import OrderCreate, OrderUpdate, OrderItemCreate


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: UUID, include_relations: bool = False) -> Optional[Order]:
        query = select(Order).where(Order.id == order_id)

        if include_relations:
            query = query.options(
                joinedload(Order.user),
                joinedload(Order.delivery_address),
                joinedload(Order.order_items).joinedload(OrderItem.product)
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID, count: int = 10, page: int = 1) -> List[Order]:
        offset = (page - 1) * count
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(count)
        )
        return list(result.scalars().all())

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs) -> List[Order]:
        offset = (page - 1) * count
        query = select(Order)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(Order, key):
                    if key == 'created_after':
                        query = query.where(Order.created_at >= value)
                    elif key == 'created_before':
                        query = query.where(Order.created_at <= value)
                    elif key == 'min_amount':
                        query = query.where(Order.total_amount >= value)
                    elif key == 'max_amount':
                        query = query.where(Order.total_amount <= value)
                    else:
                        query = query.where(getattr(Order, key) == value)

        query = query.order_by(Order.created_at.desc()).offset(offset).limit(count)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_total_count(self, **kwargs) -> int:
        query = select(Order)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(Order, key):
                    if key == 'created_after':
                        query = query.where(Order.created_at >= value)
                    elif key == 'created_before':
                        query = query.where(Order.created_at <= value)
                    elif key == 'min_amount':
                        query = query.where(Order.total_amount >= value)
                    elif key == 'max_amount':
                        query = query.where(Order.total_amount <= value)
                    else:
                        query = query.where(getattr(Order, key) == value)

        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def create(self, order_data: OrderCreate) -> Order:
        # Создаем заказ
        order = Order(
            user_id=order_data.user_id,
            delivery_address_id=order_data.delivery_address_id,
            status=order_data.status,
            total_amount=0.0  # Рассчитаем ниже
        )
        self.session.add(order)
        await self.session.flush()  # Получаем order.id

        # Добавляем товары в заказ
        total_amount = 0.0
        for item_data in order_data.items:
            # Получаем текущую цену товара
            product_result = await self.session.execute(
                select(Product).where(Product.id == item_data.product_id)
            )
            product = product_result.scalar_one()

            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.price
            )
            self.session.add(order_item)
            total_amount += product.price * item_data.quantity

        # Обновляем общую сумму заказа
        order.total_amount = total_amount

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update(self, order_id: UUID, order_data: OrderUpdate) -> Optional[Order]:
        order = await self.get_by_id(order_id)
        if not order:
            return None

        update_data = order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def delete(self, order_id: UUID) -> bool:
        order = await self.get_by_id(order_id)
        if not order:
            return False

        await self.session.delete(order)
        await self.session.commit()
        return True

    async def update_status(self, order_id: UUID, status: str) -> Optional[Order]:
        order = await self.get_by_id(order_id)
        if not order:
            return None

        order.status = status
        await self.session.commit()
        await self.session.refresh(order)
        return order
