"""
Master Data Schemas
Pydantic models for request/response
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


# ============================================
# GEOGRAPHY SCHEMAS
# ============================================

class CountryBase(BaseModel):
    code: str = Field(..., max_length=3, description="ISO 3166-1 alpha-3 code")
    name: str = Field(..., max_length=200)
    phone_code: Optional[str] = Field(None, max_length=10)
    currency_code: Optional[str] = Field(None, max_length=3)
    is_active: bool = True


class CountryCreate(CountryBase):
    pass


class CountryResponse(CountryBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StateBase(BaseModel):
    country_code: str = Field(..., max_length=3)
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=200)
    is_active: bool = True


class StateCreate(StateBase):
    pass


class StateResponse(StateBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CityBase(BaseModel):
    state_code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=200)
    is_active: bool = True


class CityCreate(CityBase):
    pass


class CityResponse(CityBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PincodeBase(BaseModel):
    pincode: str = Field(..., max_length=10)
    city: str = Field(..., max_length=200)
    state_code: str = Field(..., max_length=10)
    district: Optional[str] = Field(None, max_length=200)
    is_active: bool = True


class PincodeCreate(PincodeBase):
    pass


class PincodeResponse(PincodeBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# BANKING SCHEMAS
# ============================================

class BankBase(BaseModel):
    code: str = Field(..., max_length=20)
    name: str = Field(..., max_length=200)
    short_name: Optional[str] = Field(None, max_length=100)
    bank_type: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class BankCreate(BankBase):
    pass


class BankResponse(BankBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BankBranchBase(BaseModel):
    bank_code: str = Field(..., max_length=20)
    ifsc_code: str = Field(..., max_length=20)
    micr_code: Optional[str] = Field(None, max_length=20)
    branch_name: str = Field(..., max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=200)
    state_code: Optional[str] = Field(None, max_length=10)
    pincode: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


class BankBranchCreate(BankBranchBase):
    pass


class BankBranchResponse(BankBranchBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# FINANCIAL SCHEMAS
# ============================================

class CurrencyBase(BaseModel):
    code: str = Field(..., max_length=3, description="ISO 4217 code")
    name: str = Field(..., max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    decimal_places: int = Field(default=2, ge=0, le=4)
    is_active: bool = True


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyResponse(CurrencyBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentTypeBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    is_mandatory: bool = False
    is_active: bool = True


class DocumentTypeCreate(DocumentTypeBase):
    pass


class DocumentTypeResponse(DocumentTypeBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OccupationBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class OccupationCreate(OccupationBase):
    pass


class OccupationResponse(OccupationBase):
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# LIST RESPONSE SCHEMAS
# ============================================

class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list


class CountryListResponse(PaginatedResponse):
    items: list[CountryResponse]


class StateListResponse(PaginatedResponse):
    items: list[StateResponse]


class BankListResponse(PaginatedResponse):
    items: list[BankResponse]


class DocumentTypeListResponse(PaginatedResponse):
    items: list[DocumentTypeResponse]
