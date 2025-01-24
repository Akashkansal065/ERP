from reqSchemas.productSchema import (
    ImageCreate, ImageResponse, ProductCreate, ProductResponse,
    SKUCreate, SKUResponse, StockPriceCreate, StockPriceResponse
)
from models.products_model import Product, ProductImages, ProductSku, ProductStockPrice
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from models.products_model import Product
from models.users_model import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from reqSchemas.productSchema import ProductCreate, ProductResponse

productR = APIRouter(prefix='/product', tags=['Product'])
UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


# Product Endpoints
@productR.post("/create_product/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@productR.get("/get_product/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# SKU Endpoints
@productR.post("/create_sku", response_model=SKUResponse)
async def create_sku(sku: SKUCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == sku.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    new_sku = ProductSku(**sku.model_dump())
    db.add(new_sku)
    await db.commit()
    await db.refresh(new_sku)
    return new_sku


@productR.get("/get_sku/{sku_id}", response_model=SKUResponse)
async def get_sku(sku_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku


@productR.put("/update_sku/{sku_id}", response_model=SKUResponse)
async def update_sku(sku_id: str, sku_data: SKUCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    for key, value in sku_data.dict().items():
        setattr(sku, key, value)

    await db.commit()
    await db.refresh(sku)
    return sku


@productR.delete("/delete_sku/{sku_id}")
async def delete_sku(sku_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    await db.delete(sku)
    await db.commit()
    return {"message": "SKU deleted successfully"}


# Stock and Price Endpoints
@productR.post("/cretae_skus_stock_price/{sku_id}", response_model=StockPriceResponse)
async def create_stock_price(sku_id: str, stock_price: StockPriceCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    new_stock_price = ProductStockPrice(
        sku_id=sku.id, **stock_price.model_dump())
    db.add(new_stock_price)
    await db.commit()
    await db.refresh(new_stock_price)
    return new_stock_price


@productR.get("/stock_price/{sku_id}", response_model=StockPriceResponse)
async def get_stock_price(sku_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    stockresult = await db.execute(select(ProductStockPrice).filter(ProductStockPrice.sku_id == sku.id))
    stock_price = stockresult.scalar_one_or_none()
    if not stock_price:
        raise HTTPException(status_code=404, detail="Stock price not found")
    return stock_price


# Image Endpoints
@productR.post("/skus/{sku_id}/images/", response_model=ImageResponse)
async def create_image(sku_id: str, image: ImageCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    new_image = ProductImages(sku_id=sku_id, **image.dict())
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    return new_image


@productR.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductImages).filter(ProductImages.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image
