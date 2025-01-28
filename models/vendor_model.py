from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

import pytz
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String, Column, Integer, String, Boolean, Enum, DateTime, text
)
from sqlalchemy import Boolean, Float, Text
from sqlalchemy import CHAR, Date
from sqlalchemy import DECIMAL, TIMESTAMP
from sqlalchemy import Enum
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

from models.users_model import Base

UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(15), nullable=False, index=True)
    category = Column(
        Enum('Buyer', 'Supplier', name="vendor_roles"), default='Buyer', index=True)
    gst = Column(String(15), nullable=True)
    swift_code = Column(String(255), nullable=True)
    micr_code = Column(String(255), nullable=True)
    no_of_expiry_days = Column(Integer, nullable=True)
    min_order_value = Column(String(255), nullable=True)
    is_tax_exempted = Column(String(255), nullable=True)
    gl_code = Column(String(255), nullable=True)
    credit_days = Column(Integer, nullable=True)
    sor_days = Column(Integer, nullable=True)
    is_cost_based_on_margin = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    # Relationships
    bank_accounts = relationship(
        "Bank", back_populates="vendor", cascade="all, delete-orphan")
    stock_entries = relationship("ProductSku", back_populates="vendor")
    address = relationship(
        "Address", back_populates="vendor", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="vendor")


class Bank(Base):
    __tablename__ = "bank"

    id = Column(Integer, primary_key=True, index=True)
    bank_ifsc = Column(String(15), nullable=True)
    bank_account_no = Column(String(20), nullable=True)
    bank_account_name = Column(String(255), nullable=True)
    bank_account_type = Column(String(255), nullable=True)
    bank_branch = Column(String(255), nullable=True)
    vendor_id = Column(Integer, ForeignKey(
        'vendors.id', ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    # Back relationship to Vendor
    vendor = relationship("Vendor", back_populates="bank_accounts")


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ship_address = Column(String(500), nullable=False)
    billing_address = Column(String(500), nullable=False)
    ship_contact_person = Column(String(255), nullable=True)
    ship_phone = Column(String(15), nullable=True)
    ship_email = Column(String(255), nullable=True)
    ship_state = Column(String(255), nullable=True)
    ship_country = Column(String(255), nullable=True)
    ship_city = Column(String(255), nullable=True)
    ship_pincode = Column(String(15), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    bill_contact_person = Column(String(255), nullable=True)
    bill_phone = Column(String(15), nullable=True)
    bill_email = Column(String(255), nullable=True)
    bill_state = Column(String(255), nullable=True)
    bill_country = Column(String(255), nullable=True)
    bill_city = Column(String(255), nullable=True)
    bill_pincode = Column(String(15), nullable=True)
    vendor_id = Column(Integer, ForeignKey(
        'vendors.id', ondelete="CASCADE"), nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    created_at = Column(DateTime, default=datetime.now(IST))
    # Back relationship to Vendor
    vendor = relationship("Vendor", back_populates="address")
