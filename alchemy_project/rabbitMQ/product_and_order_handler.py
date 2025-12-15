import os

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from address_repository import AddressRepository
from address_service import AddressService
from order_service import OrderService
from product_service import ProductService
from order_repository import OrderRepository
from product_repository import ProductRepository
from schemas import OrderCreate, OrderUpdate, ProductCreate, ProductUpdate, UserCreate, AddressCreate
import asyncio

from user_repository import UserRepository
from user_service import UserService

broker = RabbitBroker("amqp://guest:guest@localhost:5672/local")
app = FastStream(broker)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
)
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@broker.subscriber("product")
async def handle_product(product_data: dict):
    session = None
    try:
        session = async_session()

        product_repo = ProductRepository(session)
        product_service = ProductService(product_repo)

        action = product_data.get("action")

        if action == "create":
            product_create = ProductCreate(**product_data["data"])
            result = await product_service.create(product_create)
            await session.commit()
            return {"success": True, "product_id": str(result.id)}

        elif action == "update":
            if "in_stock" in product_data["data"] and not product_data["data"]["in_stock"]:
                product = await product_service.get_by_id(product_data["product_id"])
                await broker.publish({
                    "type": "out_of_stock",
                    "product_id": product_data["product_id"],
                    "product_name": product.name
                }, "notifications")

            product_update = ProductUpdate(**product_data["data"])
            await product_service.update(product_data["product_id"], product_update)
            await session.commit()
            return {"success": True}

        elif action == "delete":
            await product_service.delete(product_data["product_id"])
            await session.commit()
            return {"success": True}

        else:
            return {"error": f"Unknown action: {action}"}

    except Exception as e:
        if session:
            await session.rollback()
        return {"error": str(e)}
    finally:
        if session:
            await session.close()


@broker.subscriber("order")
async def handle_order(order_data: dict):
    session = None
    try:
        session = async_session()

        order_repo = OrderRepository(session)
        order_service = OrderService(order_repo)
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)
        address_repository = AddressRepository(session)
        address_service = AddressService(address_repository)

        action = order_data.get("action")

        if action == "create":
            data = order_data["data"]

            if not data.get("user_id"):
                user = await user_service.create(UserCreate(username='username', email='email'))
                data["user_id"] = user.id

            if not data.get("delivery_address_id") and data.get("user_id"):
                address = await address_service.create(AddressCreate(user_id=data["user_id"], street='street',
                                                                     city='city', state='state',
                                                                     zip_code='zip_code', country='country'))
            data["delivery_address_id"] = address.id

            order_create = OrderCreate(**order_data["data"])

            result = await order_service.create(order_create)
            await session.commit()
            return {"success": True, "order_id": str(result.id)}

        elif action == "update":
            order_update = OrderUpdate(**order_data["data"])
            await order_service.update(order_data["order_id"], order_update)
            await session.commit()
            return {"success": True}

        elif action == "delete":
            await order_service.delete(order_data["order_id"])
            await session.commit()
            return {"success": True}

        else:
            return {"error": f"Unknown action: {action}"}

    except Exception as e:
        if session:
            await session.rollback()
        return {"error": str(e)}
    finally:
        if session:
            await session.close()


if __name__ == "__main__":
    asyncio.run(app.run())
