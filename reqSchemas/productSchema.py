from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# Product Schemas
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]


# Product Variant Schemas
class ProductVariantCreate(BaseModel):
    product_id: int
    size: Optional[str] = None
    weight: Optional[Decimal] = None


class ProductVariantUpdate(BaseModel):
    size: Optional[str]
    weight: Optional[Decimal]


# Product Stock Price Schemas
class ProductStockPriceCreate(BaseModel):
    variant_id: int
    vendor_id: int
    stock: Optional[int] = 0
    purchase_price: Decimal
    selling_price: Optional[Decimal] = None


class ProductStockPriceUpdate(BaseModel):
    stock: Optional[int]
    purchase_price: Optional[Decimal]
    selling_price: Optional[Decimal]


# Product Price History Schemas
class ProductPriceHistoryCreate(BaseModel):
    price_id: int
    old_purchase_price: Decimal
    old_selling_price: Decimal


# Vendor-related schemas (optional based on your model)
class VendorCreate(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    category: str = "Buyer"
    gst: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductVariantResponse(BaseModel):
    id: int
    product_id: int
    size: Optional[str]
    weight: Optional[Decimal]

    class Config:
        from_attributes = True


class ProductStockPriceResponse(BaseModel):
    id: int
    variant_id: int
    vendor_id: int
    stock: int
    purchase_price: Decimal
    selling_price: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


class ProductPriceHistoryResponse(BaseModel):
    id: int
    price_id: int
    old_purchase_price: Decimal
    old_selling_price: Decimal
    changed_at: datetime

    class Config:
        from_attributes = True
