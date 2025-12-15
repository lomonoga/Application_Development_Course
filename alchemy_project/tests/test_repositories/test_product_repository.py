import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from product_repository import ProductRepository
from schemas import ProductCreate, ProductUpdate


class TestProductRepository:
    @pytest.mark.asyncio
    async def test_create_product(self, product_repository: ProductRepository):
        product = await product_repository.create(
            ProductCreate(
                name="Тестовый продукт",
                description="Описание тестового продукта",
                price=100.50,
                category="Категория",
                in_stock=True,
            )
        )

        assert product.id is not None
        assert product.name == "Тестовый продукт"
        assert product.description == "Описание тестового продукта"
        assert product.price == 100.50
        assert product.category == "Категория"
        assert product.in_stock == True

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, product_repository: ProductRepository):
        created_product = await product_repository.create(
            ProductCreate(
                name="Продукт для поиска",
                description="Будем искать по ID",
                price=50.0,
                category="Электроника",
                in_stock=True,
            )
        )

        found_product = await product_repository.get_by_id(created_product.id)

        assert found_product is not None
        assert found_product.id == created_product.id
        assert found_product.name == "Продукт для поиска"
        assert found_product.price == 50.0
        assert found_product.category == "Электроника"

    @pytest.mark.asyncio
    async def test_update_product(self, product_repository: ProductRepository):
        product = await product_repository.create(
            ProductCreate(
                name="Старое название",
                description="Старое описание",
                price=10.0,
                category="Категория 1",
                in_stock=True,
            )
        )

        updated_product = await product_repository.update(
            product.id,
            ProductUpdate(name="Новое название", price=20.0, category="Категория 2"),
        )

        assert updated_product is not None
        assert updated_product.id == product.id
        assert updated_product.name == "Новое название"
        assert updated_product.price == 20.0
        assert updated_product.category == "Категория 2"
        assert updated_product.description == "Старое описание"
        assert updated_product.in_stock == True

    @pytest.mark.asyncio
    async def test_get_all_products(self, product_repository: ProductRepository):
        await product_repository.create(
            ProductCreate(
                name="Продукт 1",
                description="Описание 1",
                price=10.0,
                category="Категория А",
                in_stock=True,
            )
        )

        await product_repository.create(
            ProductCreate(
                name="Продукт 2",
                description="Описание 2",
                price=20.0,
                category="Категория Б",
                in_stock=False,
            )
        )

        products = await product_repository.get_by_filter()

        assert len(products) >= 2

    @pytest.mark.asyncio
    async def test_delete_product(self, product_repository: ProductRepository):
        product = await product_repository.create(
            ProductCreate(
                name="Удаляемый продукт",
                description="Будет удален",
                price=30.0,
                category="Тестовая категория",
                in_stock=True,
            )
        )

        deleted = await product_repository.delete(product.id)

        assert deleted is True

        found_product = await product_repository.get_by_id(product.id)
        assert found_product is None

    @pytest.mark.asyncio
    async def test_get_by_filter_name(self, product_repository: ProductRepository):
        await product_repository.create(
            ProductCreate(
                name="Уникальное имя продукта",
                description="Тестовый продукт",
                price=100.0,
                category="Тест",
                in_stock=True,
            )
        )

        products = await product_repository.get_by_filter(
            name="Уникальное имя продукта"
        )

        assert len(products) >= 1
        assert products[0].name == "Уникальное имя продукта"

    @pytest.mark.asyncio
    async def test_get_by_filter_category(self, product_repository: ProductRepository):
        await product_repository.create(
            ProductCreate(
                name="Продукт в категории",
                description="Тестовый продукт",
                price=100.0,
                category="Спецкатегория",
                in_stock=True,
            )
        )

        products = await product_repository.get_by_filter(category="Спецкатегория")

        assert len(products) >= 1
        assert products[0].category == "Спецкатегория"

    @pytest.mark.asyncio
    async def test_get_total_count(self, product_repository: ProductRepository):
        initial_count = await product_repository.get_total_count()

        await product_repository.create(
            ProductCreate(
                name="Продукт для подсчета",
                description="Тестовый продукт",
                price=50.0,
                category="Тест",
                in_stock=True,
            )
        )

        new_count = await product_repository.get_total_count()

        assert new_count >= initial_count + 1

    @pytest.mark.asyncio
    async def test_get_total_count_with_filter(
        self, product_repository: ProductRepository
    ):
        await product_repository.create(
            ProductCreate(
                name="Фильтруемый продукт",
                description="Тестовый продукт",
                price=100.0,
                category="Особая категория",
                in_stock=True,
            )
        )

        count = await product_repository.get_total_count(category="Особая категория")

        assert count >= 1

    @pytest.mark.asyncio
    async def test_update_product_in_stock(self, product_repository: ProductRepository):
        product = await product_repository.create(
            ProductCreate(
                name="Продукт для обновления",
                description="Тестовый продукт",
                price=100.0,
                category="Тест",
                in_stock=True,
            )
        )

        updated_product = await product_repository.update(
            product.id, ProductUpdate(in_stock=False)
        )

        assert updated_product is not None
        assert updated_product.id == product.id
        assert updated_product.in_stock == False
        assert updated_product.name == "Продукт для обновления"
        assert updated_product.price == 100.0

    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(
        self, product_repository: ProductRepository
    ):
        import uuid

        random_id = uuid.uuid4()

        product = await product_repository.get_by_id(random_id)

        assert product is None
