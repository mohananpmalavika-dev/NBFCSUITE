from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    dob: str
    gender: str
    branch_id: Optional[str] = None


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    pan: Optional[str] = None
    aadhar: Optional[str] = None
    branch_id: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    kyc_status: str
    pan: Optional[str] = None
    aadhar: Optional[str] = None
    branch_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AddressCreate(BaseModel):
    address_type: str
    street: str
    city: str
    state: str
    postal_code: str
    is_primary: bool = False


class DocumentResponse(BaseModel):
    id: str
    document_type: str
    document_number: str
    document_url: str
    verification_status: str
    expiry_date: Optional[datetime] = None

    class Config:
        from_attributes = True



class OfficeCreateBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool = True


class HeadOfficeCreate(OfficeCreateBase):
    pass


class ZonalOfficeCreate(OfficeCreateBase):
    head_office_id: str


class RegionalOfficeCreate(OfficeCreateBase):
    zonal_office_id: str


class AreaOfficeCreate(OfficeCreateBase):
    regional_office_id: str


class BranchOfficeCreate(OfficeCreateBase):
    area_office_id: str
    branch_type: Optional[str] = None
    postal_code: Optional[str] = None


class BranchTransactionCreate(BaseModel):
    transaction_type: str
    amount: float
    currency: Optional[str] = "INR"
    status: Optional[str] = "completed"
    metadata: Optional[dict] = None


class BranchResponse(BaseModel):
    id: str
    area_office_id: str
    name: str
    code: str
    branch_type: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    is_active: bool
    created_at: datetime

    @field_validator("is_active", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes", "active"}

    class Config:
        from_attributes = True



class BranchTransactionResponse(BaseModel):
    id: str
    customer_id: str
    branch_id: str
    transaction_type: str
    amount: float
    currency: str
    status: str
    metadata: Optional[dict]
    created_at: datetime

    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, value):
        return float(value or 0)

    class Config:
        from_attributes = True



class FinancialProfileUpdate(BaseModel):
    annual_income: Optional[str] = None
    employment_type: Optional[str] = None
    employer: Optional[str] = None
    occupation: Optional[str] = None
    assets: Optional[dict] = None
    liabilities: Optional[dict] = None
    credit_score: Optional[int] = None
    behavior_score: Optional[str] = None
    risk_level: Optional[str] = None


class FinancialProfileResponse(BaseModel):
    id: str
    customer_id: str
    annual_income: Optional[str] = None
    employment_type: Optional[str] = None
    employer: Optional[str] = None
    occupation: Optional[str] = None
    assets: Optional[dict] = None
    liabilities: Optional[dict] = None
    credit_score: Optional[int] = None
    behavior_score: Optional[str] = None
    risk_level: Optional[str] = None
    last_updated: datetime

    class Config:
        from_attributes = True
