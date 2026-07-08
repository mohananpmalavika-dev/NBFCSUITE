"""
Insurance & Bancassurance Pydantic Schemas

Comprehensive schemas for all insurance operations including:
- Policy management
- Premium collection
- Claims processing
- Commission tracking
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import uuid


# ==================== ENUMS ====================

class PolicyStatus(str, Enum):
    """Policy status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    LAPSED = "lapsed"
    SURRENDERED = "surrendered"
    MATURED = "matured"
    CANCELLED = "cancelled"


class PolicyType(str, Enum):
    """Insurance policy types"""
    LIFE = "life"
    HEALTH = "health"
    GENERAL = "general"
    MOTOR = "motor"
    ENDOWMENT = "endowment"
    TERM = "term"
    ULIP = "ulip"
    PENSION = "pension"


class PremiumFrequency(str, Enum):
    """Premium payment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUALLY = "annually"
    SINGLE = "single"


class PremiumStatus(str, Enum):
    """Premium payment status"""
    DUE = "due"
    PAID = "paid"
    OVERDUE = "overdue"
    WAIVED = "waived"
    CANCELLED = "cancelled"


class ClaimStatus(str, Enum):
    """Claim processing status"""
    REGISTERED = "registered"
    UNDER_REVIEW = "under_review"
    DOCUMENTS_PENDING = "documents_pending"
    ASSESSMENT_COMPLETE = "assessment_complete"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class ClaimType(str, Enum):
    """Types of insurance claims"""
    DEATH = "death"
    MATURITY = "maturity"
    SURRENDER = "surrender"
    HEALTH = "health"
    ACCIDENT = "accident"
    DAMAGE = "damage"
    THEFT = "theft"
    OTHER = "other"


class CommissionStatus(str, Enum):
    """Commission payment status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


# ==================== POLICY SCHEMAS ====================

class InsurancePolicyBase(BaseModel):
    """Base schema for insurance policy"""
    policy_type: PolicyType
    customer_id: uuid.UUID
    customer_name: str = Field(..., min_length=2, max_length=200)
    
    # Insured information
    insured_name: str = Field(..., min_length=2, max_length=200)
    insured_dob: datetime
    insured_age: int = Field(..., ge=0, le=120)
    insured_gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    
    # Insurance provider
    insurance_company: str = Field(..., min_length=2, max_length=200)
    insurance_company_code: Optional[str] = Field(None, max_length=50)
    product_name: str = Field(..., min_length=2, max_length=200)
    product_code: Optional[str] = Field(None, max_length=50)
    
    # Policy details
    sum_assured: Decimal = Field(..., gt=0)
    policy_term_years: int = Field(..., ge=1, le=100)
    premium_paying_term_years: int = Field(..., ge=1, le=100)
    
    # Premium details
    premium_amount: Decimal = Field(..., gt=0)
    premium_frequency: PremiumFrequency
    premium_mode: Optional[str] = None
    
    # Dates
    policy_start_date: datetime
    policy_end_date: datetime
    first_premium_date: datetime
    
    # Agent/Bancassurance details
    agent_id: Optional[uuid.UUID] = None
    agent_name: Optional[str] = Field(None, max_length=200)
    agent_code: Optional[str] = Field(None, max_length=50)
    channel: str = Field("bancassurance", pattern="^(bancassurance|direct|broker)$")
    
    # Branch information
    branch_id: Optional[uuid.UUID] = None
    branch_name: Optional[str] = Field(None, max_length=200)
    
    # Nominee information
    nominee_name: Optional[str] = Field(None, max_length=200)
    nominee_relationship: Optional[str] = Field(None, max_length=100)
    nominee_dob: Optional[datetime] = None
    nominee_percentage: Optional[Decimal] = Field(100.00, ge=0, le=100)
    
    # Status tracking
    grace_period_days: int = Field(30, ge=0, le=90)
    
    # Documents and remarks
    documents: Optional[List[Dict[str, Any]]] = None
    remarks: Optional[str] = None
    policy_conditions: Optional[str] = None
    
    # Additional details
    medical_examination_required: bool = False
    medical_examination_status: Optional[str] = None
    rider_details: Optional[List[Dict[str, Any]]] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    @validator('policy_end_date')
    def validate_end_date(cls, v, values):
        if 'policy_start_date' in values and v <= values['policy_start_date']:
            raise ValueError('Policy end date must be after start date')
        return v
    
    @validator('premium_paying_term_years')
    def validate_premium_term(cls, v, values):
        if 'policy_term_years' in values and v > values['policy_term_years']:
            raise ValueError('Premium paying term cannot exceed policy term')
        return v


class InsurancePolicyCreate(InsurancePolicyBase):
    """Schema for creating insurance policy"""
    pass


class InsurancePolicyUpdate(BaseModel):
    """Schema for updating insurance policy"""
    policy_status: Optional[PolicyStatus] = None
    customer_name: Optional[str] = Field(None, min_length=2, max_length=200)
    agent_id: Optional[uuid.UUID] = None
    agent_name: Optional[str] = Field(None, max_length=200)
    branch_id: Optional[uuid.UUID] = None
    branch_name: Optional[str] = Field(None, max_length=200)
    nominee_name: Optional[str] = Field(None, max_length=200)
    nominee_relationship: Optional[str] = Field(None, max_length=100)
    documents: Optional[List[Dict[str, Any]]] = None
    remarks: Optional[str] = None
    medical_examination_status: Optional[str] = None
    rider_details: Optional[List[Dict[str, Any]]] = None
    surrender_value: Optional[Decimal] = Field(None, ge=0)
    maturity_value: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class InsurancePolicyResponse(BaseModel):
    """Schema for insurance policy response"""
    id: uuid.UUID
    tenant_id: str
    policy_number: str
    policy_type: PolicyType
    policy_status: PolicyStatus
    customer_id: uuid.UUID
    customer_name: str
    insured_name: str
    insured_age: int
    insurance_company: str
    product_name: str
    sum_assured: Decimal
    policy_term_years: int
    premium_amount: Decimal
    premium_frequency: PremiumFrequency
    policy_start_date: datetime
    policy_end_date: datetime
    next_premium_due_date: Optional[datetime]
    agent_name: Optional[str]
    channel: str
    total_premium_paid: Decimal
    outstanding_premium: Decimal
    is_active: bool
    is_lapsed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PREMIUM SCHEMAS ====================

class InsurancePremiumBase(BaseModel):
    """Base schema for insurance premium"""
    policy_id: uuid.UUID
    premium_amount: Decimal = Field(..., gt=0)
    premium_due_date: datetime
    premium_frequency: PremiumFrequency
    installment_number: int = Field(..., ge=1)
    
    # Late payment
    late_fee: Optional[Decimal] = Field(0, ge=0)
    
    # Waiver/discount
    discount_amount: Optional[Decimal] = Field(0, ge=0)
    discount_reason: Optional[str] = Field(None, max_length=200)
    waived_amount: Optional[Decimal] = Field(0, ge=0)
    waived_reason: Optional[str] = Field(None, max_length=200)
    
    remarks: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class InsurancePremiumCreate(InsurancePremiumBase):
    """Schema for creating insurance premium"""
    pass


class InsurancePremiumPayment(BaseModel):
    """Schema for recording premium payment"""
    payment_date: datetime
    payment_amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(cash|cheque|online|neft|rtgs|upi)$")
    payment_reference: Optional[str] = Field(None, max_length=100)
    transaction_id: Optional[str] = Field(None, max_length=100)
    receipt_number: Optional[str] = Field(None, max_length=50)
    collected_by: Optional[uuid.UUID] = None
    collected_by_name: Optional[str] = Field(None, max_length=200)
    collection_branch: Optional[str] = Field(None, max_length=200)
    late_fee: Optional[Decimal] = Field(0, ge=0)
    remarks: Optional[str] = None


class InsurancePremiumResponse(BaseModel):
    """Schema for insurance premium response"""
    id: uuid.UUID
    tenant_id: str
    policy_id: uuid.UUID
    policy_number: str
    premium_number: str
    premium_amount: Decimal
    premium_due_date: datetime
    premium_frequency: PremiumFrequency
    installment_number: int
    premium_status: PremiumStatus
    payment_date: Optional[datetime]
    payment_amount: Optional[Decimal]
    payment_method: Optional[str]
    late_fee: Optional[Decimal]
    discount_amount: Optional[Decimal]
    waived_amount: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CLAIM SCHEMAS ====================

class InsuranceClaimBase(BaseModel):
    """Base schema for insurance claim"""
    policy_id: uuid.UUID
    claim_type: ClaimType
    claim_amount: Decimal = Field(..., gt=0)
    incident_date: datetime
    incident_description: str = Field(..., min_length=10)
    incident_location: Optional[str] = Field(None, max_length=500)
    
    # Claimant details
    claimant_name: str = Field(..., min_length=2, max_length=200)
    claimant_relationship: str = Field(..., max_length=100)
    claimant_contact: Optional[str] = Field(None, max_length=20)
    claimant_address: Optional[str] = None
    
    # Documents
    documents_submitted: Optional[List[Dict[str, Any]]] = None
    investigation_required: bool = False
    
    remarks: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class InsuranceClaimCreate(InsuranceClaimBase):
    """Schema for creating insurance claim"""
    pass


class InsuranceClaimAssessment(BaseModel):
    """Schema for claim assessment"""
    assessed_amount: Decimal = Field(..., gt=0)
    assessment_remarks: Optional[str] = None
    documents_verified: bool = False
    deductions: Optional[Decimal] = Field(0, ge=0)
    deduction_details: Optional[Dict[str, Any]] = None
    investigation_status: Optional[str] = None
    investigation_remarks: Optional[str] = None


class InsuranceClaimApproval(BaseModel):
    """Schema for claim approval"""
    approved_amount: Decimal = Field(..., gt=0)
    approval_remarks: Optional[str] = None
    target_settlement_date: Optional[datetime] = None


class InsuranceClaimRejection(BaseModel):
    """Schema for claim rejection"""
    rejection_reason: str = Field(..., min_length=10)


class InsuranceClaimSettlement(BaseModel):
    """Schema for claim settlement"""
    settlement_amount: Decimal = Field(..., gt=0)
    settlement_method: str = Field(..., pattern="^(cheque|neft|rtgs|cash)$")
    settlement_reference: Optional[str] = Field(None, max_length=100)
    settlement_remarks: Optional[str] = None


class InsuranceClaimResponse(BaseModel):
    """Schema for insurance claim response"""
    id: uuid.UUID
    tenant_id: str
    policy_id: uuid.UUID
    policy_number: str
    claim_number: str
    claim_type: ClaimType
    claim_status: ClaimStatus
    claim_amount: Decimal
    claimed_date: datetime
    incident_date: datetime
    claimant_name: str
    claimant_relationship: str
    assessed_amount: Optional[Decimal]
    approved_amount: Optional[Decimal]
    settlement_amount: Optional[Decimal]
    settlement_date: Optional[datetime]
    documents_verified: bool
    processing_days: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== COMMISSION SCHEMAS ====================

class InsuranceCommissionBase(BaseModel):
    """Base schema for insurance commission"""
    policy_id: uuid.UUID
    agent_id: uuid.UUID
    agent_name: str = Field(..., min_length=2, max_length=200)
    agent_code: Optional[str] = Field(None, max_length=50)
    agent_type: Optional[str] = Field(None, pattern="^(employee|external|partner)$")
    
    commission_type: str = Field(..., pattern="^(first_year|renewal|performance)$")
    base_amount: Decimal = Field(..., gt=0)
    commission_rate: Decimal = Field(..., ge=0, le=100)
    
    commission_period: Optional[str] = Field(None, max_length=50)
    premium_id: Optional[uuid.UUID] = None
    
    branch_id: Optional[uuid.UUID] = None
    branch_name: Optional[str] = Field(None, max_length=200)
    
    # Deductions
    tds_percentage: Optional[Decimal] = Field(0, ge=0, le=100)
    other_deductions: Optional[Decimal] = Field(0, ge=0)
    deduction_details: Optional[Dict[str, Any]] = None
    
    # Performance
    target_achievement_percentage: Optional[Decimal] = Field(None, ge=0)
    bonus_amount: Optional[Decimal] = Field(0, ge=0)
    penalty_amount: Optional[Decimal] = Field(0, ge=0)
    
    remarks: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class InsuranceCommissionCreate(InsuranceCommissionBase):
    """Schema for creating insurance commission"""
    pass


class InsuranceCommissionApproval(BaseModel):
    """Schema for commission approval"""
    approved_by: uuid.UUID
    approval_remarks: Optional[str] = None


class InsuranceCommissionPayment(BaseModel):
    """Schema for commission payment"""
    payment_method: str = Field(..., pattern="^(cheque|neft|rtgs|cash)$")
    payment_reference: Optional[str] = Field(None, max_length=100)
    paid_amount: Decimal = Field(..., gt=0)
    payment_remarks: Optional[str] = None


class InsuranceCommissionResponse(BaseModel):
    """Schema for insurance commission response"""
    id: uuid.UUID
    tenant_id: str
    policy_id: uuid.UUID
    policy_number: str
    commission_number: str
    commission_status: CommissionStatus
    agent_id: uuid.UUID
    agent_name: str
    agent_code: Optional[str]
    commission_type: str
    base_amount: Decimal
    commission_rate: Decimal
    commission_amount: Decimal
    tds_amount: Optional[Decimal]
    other_deductions: Optional[Decimal]
    net_payable: Optional[Decimal]
    calculation_date: datetime
    approval_date: Optional[datetime]
    payment_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== AGENT SCHEMAS ====================

class InsuranceAgentBase(BaseModel):
    """Base schema for insurance agent"""
    agent_code: str = Field(..., min_length=2, max_length=50)
    agent_name: str = Field(..., min_length=2, max_length=200)
    agent_type: str = Field(..., pattern="^(employee|external|partner|bancassurance)$")
    
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    
    # Address
    address_line1: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    
    # License
    license_number: Optional[str] = Field(None, max_length=100)
    license_valid_till: Optional[datetime] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    
    # Organization
    branch_id: Optional[uuid.UUID] = None
    branch_name: Optional[str] = Field(None, max_length=200)
    
    # Commission
    default_commission_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    commission_structure: Optional[Dict[str, Any]] = None
    
    # Bank details
    bank_name: Optional[str] = Field(None, max_length=200)
    account_number: Optional[str] = Field(None, max_length=50)
    ifsc_code: Optional[str] = Field(None, max_length=20)
    
    # Tax
    pan_number: Optional[str] = Field(None, max_length=20)
    gst_number: Optional[str] = Field(None, max_length=20)
    tds_applicable: bool = True
    
    joining_date: Optional[datetime] = None
    remarks: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class InsuranceAgentCreate(InsuranceAgentBase):
    """Schema for creating insurance agent"""
    pass


class InsuranceAgentUpdate(BaseModel):
    """Schema for updating insurance agent"""
    agent_name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    address_line1: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    license_valid_till: Optional[datetime] = None
    branch_id: Optional[uuid.UUID] = None
    branch_name: Optional[str] = Field(None, max_length=200)
    default_commission_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    bank_name: Optional[str] = Field(None, max_length=200)
    account_number: Optional[str] = Field(None, max_length=50)
    ifsc_code: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    remarks: Optional[str] = None


class InsuranceAgentResponse(BaseModel):
    """Schema for insurance agent response"""
    id: uuid.UUID
    tenant_id: str
    agent_code: str
    agent_name: str
    agent_type: str
    email: Optional[str]
    phone: Optional[str]
    mobile: Optional[str]
    license_number: Optional[str]
    license_valid_till: Optional[datetime]
    branch_name: Optional[str]
    default_commission_rate: Optional[Decimal]
    total_policies_sold: int
    total_premium_collected: Decimal
    total_commission_earned: Decimal
    active_policies_count: int
    is_active: bool
    joining_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True



# ==================== FILTER & QUERY SCHEMAS ====================

class PolicyFilter(BaseModel):
    """Schema for policy filtering"""
    policy_type: Optional[PolicyType] = None
    policy_status: Optional[PolicyStatus] = None
    customer_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None
    insurance_company: Optional[str] = None
    is_active: Optional[bool] = None
    is_lapsed: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class PremiumFilter(BaseModel):
    """Schema for premium filtering"""
    policy_id: Optional[uuid.UUID] = None
    premium_status: Optional[PremiumStatus] = None
    from_due_date: Optional[datetime] = None
    to_due_date: Optional[datetime] = None
    from_payment_date: Optional[datetime] = None
    to_payment_date: Optional[datetime] = None


class ClaimFilter(BaseModel):
    """Schema for claim filtering"""
    policy_id: Optional[uuid.UUID] = None
    claim_type: Optional[ClaimType] = None
    claim_status: Optional[ClaimStatus] = None
    from_claimed_date: Optional[datetime] = None
    to_claimed_date: Optional[datetime] = None


class CommissionFilter(BaseModel):
    """Schema for commission filtering"""
    policy_id: Optional[uuid.UUID] = None
    agent_id: Optional[uuid.UUID] = None
    commission_status: Optional[CommissionStatus] = None
    commission_type: Optional[str] = None
    from_calculation_date: Optional[datetime] = None
    to_calculation_date: Optional[datetime] = None


# ==================== STATISTICS & REPORTS ====================

class PolicyStatistics(BaseModel):
    """Schema for policy statistics"""
    total_policies: int
    active_policies: int
    lapsed_policies: int
    matured_policies: int
    total_sum_assured: Decimal
    total_premium_collected: Decimal
    outstanding_premium: Decimal
    policies_by_type: Dict[str, int]
    policies_by_status: Dict[str, int]


class PremiumStatistics(BaseModel):
    """Schema for premium statistics"""
    total_premiums: int
    paid_premiums: int
    due_premiums: int
    overdue_premiums: int
    total_premium_amount: Decimal
    total_collected: Decimal
    total_outstanding: Decimal
    collection_rate: Decimal


class ClaimStatistics(BaseModel):
    """Schema for claim statistics"""
    total_claims: int
    claims_by_status: Dict[str, int]
    claims_by_type: Dict[str, int]
    total_claimed_amount: Decimal
    total_assessed_amount: Decimal
    total_approved_amount: Decimal
    total_settled_amount: Decimal
    average_processing_days: Optional[int]
    settlement_rate: Decimal


class CommissionStatistics(BaseModel):
    """Schema for commission statistics"""
    total_commissions: int
    pending_commissions: int
    approved_commissions: int
    paid_commissions: int
    total_commission_amount: Decimal
    total_paid_amount: Decimal
    total_outstanding: Decimal
    commissions_by_type: Dict[str, int]
    commissions_by_agent: List[Dict[str, Any]]


class DashboardSummary(BaseModel):
    """Schema for insurance dashboard summary"""
    policy_stats: PolicyStatistics
    premium_stats: PremiumStatistics
    claim_stats: ClaimStatistics
    commission_stats: CommissionStatistics



# ==================== BATCH OPERATIONS ====================

class BatchPremiumGeneration(BaseModel):
    """Schema for batch premium generation"""
    generation_date: datetime
    frequency: PremiumFrequency
    policy_ids: Optional[List[uuid.UUID]] = None  # If None, generate for all eligible


class BatchCommissionCalculation(BaseModel):
    """Schema for batch commission calculation"""
    calculation_period: str = Field(..., pattern="^(Q[1-4]-\\d{4}|\\w{3}-\\d{4})$")  # Q1-2024 or Jan-2024
    commission_type: str = Field(..., pattern="^(first_year|renewal|performance)$")
    agent_ids: Optional[List[uuid.UUID]] = None  # If None, calculate for all


# ==================== UTILITY SCHEMAS ====================

class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class SortParams(BaseModel):
    """Schema for sorting parameters"""
    sort_by: str = Field("created_at")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class BulkResponse(BaseModel):
    """Schema for bulk operation response"""
    total: int
    successful: int
    failed: int
    errors: Optional[List[Dict[str, Any]]] = None
    results: Optional[List[Dict[str, Any]]] = None
