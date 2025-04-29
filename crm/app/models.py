from pydantic import BaseModel, EmailStr
from datetime import date

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    address: str

class CustomerOrderCreate(BaseModel):
    customer_id: str
    order_date: date
    order_amount: str
    order_status: int