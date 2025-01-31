import os
import shutil
from time import sleep, time
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List
from utils.kitimages import imagekit
from io import BytesIO
from reqSchemas.productSchema import (
    ImageCreate, ImageResponse, InvoiceCreateSchema, InvoiceResponseSchema, ProductCreate, ProductImageResponse, ProductResponse, ProductSkuResponse,
    SKUCreate, SKUExtendedResponse, SKUResponse
)
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from models.products_model import Invoice, Product, ProductImages, ProductSku, ProductStockPrice
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from models.products_model import Product
from models.users_model import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import pytz
from fastapi import File, UploadFile
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from reqSchemas.productSchema import ProductCreate, ProductResponse
from routes.userRoute import get_admin_user, get_current_user

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
async def get_product(request: Request, product_id: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@productR.get("/get_products", response_model=List[ProductResponse])
async def get_product(request: Request, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    product = result.scalars().all()
    if not product:
        raise HTTPException(status_code=200, detail="Product not found")
    return product


@productR.get("/get_products_sku_all", response_model=List[ProductSkuResponse])
async def get_all_skus(request: Request, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductSku)
        .options(
            selectinload(ProductSku.product),
            selectinload(ProductSku.product_stock_price),
            selectinload(ProductSku.vendor),
            selectinload(ProductSku.images)
        )
    )
    skus = result.scalars().all()
    if not skus:
        raise HTTPException(status_code=404, detail="No SKUs found")
    return skus


# SKU Endpoints
@productR.post("/create_sku", response_model=SKUResponse)
async def create_sku(request: Request, sku: SKUCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == sku.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        new_sku = ProductSku(**sku.model_dump())
        db.add(new_sku)
        await db.commit()
        await db.refresh(new_sku)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return new_sku


@productR.get("/get_sku/{sku_id}", response_model=ProductSkuResponse)
async def get_sku(request: Request, sku_id: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductSku)
        .where(ProductSku.id == sku_id)
        .options(
            # Load related product details
            selectinload(ProductSku.product),
            selectinload(ProductSku.vendor),
            selectinload(ProductSku.product_stock_price),
            selectinload(ProductSku.images)
        )
    )
    sku_data = result.scalars().first()
    if not sku_data:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku_data


@productR.get("/get_product_skus/{product_id}", response_model=List[SKUExtendedResponse])
async def get_sku(request: Request, product_id: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductSku)
        .where(ProductSku.product_id == product_id)
    )
    sku_data = result.scalars().unique().all()
    if not sku_data:
        raise HTTPException(status_code=200, detail="SKU's not found")
    return sku_data


@productR.put("/update_sku/{sku_id}", response_model=SKUResponse)
async def update_sku(request: Request, sku_id: int, sku_data: SKUCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.id == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    for key, value in sku_data.dict().items():
        setattr(sku, key, value)

    await db.commit()
    await db.refresh(sku)
    return sku


@productR.delete("/delete_sku/{sku_id}")
async def delete_sku(request: Request, sku_id: int, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.id == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    await db.delete(sku)
    await db.commit()
    return {"message": "SKU deleted successfully"}


# # Stock and Price Endpoints
# @productR.post("/create_skus_stock_price/{sku}", response_model=StockPriceResponse)
# async def create_stock_price(request: Request, sku: str, stock_price: StockPriceCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku))
#     sku = result.scalar_one_or_none()
#     if not sku:
#         raise HTTPException(status_code=404, detail="SKU not found")
#     new_stock_price = ProductStockPrice(
#         sku_id=sku.id, **stock_price.model_dump())
#     db.add(new_stock_price)
#     await db.commit()
#     await db.refresh(new_stock_price)
#     return new_stock_price


# @productR.get("/stock_price/{sku}", response_model=StockPriceResponse)
# async def get_stock_price(request: Request, sku: str, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku))
#     sku = result.scalar_one_or_none()
#     if not sku:
#         raise HTTPException(status_code=404, detail="SKU not found")
#     stockresult = await db.execute(select(ProductStockPrice).filter(ProductStockPrice.sku_id == sku.id))
#     stock_price = stockresult.scalar_one_or_none()
#     if not stock_price:
#         raise HTTPException(status_code=404, detail="Stock price not found")
#     return stock_price

@productR.post("/create_invoice", response_model=InvoiceResponseSchema)
async def create_invoice_with_stock(request: Request, invoice_data: InvoiceCreateSchema, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    new_invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        invoice_date=invoice_data.invoice_date,
        vendor_id=invoice_data.vendor_id,
        total_amount=invoice_data.total_amount
    )
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)

    for stock_entry in invoice_data.stock_entries:
        new_stock = ProductStockPrice(
            sku_id=stock_entry.sku_id,
            quantity=stock_entry.quantity,
            purchase_rate=stock_entry.purchase_rate,
            warehouse=stock_entry.warehouse,
            invoice_id=new_invoice.id,
            weight=stock_entry.weight,
            total_amount=stock_entry.total_amount
        )
        db.add(new_stock)

    await db.commit()
    await db.refresh(new_stock)
    return new_invoice


@productR.put("/update_invoice", response_model=InvoiceResponseSchema)
async def update_invoice_with_stock(
    request: Request,
    invoice_data: InvoiceCreateSchema,
    current_user: dict = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
    max_retries: int = 3,  # Define maximum retry attempts
):
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Check if the invoice exists
            check_invoice = await db.execute(
                select(Invoice)
                .filter(Invoice.id == invoice_data.id)
                .options(selectinload(Invoice.stock_entries))
            )
            existing_invoice = check_invoice.scalar_one_or_none()
            if not existing_invoice:
                raise HTTPException(
                    status_code=404, detail="Invoice not found")

            # Update the existing invoice
            existing_invoice.invoice_number = invoice_data.invoice_number
            existing_invoice.invoice_date = invoice_data.invoice_date
            existing_invoice.vendor_id = invoice_data.vendor_id
            existing_invoice.total_amount = invoice_data.total_amount
            await db.commit()
            await db.refresh(existing_invoice)

            # Clear old stock entries linked to this invoice
            await db.execute(
                select(ProductStockPrice)
                .filter(ProductStockPrice.invoice_id == existing_invoice.id)
            )
            await db.commit()

            # Add updated stock entries
            for stock_entry in invoice_data.stock_entries:
                new_stock = ProductStockPrice(
                    sku_id=stock_entry.sku_id,
                    quantity=stock_entry.quantity,
                    purchase_rate=stock_entry.purchase_rate,
                    warehouse=stock_entry.warehouse,
                    invoice_id=existing_invoice.id,
                    weight=stock_entry.weight,
                    total_amount=stock_entry.total_amount,
                )
                db.add(new_stock)

            await db.commit()
            return existing_invoice

        except SQLAlchemyError as e:
            await db.rollback()
            retry_count += 1
            if retry_count >= max_retries:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to update invoice after {max_retries} attempts: {str(e)}",
                )
            sleep(1)  # Optional delay before retrying


@productR.post("/upload-image/")
async def upload_image(request: Request,
                       sku_id: int,
                       file: UploadFile = File(...),
                       current_user: dict = Depends(get_admin_user),
                       db: AsyncSession = Depends(get_db)
                       ):
    try:
        file_path = os.path.join("temp.png")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving file: {str(e)}")
    result = await db.execute(select(ProductSku).filter(ProductSku.id == sku_id))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    try:
        folderName = f"product_images/{str(sku.id).strip()}/"
        options = UploadFileRequestOptions(
            use_unique_file_name=False,
            tags=["product", f"sku_{sku.sku}"],
            folder=folderName,
            # checks=f"'request.folder' : '/product_images/{str(sku.sku).strip()}/'",
            is_private_file=False,
        )
        result = imagekit.upload_file(file=open(file_path, "rb"),
                                      file_name=str(
                                          sku.sku_name).strip() + "_"+str(time()),
                                      options=options)
        # Raw Response
        print(result.response_metadata.raw)
        # print that uploaded file's ID
        print(result.file_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading to ImageKit: {str(e)}")

    # Store image URL in DB
    new_image = ProductImages(
        sku_id=sku.id,
        image_url=result.response_metadata.raw['url'],
        alt_text=sku.sku,
        image_metadata=result.response_metadata.raw
    )

    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    return new_image


@productR.get("/images/{image_id}", response_model=List[ImageResponse])
async def get_image(request: Request, sku: str, image_id: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductSku).filter(ProductSku.sku == sku))
    sku = result.scalar_one_or_none()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")

    result = await db.execute(select(ProductImages).filter(ProductImages.sku_id == sku.id).filter(ProductImages.is_active == 1))
    image = result.scalars().all()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@productR.get("/images_sku_all/{sku_id}", response_model=List[ProductImageResponse])
async def get_sku(request: Request, sku_id: int, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductImages).where(ProductImages.sku_id == sku_id))
    sku_data = result.scalars().all()
    if not sku_data:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku_data


@productR.delete("/delete-image/{image_id}")
async def delete_image(image_id: int, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductImages).filter(ProductImages.id == image_id))
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete from ImageKit using file_id (optional)
    try:
        file_id = image.image_metadata['fileId']
        result = imagekit.delete_file(file_id)
    except Exception as e:
        await db.delete(image)
        await db.commit()
        raise HTTPException(
            status_code=500, detail=f"Error deleting from ImageKit: {str(e)}")
    print(result.response_metadata.raw)
    # Remove from database
    await db.delete(image)
    await db.commit()
    return {"message": "Image deleted successfully"}
