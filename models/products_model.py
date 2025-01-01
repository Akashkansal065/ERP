from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Text, text
from datetime import datetime
import pytz
from sqlalchemy.orm import relationship

from models.users_model import Base

UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(255), nullable=True)
    created_at = Column(
        DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
# Relationship
    variants = relationship("ProductVariant", back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    size = Column(String(50), nullable=True)  # e.g., Small, Medium, Large
    weight = Column(DECIMAL(10, 3), nullable=True)  # e.g., 0.5 kg, 1.5 kg
    # Relationships
    product = relationship("Product", back_populates="variants")
    product_stock_price = relationship(
        "ProductStockPrice", back_populates="variant")


class ProductStockPrice(Base):
    __tablename__ = "product_stock_price"
    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey(
        "product_variants.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    stock = Column(Integer, server_default=text('0'))
    purchase_price = Column(DECIMAL(10, 2), nullable=False)
    selling_price = Column(DECIMAL(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="stock_entries")
    variant = relationship(
        "ProductVariant", back_populates="product_stock_price")


class ProductPriceHistory(Base):
    __tablename__ = "product_price_history"
    id = Column(Integer, primary_key=True, index=True)
    price_id = Column(Integer, ForeignKey(
        "product_stock_price.id"), nullable=False)
    old_purchase_price = Column(DECIMAL(10, 2), nullable=False)
    old_selling_price = Column(DECIMAL(10, 2), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    price = relationship("ProductStockPrice")


# class Vendor(Base):
#     __tablename__ = "vendors"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     email = Column(String(255), unique=True, nullable=False)
#     phone = Column(String(15), nullable=False)
#     address = Column(String(500), nullable=False)
#     category = Column(
#         Enum('Buyer', 'Supplier', name="vendor_roles"), default='Buyer')
#     gst = Column(String(15), nullable=True)

#     # Relationships
#     bank_accounts = relationship(
#         "Bank", back_populates="vendor", cascade="all, delete-orphan")
#     stock_entries = relationship("ProductStockPrice", back_populates="vendor")


# class Bank(Base):
#     __tablename__ = "bank"
#     id = Column(Integer, primary_key=True, index=True)
#     bank_ifsc = Column(String(15), nullable=True)
#     bank_account_no = Column(String(20), nullable=True)
#     bank_account_name = Column(String(255), nullable=True)
#     bank_account_type = Column(String(255), nullable=True)
#     bank_branch = Column(String(255), nullable=True)
#     vendor_id = Column(Integer, ForeignKey(
#         'vendors.id', ondelete="CASCADE"), nullable=False)

#     # Back relationship to Vendor
#     vendor = relationship("Vendor", back_populates="bank_accounts")
