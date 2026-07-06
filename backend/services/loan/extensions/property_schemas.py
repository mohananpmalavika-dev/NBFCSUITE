"""
Property Loan Schemas
Pydantic models for property/mortgage loan operations
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================
# Enums
# ============================================

class PropertyTypeEnum(str, Enum):
    """Property types"""
    RESIDENTIAL_FLAT = "residential_flat"
    RESIDENTIAL_HOUSE = "residential_house"
    RESIDENTIAL_PLOT = "residential_plot"
    COMMERCIAL_OFFICE = "commercial_office"
    COMMERCIAL_SHOP = "commercial_shop"
    COMMERCIAL_PLOT = "commercial_plot"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"


class PropertyOwnershipEnum(str, Enum):
    """Property ownership"""
    FREEHOLD = "freehold"
    LEASEHOLD = "leasehold"
    POWER_OF_ATTORNEY = "power_of_attorney"
    CO_OWNERSHIP = "co_ownership"


class PropertyStatusEnum(str, Enum):
    """Property status"""
    UNDER_CONSTRUCTION = "under_construction"
    READY_TO_MOVE = "ready_to_move"
    OCCUPIED = "occupied"
    VACANT = "vacant"


class LegalStatusEnum(str, Enum):
    """Legal verification status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CLEAR = "clear"
    ISSUES_FOUND = "issues_found"
    REJECTED = "rejected"


class TechnicalStatusEnum(str, Enum):
    """Technical verification status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class MortgageStatusEnum(str, Enum):
    """Mortgage status"""
    PENDING = "pending"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    REGISTERED = "registered"
    DISCHARGED = "discharged"


# ============================================
# Property Details Schemas
# ============================================

class PropertyDetailsBase(BaseModel):
    """Base property details"""
    property_type: PropertyTypeEnum
    property_ownership_type: PropertyOwnershipEnum
    property_status: PropertyStatusEnum
    
    # Location
    address_line1: str = Field(..., max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    state: str = Field(..., max_length=50)
    pincode: str = Field(..., max_length=10)
    
    # Measurements
    plot_area: Optional[Decimal] = Field(None, ge=0)
    built_up_area: Optional[Decimal] = Field(None, ge=0)
    carpet_area: Optional[Decimal] = Field(None, ge=0)
    
    # Valuation
    market_value: Decimal = Field(..., ge=0)
    loan_amount: Decimal = Field(..., ge=0)


class PropertyDetailsCreate(PropertyDetailsBase):
    """Create property details"""
    loan_application_id: int
    survey_number: Optional[str] = None
    plot_number: Optional[str] = None
    current_owner_name: Optional[str] = None
    distress_sale_value: Optional[Decimal] = None


class PropertyDetailsUpdate(BaseModel):
    """Update property details"""
    property_status: Optional[PropertyStatusEnum] = None
    market_value: Optional[Decimal] = None
    bank_valuation: Optional[Decimal] = None
    construction_year: Optional[int] = None
    property_age: Optional[int] = None
    has_clear_title: Optional[bool] = None


class PropertyDetailsResponse(PropertyDetailsBase):
    """Property details response"""
    id: int
    loan_application_id: int
    survey_number: Optional[str] = None
    plot_number: Optional[str] = None
    construction_year: Optional[int] = None
    property_age: Optional[int] = None
    bank_valuation: Optional[Decimal] = None
    loan_to_value: Optional[Decimal] = None
    legal_verification_status: LegalStatusEnum
    technical_verification_status: TechnicalStatusEnum
    mortgage_status: MortgageStatusEnum
    has_clear_title: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Legal Verification Schemas
# ============================================

class LegalVerificationBase(BaseModel):
    """Base legal verification"""
    advocate_name: Optional[str] = Field(None, max_length=200)
    advocate_contact: Optional[str] = Field(None, max_length=20)
    legal_firm_name: Optional[str] = Field(None, max_length=200)


class LegalVerificationCreate(LegalVerificationBase):
    """Create legal verification"""
    property_loan_id: int
    loan_application_id: int
    verification_date: Optional[date] = None


class LegalVerificationUpdate(BaseModel):
    """Update legal verification"""
    title_clear: Optional[bool] = None
    title_issues: Optional[str] = None
    ec_obtained: Optional[bool] = None
    ec_period_from: Optional[date] = None
    ec_period_to: Optional[date] = None
    encumbrances_found: Optional[bool] = None
    encumbrance_details: Optional[str] = None
    property_tax_verified: Optional[bool] = None
    sale_deed_verified: Optional[bool] = None
    legal_opinion_given: Optional[bool] = None
    legal_opinion_summary: Optional[str] = None
    legal_opinion_status: Optional[LegalStatusEnum] = None
    approved: Optional[bool] = None
    rejection_reason: Optional[str] = None


class LegalVerificationResponse(LegalVerificationBase):
    """Legal verification response"""
    id: int
    property_loan_id: int
    loan_application_id: int
    verification_date: Optional[date] = None
    title_clear: bool
    ec_obtained: bool
    encumbrances_found: bool
    property_tax_verified: bool
    sale_deed_verified: bool
    legal_opinion_given: bool
    legal_opinion_status: LegalStatusEnum
    approved: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Technical Verification Schemas
# ============================================

class TechnicalVerificationBase(BaseModel):
    """Base technical verification"""
    engineer_name: Optional[str] = Field(None, max_length=200)
    engineer_contact: Optional[str] = Field(None, max_length=20)
    engineer_license: Optional[str] = Field(None, max_length=100)


class TechnicalVerificationCreate(TechnicalVerificationBase):
    """Create technical verification"""
    property_loan_id: int
    loan_application_id: int


class SiteVisitSchedule(BaseModel):
    """Schedule site visit"""
    inspection_date: date
    inspection_time: Optional[str] = None
    engineer_name: str = Field(..., max_length=200)
    engineer_contact: Optional[str] = None


class TechnicalVerificationUpdate(BaseModel):
    """Update technical verification"""
    inspection_date: Optional[date] = None
    site_visited: Optional[bool] = None
    plot_area_verified: Optional[Decimal] = None
    built_up_area_verified: Optional[Decimal] = None
    construction_quality: Optional[str] = None
    property_condition: Optional[str] = None
    market_value_assessed: Optional[Decimal] = None
    distress_sale_value_assessed: Optional[Decimal] = None
    recommended_loan_amount: Optional[Decimal] = None
    recommended_ltv: Optional[Decimal] = None
    property_marketable: Optional[bool] = None
    remarks: Optional[str] = None
    status: Optional[TechnicalStatusEnum] = None
    approved: Optional[bool] = None
    rejection_reason: Optional[str] = None


class TechnicalVerificationResponse(TechnicalVerificationBase):
    """Technical verification response"""
    id: int
    property_loan_id: int
    loan_application_id: int
    inspection_date: Optional[date] = None
    site_visited: bool
    construction_quality: Optional[str] = None
    property_condition: Optional[str] = None
    market_value_assessed: Optional[Decimal] = None
    recommended_loan_amount: Optional[Decimal] = None
    recommended_ltv: Optional[Decimal] = None
    property_marketable: bool
    status: TechnicalStatusEnum
    approved: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Document Schemas
# ============================================

class PropertyDocumentBase(BaseModel):
    """Base property document"""
    document_type: str = Field(..., max_length=100)
    document_name: str = Field(..., max_length=200)
    document_number: Optional[str] = Field(None, max_length=100)
    document_date: Optional[date] = None


class PropertyDocumentUpload(PropertyDocumentBase):
    """Upload property document"""
    property_loan_id: int
    loan_application_id: int
    file_path: str = Field(..., max_length=500)
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_original: bool = False
    is_certified_copy: bool = False


class DocumentVerification(BaseModel):
    """Verify document"""
    is_verified: bool
    verification_remarks: str


class PropertyDocumentResponse(PropertyDocumentBase):
    """Property document response"""
    id: int
    property_loan_id: int
    file_path: str
    file_name: Optional[str] = None
    is_verified: bool
    verified_date: Optional[date] = None
    is_original: bool
    is_certified_copy: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentComplianceStatus(BaseModel):
    """Document compliance status"""
    all_uploaded: bool
    missing_documents: List[str]
    uploaded_count: int
    required_count: int


# ============================================
# Mortgage Schemas
# ============================================

class MortgageBase(BaseModel):
    """Base mortgage info"""
    mortgage_type: str = Field(..., max_length=50)
    mortgage_amount: Decimal = Field(..., ge=0)
    lien_holder_name: Optional[str] = Field(None, max_length=200)


class MortgageCreate(MortgageBase):
    """Create mortgage"""
    property_loan_id: int
    loan_application_id: int
    sub_registrar_office: Optional[str] = None
    sub_registrar_district: Optional[str] = None


class MortgageStatusUpdate(BaseModel):
    """Update mortgage status"""
    mortgage_status: MortgageStatusEnum
    submission_date: Optional[date] = None
    registration_date: Optional[date] = None
    registration_number: Optional[str] = None
    registration_fees: Optional[Decimal] = None
    stamp_duty_paid: Optional[Decimal] = None
    discharge_date: Optional[date] = None


class MortgageDischarge(BaseModel):
    """Initiate mortgage discharge"""
    loan_closed_date: date


class MortgageResponse(MortgageBase):
    """Mortgage response"""
    id: int
    property_loan_id: int
    loan_application_id: int
    mortgage_status: MortgageStatusEnum
    sub_registrar_office: Optional[str] = None
    registration_date: Optional[date] = None
    registration_number: Optional[str] = None
    lien_marked: bool
    lien_marked_date: Optional[date] = None
    original_documents_submitted: bool
    discharge_initiated: bool
    discharge_registered: bool
    documents_returned: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Summary Schemas
# ============================================

class VerificationStatus(BaseModel):
    """Verification status summary"""
    legal_status: LegalStatusEnum
    legal_approved: bool
    technical_status: TechnicalStatusEnum
    technical_approved: bool
    both_approved: bool


class DisbursementReadiness(BaseModel):
    """Disbursement readiness check"""
    is_ready: bool
    issues: List[str]


class PropertyLoanSummary(BaseModel):
    """Complete property loan summary"""
    property_details: PropertyDetailsResponse
    legal_verification: Optional[LegalVerificationResponse] = None
    technical_verification: Optional[TechnicalVerificationResponse] = None
    mortgage: Optional[MortgageResponse] = None
    document_compliance: DocumentComplianceStatus
    verification_status: VerificationStatus
    is_ready_for_disbursement: DisbursementReadiness


class PropertyStatistics(BaseModel):
    """Property loan statistics"""
    total_property_loans: int
    pending_legal_verifications: int
    pending_technical_verifications: int
    pending_mortgage_registrations: int
    pending_discharges: int
