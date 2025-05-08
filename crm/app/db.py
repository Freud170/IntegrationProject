from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, String, Date, ForeignKey, text, Integer, Enum
import os
import enum

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/crm")

engine = create_async_engine(POSTGRES_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Enum für PreferredContactMethod
class PreferredContactMethod(enum.Enum):
    Email = "Email"
    Telefon = "Telefon"

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True) 
    address = Column(String, nullable=False)
    preferred_contact_method = Column(Enum(PreferredContactMethod), nullable=True)  #
    customer_orders = relationship("CustomerOrder", backref="customer")

class CustomerOrder(Base):
    __tablename__ = 'customer_orders'
    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey('customers.customer_id'), nullable=False)
    order_date = Column(Date,nullable=False)
    order_amount = Column(String, nullable=False)
    order_status = Column(Integer, nullable=False)

async def init_db():
    async with engine.begin() as conn:
        # Tabellen leeren
        await conn.execute(text("TRUNCATE TABLE customer_orders"))
        # Tabellen neu erstellen
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)