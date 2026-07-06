"""
Loan Restructuring Schemas
Pydantic models for loan restructuring operations
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================
# Enums
# ============================================

class RestructuringTypeEnum(str, Enum):
    EMI_REDUCTION = "emi_reduction"
    TENURE_EXTENSION = "tenure_extension"
    MORATORIUM = "moratorium"
    INTEREST_RATE_REDUCTION = "interest_rate_reduction"
    PRINCIPAL_RESTRUCTURE = "principal_restructure"
    HYBRID = "hybrid"


class RestructuringReasonEnum(str, Enum):
    FINANCIAL_HARDSHIP = "financial_hardship"
    JOB_LOSS = "job_loss"
    MEDICAL_EMERGENCY = "medical_emergency"
    BUSINESS_LOSS = "business_loss"
    NATURAL_DISASTER = "natural_disaster"
    COVID_IMPACT = "covid_impact"
    OTHER = "other"


class RestructuringStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class ImpactAssessmentEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================
# Restructuring Request Schemas
# ============================================

class RestructuringRequestCreate(BaseModel):
    """Schema for creating restructuring request"""
    loan_account_id: int = Field(..., description="Loan account ID")
    restructuring_type: RestructuringTypeEnum = Field(..., description="Type of restructuring")
    reason: RestructuringReasonEnum = Field(..., description="Reason for restructuring")
    reason_details: str = Field(..., min_length=20, description="Detailed explanation of reason")
    
    # Current loan details (for reference)
    current_emi: Decimal = Field(..., gt=0, description="Current EMI amount")
    current_outstanding: Decimal = Field(..., gt=0, description="Current outstanding principal")
    current_tenure_remaining: int = Field(..., gt=0, description="Remaining tenure in months")
    
    # Proposed restructuring parameters
    proposed_emi: Optional[Decimal] = Field(None, gt=0, description="Proposed new EMI (if applicable)")
    proposed_tenure: Optional[int] = Field(None, gt=0, description="Proposed new tenure (if applicable)")
    proposed_interest_rate: Optional[Decimal] = Field(None, gt=0, le=100, description="Proposed interest rate")
    moratorium_months: Optional[int] = Field(None, ge=0, le=12, description="Moratorium period in months")
    
    # Supporting information
    customer_income: Optional[Decimal] = Field(None, description="Current monthly income")
    customer_obligations: Optional[Decimal] = Field(None, description="Other monthly obligations")
    supporting_documents: Optional[List[str]] = Field(None, description="Document URLs/references")
    
    # Customer contact
    customer_mobile: Optional[str] = Field(None, max_length=15)
    customer_email: Optional[str] = Field(None, max_length=100)
    
    @field_validator('proposed_emi')
    @classmethod
    def validate_proposed_emi(cls, v, info):
        if v and 'current_emi' in info.data and v > info.data['current_emi']:
            raise ValueError('Proposed EMI cannot be higher than current EMI for restructuring')
        return v
    
    @field_validator('proposed_tenure')
    @classmethod
    def validate_proposed_tenure(cls, v, info):
        if v and 'current_tenure_remaining' in info.data and v < info.data['current_tenure_remaining']:
            raise ValueError('Proposed tenure cannot be less than current remaining tenure')
        return v


class RestructuringRequestUpdate(BaseModel):
    """Schema for updating restructuring request"""
    reason_details: Optional[str] = Field(None, min_length=20)
    proposed_emi: Optional[Decimal] = Field(None, gt=0)
    proposed_tenure: Optional[int] = Field(None, gt=0)
    proposed_interest_rate: Optional[Decimal] = Field(None, gt=0, le=100)
    moratorium_months: Optional[int] = Field(None, ge=0, le=12)
    customer_income: Optional[Decimal] = None
    customer_obligations: Optional[Decimal] = None
    supporting_documents: Optional[List[str]] = None
    
    class Config:
        extra = "forbid"


class RestructuringApprovalRequest(BaseModel):
    """Schema for approving restructuring"""
    approved_emi: Optional[Decimal] = Field(None, gt=0, description="Final approved EMI")
    approved_tenure: Optional[int] = Field(None, gt=0, description="Final approved tenure")
    approved_interest_rate: Optional[Decimal] = Field(None, gt=0, le=100, description="Final approved interest rate")
    approved_moratorium_months: Optional[int] = Field(None, ge=0, le=12)
    
    approval_remarks: str = Field(..., min_length=10, description="Approval remarks and conditions")
    waiver_amount: Optional[Decimal] = Field(None, ge=0, description="Any waiver amount approved")
    waiver_type: Optional[str] = Field(None, description="Type of waiver (penalty, interest, etc.)")
    
    # Risk assessment
    credit_committee_approval: bool = Field(default=False, description="Credit committee approval received")
    risk_assessment: Optional[str] = Field(None, description="Risk assessment notes")
    
    # Financial impact
    estimated_loss: Optional[Decimal] = Field(None, description="Estimated financial loss from restructuring")
    recovery_probability: Optional[Decimal] = Field(None, ge=0, le=100, description="Estimated recovery probability %")


class RestructuringRejectionRequest(BaseModel):
    """Schema for rejecting restructuring"""
    rejection_reason: str = Field(..., min_length=20, description="Detailed rejection reason")
    alternative_suggestions: Optional[str] = Field(None, description="Alternative options for customer")
    can_reapply: bool = Field(default=True, description="Can customer reapply later")
    reapply_after_days: Optional[int] = Field(None, ge=0, description="Days to wait before reapply")


class RestructuringImplementationRequest(BaseModel):
    """Schema for implementing approved restructuring"""
    implementation_date: date = Field(..., description="Date of implementation")
    first_emi_date: date = Field(..., description="First EMI date after restructuring")
    
    # Final confirmed parameters
    final_emi: Decimal = Field(..., gt=0, description="Final EMI amount")
    final_tenure: int = Field(..., gt=0, description="Final tenure in months")
    final_interest_rate: Decimal = Field(..., gt=0, le=100, description="Final interest rate")
    final_outstanding: Decimal = Field(..., gt=0, description="Outstanding principal after adjustments")
    
    # Implementation details
    moratorium_start_date: Optional[date] = None
    moratorium_end_date: Optional[date] = None
    waiver_applied: Optional[Decimal] = Field(None, ge=0)
    
    implementation_remarks: Optional[str] = Field(None, description="Implementation notes")
    
    @field_validator('first_emi_date')
    @classmethod
    def validate_first_emi_date(cls, v, info):
        if 'implementation_date' in info.data and v < info.data['implementation_date']:
            raise ValueError('First EMI date must be on or after implementation date')
        return v
    
    @field_validator('moratorium_end_date')
    @classmethod
    def validate_moratorium_end_date(cls, v, info):
        if v and 'moratorium_start_date' in info.data:
            if not info.data['moratorium_start_date']:
                raise ValueError('Moratorium start date required if end date provided')
            if v <= info.data['moratorium_start_date']:
                raise ValueError('Moratorium end date must be after start date')
        return v


class RestructuringResponse(BaseModel):
    """Schema for restructuring response"""
    id: int
    loan_account_id: int
    restructuring_number: str
    restructuring_type: RestructuringTypeEnum
    reason: RestructuringReasonEnum
    reason_details: str
    status: RestructuringStatusEnum
    
    # Current loan details
    current_emi: Decimal
    current_outstanding: Decimal
    current_tenure_remaining: int
    
    # Proposed parameters
    proposed_emi: Optional[Decimal] = None
    proposed_tenure: Optional[int] = None
    proposed_interest_rate: Optional[Decimal] = None
    moratorium_months: Optional[int] = None
    
    # Approved parameters
    approved_emi: Optional[Decimal] = None
    approved_tenure: Optional[int] = None
    approved_interest_rate: Optional[Decimal] = None
    approved_moratorium_months: Optional[int] = None
    
    # Implemented parameters
    final_emi: Optional[Decimal] = None
    final_tenure: Optional[int] = None
    final_interest_rate: Optional[Decimal] = None
    final_outstanding: Optional[Decimal] = None
    
    # Financial details
    customer_income: Optional[Decimal] = None
    customer_obligations: Optional[Decimal] = None
    waiver_amount: Optional[Decimal] = None
    waiver_type: Optional[str] = None
    estimated_loss: Optional[Decimal] = None
    recovery_probability: Optional[Decimal] = None
    
    # Supporting information
    supporting_documents: Optional[List[str]] = None
    
    # Approval details
    approval_remarks: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    credit_committee_approval: bool
    risk_assessment: Optional[str] = None
    
    # Rejection details
    rejection_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    alternative_suggestions: Optional[str] = None
    can_reapply: Optional[bool] = None
    reapply_after_days: Optional[int] = None
    
    # Implementation details
    implementation_date: Optional[date] = None
    first_emi_date: Optional[date] = None
    moratorium_start_date: Optional[date] = None
    moratorium_end_date: Optional[date] = None
    implemented_at: Optional[datetime] = None
    implemented_by: Optional[int] = None
    implementation_remarks: Optional[str] = None
    
    # Customer contact
    customer_mobile: Optional[str] = None
    customer_email: Optional[str] = None
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class RestructuringListFilter(BaseModel):
    """Filters for restructuring list"""
    loan_account_id: Optional[int] = None
    status: Optional[RestructuringStatusEnum] = None
    restructuring_type: Optional[RestructuringTypeEnum] = None
    reason: Optional[RestructuringReasonEnum] = None
    created_from: Optional[date] = None
    created_to: Optional[date] = None


class RestructuringSummary(BaseModel):
    """Summary of restructuring for a loan"""
    loan_account_id: int
    total_restructurings: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int
    implemented_requests: int
    last_restructuring_date: Optional[date] = None
    total_waiver_amount: Decimal
    current_status: Optional[RestructuringStatusEnum] = None
    can_request_new: bool
    cooling_period_days: Optional[int] = None


class RestructuringStatistics(BaseModel):
    """Overall restructuring statistics"""
    total_requests: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int
    implemented_requests: int
    cancelled_requests: int
    
    # By type
    by_type: dict
    
    # By reason
    by_reason: dict
    
    # Financial impact
    total_waiver_amount: Decimal
    total_estimated_loss: Decimal
    average_waiver_per_case: Decimal
    
    # Performance metrics
    average_approval_time_days: Optional[float] = None
    average_implementation_time_days: Optional[float] = None
    approval_rate: float
    implementation_rate: float


class RestructuringImpactAnalysis(BaseModel):
    """Impact analysis for a restructuring request"""
    loan_account_id: int
    restructuring_id: Optional[int] = None
    
    # Current state
    current_emi: Decimal
    current_outstanding: Decimal
    current_tenure_remaining: int
    current_total_payable: Decimal
    
    # Proposed state
    proposed_emi: Decimal
    proposed_tenure: int
    proposed_total_payable: Decimal
    
    # Impact calculation
    emi_reduction: Decimal
    emi_reduction_percentage: float
    tenure_increase: int
    additional_interest: Decimal
    npv_loss: Decimal
    
    # Risk assessment
    debt_to_income_ratio: Optional[float] = None
    modified_dti_ratio: Optional[float] = None
    impact_level: ImpactAssessmentEnum
    recommendation: str
    
    # Affordability check
    is_affordable: bool
    minimum_required_income: Decimal
    surplus_after_emi: Optional[Decimal] = None


class RestructuringHistory(BaseModel):
    """Historical restructuring record"""
    restructuring_response: RestructuringResponse
    previous_restructurings: List[RestructuringResponse]
    time_since_last_restructuring_days: Optional[int] = None
    restructuring_count: int
    pattern_analysis: Optional[str] = None


# ============================================
# Bulk Operation Schemas
# ============================================

class BulkRestructuringRequest(BaseModel):
    """Request for bulk restructuring (e.g., COVID relief)"""
    loan_account_ids: List[int] = Field(..., min_length=1, max_length=1000)
    restructuring_type: RestructuringTypeEnum
    reason: RestructuringReasonEnum
    reason_details: str = Field(..., min_length=20)
    
    # Common parameters
    moratorium_months: Optional[int] = Field(None, ge=0, le=12)
    tenure_extension_months: Optional[int] = Field(None, ge=0)
    interest_rate_reduction: Optional[Decimal] = Field(None, ge=0)
    
    # Approval details
    bulk_approval_reference: str = Field(..., description="Reference for bulk approval")
    approved_by_committee: bool = Field(default=True)
    
    # Implementation
    auto_implement: bool = Field(default=False, description="Auto-implement after creation")


class BulkRestructuringResponse(BaseModel):
    """Response for bulk restructuring"""
    total_requests: int
    successful: int
    failed: int
    bulk_approval_reference: str
    restructuring_responses: List[RestructuringResponse]
    errors: List[dict]
