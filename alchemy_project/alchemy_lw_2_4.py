from sqlalchemy import select
from sqlalchemy.orm import selectinload

from alchemy_lw_2 import session_factory
from tables import User, Address, Product, Order, OrderItem


def seed_data():
    with session_factory() as session:
        users = session.execute(select(User).options(selectinload(User.addresses))).scalars().all()

        addresses = [
            Address(
                user_id=users[0].id,
                street="ул. Ленина 15",
                city="Москва",
                state="НСК",
                zip_code="101000",
                country="Китай"
            ),
            Address(
                user_id=users[0].id,
                street="ул. Ленина 16",
                city="Москва",
                state="НСК",
                zip_code="101001",
                country="НеГрози"
            ),
            Address(
                user_id=users[1].id,
                street="ул. Ленина 17",
                city="Москва",
                state="НСК",
                zip_code="101002",
                country="ЮжномуЦентралу"
            ),
            Address(
                user_id=users[2].id,
                street="ул. Ленина 18",
                city="Москва",
                state="НСК",
                zip_code="101003",
                country="ПопиваяСок"
            ),
            Address(
                user_id=users[3].id,
                street="ул. Ленина 19",
                city="Москва",
                state="НСК",
                zip_code="101004",
                country="УСебяВКвартале"
            ),
            Address(
                user_id=users[4].id,
                street="ул. Ленина 20",
                city="Москва",
                state="НСК",
                zip_code="101005",
                country="Казахстан",
                is_primary=True
            ),
        ]
        session.add_all(addresses)
        session.flush()

        products = [
            Product(
                name="Ноутбук",
                description="Что-то там",
                price=9999.99,
                category="Электроника"
            ),
            Product(
                name="Ноутбук 2",
                description="Что-то там",
                price=999.99,
                category="Электроника"
            ),
            Product(
                name="Ноутбук 3",
                description="Что-то там",
                price=99.99,
                category="Электроника"
            ),
            Product(
                name="Ноутбук 4",
                description="Что-то там",
                price=9.99,
                category="Электроника"
            ),
            Product(
                name="Ноутбук 5",
                description="Что-то там",
                price=0.99,
                category="Электроника"
            ),
        ]
        session.add_all(products)
        session.flush()

        orders = [
            Order(user_id=users[0].id, delivery_address_id=addresses[0].id, status="completed", total_amount=9999.99),
            Order(user_id=users[1].id, delivery_address_id=addresses[2].id, status="pending", total_amount=999.99),
            Order(user_id=users[2].id, delivery_address_id=addresses[3].id, status="completed", total_amount=99.99),
            Order(user_id=users[3].id, delivery_address_id=addresses[4].id, status="completed", total_amount=9.99),
            Order(user_id=users[4].id, delivery_address_id=addresses[5].id, status="pending", total_amount=0.99),
        ]
        session.add_all(orders)
        session.flush()

        order_items = [
            OrderItem(order_id=orders[0].id, product_id=products[0].id, quantity=1, unit_price=9999.99),
            OrderItem(order_id=orders[1].id, product_id=products[1].id, quantity=1, unit_price=999.99),
            OrderItem(order_id=orders[1].id, product_id=products[3].id, quantity=1, unit_price=99.99),
            OrderItem(order_id=orders[2].id, product_id=products[2].id, quantity=1, unit_price=9.99),
            OrderItem(order_id=orders[3].id, product_id=products[3].id, quantity=1, unit_price=0.99),
            OrderItem(order_id=orders[4].id, product_id=products[4].id, quantity=1, unit_price=99999.99),
        ]
        session.add_all(order_items)

        session.commit()


seed_data()
