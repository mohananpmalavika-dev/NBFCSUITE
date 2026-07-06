"""
Loan Insurance Schemas
Pydantic models for loan insurance tracking operations
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================
# Enums
# ============================================

class InsuranceTypeEnum(str, Enum):
    LIFE = "life"
    CREDIT_PROTECTION = "credit_protection"
    ASSET = "asset"
    HEALTH = "health"
    PROPERTY = "property"
    VEHICLE_COMPREHENSIVE = "vehicle_comprehensive"
    OTHER = "other"


class InsuranceStatusEnum(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    LAPSED = "lapsed"
    PENDING_RENEWAL = "pending_renewal"
    PENDING_ACTIVATION = "pending_activation"


class PremiumFrequencyEnum(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"


class PremiumPaymentStatusEnum(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"
    FAILED = "failed"
    WAIVED = "waived"


class ClaimStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    CANCELLED = "cancelled"


class ClaimTypeEnum(str, Enum):
    DEATH = "death"
    DISABILITY = "disability"
    CRITICAL_ILLNESS = "critical_illness"
    JOB_LOSS = "job_loss"
    ACCIDENT = "accident"
    ASSET_DAMAGE = "asset_damage"
    THEFT = "theft"
    NATURAL_CALAMITY = "natural_calamity"
    OTHER = "other"


# ============================================
# Insurance Policy Schemas
# ============================================

class InsurancePolicyCreate(BaseModel):
    """Schema for creating insurance policy"""
    loan_account_id: int = Field(..., description="Loan account ID")
    insurance_type: InsuranceTypeEnum = Field(..., description="Type of insurance")
    insurance_provider: str = Field(..., min_length=2, max_length=100, description="Insurance company name")
    policy_number: str = Field(..., min_length=5, max_length=50, description="Policy number")
    
    # Coverage details
    sum_assured: Decimal = Field(..., gt=0, description="Sum assured/coverage amount")
    premium_amount: Decimal = Field(..., gt=0, description="Premium amount")
    premium_frequency: PremiumFrequencyEnum = Field(..., description="Premium payment frequency")
    
    # Policy period
    policy_start_date: date = Field(..., description="Policy start date")
    policy_end_date: date = Field(..., description="Policy end date")
    
    # Beneficiary details
    nominee_name: Optional[str] = Field(None, max_length=100)
    nominee_relationship: Optional[str] = Field(None, max_length=50)
    nominee_contact: Optional[str] = Field(None, max_length=15)
    
    # Policy terms
    is_mandatory: bool = Field(default=False, description="Is this insurance mandatory for loan")
    is_bundled: bool = Field(default=False, description="Is premium bundled with EMI")
    cover_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Percentage of loan covered")
    
    # Additional details
    policy_document_url: Optional[str] = Field(None, description="Policy document storage URL")
    agent_name: Optional[str] = Field(None, max_length=100)
    agent_contact: Optional[str] = Field(None, max_length=15)
    remarks: Optional[str] = None
    
    @field_validator('policy_end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'policy_start_date' in info.data and v <= info.data['policy_start_date']:
            raise ValueError('Policy end date must be after start date')
        return v


class InsurancePolicyUpdate(BaseModel):
    """Schema for updating insurance policy"""
    insurance_provider: Optional[str] = Field(None, min_length=2, max_length=100)
    sum_assured: Optional[Decimal] = Field(None, gt=0)
    premium_amount: Optional[Decimal] = Field(None, gt=0)
    policy_end_date: Optional[date] = None
    nominee_name: Optional[str] = Field(None, max_length=100)
    nominee_relationship: Optional[str] = Field(None, max_length=50)
    nominee_contact: Optional[str] = Field(None, max_length=15)
    policy_document_url: Optional[str] = None
    agent_name: Optional[str] = Field(None, max_length=100)
    agent_contact: Optional[str] = Field(None, max_length=15)
    remarks: Optional[str] = None
    
    class Config:
        extra = "forbid"


class InsurancePolicyResponse(BaseModel):
    """Schema for insurance policy response"""
    id: int
    loan_account_id: int
    insurance_type: InsuranceTypeEnum
    insurance_provider: str
    policy_number: str
    status: InsuranceStatusEnum
    
    # Coverage details
    sum_assured: Decimal
    premium_amount: Decimal
    premium_frequency: PremiumFrequencyEnum
    
    # Policy period
    policy_start_date: date
    policy_end_date: date
    
    # Beneficiary details
    nominee_name: Optional[str] = None
    nominee_relationship: Optional[str] = None
    nominee_contact: Optional[str] = None
    
    # Policy terms
    is_mandatory: bool
    is_bundled: bool
    cover_percentage: Optional[Decimal] = None
    
    # Renewal tracking
    last_renewal_date: Optional[date] = None
    next_renewal_date: Optional[date] = None
    renewal_reminder_sent: bool
    renewal_reminder_sent_at: Optional[datetime] = None
    
    # Cancellation
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    # Additional details
    policy_document_url: Optional[str] = None
    agent_name: Optional[str] = None
    agent_contact: Optional[str] = None
    remarks: Optional[str] = None
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class InsurancePolicyRenewal(BaseModel):
    """Schema for policy renewal"""
    policy_number: str = Field(..., description="New/renewed policy number")
    policy_start_date: date = Field(..., description="New policy start date")
    policy_end_date: date = Field(..., description="New policy end date")
    sum_assured: Decimal = Field(..., gt=0, description="Updated sum assured")
    premium_amount: Decimal = Field(..., gt=0, description="Updated premium amount")
    policy_document_url: Optional[str] = None
    renewal_remarks: Optional[str] = None
    
    @field_validator('policy_end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'policy_start_date' in info.data and v <= info.data['policy_start_date']:
            raise ValueError('Policy end date must be after start date')
        return v


class InsurancePolicyCancellation(BaseModel):
    """Schema for policy cancellation"""
    cancellation_reason: str = Field(..., min_length=10, description="Reason for cancellation")
    cancellation_date: date = Field(..., description="Cancellation date")
    refund_amount: Optional[Decimal] = Field(None, ge=0, description="Refund amount if any")


class InsurancePolicyListFilter(BaseModel):
    """Filters for insurance policy list"""
    loan_account_id: Optional[int] = None
    insurance_type: Optional[InsuranceTypeEnum] = None
    status: Optional[InsuranceStatusEnum] = None
    is_mandatory: Optional[bool] = None
    expiring_before: Optional[date] = None


# ============================================
# Premium Payment Schemas
# ============================================

class PremiumPaymentCreate(BaseModel):
    """Schema for creating premium payment record"""
    insurance_policy_id: int = Field(..., description="Insurance policy ID")
    due_date: date = Field(..., description="Premium due date")
    premium_amount: Decimal = Field(..., gt=0, description="Premium amount due")
    payment_frequency: PremiumFrequencyEnum = Field(..., description="Payment frequency")


class PremiumPaymentUpdate(BaseModel):
    """Schema for updating premium payment"""
    payment_date: date = Field(..., description="Actual payment date")
    amount_paid: Decimal = Field(..., gt=0, description="Amount paid")
    payment_method: str = Field(..., description="Payment method (EMI, Direct, etc.)")
    transaction_reference: Optional[str] = Field(None, description="Payment transaction reference")
    receipt_url: Optional[str] = Field(None, description="Receipt document URL")
    remarks: Optional[str] = None


class PremiumPaymentResponse(BaseModel):
    """Schema for premium payment response"""
    id: int
    insurance_policy_id: int
    due_date: date
    premium_amount: Decimal
    payment_frequency: PremiumFrequencyEnum
    payment_status: PremiumPaymentStatusEnum
    
    # Payment details
    payment_date: Optional[date] = None
    amount_paid: Optional[Decimal] = None
    payment_method: Optional[str] = None
    transaction_reference: Optional[str] = None
    receipt_url: Optional[str] = None
    
    # Overdue tracking
    is_overdue: bool
    overdue_days: Optional[int] = None
    
    # Waiver
    is_waived: bool
    waiver_reason: Optional[str] = None
    waived_amount: Optional[Decimal] = None
    
    remarks: Optional[str] = None
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================
# Insurance Claim Schemas
# ============================================

class InsuranceClaimCreate(BaseModel):
    """Schema for creating insurance claim"""
    insurance_policy_id: int = Field(..., description="Insurance policy ID")
    loan_account_id: int = Field(..., description="Loan account ID")
    claim_type: ClaimTypeEnum = Field(..., description="Type of claim")
    
    # Claim details
    claim_amount: Decimal = Field(..., gt=0, description="Claimed amount")
    incident_date: date = Field(..., description="Date of incident")
    incident_description: str = Field(..., min_length=20, description="Detailed incident description")
    incident_location: Optional[str] = Field(None, description="Location of incident")
    
    # Supporting documents
    supporting_documents: List[str] = Field(..., min_length=1, description="List of document URLs")
    police_report_number: Optional[str] = Field(None, description="Police report reference (if applicable)")
    medical_report_reference: Optional[str] = Field(None, description="Medical report reference (if applicable)")
    
    # Claimant details
    claimant_name: str = Field(..., min_length=2, max_length=100)
    claimant_relationship: str = Field(..., max_length=50)
    claimant_contact: str = Field(..., max_length=15)
    claimant_address: Optional[str] = None
    
    remarks: Optional[str] = None
    
    @field_validator('incident_date')
    @classmethod
    def validate_incident_date(cls, v):
        if v > date.today():
            raise ValueError('Incident date cannot be in the future')
        return v


class InsuranceClaimUpdate(BaseModel):
    """Schema for updating insurance claim"""
    claim_amount: Optional[Decimal] = Field(None, gt=0)
    incident_description: Optional[str] = Field(None, min_length=20)
    supporting_documents: Optional[List[str]] = None
    police_report_number: Optional[str] = None
    medical_report_reference: Optional[str] = None
    claimant_contact: Optional[str] = Field(None, max_length=15)
    claimant_address: Optional[str] = None
    remarks: Optional[str] = None
    
    class Config:
        extra = "forbid"


class InsuranceClaimReview(BaseModel):
    """Schema for claim review/approval"""
    status: ClaimStatusEnum = Field(..., description="New claim status")
    approved_amount: Optional[Decimal] = Field(None, gt=0, description="Approved claim amount")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason if rejected")
    review_remarks: str = Field(..., min_length=10, description="Review comments")
    surveyor_name: Optional[str] = Field(None, description="Insurance surveyor name")
    surveyor_report_url: Optional[str] = Field(None, description="Surveyor report URL")


class InsuranceClaimPayment(BaseModel):
    """Schema for recording claim payment"""
    payment_date: date = Field(..., description="Payment date")
    amount_paid: Decimal = Field(..., gt=0, description="Amount paid")
    payment_method: str = Field(..., description="Payment method")
    payment_reference: str = Field(..., description="Payment reference/cheque number")
    payee_name: str = Field(..., description="Payee name")
    bank_name: Optional[str] = None
    remarks: Optional[str] = None


class InsuranceClaimResponse(BaseModel):
    """Schema for insurance claim response"""
    id: int
    insurance_policy_id: int
    loan_account_id: int
    claim_number: str
    claim_type: ClaimTypeEnum
    claim_status: ClaimStatusEnum
    
    # Claim details
    claim_amount: Decimal
    incident_date: date
    incident_description: str
    incident_location: Optional[str] = None
    
    # Supporting documents
    supporting_documents: List[str]
    police_report_number: Optional[str] = None
    medical_report_reference: Optional[str] = None
    
    # Claimant details
    claimant_name: str
    claimant_relationship: str
    claimant_contact: str
    claimant_address: Optional[str] = None
    
    # Review details
    approved_amount: Optional[Decimal] = None
    rejection_reason: Optional[str] = None
    review_remarks: Optional[str] = None
    surveyor_name: Optional[str] = None
    surveyor_report_url: Optional[str] = None
    
    # Payment details
    payment_date: Optional[date] = None
    amount_paid: Optional[Decimal] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    payee_name: Optional[str] = None
    bank_name: Optional[str] = None
    
    # Workflow tracking
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    paid_at: Optional[datetime] = None
    
    remarks: Optional[str] = None
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class InsuranceClaimListFilter(BaseModel):
    """Filters for insurance claim list"""
    insurance_policy_id: Optional[int] = None
    loan_account_id: Optional[int] = None
    claim_type: Optional[ClaimTypeEnum] = None
    claim_status: Optional[ClaimStatusEnum] = None
    incident_date_from: Optional[date] = None
    incident_date_to: Optional[date] = None


# ============================================
# Dashboard & Analytics Schemas
# ============================================

class InsurancePolicyExpiryAlert(BaseModel):
    """Schema for expiring policy alert"""
    id: int
    loan_account_id: int
    policy_number: str
    insurance_type: InsuranceTypeEnum
    insurance_provider: str
    policy_end_date: date
    days_to_expiry: int
    sum_assured: Decimal
    premium_amount: Decimal
    is_mandatory: bool
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None


class PremiumOverdueAlert(BaseModel):
    """Schema for overdue premium alert"""
    id: int
    insurance_policy_id: int
    loan_account_id: int
    policy_number: str
    due_date: date
    overdue_days: int
    premium_amount: Decimal
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None


class InsuranceStatistics(BaseModel):
    """Overall insurance statistics"""
    total_policies: int
    active_policies: int
    expired_policies: int
    cancelled_policies: int
    
    # By type
    by_type: dict
    
    # Coverage
    total_sum_assured: Decimal
    total_premium_collected: Decimal
    average_coverage_per_loan: Decimal
    
    # Expiry tracking
    expiring_30_days: int
    expiring_60_days: int
    expiring_90_days: int
    
    # Premium tracking
    total_premiums_due: Decimal
    total_premiums_overdue: Decimal
    overdue_premium_count: int
    
    # Claims
    total_claims: int
    pending_claims: int
    approved_claims: int
    rejected_claims: int
    total_claim_amount: Decimal
    total_paid_amount: Decimal
    claim_settlement_ratio: float


class InsuranceDashboard(BaseModel):
    """Combined insurance dashboard data"""
    statistics: InsuranceStatistics
    expiring_policies: List[InsurancePolicyExpiryAlert]
    overdue_premiums: List[PremiumOverdueAlert]
    pending_claims: List[InsuranceClaimResponse]
    recent_renewals: List[InsurancePolicyResponse]


class InsuranceCoverageReport(BaseModel):
    """Insurance coverage report for portfolio"""
    total_loan_portfolio: Decimal
    total_insured_amount: Decimal
    coverage_percentage: float
    uninsured_amount: Decimal
    
    # By loan type
    coverage_by_loan_type: dict
    
    # Mandatory vs optional
    mandatory_coverage: Decimal
    optional_coverage: Decimal
    
    # Risk exposure
    loans_without_insurance: int
    loans_with_expired_insurance: int
    high_risk_loans: List[dict]


class BulkRenewalRequest(BaseModel):
    """Request for bulk policy renewal"""
    policy_ids: List[int] = Field(..., min_length=1, max_length=500)
    renewal_start_date: date
    renewal_end_date: date
    premium_increase_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    bulk_renewal_reference: str
    
    @field_validator('renewal_end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if 'renewal_start_date' in info.data and v <= info.data['renewal_start_date']:
            raise ValueError('Renewal end date must be after start date')
        return v


class BulkRenewalResponse(BaseModel):
    """Response for bulk renewal"""
    total_policies: int
    successful: int
    failed: int
    bulk_renewal_reference: str
    renewed_policies: List[InsurancePolicyResponse]
    errors: List[dict]
