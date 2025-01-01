from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class VendorCreateRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    category: str = "Buyer"
    gst: Optional[str] = None

    @field_validator("name", "address")
    def validate_non_empty(cls, value, field):
        if not value.strip():
            raise ValueError(f"{field.name.capitalize()} cannot be empty.")
        return value

    @field_validator("phone")
    def validate_phone(cls, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be exactly 10 digits.")
        return value

    @field_validator("category")
    def validate_category(cls, value):
        if value not in {"Buyer", "Supplier"}:
            raise ValueError("Category must be either 'Buyer' or 'Supplier'.")
        return value


class BankCreateRequest(BaseModel):
    bank_ifsc: Optional[str]
    bank_account_no: Optional[str]
    bank_account_name: Optional[str]
    bank_account_type: Optional[str]
    bank_branch: Optional[str]

    @field_validator("bank_ifsc")
    def validate_ifsc(cls, value):
        if value and len(value) != 11:
            raise ValueError("IFSC code must be exactly 11 characters.")
        return value

    @field_validator("bank_account_no")
    def validate_account_no(cls, value):
        if value and len(value) > 30:
            raise ValueError(
                "Bank account number cannot exceed 20 characters.")
        return value
