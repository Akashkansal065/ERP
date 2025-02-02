from sqlalchemy import JSON, Boolean, Column, Integer, String, DateTime, ForeignKey, DECIMAL, Text, text, Enum
from datetime import datetime
import pytz
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from models.users_model import Base

UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


class UnitEnum(PyEnum):
    CARTON_BOX = "Carton Box"
    EACH = "EACH"
    KARTON = "KARTON"
    KG = "KG"
    PIECES = "PIECES"
    SET = "SET"


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(255), nullable=True)
    created_at = Column(
        DateTime, default=datetime.now(IST), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
# Relationship
    skus = relationship("ProductSku", back_populates="product")


class ProductSku(Base):
    __tablename__ = "product_sku"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey(
        "products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku_name = Column(String(100),
                      nullable=False, index=True)
    company_name = Column(String(100),
                          nullable=False, index=True)
    sku = Column(String(100),
                 nullable=False, index=True, unique=True)
    sub_category = Column(String(255), nullable=True)
    size = Column(String(50), nullable=True)  # e.g., Small, Medium, Large
    color = Column(String(50), nullable=True)  # e.g., Red, Blue, Green
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    unit = Column(Enum(UnitEnum), nullable=False, default=UnitEnum.EACH)
    material = Column(String(50), nullable=True)  # e.g., Cotton, Silk, Wool
    selling_price = Column(DECIMAL(10, 2), nullable=True)
    length = Column(DECIMAL(10, 2), nullable=True)
    breadth = Column(DECIMAL(10, 2), nullable=True)
    height = Column(DECIMAL(10, 2), nullable=True)
    # images = Column(Text, nullable=True)
    hsn_sac_code = Column(String(50), nullable=True)
    vendor_id = Column(Integer, ForeignKey(
        "vendors.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=1)
    is_gst_applicable = Column(Boolean, default=1)
    gst_rate = Column(DECIMAL(10, 2), default=0.00)
    cgst = Column(DECIMAL(10, 2), default=0.00)
    sgst = Column(DECIMAL(10, 2), default=0.00)
    # Relationships
    product = relationship("Product", back_populates="skus")
    product_stock_price = relationship(
        "ProductStockPrice", back_populates="sku")
    vendor = relationship("Vendor", back_populates="stock_entries")
    images = relationship("ProductImages", back_populates="sku")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(255), unique=True, nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    vendor_id = Column(Integer, ForeignKey(
        "vendors.id", ondelete="CASCADE"), nullable=False)
    total_invoice_amount = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    stock_entries = relationship("ProductStockPrice", back_populates="invoice")


class ProductStockPrice(Base):
    __tablename__ = "product_stock_price"
    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, ForeignKey(
        "product_sku.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, server_default=text('0'))
    purchase_rate = Column(DECIMAL(10, 2), nullable=True)
    warehouse = Column(String(255), default="")
    invoice_id = Column(Integer, ForeignKey(
        "invoices.id", ondelete="CASCADE"), nullable=False)
    weight = Column(DECIMAL(10, 3), nullable=True)
    discount = Column(DECIMAL(10, 3), nullable=True)
    total_sku_amount = Column(DECIMAL(10, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    # Relationships
    sku = relationship(
        "ProductSku", back_populates="product_stock_price")
    invoice = relationship(
        "Invoice", back_populates="stock_entries")


class ProductImages(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, ForeignKey("product_sku.id",
                    ondelete="CASCADE"), nullable=False)
    image_url = Column(String(512), nullable=False)
    image_metadata = Column(JSON, nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now(IST))
    # Relationships
    sku = relationship("ProductSku", back_populates="images")
