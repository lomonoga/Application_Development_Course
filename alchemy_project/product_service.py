from typing import List
from uuid import UUID

from litestar.exceptions import NotFoundException
from product_repository import ProductRepository
from schemas import ProductCreate, ProductResponse, ProductUpdate


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def get_by_id(self, product_id: UUID) -> ProductResponse:
        """Получить продукт по ID"""
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")
        return ProductResponse.model_validate(product)

    async def get_by_filter(
        self, count: int = 10, page: int = 1, **kwargs
    ) -> List[ProductResponse]:
        """Получить продукты с фильтрацией"""
        products = await self.repository.get_by_filter(count=count, page=page, **kwargs)
        return [ProductResponse.model_validate(product) for product in products]

    async def get_total_count(self, **kwargs) -> int:
        """Получить общее количество продуктов"""
        return await self.repository.get_total_count(**kwargs)

    async def create(self, product_data: ProductCreate) -> ProductResponse:
        """Создать новый продукт"""
        product = await self.repository.create(product_data)
        return ProductResponse.model_validate(product)

    async def update(
        self, product_id: UUID, product_data: ProductUpdate
    ) -> ProductResponse:
        """Обновить продукт"""
        product = await self.repository.update(product_id, product_data)
        if not product:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")
        return ProductResponse.model_validate(product)

    async def delete(self, product_id: UUID) -> None:
        """Удалить продукт"""
        success = await self.repository.delete(product_id)
        if not success:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")
