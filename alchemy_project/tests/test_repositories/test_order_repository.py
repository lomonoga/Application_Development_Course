import pytest
from uuid import uuid4

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from order_repository import OrderRepository
from user_repository import UserRepository
from product_repository import ProductRepository
from schemas import OrderCreate, OrderUpdate, OrderItemCreate, UserCreate, ProductCreate


class TestOrderRepository:
    @pytest.mark.asyncio
    async def test_create_order_with_multiple_products(
            self,
            order_repository: OrderRepository,
            user_repository: UserRepository,
            product_repository: ProductRepository
    ):
        user = await user_repository.create(UserCreate(
            email="test_order_user@example.com",
            username="order_user",
            description="For order test"
        ))

        product1 = await product_repository.create(ProductCreate(
            name="Ноутбук",
            description="Мощный ноутбук",
            price=50000.0,
            category="Электроника",
            in_stock=True
        ))

        product2 = await product_repository.create(ProductCreate(
            name="Мышь",
            description="Беспроводная мышь",
            price=2000.0,
            category="Аксессуары",
            in_stock=True
        ))

        fake_address_id = uuid4()
        order = await order_repository.create(OrderCreate(
            user_id=user.id,
            delivery_address_id=fake_address_id,
            status="pending",
            items=[
                OrderItemCreate(
                    product_id=product1.id,
                    quantity=1,
                    unit_price=product1.price,
                    order_id=fake_address_id
                ),
                OrderItemCreate(
                    product_id=product2.id,
                    quantity=2,
                    unit_price=product2.price,
                    order_id=fake_address_id
                )
            ]
        ))

        assert order.id is not None
        assert order.user_id == user.id
        assert order.status == "pending"
        assert order.delivery_address_id == fake_address_id
        assert order.total_amount == 54000.0

    @pytest.mark.asyncio
    async def test_get_order_by_id(
            self,
            order_repository: OrderRepository,
            user_repository: UserRepository,
            product_repository: ProductRepository
    ):
        user = await user_repository.create(UserCreate(
            email="get_order@example.com",
            username="get_order_user",
            description="For get test"
        ))

        product = await product_repository.create(ProductCreate(
            name="Клавиатура",
            description="Механическая клавиатура",
            price=5000.0,
            category="Электроника",
            in_stock=True
        ))

        fake_address_id = uuid4()
        created_order = await order_repository.create(OrderCreate(
            user_id=user.id,
            delivery_address_id=fake_address_id,
            status="processing",
            items=[OrderItemCreate(
                product_id=product.id,
                quantity=1,
                unit_price=product.price,
                order_id=fake_address_id
            )]
        ))

        found_order = await order_repository.get_by_id(created_order.id)

        assert found_order is not None
        assert found_order.id == created_order.id
        assert found_order.user_id == user.id
        assert found_order.status == "processing"
        assert found_order.delivery_address_id == fake_address_id

    @pytest.mark.asyncio
    async def test_update_order(
            self,
            order_repository: OrderRepository,
            user_repository: UserRepository,
            product_repository: ProductRepository
    ):
        user = await user_repository.create(UserCreate(
            email="update_order@example.com",
            username="update_user",
            description="For update test"
        ))

        product = await product_repository.create(ProductCreate(
            name="Монитор",
            description="27-дюймовый монитор",
            price=15000.0,
            category="Электроника",
            in_stock=True
        ))

        fake_address_id = uuid4()
        order = await order_repository.create(OrderCreate(
            user_id=user.id,
            delivery_address_id=fake_address_id,
            status="pending",
            items=[OrderItemCreate(
                product_id=product.id,
                quantity=1,
                unit_price=product.price,
                order_id=fake_address_id
            )]
        ))

        updated_order = await order_repository.update(
            order.id,
            OrderUpdate(status="completed")
        )

        assert updated_order is not None
        assert updated_order.id == order.id
        assert updated_order.status == "completed"
        assert updated_order.user_id == user.id
        assert updated_order.delivery_address_id == fake_address_id

    @pytest.mark.asyncio
    async def test_get_orders_list(
            self,
            order_repository: OrderRepository,
            user_repository: UserRepository,
            product_repository: ProductRepository
    ):
        user = await user_repository.create(UserCreate(
            email="list_orders@example.com",
            username="list_user",
            description="For list test"
        ))

        product = await product_repository.create(ProductCreate(
            name="Наушники",
            description="Беспроводные наушники",
            price=3000.0,
            category="Аудио",
            in_stock=True
        ))

        fake_address_id = uuid4()
        for i in range(3):
            await order_repository.create(OrderCreate(
                user_id=user.id,
                delivery_address_id=fake_address_id,
                status="pending",
                items=[OrderItemCreate(
                    product_id=product.id,
                    quantity=i + 1,
                    unit_price=product.price,
                    order_id=fake_address_id
                )]
            ))

        orders = await order_repository.get_by_user_id(user.id, count=10, page=1)

        assert len(orders) >= 3
        for order in orders:
            assert order.user_id == user.id
            assert order.status == "pending"
            assert order.delivery_address_id == fake_address_id

    @pytest.mark.asyncio
    async def test_delete_order(
            self,
            order_repository: OrderRepository,
            user_repository: UserRepository,
            product_repository: ProductRepository
    ):
        user = await user_repository.create(UserCreate(
            email="delete_order@example.com",
            username="delete_user",
            description="For delete test"
        ))

        product = await product_repository.create(ProductCreate(
            name="Камера",
            description="Цифровая камера",
            price=25000.0,
            category="Фото",
            in_stock=True
        ))

        fake_address_id = uuid4()
        order = await order_repository.create(OrderCreate(
            user_id=user.id,
            delivery_address_id=fake_address_id,
            status="pending",
            items=[OrderItemCreate(
                product_id=product.id,
                quantity=1,
                unit_price=product.price,
                order_id=fake_address_id
            )]
        ))

        deleted = await order_repository.delete(order.id)

        assert deleted is True

        found_order = await order_repository.get_by_id(order.id)
        assert found_order is None

    @pytest.mark.asyncio
    async def test_update_order_status(
            self,
            order_repository: OrderRepository,
            user_repository: UserRepository,
            product_repository: ProductRepository
    ):
        user = await user_repository.create(UserCreate(
            email="status_order@example.com",
            username="status_user",
            description="For status test"
        ))

        product = await product_repository.create(ProductCreate(
            name="Телефон",
            description="Смартфон",
            price=40000.0,
            category="Электроника",
            in_stock=True
        ))

        fake_address_id = uuid4()
        order = await order_repository.create(OrderCreate(
            user_id=user.id,
            delivery_address_id=fake_address_id,
            status="pending",
            items=[OrderItemCreate(
                product_id=product.id,
                quantity=1,
                unit_price=product.price,
                order_id=fake_address_id
            )]
        ))

        updated_order = await order_repository.update_status(order.id, "shipped")

        assert updated_order is not None
        assert updated_order.id == order.id
        assert updated_order.status == "shipped"
