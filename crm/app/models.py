from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from enum import Enum

# Enum für PreferredContactMethod
class PreferredContactMethod(str, Enum):
    Email = "Email"
    Telefon = "Telefon"

# Pydantic-Modell für die Validierung der Daten
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str]  
    address: str
    preferred_contact_method: Optional[PreferredContactMethod]  

# Pydantic-Modell für die Validierung der Bestelldaten
class CustomerOrderCreate(BaseModel):
    order_id: str  
    customer_id: str
    order_date: date
    order_amount: str
    order_status: int