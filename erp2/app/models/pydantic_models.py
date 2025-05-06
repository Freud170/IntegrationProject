from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class OrderStatus(str, Enum):
    Processed = "Processed"
    Shipped = "Shipped"
    Cancelled = "Cancelled"

class ProductBase(BaseModel):
    product_id: str
    product_name: str
    supplier: Optional[str] = None
    cost_price: float
    retail_price: float
    stock_level: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    pass

class OrderBase(BaseModel):
    order_id: str
    customer_id: str
    product_id: str
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    order_status: OrderStatus
    shipping_date: Optional[date] = None

class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    product_id: str
    quantity: int
    order_status: str
    shipping_date: date

class StatusUpdate(BaseModel):
    order_id: str
    status: str