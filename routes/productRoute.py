from reqSchemas.productSchema import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductVariantCreate, ProductVariantUpdate, ProductVariantResponse,
    ProductStockPriceCreate, ProductStockPriceUpdate, ProductStockPriceResponse,
    ProductPriceHistoryCreate, ProductPriceHistoryResponse
)
from models.products_model import Product, ProductVariant, ProductStockPrice
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from models.products_model import Product, ProductVariant
from models.vendor_model import Vendor
from models.users_model import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from reqSchemas.productSchema import ProductCreate, ProductResponse
from routes.userRoute import get_admin_user

productR = APIRouter(prefix='/product', tags=['Product'])
UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


@productR.post("/create", response_model=ProductResponse)
async def create_product(product: ProductCreate, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    new_product = Product(
        name=product.name,
        description=product.description,
        category=product.category,
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@productR.get("/all", response_model=list[ProductResponse])
async def get_all_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products


@productR.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@productR.put("/update/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    return product


@productR.delete("/delete/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted successfully"}

# --- Product Variant Endpoints ---


@productR.post("/create/variants", response_model=ProductVariantResponse)
async def create_product_variant(variant: ProductVariantCreate, db: AsyncSession = Depends(get_db)):
    new_variant = ProductVariant(
        product_id=variant.product_id,
        size=variant.size,
        weight=variant.weight,
    )
    db.add(new_variant)
    await db.commit()
    await db.refresh(new_variant)
    return new_variant


@productR.get("/{product_id}/variants", response_model=list[ProductVariantResponse])
async def get_variants_for_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductVariant).filter(ProductVariant.product_id == product_id)
    )
    variants = result.scalars().all()
    return variants


@productR.get("/variants/{variant_id}", response_model=ProductVariantResponse)
async def get_variant(variant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductVariant).filter(ProductVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@productR.put("/update/variants/{variant_id}", response_model=ProductVariantResponse)
async def update_variant(variant_id: int, variant_update: ProductVariantUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductVariant).filter(ProductVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    for key, value in variant_update.dict(exclude_unset=True).items():
        setattr(variant, key, value)
    await db.commit()
    await db.refresh(variant)
    return variant


@productR.delete("/delete/variants/{variant_id}")
async def delete_variant(variant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductVariant).filter(ProductVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    await db.delete(variant)
    await db.commit()
    return {"message": "Variant deleted successfully"}

# --- Product Stock Price Endpoints ---


@productR.post("/stock-prices", response_model=ProductStockPriceResponse)
async def create_stock_price(stock_price: ProductStockPriceCreate, db: AsyncSession = Depends(get_db)):
    new_stock_price = ProductStockPrice(
        variant_id=stock_price.variant_id,
        vendor_id=stock_price.vendor_id,
        stock=stock_price.stock,
        purchase_price=stock_price.purchase_price,
        selling_price=stock_price.selling_price,
    )
    db.add(new_stock_price)
    await db.commit()
    await db.refresh(new_stock_price)
    return new_stock_price


@productR.get("/variants/{variant_id}/stock-prices", response_model=list[ProductStockPriceResponse])
async def get_stock_prices_for_variant(variant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductStockPrice).filter(
            ProductStockPrice.variant_id == variant_id)
    )
    stock_prices = result.scalars().all()
    return stock_prices


@productR.put("/stock-prices/{price_id}", response_model=ProductStockPriceResponse)
async def update_stock_price(price_id: int, stock_price_update: ProductStockPriceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductStockPrice).filter(ProductStockPrice.id == price_id))
    stock_price = result.scalar_one_or_none()
    if not stock_price:
        raise HTTPException(
            status_code=404, detail="Stock price entry not found")
    for key, value in stock_price_update.dict(exclude_unset=True).items():
        setattr(stock_price, key, value)
    await db.commit()
    await db.refresh(stock_price)
    return stock_price


@productR.delete("/stock-prices/{price_id}")
async def delete_stock_price(price_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProductStockPrice).filter(ProductStockPrice.id == price_id))
    stock_price = result.scalar_one_or_none()
    if not stock_price:
        raise HTTPException(
            status_code=404, detail="Stock price entry not found")
    await db.delete(stock_price)
    await db.commit()
    return {"message": "Stock price entry deleted successfully"}

# --- Product Price History Endpoints ---


# @productR.post("/create", response_model=ProductResponse)
# async def create_product(
#     product: ProductCreate,
#     current_user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """
# Create a new product.

# Args:
#     product (ProductCreate): The product data to create.
#     current_user (dict, optional): The current authenticated user. Defaults to Depends(get_current_user).
#     db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

# Returns:
#     Product: The newly created product.
# """
#     new_product = Product(
#         name=product.name,
#         description=product.description,
#         category=product.category,
#     )
#     db.add(new_product)
#     await db.commit()
#     await db.refresh(new_product)
#     return new_product


# @productR.post("/products")
# def create_product_with_variants(data: dict, db: AsyncSession = Depends(get_db)):
#     product = Product(
#         name=data["name"],
#         description=data.get("description"),
#         category=data.get("category"),
#     )
#     db.add(product)
#     db.commit()

#     # Add variants
#     for variant in data.get("variants", []):
#         vendor = db.query(Vendor).filter(
#             Vendor.id == variant["vendor_id"]).first()
#         if not vendor:
#             raise HTTPException(status_code=400, detail="Invalid vendor ID")

#         new_variant = ProductVariant(
#             product_id=product.id,
#             size=variant.get("size"),
#             weight=variant.get("weight"),
#             price=variant["price"],
#             stock=variant.get("stock", 0),
#             vendor_id=variant["vendor_id"],
#         )
#         db.add(new_variant)

#     db.commit()
#     return product


# @productR.get("/products/{product_id}")
# def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product


# @productR.get("/products")
# def list_products(category: str = None, db: AsyncSession = Depends(get_db)):
#     query = db.query(Product)
#     if category:
#         query = query.filter(Product.category == category)
#     return query.all()


# # @productR.put("/products/{product_id}")
# # def update_product(product_id: int, updated_data: Product, db: AsyncSession = Depends(get_db)):
# #     product = db.query(Product).filter(Product.id == product_id).first()
# #     if not product:
# #         raise HTTPException(status_code=404, detail="Product not found")

# #     for key, value in updated_data.dict(exclude_unset=True).items():
# #         setattr(product, key, value)

# #     db.commit()
# #     db.refresh(product)
# #     return product


# @productR.delete("/products/{product_id}")
# def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")

#     db.delete(product)
#     db.commit()
#     return {"message": "Product deleted successfully"}
