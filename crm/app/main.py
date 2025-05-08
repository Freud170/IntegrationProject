from fastapi import FastAPI
from app.models import CustomerCreate, CustomerOrderCreate
from app import crud, db
import asyncio
from app.crud import get_all_customers_with_orders
from app.rabbitmq_consumer import consume_order_updates, consume_status_updates  # Importiere den Consumer

app = FastAPI()
loop = asyncio.get_event_loop()

@app.on_event("startup")
async def startup_event():
    await db.init_db()
    # Startet die RabbitMQ-Consumer
    loop.create_task(consume_status_updates())
    loop.create_task(consume_order_updates())

@app.post("/customers")
async def create_customer(customer: CustomerCreate):
    await crud.create_customer(customer)
    return {"message": "Customer created successfully"}

@app.post("/orders")
async def create_customer_order(order: CustomerOrderCreate):
    await crud.create_customer_order(order)
    return {"message": "Order created successfully"}

@app.get("/getcustomers")
async def read_customers_with_orders():
    customers = await get_all_customers_with_orders()
    return customers