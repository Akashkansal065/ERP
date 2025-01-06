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
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    category = Column(
        Enum('Buyer', 'Supplier', name="vendor_roles"), default='Buyer')
    gst = Column(String(15), nullable=True)

    # Relationships
    bank_accounts = relationship(
        "Bank", back_populates="vendor", cascade="all, delete-orphan")
    stock_entries = relationship("ProductStockPrice", back_populates="vendor")
    address = relationship(
        "Address", back_populates="vendor", cascade="all, delete-orphan")


class Bank(Base):
    __tablename__ = "bank"
    id = Column(Integer, primary_key=True, index=True)
    bank_ifsc = Column(String(15), nullable=True)
    bank_account_no = Column(String(20), nullable=True)
    bank_account_name = Column(String(255), nullable=True)
    bank_account_type = Column(String(255), nullable=True)
    bank_branch = Column(String(255), nullable=True)
    vendor_id = Column(Integer, ForeignKey(
        'vendors.id', ondelete="CASCADE"), nullable=False)

    # Back relationship to Vendor
    vendor = relationship("Vendor", back_populates="bank_accounts")


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shipaddress = Column(String(500), nullable=False)
    billingaddress = Column(String(500), nullable=False)
    vendor_id = Column(Integer, ForeignKey(
        'vendors.id', ondelete="CASCADE"), nullable=False)

    # Back relationship to Vendor
    vendor = relationship("Vendor", back_populates="address")
