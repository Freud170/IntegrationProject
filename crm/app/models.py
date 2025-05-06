from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from enum import Enum

class PreferredContactMethod(str, Enum):
    Email = "Email"
    Telefon = "Telefon"

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]  
    address: str
    preferred_contact_method: Optional[PreferredContactMethod]  

class CustomerOrderCreate(BaseModel):
    order_id: str  
    customer_id: str
    order_date: str
    order_amount: str
    order_status: int