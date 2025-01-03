from sqlalchemy.orm import joinedload
from fastapi import Depends, HTTPException
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy import select
from models.vendor_model import Bank, Vendor
from models.users_model import get_db
# import jwt
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from reqSchemas.vendorSchema import BankCreateRequest, VendorCreateRequest
from routes.userRoute import get_admin_user

vendorR = APIRouter(prefix='/vendor', tags=['Vendor'])
UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


@vendorR.post("/create_vendor", response_model=None)
async def create_vendor(vendor: VendorCreateRequest, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Create a new vendor.

    Endpoint: POST /create_vendor

    Args:
        vendor (VendorCreateRequest): The request body containing vendor details.
        current_user (dict, optional): The current authenticated admin user. Defaults to Depends(get_admin_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Vendor: The newly created vendor object.
    """
    new_product = Vendor(
        name=vendor.name,
        email=str(vendor.email).lower().strip(),
        phone=vendor.phone,
        address=vendor.address,
        category=vendor.category,
        gst=vendor.gst
    )
    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
    except Exception as e:
        return {"message": str(e)}
    return new_product


@vendorR.get("/all_vendors")
async def get_all_vendors(current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Fetch all vendors from the database.

    This asynchronous function retrieves all vendor records from the database.
    It requires the current user to be an admin and uses dependency injection
    to get the database session.

    Args:
        current_user (dict): The current user, expected to be an admin.
        db (AsyncSession): The database session.

    Returns:
        list: A list of all vendor records.
    """
    result = await db.execute(select(Vendor))
    vendors = result.scalars().all()
    return vendors


@vendorR.get("/email_phone/{email_phone}")
async def get_vendor_by_email_or_phone(email_phone: str, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Retrieve vendor details by email or phone number.

    This asynchronous function fetches vendor details from the database based on the provided email or phone number.
    If the input is a digit, it searches by phone number; otherwise, it searches by email.

    Args:
        email_phone (str): The email or phone number to search for.
        current_user (dict, optional): The current authenticated admin user. Defaults to Depends(get_admin_user).
        db (AsyncSession, optional): The database session dependency. Defaults to Depends(get_db).

    Returns:
        list: A list of vendor details if found, otherwise a message indicating no vendor was found.
    """
    if str(email_phone).isdigit():
        result = await db.execute(select(Vendor).filter(
            Vendor.phone == email_phone))
    else:
        result = await db.execute(select(Vendor).filter(
            Vendor.email == email_phone))
    vendors = result.scalars().all()
    if not vendors:
        return {"message": "No vendor found with this email/phone"}
    # else:
    #     vendorDetails = vendors[0]
    return vendors


@vendorR.get("/by_id/{vendor_id}")
async def get_vendor(vendor_id: int, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to retrieve a vendor by its ID.

    Args:
        vendor_id (int): The ID of the vendor to retrieve.
        current_user (dict, optional): The current authenticated admin user. Defaults to Depends(get_admin_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary containing vendor details and associated bank accounts.

    Raises:
        HTTPException: If the vendor with the specified ID is not found, raises a 404 HTTPException.
    """
    result = await db.execute(
        select(Vendor).options(joinedload(Vendor.bank_accounts)
                               ).filter(Vendor.id == vendor_id)
    )
    vendor = result.scalars().unique().first()

    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return {
        "vendor": {
            "id": vendor.id,
            "name": vendor.name,
            "email": vendor.email,
            "phone": vendor.phone,
            "address": vendor.address,
            "category": vendor.category,
            "gst": vendor.gst
        },
        "bank_accounts": [
            {
                "id": bank.id,
                "bank_ifsc": bank.bank_ifsc,
                "bank_account_no": bank.bank_account_no,
                "bank_account_name": bank.bank_account_name,
                "bank_account_type": bank.bank_account_type,
                "bank_branch": bank.bank_branch
            }
            for bank in vendor.bank_accounts
        ]
    }


@vendorR.put("/update/{vendor_id}")
async def update_vendor(vendor_id: int, vendor: VendorCreateRequest, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Update an existing vendor's information.

    Args:
        vendor_id (int): The ID of the vendor to update.
        vendor (VendorCreateRequest): The request body containing the updated vendor information.
        current_user (dict, optional): The current authenticated admin user. Defaults to Depends(get_admin_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the vendor with the specified ID is not found.

    Returns:
        dict: A dictionary containing a success message and the updated vendor data.
    """
    result = await db.execute(select(Vendor).filter(
        Vendor.id == vendor_id))
    existing_vendor = result.scalar_one_or_none()
    if not existing_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    for key, value in vendor.dict(exclude_unset=True).items():
        setattr(existing_vendor, key, value)

    await db.commit()
    await db.refresh(existing_vendor)
    return {"message": "Vendor updated successfully", "data": existing_vendor}


@vendorR.delete("/delete/{vendor_id}")
async def delete_vendor(vendor_id: int, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Delete a vendor by ID.

    Args:
        vendor_id (int): The ID of the vendor to delete.
        current_user (dict, optional): The current authenticated user, defaults to the result of Depends(get_admin_user).
        db (AsyncSession, optional): The database session, defaults to the result of Depends(get_db).

    Raises:
        HTTPException: If the vendor with the given ID is not found.

    Returns:
        dict: A message indicating that the vendor was deleted successfully.
    """
    result = await db.execute(select(Vendor).filter(
        Vendor.id == vendor_id))
    existing_vendor = result.scalar_one_or_none()
    if not existing_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    await db.delete(existing_vendor)
    await db.commit()
    return {"message": "Vendor deleted successfully"}


@vendorR.post("/{vendor_id}/bank-accounts")
async def add_bank_account(vendor_id: int, bank: BankCreateRequest, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Add a bank account for a vendor.

    Args:
        vendor_id (int): The ID of the vendor to add the bank account for.
        bank (BankCreateRequest): The bank account details to be added.
        current_user (dict, optional): The current authenticated admin user. Defaults to Depends(get_admin_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict: A dictionary containing a success message and the newly added bank account details.

    Raises:
        HTTPException: If the vendor with the given ID is not found.
    """
    result = await db.execute(select(Vendor).filter(
        Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    new_bank = Bank(**bank.model_dump(exclude_unset=True))
    new_bank.vendor_id = vendor_id
    db.add(new_bank)
    await db.commit()
    await db.refresh(new_bank)
    return {"message": "Bank account added successfully", "data": new_bank}


@vendorR.put("/{vendor_id}/bank-accounts/{bank_id}")
async def update_bank_account(vendor_id: int, bank_id: int, bank: BankCreateRequest, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Update a bank account for a specific vendor.

    Args:
        vendor_id (int): The ID of the vendor.
        bank_id (int): The ID of the bank account to update.
        bank (BankCreateRequest): The new bank account data.
        current_user (dict, optional): The current authenticated admin user. Defaults to Depends(get_admin_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the bank account is not found.

    Returns:
        dict: A dictionary containing a success message and the updated bank account data.
    """
    result = await db.execute(select(Bank).filter(Bank.id == bank_id,
                                                  Bank.vendor_id == vendor_id))
    existing_bank = result.scalar_one_or_none()
    if not existing_bank:
        raise HTTPException(status_code=404, detail="Bank account not found")

    for key, value in bank.model_dump().items():
        setattr(existing_bank, key, value)

    await db.commit()
    await db.refresh(existing_bank)
    return {"message": "Bank account updated successfully", "data": existing_bank}


@vendorR.delete("/{vendor_id}/bank-accounts/{bank_id}")
async def delete_bank_account(vendor_id: int, bank_id: int, current_user: dict = Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    """
    Delete a bank account for a specific vendor.

    Args:
        vendor_id (int): The ID of the vendor.
        bank_id (int): The ID of the bank account to be deleted.
        current_user (dict, optional): The current authenticated admin user. Defaults to Depends(get_admin_user).
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If the bank account is not found.

    Returns:
        dict: A message indicating the bank account was deleted successfully.
    """
    result = await db.execute(select(Bank).filter(Bank.id == bank_id,
                                                  Bank.vendor_id == vendor_id))
    bank = await result.scalar_one_or_none()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank account not found")

    await db.delete(bank)
    await db.commit()
    return {"message": "Bank account deleted successfully"}
