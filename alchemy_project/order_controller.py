from datetime import datetime
from typing import Optional
from uuid import UUID

from litestar import Controller, delete, get, post, put
from litestar.params import Body, Parameter
from order_service import OrderService
from schemas import OrderCreate, OrderResponse, OrderUpdate


class OrderController(Controller):
    path = "/orders"
    tags = ["Order Management"]

    @get("/get_order/{order_id:uuid}")
    async def get_order_by_id(
        self, order_service: OrderService, order_id: UUID
    ) -> OrderResponse:
        """Get order by ID with all details"""
        return await order_service.get_by_id(order_id, include_relations=True)

    @get("/get_user_orders/{user_id:uuid}")
    async def get_orders_by_user_id(
        self,
        order_service: OrderService,
        user_id: UUID,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(gt=0, default=1),
    ) -> dict:
        """Get all orders for a specific user"""
        orders = await order_service.get_by_user_id(user_id, count, page)
        total_count = await order_service.get_total_count(user_id=user_id)

        return {
            "orders": orders,
            "total_count": total_count,
            "user_id": user_id,
            "page": page,
            "count": count,
        }

    @get("/get_all_orders")
    async def get_all_orders(
        self,
        order_service: OrderService,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(gt=0, default=1),
        user_id: Optional[UUID] = Parameter(default=None),
        status: Optional[str] = Parameter(default=None),
        min_amount: Optional[float] = Parameter(default=None, ge=0),
        max_amount: Optional[float] = Parameter(default=None, ge=0),
        created_after: Optional[datetime] = Parameter(default=None),
        created_before: Optional[datetime] = Parameter(default=None),
    ) -> dict:
        """Get all orders with pagination and filtering"""
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if status:
            filters["status"] = status
        if min_amount is not None:
            filters["min_amount"] = min_amount
        if max_amount is not None:
            filters["max_amount"] = max_amount
        if created_after:
            filters["created_after"] = created_after
        if created_before:
            filters["created_before"] = created_before

        orders = await order_service.get_by_filter(count=count, page=page, **filters)
        total_count = await order_service.get_total_count(**filters)

        return {
            "orders": orders,
            "total_count": total_count,
            "page": page,
            "count": count,
            "filters": filters,
        }

    @post("/create_order")
    async def create_order(
        self,
        order_service: OrderService,
        data: OrderCreate = Body(media_type="application/json"),
    ) -> OrderResponse:
        """Create a new order"""
        await order_service.validate_order_items(data.items)
        return await order_service.create(data)

    @put("/update_order/{order_id:uuid}")
    async def update_order(
        self,
        order_service: OrderService,
        order_id: UUID,
        data: OrderUpdate = Body(media_type="application/json"),
    ) -> OrderResponse:
        """Update order"""
        return await order_service.update(order_id, data)

    @delete("/delete_order/{order_id:uuid}")
    async def delete_order(self, order_service: OrderService, order_id: UUID) -> None:
        """Delete order"""
        await order_service.delete(order_id)
