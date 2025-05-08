# app/main.py

from fastapi import FastAPI, HTTPException
from app.models import OrderCreate, OrderResponse, ProductCreate
from app import crud, rabbitmq, db
from app.db import Order, async_session
import asyncio
from sqlalchemy import select

# FastAPI-Instanz
app = FastAPI()

# Event-Loop für Hintergrundtasks (RabbitMQ)
loop = asyncio.get_event_loop()

@app.on_event("startup")
async def startup_event():
    """Startet die DB-Verbindung und den RabbitMQ-Listener beim Containerstart."""
    await db.init_db()  # Verbindet sich mit Postgres und legt Tabellen an, falls nötig
    loop.create_task(rabbitmq.consume_order_status_updates())

@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    """
    REST-Endpunkt: Neue Bestellung anlegen.
    Speichert in Postgres und gibt Lieferdatum + Status zurück.
    """
    try:
        created_order = await crud.create_order(order)

        # Publish the order update to RabbitMQ
        await rabbitmq.publish_order_update(
            order_id=created_order.order_id,
            order_date=created_order.order_date,
            total_amount=created_order.total_amount,
            status=created_order.status,
            customer_id=order.customer_id
        )

        return created_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/products")
async def create_product(product: ProductCreate):
    """
    REST-Endpunkt: Produkt anlegen.
    """
    try:
        await crud.create_product(product)
        return {"message": "Product created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """
    REST-Endpunkt: Bestellung anhand der ID abfragen.
    Praktisch zum Testen.
    """
    try:
        order = await crud.get_order(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/products")
async def read_products():
    """
    REST-Endpunkt: Alle Produkte abrufen.
    """
    try:
        products = await crud.get_all_products()
        return [
            {
                "product_id": p.product_id,
                "product_name": p.product_name,
                "category": p.category,
                "price": float(p.price),
                "stock_quantity": p.stock_quantity
            }
            for p in products
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders")
async def get_all_orders():
    """
    REST-Endpunkt: Gibt alle Bestellungen zurück.
    """
    try:
        async with async_session() as session:
            result = await session.execute(select(Order))
            orders = result.scalars().all()
            return [
                {
                    "order_id": order.order_id,
                    "customer_id": order.customer_id,
                    "email": order.email,
                    "address": order.address,
                    "product_id": order.product_id,
                    "quantity": order.quantity,
                    "order_date": order.order_date,
                    "order_status": order.order_status.value,
                    "delivery_date": order.delivery_date,
                    "payment_method": order.payment_method
                }
                for order in orders
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))