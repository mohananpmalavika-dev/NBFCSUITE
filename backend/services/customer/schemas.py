"""
Customer Management Pydantic Schemas
Request/Response models for customer API
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
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



# ============================================================================
# CUSTOMER FAMILY UPDATE SCHEMA
# ============================================================================

class CustomerFamilyUpdate(BaseModel):
    """Update family member (all fields optional)"""
    relationship_type_id: Optional[int] = None
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    mobile: Optional[str] = None
    occupation: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    is_dependent: Optional[bool] = None
    is_emergency_contact: Optional[bool] = None
    is_nominee: Optional[bool] = None
    nominee_percentage: Optional[Decimal] = None


# ============================================================================
# CUSTOMER BANK ACCOUNT UPDATE SCHEMA
# ============================================================================

class CustomerBankAccountUpdate(BaseModel):
    """Update bank account (all fields optional)"""
    bank_id: Optional[int] = None
    account_number: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_type: Optional[AccountTypeEnum] = None
    ifsc_code: Optional[str] = None
    is_primary: Optional[bool] = None
    use_for_disbursement: Optional[bool] = None
    use_for_collection: Optional[bool] = None
    is_active: Optional[bool] = None



# ============================================================================
# CUSTOMER TIMELINE SCHEMAS
# ============================================================================

class TimelineActivityCreate(BaseModel):
    """Create timeline activity"""
    activity_type: str  # Will be converted to ActivityType enum
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    event_category: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    is_important: bool = False
    is_visible_to_customer: bool = False


class TimelineActivityResponse(BaseModel):
    """Timeline activity response"""
    id: int
    customer_id: int
    activity_type: str
    title: str
    description: Optional[str] = None
    event_date: datetime
    event_category: Optional[str] = None
    event_source: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    performed_by: Optional[int] = None
    performed_by_name: Optional[str] = None
    performed_by_role: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_important: bool
    is_system_generated: bool
    is_visible_to_customer: bool
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedTimelineResponse(BaseModel):
    """Paginated timeline response"""
    items: List[TimelineActivityResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TimelineSummaryResponse(BaseModel):
    """Timeline activity summary"""
    customer_id: int
    days: int
    activity_counts: Dict[str, int]



# ============================================================================
# CREDIT BUREAU SCHEMAS
# ============================================================================

class BureauPullRequest(BaseModel):
    """Request to pull credit report"""
    bureau_provider: str  # cibil, equifax, experian, crif
    request_purpose: Optional[str] = "loan_application"


class BureauPullResponse(BaseModel):
    """Bureau pull response"""
    id: int
    customer_id: int
    bureau_provider: str
    bureau_request_id: str
    request_date: datetime
    response_date: Optional[datetime] = None
    status: str
    credit_score: Optional[int] = None
    score_date: Optional[date] = None
    total_accounts: Optional[int] = None
    active_accounts: Optional[int] = None
    total_outstanding: Optional[Decimal] = None
    recent_enquiries_1m: Optional[int] = None
    recent_enquiries_3m: Optional[int] = None
    recent_enquiries_6m: Optional[int] = None
    recent_enquiries_12m: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class BureauHistoryResponse(BaseModel):
    """Bureau pull history item"""
    id: int
    bureau_provider: str
    request_date: datetime
    status: str
    credit_score: Optional[int] = None
    response_time_ms: Optional[int] = None
    
    class Config:
        from_attributes = True


class CreditScoreResponse(BaseModel):
    """Credit score response"""
    customer_id: int
    credit_score: int



# ============================================================================
# eKYC / AADHAAR SCHEMAS
# ============================================================================

class AadhaarOTPInitRequest(BaseModel):
    """Request to initiate Aadhaar OTP"""
    aadhaar_number: str = Field(..., min_length=12, max_length=12, pattern="^[0-9]{12}$")
    
    @validator('aadhaar_number')
    def validate_aadhaar(cls, v):
        if not v.isdigit() or len(v) != 12:
            raise ValueError('Aadhaar must be exactly 12 digits')
        return v


class AadhaarOTPInitResponse(BaseModel):
    """Response from OTP initiation"""
    success: bool
    request_id: str
    message: str
    expires_at: str


class AadhaarOTPVerifyRequest(BaseModel):
    """Request to verify Aadhaar OTP"""
    aadhaar_number: str = Field(..., min_length=12, max_length=12)
    otp: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
    request_id: str
    
    @validator('otp')
    def validate_otp(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('OTP must be exactly 6 digits')
        return v


class AadhaarOTPVerifyResponse(BaseModel):
    """Response from OTP verification"""
    success: bool
    verified: bool
    message: str
    ekyc_data: Optional[Dict[str, Any]] = None


class BiometricVerifyRequest(BaseModel):
    """Request for biometric verification"""
    aadhaar_number: str = Field(..., min_length=12, max_length=12)
    biometric_data: str = Field(..., description="Base64 encoded biometric data")
    biometric_type: str = Field(default="fingerprint", description="fingerprint or iris")


class BiometricVerifyResponse(BaseModel):
    """Response from biometric verification"""
    success: bool
    verified: bool
    message: str
    ekyc_data: Optional[Dict[str, Any]] = None



# ============================================================================
# DIGILOCKER SCHEMAS
# ============================================================================

class DigiLockerAuthInitResponse(BaseModel):
    """Response from DigiLocker authorization initiation"""
    authorization_url: str
    state: str


class DigiLockerAuthCompleteRequest(BaseModel):
    """Request to complete DigiLocker authorization"""
    code: str = Field(..., description="Authorization code from callback")
    redirect_uri: str = Field(..., description="Same redirect URI used in /authorize")


class DigiLockerAuthCompleteResponse(BaseModel):
    """Response from DigiLocker authorization completion"""
    success: bool
    access_token: str
    expires_in: int
    documents: List[Dict[str, Any]]


class DigiLockerDocumentResponse(BaseModel):
    """DigiLocker document metadata"""
    uri: str
    name: str
    type: str
    size: int
    date: str
    issuer: str


class DigiLockerFetchDocumentRequest(BaseModel):
    """Request to fetch and store document"""
    access_token: str
    document_uri: str
    document_type_id: str = Field(..., description="Document type UUID from master data")


class CustomerDocumentResponse(BaseModel):
    """Customer document response"""
    id: int
    customer_id: int
    document_type_id: int
    document_name: str
    document_url: str
    document_format: str
    status: str
    uploaded_date: datetime
    
    class Config:
        from_attributes = True
