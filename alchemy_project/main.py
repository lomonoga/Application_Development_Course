import os

from address_controller import AddressController
from address_repository import AddressRepository
from address_service import AddressService
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig
from order_controller import OrderController
from order_item_repository import OrderItemRepository
from order_item_service import OrderItemService
from order_repository import OrderRepository
from order_service import OrderService
from product_controller import ProductController
from product_repository import ProductRepository
from product_service import ProductService
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from user_controller import UserController
from user_repository import UserRepository
from user_service import UserService

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def provide_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)


async def provide_user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)


async def provide_address_repository(db_session: AsyncSession) -> AddressRepository:
    return AddressRepository(db_session)


async def provide_address_service(
    address_repository: AddressRepository,
) -> AddressService:
    return AddressService(address_repository)


async def provide_product_repository(db_session: AsyncSession) -> ProductRepository:
    return ProductRepository(db_session)


async def provide_product_service(
    product_repository: ProductRepository,
) -> ProductService:
    return ProductService(product_repository)


async def provide_order_repository(db_session: AsyncSession) -> OrderRepository:
    return OrderRepository(db_session)


async def provide_order_service(order_repository: OrderRepository) -> OrderService:
    return OrderService(order_repository)


async def provide_order_item_repository(
    db_session: AsyncSession,
) -> OrderItemRepository:
    return OrderItemRepository(db_session)


async def provide_order_item_service(
    order_item_repository: OrderItemRepository,
) -> OrderItemService:
    return OrderItemService(order_item_repository)


cors_config = CORSConfig(
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001, http://localhost:6379", "http://127.0.0.1:6379"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = Litestar(
    route_handlers=[
        UserController,
        AddressController,
        ProductController,
        OrderController,
    ],
    dependencies={
        # DB session
        "db_session": Provide(provide_db_session),
        # User dependencies
        "user_repository": Provide(provide_user_repository),
        "user_service": Provide(provide_user_service),
        # Address dependencies
        "address_repository": Provide(provide_address_repository),
        "address_service": Provide(provide_address_service),
        # Product dependencies
        "product_repository": Provide(provide_product_repository),
        "product_service": Provide(provide_product_service),
        # Order dependencies
        "order_repository": Provide(provide_order_repository),
        "order_service": Provide(provide_order_service),
        # OrderItem dependencies
        "order_item_repository": Provide(provide_order_item_repository),
        "order_item_service": Provide(provide_order_item_service),
    },
    cors_config=cors_config,
    openapi_config=OpenAPIConfig(
        title="API",
        version="1.0.0",
        description="Full-featured API with users, products, addresses, and orders",
        tags=[
            {"name": "User Management", "description": "User management operations"},
            {"name": "Address Management", "description": "User address management"},
            {"name": "Product Management", "description": "Product catalog management"},
            {
                "name": "Order Management",
                "description": "Order processing and management",
            },
        ],
    ),
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
