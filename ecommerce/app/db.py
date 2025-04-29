# app/db.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Date, Enum, DECIMAL, ForeignKey
import enum
import os

# ENV Variablen (Postgres URL)
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce")

# Datenbankengine
engine = create_async_engine(POSTGRES_URL, echo=True)

# Session-Factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Basisklasse für unsere ORM-Modelle
Base = declarative_base()

# Enum für Lieferstatus
class OrderStatus(str, enum.Enum):
    Processed = "Processed"
    Shipped = "Shipped"
    Cancelled = "Cancelled"

# Produkt-Tabelle
class Product(Base):
    __tablename__ = 'products'

    product_id = Column(String, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    category = Column(String)
    price = Column(DECIMAL, nullable=False)
    stock_quantity = Column(Integer, nullable=False)

# Bestellung-Tabelle
class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    product_id = Column(String, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_status = Column(Enum(OrderStatus), nullable=False)
    delivery_date = Column(Date, nullable=False)
    payment_method = Column(String, nullable=False)

# DB Initialisierung (Tabellen erstellen)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)