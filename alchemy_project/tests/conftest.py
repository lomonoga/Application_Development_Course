import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

try:
    from base import Base
except ImportError:
    try:
        from tables import Base
    except ImportError:
        from sqlalchemy.orm import declarative_base

        Base = declarative_base()

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Создаем асинхронный движок для тестовой базы"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session(engine):
    """Создаем асинхронную сессию для тестов"""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
async def user_repository(session):
    """Фикстура для репозитория пользователей"""
    from user_repository import UserRepository
    return UserRepository(session)


@pytest.fixture
async def product_repository(session):
    """Фикстура для репозитория продуктов"""
    from product_repository import ProductRepository
    return ProductRepository(session)


@pytest.fixture
async def order_repository(session):
    """Фикстура для репозитория заказов"""
    from order_repository import OrderRepository
    return OrderRepository(session)
