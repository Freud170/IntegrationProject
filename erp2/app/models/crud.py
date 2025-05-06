from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
import uuid

from app.models.db_models import Product, Order, OrderStatus, async_session
from app.models.pydantic_models import ProductCreate, OrderCreate, OrderUpdate

# Product CRUD operations
async def create_product(product: ProductCreate):
    """Create a new product in the database."""
    async with async_session() as session:
        db_product = Product(
            product_id=product.product_id,
            product_name=product.product_name,
            supplier=product.supplier,
            cost_price=product.cost_price,
            retail_price=product.retail_price,
            stock_level=product.stock_level
        )
        session.add(db_product)
        await session.commit()
        return db_product

async def get_product(product_id: str):
    """Get a product by ID."""
    async with async_session() as session:
        result = await session.execute(
            select(Product).where(Product.product_id == product_id)
        )
        return result.scalars().first()

async def update_product_stock(product_id: str, quantity: int):
    """Update product stock level."""
    async with async_session() as session:
        result = await session.execute(
            select(Product).where(Product.product_id == product_id)
        )
        product = result.scalars().first()
        if product:
            product.stock_level = product.stock_level - quantity
            await session.commit()
            return product
        return None

# Order CRUD operations
async def create_order(order: OrderCreate):
    """Create a new order in the database."""
    async with async_session() as session:
        # First, check if product exists and has enough stock
        result = await session.execute(
            select(Product).where(Product.product_id == order.product_id)
        )
        product = result.scalars().first()
        
        if not product:
            raise ValueError(f"Product {order.product_id} not found")
        
        if product.stock_level < order.quantity:
            # If not enough stock, create order but mark as cancelled
            db_order = Order(
                order_id=order.order_id,
                customer_id=order.customer_id,
                product_id=order.product_id,
                quantity=order.quantity,
                order_status=OrderStatus.Cancelled,
                shipping_date=None
            )
        else:
            # If enough stock, create order and reduce stock
            db_order = Order(
                order_id=order.order_id,
                customer_id=order.customer_id,
                product_id=order.product_id,
                quantity=order.quantity,
                order_status=OrderStatus.Processed,
                shipping_date=date.today() + timedelta(days=3)  # Ship in 3 days
            )
            product.stock_level -= order.quantity
            
        session.add(db_order)
        await session.commit()
        return db_order

async def get_order(order_id: str):
    """Get an order by ID."""
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        return result.scalars().first()

async def update_order_status(order_id: str, update_data: OrderUpdate):
    """Update an order's status and shipping date."""
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalars().first()
        if order:
            order.order_status = update_data.order_status
            if update_data.shipping_date:
                order.shipping_date = update_data.shipping_date
            await session.commit()
            return order
        return None

# Initialize database with some dummy products
async def initialize_demo_data():
    """Initialize the database with some demo products."""
    products = [
        ProductCreate(
            product_id="PROD001",
            product_name="Laptop",
            supplier="TechSupplier",
            cost_price=800.00,
            retail_price=1200.00,
            stock_level=50
        ),
        ProductCreate(
            product_id="PROD002",
            product_name="Smartphone",
            supplier="MobileSupplier",
            cost_price=400.00,
            retail_price=799.99,
            stock_level=100
        ),
        ProductCreate(
            product_id="PROD003",
            product_name="Headphones",
            supplier="AudioSupplier",
            cost_price=50.00,
            retail_price=99.99,
            stock_level=200
        ),
    ]
    
    for product in products:
        # Check if product already exists before creating
        existing = await get_product(product.product_id)
        if not existing:
            await create_product(product)
            
    print("Demo data initialized")