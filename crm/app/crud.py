from app.db import async_session, Customer, CustomerOrder
from app.models import CustomerCreate, CustomerOrderCreate
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
import uuid

async def create_customer(customer: CustomerCreate):
    async with async_session() as session:
        new_customer = Customer(
            customer_id=str(uuid.uuid4()),
            name=customer.name,
            email=customer.email,
            address=customer.address
        )
        session.add(new_customer)
        await session.commit()

async def create_customer_order(order: CustomerOrderCreate):
    async with async_session() as session:
        new_order = CustomerOrder(
            order_id=str(uuid.uuid4()),
            customer_id=order.customer_id,
            order_date=order.order_date,
            order_amount=order.order_amount,
            order_status=order.order_status
        )
        session.add(new_order)
        await session.commit()

# Richtig: Funktion ist jetzt global definiert
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
                "address": customer.address,
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