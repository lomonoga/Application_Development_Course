from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    email: str
    description: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsersResponse(BaseModel):
    users: list[UserResponse]
    total_count: int


class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str
    is_primary: bool = False


class AddressCreate(AddressBase):
    user_id: UUID


class AddressUpdate(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    is_primary: Optional[bool] = None


class AddressResponse(AddressBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str = Field(..., max_length=50)
    in_stock: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    in_stock: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    order_id: UUID


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)


class OrderItemResponse(OrderItemBase):
    id: UUID
    order_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: UUID
    delivery_address_id: UUID
    status: str = Field(default="pending", max_length=20)


class OrderCreate(OrderBase):
    items: List[OrderItemBase]


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=20)


class OrderResponse(OrderBase):
    id: UUID
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrdersResponse(BaseModel):
    orders: List[OrderResponse]
    total_count: int
