from typing import List
from utils.kitimages import imagekit
from io import BytesIO
from reqSchemas.productSchema import (
    ImageCreate, ImageResponse, ProductCreate, ProductResponse,
    SKUCreate, SKUResponse, StockPriceCreate, StockPriceResponse
)
from sqlalchemy.orm import joinedload
from models.products_model import Product, ProductImages, ProductSku, ProductStockPrice
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from models.products_model import Product
from models.users_model import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from reqSchemas.productSchema import ProductCreate, ProductResponse
from routes.userRoute import get_admin_user

productR = APIRouter(prefix='/product', tags=['Product'])
UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


# Product Endpoints
@productR.post("/create_product/", response_model=ProductResponse)
async def create_product(request: Request, product: ProductCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@productR.get("/get_product/{product_id}", response_model=ProductResponse)
async def get_product(request: Request, product_id: int, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@productR.get("/get_products", response_model=List[ProductResponse])
async def get_product(request: Request, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    product = result.scalars().all()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@productR.get("/get_products_sku_all")
async def get_product(request: Request, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).options(joinedload(ProductSku.product), joinedload(ProductSku.product_stock_price)))
    product = result.scalars().unique().all()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
#  = relationship("Product", back_populates="variants")
    # vendor = relationship("Vendor", back_populates="stock_entries")
    # images = relationship("ProductImages", back_populates="sku")
# SKU Endpoints


@productR.post("/create_sku", response_model=SKUResponse)
async def create_sku(request: Request, sku: SKUCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
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
async def get_sku(request: Request, sku_id: str, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku


@productR.put("/update_sku/{sku_id}", response_model=SKUResponse)
async def update_sku(request: Request, sku_id: str, sku_data: SKUCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
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
async def delete_sku(request: Request, sku_id: str, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    await db.delete(sku)
    await db.commit()
    return {"message": "SKU deleted successfully"}


# Stock and Price Endpoints
@productR.post("/cretae_skus_stock_price/{sku_id}", response_model=StockPriceResponse)
async def create_stock_price(request: Request, sku_id: str, stock_price: StockPriceCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
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
async def get_stock_price(request: Request, sku_id: str, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    stockresult = await db.execute(select(ProductStockPrice).filter(ProductStockPrice.sku_id == sku.id))
    stock_price = stockresult.scalar_one_or_none()
    if not stock_price:
        raise HTTPException(status_code=404, detail="Stock price not found")
    return stock_price

# Image Upload Endpoint


@productR.post("/upload-image/", response_model=ImageResponse)
async def upload_image(request: Request,
                       sku_id: str = Form(...),
                       file: UploadFile = Form(...),
                       current_user: dict = Depends(get_admin_user),
                       db: AsyncSession = Depends(get_db)
                       ):
    # Check if SKU exists
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    # Read image file bytes
    file_content = await file.read()
    file_stream = BytesIO(file_content)

    # Upload to ImageKit
    try:
        upload_response = imagekit.upload(
            file=file_stream,
            file_name=file.filename,
            options={
                "folder": f"/product_images/{sku_id}/",
                "use_unique_file_name": True,
                "tags": ["product", f"sku_{sku_id}"],
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading to ImageKit: {str(e)}")

    # Store image URL in DB
    new_image = ProductImages(
        sku_id=sku.id,
        image_url=upload_response.get("url"),
        alt_text=sku_id
    )

    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    return new_image


@productR.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(request: Request, image_id: int, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductImages).filter(ProductImages.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@productR.delete("/delete-image/{image_id}")
async def delete_image(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductImages).filter(ProductImages.id == image_id))
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete from ImageKit using file_id (optional)
    try:
        file_id = image.image_url.split("/")[-1].split("?")[0]
        imagekit.delete_file(file_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting from ImageKit: {str(e)}")

    # Remove from database
    await db.delete(image)
    await db.commit()
    return {"message": "Image deleted successfully"}
