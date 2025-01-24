from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, DECIMAL, Text, text, Enum
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
    KARTON = "karton"
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
    variants = relationship("ProductSku", back_populates="product")


class ProductSku(Base):
    __tablename__ = "product_sku"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey(
        "products.id"), nullable=False, index=True)
    sku = Column(String(100),
                 nullable=False, index=True, unique=True)
    size = Column(String(50), nullable=True)  # e.g., Small, Medium, Large
    weight = Column(DECIMAL(10, 3), nullable=True)  # e.g., 0.5 kg, 1.5 kg
    color = Column(String(50), nullable=True)  # e.g., Red, Blue, Green
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    unit = Column(Enum(UnitEnum), nullable=False, default=UnitEnum.EACH)
    material = Column(String(50), nullable=True)  # e.g., Cotton, Silk, Wool
    selling_price = Column(DECIMAL(10, 2), nullable=True)
    # images = Column(Text, nullable=True)
    hsn_sac_code = Column(String(50), nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    is_active = Column(Boolean, default=1)
    is_gst_applicable = Column(Boolean, default=1)
    gst_rate = Column(DECIMAL(10, 2), default=0.00)
    cgst = Column(DECIMAL(10, 2), default=0.00)
    sgst = Column(DECIMAL(10, 2), default=0.00)
    # Relationships
    product = relationship("Product", back_populates="variants")
    product_stock_price = relationship(
        "ProductStockPrice", back_populates="variant")
    vendor = relationship("Vendor", back_populates="stock_entries")
    images = relationship("ProductImages", back_populates="sku")


class ProductStockPrice(Base):
    __tablename__ = "product_stock_price"
    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, ForeignKey(
        "product_sku.id"), nullable=False, index=True)

    qty = Column(Integer, server_default=text('0'))
    purchase_price = Column(DECIMAL(10, 2), nullable=False)
    warehouse = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.now(IST))
    updated_at = Column(DateTime, default=datetime.now(IST),
                        onupdate=datetime.now(IST))
    # Relationships
    variant = relationship(
        "ProductSku", back_populates="product_stock_price")


class ProductImages(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, ForeignKey("product_sku.id"), nullable=False)
    image_url = Column(String(512), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now(IST))
    # Relationships
    sku = relationship("ProductSku", back_populates="images")
