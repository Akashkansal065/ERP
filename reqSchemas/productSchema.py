from enum import Enum as PyEnum
from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


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
    KARTON = "KARTON"
    KG = "KG"
    PIECES = "PIECES"
    SET = "SET"


# SKU schemas
class SKUBase(BaseModel):
    sku_name: str
    company_name: str
    sub_category: str
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
    length: Optional[float] = 0.00
    breadth: Optional[float] = 0.00
    height: Optional[float] = 0.00
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

    quantity: int
    purchase_rate: float
    invoice_number: str
    invoice_date: datetime
    weight: float
    total_amount: float


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


# Enum for vendor category
class VendorCategoryEnum(str, PyEnum):
    BUYER = "Buyer"
    SUPPLIER = "Supplier"


# Vendor schema
class VendorResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    category: VendorCategoryEnum
    gst: Optional[str] = None
    swift_code: Optional[str] = None
    micr_code: Optional[str] = None
    no_of_expiry_days: Optional[int] = None
    min_order_value: Optional[str] = None
    is_tax_exempted: Optional[str] = None
    gl_code: Optional[str] = None
    credit_days: Optional[int] = None
    sor_days: Optional[int] = None
    is_cost_based_on_margin: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Product schema
class ProductBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Product image schema
class ProductImageResponse(BaseModel):
    id: int
    sku_id: int
    image_url: str
    alt_text: Optional[str] = None
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


# Product stock price schema
class ProductStockPriceResponse(BaseModel):
    id: int
    sku_id: int
    qty: int
    purchase_price: float
    warehouse: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# SKU schema with vendor details
class ProductSkuResponse(BaseModel):
    id: int
    sku_name: str
    company_name: str
    sku: str
    size: Optional[str]
    weight: Optional[float]
    color: Optional[str]
    unit: UnitEnum
    material: Optional[str]
    selling_price: Optional[float]
    hsn_sac_code: Optional[str]
    is_active: bool
    is_gst_applicable: bool
    gst_rate: float
    cgst: float
    sgst: float
    created_at: datetime
    updated_at: datetime
    product: ProductBase
    vendor: VendorResponse
    product_stock_price: List[ProductStockPriceResponse]
    images: List[ProductImageResponse]

    class Config:
        from_attributes = True
