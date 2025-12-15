from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from tables import Product
from schemas import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        result = await self.session.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs) -> List[Product]:
        offset = (page - 1) * count
        query = select(Product)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(Product, key):
                    if key == 'price_min':
                        query = query.where(Product.price >= value)
                    elif key == 'price_max':
                        query = query.where(Product.price <= value)
                    elif key == 'name_query':
                        query = query.where(Product.name.ilike(f"%{value}%"))
                    else:
                        query = query.where(getattr(Product, key) == value)

        query = query.offset(offset).limit(count)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_in_stock(self, count: int = 10, page: int = 1) -> List[Product]:
        offset = (page - 1) * count
        result = await self.session.execute(
            select(Product)
            .where(Product.in_stock == True)
            .offset(offset)
            .limit(count)
        )
        return list(result.scalars().all())

    async def get_total_count(self, **kwargs) -> int:
        query = select(Product)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(Product, key):
                    if key == 'price_min':
                        query = query.where(Product.price >= value)
                    elif key == 'price_max':
                        query = query.where(Product.price <= value)
                    elif key == 'name_query':
                        query = query.where(Product.name.ilike(f"%{value}%"))
                    else:
                        query = query.where(getattr(Product, key) == value)

        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def create(self, product_data: ProductCreate) -> Product:
        try:
            product = Product(
                name=product_data.name,
                description=product_data.description,
                price=product_data.price,
                category=product_data.category,
                in_stock=product_data.in_stock
            )
            self.session.add(product)
            await self.session.commit()
            await self.session.refresh(product)
            return product
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update(self, product_id: UUID, product_data: ProductUpdate) -> Optional[Product]:
        try:
            product = await self.get_by_id(product_id)
            if not product:
                return None

            update_data = product_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(product, field, value)

            await self.session.commit()
            await self.session.refresh(product)
            return product
        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete(self, product_id: UUID) -> bool:
        try:
            product = await self.get_by_id(product_id)
            if not product:
                return False

            await self.session.delete(product)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e
