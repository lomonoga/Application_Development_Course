from litestar import Controller, get, post, put, delete
from litestar.params import Parameter, Body
from uuid import UUID
from typing import Optional

from product_service import ProductService
from schemas import ProductCreate, ProductUpdate, ProductResponse


class ProductController(Controller):
    path = "/products"
    tags = ["Product Management"]

    @get("/get_product/{product_id:uuid}")
    async def get_product_by_id(
            self,
            product_service: ProductService,
            product_id: UUID
    ) -> ProductResponse:
        """Get product by ID"""
        return await product_service.get_by_id(product_id)

    @get("/get_all_products")
    async def get_all_products(
            self,
            product_service: ProductService,
            count: int = Parameter(gt=0, le=100, default=10),
            page: int = Parameter(gt=0, default=1),
            category: Optional[str] = Parameter(default=None),
            in_stock: Optional[bool] = Parameter(default=None),
            price_min: Optional[float] = Parameter(default=None, ge=0),
            price_max: Optional[float] = Parameter(default=None, ge=0)
    ) -> dict:
        """Get all products with pagination and filtering"""
        filters = {}
        if category:
            filters['category'] = category
        if in_stock is not None:
            filters['in_stock'] = in_stock
        if price_min is not None:
            filters['price_min'] = price_min
        if price_max is not None:
            filters['price_max'] = price_max

        products = await product_service.get_by_filter(
            count=count,
            page=page,
            **filters
        )
        total_count = await product_service.get_total_count(**filters)

        return {
            "products": products,
            "total_count": total_count,
            "page": page,
            "count": count,
            "filters": filters
        }

    @post("/create_product")
    async def create_product(
            self,
            product_service: ProductService,
            data: ProductCreate = Body(media_type="application/json")
    ) -> ProductResponse:
        """Create a new product"""
        return await product_service.create(data)

    @put("/update_product/{product_id:uuid}")
    async def update_product(
            self,
            product_service: ProductService,
            product_id: UUID,
            data: ProductUpdate = Body(media_type="application/json")
    ) -> ProductResponse:
        """Update product"""
        return await product_service.update(product_id, data)

    @delete("/delete_product/{product_id:uuid}")
    async def delete_product(
            self,
            product_service: ProductService,
            product_id: UUID
    ) -> None:
        """Delete product"""
        await product_service.delete(product_id)
