# app/models.py

from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class OrderCreate(BaseModel):
    """
    Request-Body für das Anlegen einer Bestellung.
    """
    customer_id: str
    email: EmailStr
    address: str
    product_id: str
    quantity: int
    payment_method: str

class OrderResponse(BaseModel):
    """
    Antwort-Body nach Erstellen oder Abrufen einer Bestellung.
    """
    order_id: str
    delivery_date: date
    delivery_status: str  # (Processing, Shipped oder Delivered)

class ProductCreate(BaseModel):
    """
    Request-Body für das Anlegen eines Produkts.
    """
    product_id: str
    product_name: str
    category: str
    price: float
    stock_quantity: int