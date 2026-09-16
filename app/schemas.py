from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import UserRole, OrderStatus


# ---------- Users ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.staff


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime


# ---------- Products ----------

class ProductCreate(BaseModel):
    sku: str
    name: str
    price: Decimal
    stock_quantity: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    price: Decimal
    stock_quantity: int
    created_at: datetime


# ---------- Orders ----------

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemOut] = []
