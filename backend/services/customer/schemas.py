"""
Customer Management Pydantic Schemas
Request/Response models for customer API
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS (matching database)
# ============================================================================

class CustomerTypeEnum(str, Enum):
    INDIVIDUAL = "individual"
    PROPRIETORSHIP = "proprietorship"
    PARTNERSHIP = "partnership"
    PRIVATE_LIMITED = "private_limited"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MaritalStatusEnum(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class KYCStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class RiskRatingEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AccountTypeEnum(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    OVERDRAFT = "overdraft"


# ============================================================================
# CUSTOMER SCHEMAS
# ============================================================================

class CustomerBase(BaseModel):
    """Base customer fields"""
    customer_type: CustomerTypeEnum = CustomerTypeEnum.INDIVIDUAL
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    business_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: str
    alternate_mobile: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    
    @validator('pan_number')
    def validate_pan(cls, v):
        if v and len(v) != 10:
            raise ValueError('PAN must be 10 characters')
        return v.upper() if v else v
    
    @validator('aadhaar_number')
    def validate_aadhaar(cls, v):
        if v and len(v) != 12:
            raise ValueError('Aadhaar must be 12 digits')
        return v
    
    @validator('mobile', 'alternate_mobile')
    def validate_mobile(cls, v):
        if v and len(v) != 10:
            raise ValueError('Mobile must be 10 digits')
        return v


class CustomerCreate(CustomerBase):
    """Create new customer"""
    pass


class CustomerUpdate(BaseModel):
    """Update existing customer (all fields optional)"""
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    marital_status: Optional[MaritalStatusEnum] = None
    occupation_id: Optional[int] = None
    industry_id: Optional[int] = None
    monthly_income: Optional[Decimal] = None
    current_address_line1: Optional[str] = None
    current_city_id: Optional[int] = None
    current_state_id: Optional[int] = None
    current_pincode: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Customer response with all details"""
    id: int
    customer_code: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    occupation_name: Optional[str] = None
    industry_name: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    annual_income: Optional[Decimal] = None
    current_city_name: Optional[str] = None
    current_state_name: Optional[str] = None
    kyc_status: KYCStatusEnum
    is_kyc_verified: bool
    risk_rating: RiskRatingEnum
    cibil_score: Optional[int] = None
    is_active: bool
    is_blacklisted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CustomerListItem(BaseModel):
    """Simplified customer for list views"""
    id: int
    customer_code: str
    full_name: str
    mobile: str
    email: Optional[str] = None
    kyc_status: KYCStatusEnum
    risk_rating: RiskRatingEnum
    cibil_score: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CUSTOMER DOCUMENT SCHEMAS
# ============================================================================

class CustomerDocumentBase(BaseModel):
    """Base document fields"""
    document_type_id: int
    document_number: Optional[str] = None
    document_name: str
    document_url: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None


class CustomerDocumentCreate(CustomerDocumentBase):
    """Create new document"""
    customer_id: int


class CustomerDocumentResponse(CustomerDocumentBase):
    """Document response"""
    id: int
    customer_id: int
    document_type_name: Optional[str] = None
    status: str
    verified_by: Optional[int] = None
    verified_date: Optional[datetime] = None
    is_expired: bool
    uploaded_date: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CUSTOMER FAMILY SCHEMAS
# ============================================================================

class CustomerFamilyBase(BaseModel):
    """Base family member fields"""
    relationship_type_id: int
    name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    mobile: Optional[str] = None
    occupation: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    is_dependent: bool = True
    is_emergency_contact: bool = False
    is_nominee: bool = False
    nominee_percentage: Optional[Decimal] = None


class CustomerFamilyCreate(CustomerFamilyBase):
    """Create family member"""
    customer_id: int


class CustomerFamilyResponse(CustomerFamilyBase):
    """Family member response"""
    id: int
    customer_id: int
    relationship_type_name: Optional[str] = None
    age: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CUSTOMER BANK ACCOUNT SCHEMAS
# ============================================================================

class CustomerBankAccountBase(BaseModel):
    """Base bank account fields"""
    bank_id: int
    account_number: str
    account_holder_name: str
    account_type: AccountTypeEnum = AccountTypeEnum.SAVINGS
    ifsc_code: str
    is_primary: bool = False
    use_for_disbursement: bool = True
    use_for_collection: bool = True
    
    @validator('ifsc_code')
    def validate_ifsc(cls, v):
        if v and len(v) != 11:
            raise ValueError('IFSC code must be 11 characters')
        return v.upper()


class CustomerBankAccountCreate(CustomerBankAccountBase):
    """Create bank account"""
    customer_id: int


class CustomerBankAccountResponse(CustomerBankAccountBase):
    """Bank account response"""
    id: int
    customer_id: int
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    is_verified: bool
    verified_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# KYC SCHEMAS
# ============================================================================

class CustomerKYCUpdate(BaseModel):
    """Update KYC details"""
    aadhaar_verified: Optional[bool] = None
    aadhaar_verification_method: Optional[str] = None
    pan_verified: Optional[bool] = None
    bank_account_verified: Optional[bool] = None
    video_kyc_done: Optional[bool] = None
    in_person_verification_done: Optional[bool] = None
    cibil_consent_given: Optional[bool] = None
    overall_kyc_status: Optional[KYCStatusEnum] = None
    kyc_remarks: Optional[str] = None


class CustomerKYCResponse(BaseModel):
    """KYC details response"""
    id: int
    customer_id: int
    aadhaar_verified: bool
    aadhaar_verified_date: Optional[datetime] = None
    pan_verified: bool
    pan_verified_date: Optional[datetime] = None
    bank_account_verified: bool
    video_kyc_done: bool
    in_person_verification_done: bool
    overall_kyc_status: KYCStatusEnum
    kyc_completion_percentage: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# LIST RESPONSE WITH PAGINATION
# ============================================================================

class PaginatedCustomerResponse(BaseModel):
    """Paginated customer list"""
    items: List[CustomerListItem]
    total: int
    page: int
    page_size: int
    pages: int


class CustomerDashboardStats(BaseModel):
    """Dashboard statistics"""
    total_customers: int
    active_customers: int
    kyc_pending: int
    kyc_completed: int
    high_risk_customers: int
    blacklisted_customers: int
    new_this_month: int
    avg_cibil_score: Optional[int] = None
