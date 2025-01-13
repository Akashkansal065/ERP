from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional


class VendorCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the vendor")
    email: EmailStr = Field(..., description="Email address of the vendor")
    phone: str = Field(..., description="Phone number of the vendor")
    category: str = Field(default="Buyer",
                          description="Category of the vendor (Buyer/Supplier)")
    gst: Optional[str] = Field(None, description="GST number of the vendor")
    swift_code: Optional[str] = Field(
        None, description="SWIFT code for transactions")
    micr_code: Optional[str] = Field(
        None, description="MICR code for transactions")
    no_of_expiry_days: Optional[int] = Field(
        None, description="Number of expiry days")
    min_order_value: Optional[str] = Field(
        None, description="Minimum order value")
    is_tax_exempted: Optional[str] = Field(
        None, description="Tax exemption status")
    gl_code: Optional[str] = Field(None, description="General ledger code")
    credit_days: Optional[int] = Field(None, description="Credit days allowed")
    sor_days: Optional[int] = Field(None, description="Sourcing order days")
    is_cost_based_on_margin: Optional[str] = Field(
        None, description="Cost based on margin status")

    @field_validator("name", mode="before")
    def validate_non_empty(cls, value, field):
        if not value.strip():
            raise ValueError(f"{field.name.capitalize()} cannot be empty.")
        return value

    @field_validator("email", mode="before")
    def validate_non_empty(cls, value, field):
        if not value.strip():
            raise ValueError(f"{field.name.capitalize()} cannot be empty.")
        return value.strip().lower()

    @field_validator("phone", mode="before")
    def validate_phone(cls, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be exactly 10 digits.")
        return value

    @field_validator("category", mode="before")
    def validate_category(cls, value):
        if value not in {"Buyer", "Supplier"}:
            raise ValueError("Category must be either 'Buyer' or 'Supplier'.")
        return value


class BankCreateRequest(BaseModel):
    bank_ifsc: str = Field(None, description="IFSC code of the bank")
    bank_account_no: str = Field(
        None, description="Bank account number")
    bank_account_name: str = Field(
        None, description="Name on the bank account")
    bank_account_type: str = Field(
        None, description="Type of the bank account")
    bank_branch: str = Field(None, description="Bank branch name")

    @field_validator("bank_ifsc", mode="before")
    def validate_ifsc(cls, value):
        if value and len(value) != 11:
            raise ValueError("IFSC code must be exactly 11 characters.")
        return value

    @field_validator("bank_account_no", mode="before")
    def validate_account_no(cls, value):
        if value and len(value) > 30:
            raise ValueError(
                "Bank account number cannot exceed 20 characters.")
        return value


class AddressRequest(BaseModel):
    ship_address: str = Field(..., description="Shipping address")
    billing_address: str = Field(..., description="Billing address")
    ship_contact_person: Optional[str] = Field(
        None, description="Contact person for shipping")
    ship_phone: Optional[str] = Field(
        None, description="Phone number for shipping")
    ship_email: Optional[EmailStr] = Field(
        None, description="Email address for shipping")
    ship_state: Optional[str] = Field(None, description="State for shipping")
    ship_country: Optional[str] = Field(
        None, description="Country for shipping")
    ship_city: Optional[str] = Field(None, description="City for shipping")
    ship_pincode: Optional[str] = Field(
        None, description="Pincode for shipping")
    latitude: Optional[str] = Field(None, description="Latitude coordinates")
    longitude: Optional[str] = Field(None, description="Longitude coordinates")
    bill_contact_person: Optional[str] = Field(
        None, description="Contact person for billing")
    bill_phone: Optional[str] = Field(
        None, description="Phone number for billing")
    bill_email: Optional[EmailStr] = Field(
        None, description="Email address for billing")
    bill_state: Optional[str] = Field(None, description="State for billing")
    bill_country: Optional[str] = Field(
        None, description="Country for billing")
    bill_city: Optional[str] = Field(None, description="City for billing")
    bill_pincode: Optional[str] = Field(
        None, description="Pincode for billing")

    @field_validator("ship_address", "billing_address", mode="before")
    def validate_non_empty(cls, value, field):
        if not value.strip():
            raise ValueError(f"{field.name.capitalize()} cannot be empty.")
        return value.strip().capitalize()


class UpdateAddress(AddressRequest):
    pass
