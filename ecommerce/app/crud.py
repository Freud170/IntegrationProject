# app/crud.py

from app.db import async_session, Order, Product, OrderStatus
from app.models import OrderCreate, OrderResponse, ProductCreate
import uuid
import datetime
from sqlalchemy import select

async def create_order(order: OrderCreate) -> OrderResponse:
    """
    Legt eine neue Bestellung in der Datenbank an.
    """
    async with async_session() as session:
        new_order = Order(
            order_id=str(uuid.uuid4()),
            customer_id=order.customer_id,
            email=order.email,
            address=order.address,
            product_id=order.product_id,
            quantity=order.quantity,
            order_date=datetime.date.today(),
            order_status=OrderStatus.Processed,
            delivery_date=datetime.date.today() + datetime.timedelta(days=5),
            payment_method=order.payment_method
        )
        session.add(new_order)
        await session.commit()

        return OrderResponse(
            order_id=new_order.order_id,
            order_date=new_order.order_date,
            delivery_date=new_order.delivery_date,
            total_amount=new_order.quantity,
            status=new_order.order_status.value
        )
    
async def create_product(product: ProductCreate):
    """
    Legt ein neues Produkt in der Datenbank an.
    """
    async with async_session() as session:
        new_product = Product(
            product_id=product.product_id,
            product_name=product.product_name,
            category=product.category,
            price=product.price,
            stock_quantity=product.stock_quantity
        )
        session.add(new_product)
        await session.commit()

async def get_order(order_id: str) -> OrderResponse:
    """
    Holt eine Bestellung anhand ihrer ID aus der Datenbank.
    """
    async with async_session() as session:
        db_order = await session.get(Order, order_id)
        if db_order is None:
            return None
        return OrderResponse(
            order_id=db_order.order_id,
            order_date=db_order.order_date,
            delivery_date=db_order.delivery_date,
            total_amount=db_order.quantity,
            status=db_order.order_status.value
        )
    
async def get_all_products():
    """
    Gibt alle Produkte aus der Datenbank zurück.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Product)
        )
        products = result.scalars().all()
        return products

async def update_order_status(order_id: str, new_status: int):
    """
    Aktualisiert den Lieferstatus einer Bestellung.
    """
    status_mapping = {
        1: OrderStatus.Processed,
        2: OrderStatus.Shipped,
        3: OrderStatus.Cancelled
    }
    try:
        enum_status = status_mapping.get(int(new_status))
    except (ValueError, TypeError):
        return
    if enum_status is None:
        return
    async with async_session() as session:
        db_order = await session.get(Order, order_id)
        if db_order:
            db_order.order_status = enum_status
            await session.commit()

async def get_order_details(order_id: str):
    """
    Fetches order details from the database for a given order ID.
    Returns a dictionary with OrderID, OrderDate, TotalAmount, and Status.
    """
    async with async_session() as session:
        db_order = await session.get(Order, order_id)
        if db_order is None:
            return None

        return {
            "OrderID": db_order.order_id,
            "OrderDate": db_order.order_date,
            "TotalAmount": db_order.quantity * db_order.product.price,
            "Status": db_order.order_status.value
        }