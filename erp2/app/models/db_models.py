from sqlalchemy import Column, String, Integer, Numeric, Enum, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship
import enum
import os
from datetime import date

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/erp")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

# Enums
class OrderStatus(enum.Enum):
    Processed = "Processed"
    Shipped = "Shipped"
    Cancelled = "Cancelled"

# Models
class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(String, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    supplier = Column(String)
    cost_price = Column(Numeric(10, 2), nullable=False)
    retail_price = Column(Numeric(10, 2), nullable=False)
    stock_level = Column(Integer, default=0)
    
    # Relationship with Order
    orders = relationship("Order", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.product_id}, name={self.product_name}, stock={self.stock_level})>"

class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    product_id = Column(String, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_status = Column(Enum(OrderStatus), default=OrderStatus.Processed)
    shipping_date = Column(Date, default=date.today)
    
    # Relationship with Product
    product = relationship("Product", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.order_id}, status={self.order_status})>"

# Database initialization
async def init_db():
    """Initialize the database, creating all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database initialized")