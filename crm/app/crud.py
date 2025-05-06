from app.db import async_session, Customer, CustomerOrder
from app.models import CustomerCreate, CustomerOrderCreate
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
import uuid
from datetime import datetime  

# Erstelle einen neuen Kunden in der Datenbank
async def create_customer(customer: CustomerCreate):

    async with async_session() as session:
        new_customer = Customer(
            customer_id=str(uuid.uuid4()),
            name=customer.name,
            email=customer.email,
            phone=customer.phone,  
            address=customer.address,
            preferred_contact_method=customer.preferred_contact_method  
        )
        session.add(new_customer)
        await session.commit()

# Erstelle eine neue Bestellung in der Datenbank
async def create_customer_order(order_data):

    async with async_session() as session:
        
        new_order = CustomerOrder(
            order_id=str(order_data["order_id"]),  
            customer_id=order_data["customer_id"],
            order_date=datetime.strptime(order_data["order_date"], "%Y-%m-%d").date(),
            order_amount=str(order_data["order_amount"]),
            order_status=int(order_data["order_status"])
        )
        session.add(new_order)
        await session.commit()

# Ändert status der Bestellung in der Datenbank
async def update_order_status(order_id: str, new_status: int):
    
    async with async_session() as session:
        result = await session.execute(
            select(CustomerOrder).where(CustomerOrder.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        if order:
            order.order_status = new_status
            await session.commit()

async def get_all_customers_with_orders():
    async with async_session() as session:
        result = await session.execute(
            select(Customer).options(joinedload(Customer.customer_orders))
        )
        customers = result.unique().scalars().all()
        return [
            {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,  
                "address": customer.address,
                "preferred_contact_method": customer.preferred_contact_method.value if customer.preferred_contact_method else None,  
                "orders": [
                    {
                        "order_id": order.order_id,
                        "order_date": order.order_date,
                        "order_amount": order.order_amount,
                        "order_status": order.order_status
                    }
                    for order in customer.customer_orders
                ]
            }
            for customer in customers
        ]