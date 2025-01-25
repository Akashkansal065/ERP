from enum import Enum as PyEnum
from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Product schemas


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Define the Unit Enum for the schema


class UnitEnum(str, PyEnum):
    CARTON_BOX = "Carton Box"
    EACH = "EACH"
    KARTON = "karton"
    KG = "KG"
    PIECES = "PIECES"
    SET = "SET"


# SKU schemas
class SKUBase(BaseModel):
    sku_name: str
    company_name: str
    size: Optional[str] = None
    weight: Optional[float] = None
    color: Optional[str] = None
    material: Optional[str] = None
    selling_price: Optional[float] = None
    hsn_sac_code: Optional[str] = None
    is_active: Optional[bool] = True
    is_gst_applicable: Optional[bool] = True
    gst_rate: Optional[float] = 0.00
    cgst: Optional[float] = 0.00
    sgst: Optional[float] = 0.00
    unit: UnitEnum


class SKUCreate(SKUBase):
    sku: str
    vendor_id: int
    product_id: int


class SKUResponse(SKUBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stock and Price schemas
class StockPriceBase(BaseModel):
    stock: int
    purchase_price: float
    warehouse: str


class StockPriceCreate(StockPriceBase):
    sku_id: int


class StockPriceResponse(StockPriceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Image schemas
class ImageBase(BaseModel):
    # image_url: str
    # alt_text: Optional[str] = None
    pass


class ImageCreate(ImageBase):
    sku_id: str


class ImageResponse(ImageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
