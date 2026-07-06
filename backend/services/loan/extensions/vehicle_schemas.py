"""
Vehicle Loan Schemas
Pydantic models for vehicle loan operations
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================
# Enums
# ============================================

class VehicleTypeEnum(str, Enum):
    """Vehicle types"""
    TWO_WHEELER = "two_wheeler"
    THREE_WHEELER = "three_wheeler"
    FOUR_WHEELER = "four_wheeler"
    COMMERCIAL = "commercial"
    LUXURY = "luxury"


class VehicleConditionEnum(str, Enum):
    """Vehicle condition"""
    NEW = "new"
    USED = "used"


class HypothecationStatusEnum(str, Enum):
    """Hypothecation status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    MARKED = "marked"
    NOC_ISSUED = "noc_issued"
    REMOVED = "removed"
    FAILED = "failed"


class InsuranceStatusEnum(str, Enum):
    """Insurance status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    CANCELLED = "cancelled"


# ============================================
# Vehicle Details Schemas
# ============================================

class VehicleDetailsBase(BaseModel):
    """Base vehicle details"""
    vehicle_type: VehicleTypeEnum
    vehicle_condition: VehicleConditionEnum
    manufacturer: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    variant: Optional[str] = Field(None, max_length=100)
    manufacturing_year: Optional[int] = None
    color: Optional[str] = Field(None, max_length=50)
    fuel_type: Optional[str] = Field(None, max_length=50)
    
    chassis_number: Optional[str] = Field(None, max_length=50)
    engine_number: Optional[str] = Field(None, max_length=50)
    
    ex_showroom_price: Decimal = Field(..., ge=0)
    on_road_price: Decimal = Field(..., ge=0)
    down_payment: Decimal = Field(..., ge=0)
    financed_amount: Decimal = Field(..., ge=0)
    
    dealer_id: Optional[int] = None
    dealer_name: Optional[str] = Field(None, max_length=200)


class VehicleDetailsCreate(VehicleDetailsBase):
    """Create vehicle details"""
    loan_application_id: int


class VehicleDetailsUpdate(BaseModel):
    """Update vehicle details"""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    color: Optional[str] = None
    chassis_number: Optional[str] = None
    engine_number: Optional[str] = None
    registration_number: Optional[str] = None
    registration_date: Optional[date] = None
    dealer_id: Optional[int] = None


class VehicleDetailsResponse(VehicleDetailsBase):
    """Vehicle details response"""
    id: int
    loan_application_id: int
    registration_number: Optional[str] = None
    registration_date: Optional[date] = None
    is_registered: bool
    hypothecation_status: HypothecationStatusEnum
    loan_to_value: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Dealer Schemas
# ============================================

class DealerBase(BaseModel):
    """Base dealer info"""
    dealer_code: str = Field(..., max_length=50)
    dealer_name: str = Field(..., max_length=200)
    brand: Optional[str] = Field(None, max_length=100)
    mobile: str = Field(..., max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)


class DealerCreate(DealerBase):
    """Create dealer"""
    contact_person: Optional[str] = None
    address_line1: Optional[str] = None
    pincode: Optional[str] = None
    gstin: Optional[str] = Field(None, max_length=15)
    pan: Optional[str] = Field(None, max_length=10)


class DealerUpdate(BaseModel):
    """Update dealer"""
    dealer_name: Optional[str] = None
    contact_person: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class DealerResponse(DealerBase):
    """Dealer response"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# RTO Tracking Schemas
# ============================================

class RTOTrackingBase(BaseModel):
    """Base RTO tracking"""
    rto_state: str = Field(..., max_length=50)
    rto_office: str = Field(..., max_length=100)
    rto_code: Optional[str] = Field(None, max_length=20)
    lender_name: Optional[str] = Field(None, max_length=200)


class RTOTrackingCreate(RTOTrackingBase):
    """Create RTO tracking"""
    vehicle_loan_id: int
    loan_application_id: int


class HypothecationUpdate(BaseModel):
    """Update hypothecation status"""
    status: HypothecationStatusEnum
    submission_date: Optional[date] = None
    marked_date: Optional[date] = None
    noc_date: Optional[date] = None
    removed_date: Optional[date] = None
    reference_number: Optional[str] = None
    comments: Optional[str] = None


class RTOTrackingResponse(RTOTrackingBase):
    """RTO tracking response"""
    id: int
    vehicle_loan_id: int
    loan_application_id: int
    hypothecation_status: HypothecationStatusEnum
    form35_submitted: bool
    form35_submission_date: Optional[date] = None
    hypothecation_marked_date: Optional[date] = None
    noc_generated_date: Optional[date] = None
    hypothecation_removed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Insurance Schemas
# ============================================

class InsuranceBase(BaseModel):
    """Base insurance info"""
    policy_number: str = Field(..., max_length=50)
    policy_type: str = Field(..., max_length=50)
    insurance_company: str = Field(..., max_length=200)
    idv_amount: Decimal = Field(..., ge=0)
    premium_amount: Decimal = Field(..., ge=0)
    total_premium: Decimal = Field(..., ge=0)
    policy_start_date: date
    policy_end_date: date


class InsuranceCreate(InsuranceBase):
    """Create insurance policy"""
    vehicle_loan_id: int
    loan_application_id: int
    customer_id: str
    is_zero_depreciation: bool = False
    is_engine_protection: bool = False
    nominee_name: Optional[str] = None
    nominee_relationship: Optional[str] = None


class InsuranceUpdate(BaseModel):
    """Update insurance"""
    status: Optional[InsuranceStatusEnum] = None
    premium_paid: Optional[bool] = None
    premium_paid_date: Optional[date] = None
    renewal_notice_sent: Optional[bool] = None


class InsuranceResponse(InsuranceBase):
    """Insurance response"""
    id: int
    vehicle_loan_id: int
    status: InsuranceStatusEnum
    premium_paid: bool
    lien_marked: bool
    lien_holder_name: Optional[str] = None
    claims_count: int
    total_claim_amount: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InsuranceExpiryAlert(BaseModel):
    """Insurance expiry alert"""
    id: int
    policy_number: str
    vehicle_loan_id: int
    customer_id: str
    policy_end_date: date
    days_to_expiry: int
    insurance_company: str


# ============================================
# Insurance Claim Schemas
# ============================================

class ClaimBase(BaseModel):
    """Base claim info"""
    claim_number: str = Field(..., max_length=50)
    claim_date: date
    incident_date: date
    claim_type: str = Field(..., max_length=50)
    claim_description: str
    claimed_amount: Decimal = Field(..., ge=0)


class ClaimCreate(ClaimBase):
    """Create insurance claim"""
    insurance_id: int
    incident_location: Optional[str] = None
    police_fir_number: Optional[str] = None


class ClaimStatusUpdate(BaseModel):
    """Update claim status"""
    claim_status: str
    approved_amount: Optional[Decimal] = None
    settled_amount: Optional[Decimal] = None
    settlement_date: Optional[date] = None
    rejection_reason: Optional[str] = None


class ClaimResponse(ClaimBase):
    """Claim response"""
    id: int
    insurance_id: int
    claim_status: str
    approved_amount: Optional[Decimal] = None
    settled_amount: Optional[Decimal] = None
    settlement_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# Vehicle Model Schemas
# ============================================

class VehicleModelBase(BaseModel):
    """Base vehicle model"""
    manufacturer: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    variant: Optional[str] = Field(None, max_length=100)
    vehicle_type: VehicleTypeEnum
    body_type: Optional[str] = None
    fuel_type: Optional[str] = None


class VehicleModelCreate(VehicleModelBase):
    """Create vehicle model"""
    engine_capacity: Optional[int] = None
    seating_capacity: Optional[int] = None
    ex_showroom_price_min: Optional[Decimal] = None
    ex_showroom_price_max: Optional[Decimal] = None


class VehicleModelResponse(VehicleModelBase):
    """Vehicle model response"""
    id: int
    engine_capacity: Optional[int] = None
    seating_capacity: Optional[int] = None
    mileage: Optional[Decimal] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# ============================================
# Summary Schemas
# ============================================

class VehicleLoanSummary(BaseModel):
    """Complete vehicle loan summary"""
    vehicle_details: VehicleDetailsResponse
    rto_tracking: Optional[RTOTrackingResponse] = None
    active_insurance: Optional[InsuranceResponse] = None
    hypothecation_status: Optional[HypothecationStatusEnum] = None
    insurance_status: Optional[InsuranceStatusEnum] = None
    is_compliant: bool
    compliance_issues: List[str] = []
