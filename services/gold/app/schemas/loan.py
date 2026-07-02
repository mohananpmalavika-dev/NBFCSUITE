"""
Loan Origination & Disbursement Schemas
Phase 6: Request/Response DTOs for loan management
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApplicationStage(str, Enum):
    APPLICATION = "application"
    CREDIT_CHECK = "credit_check"
    APPROVAL = "approval"
    DISBURSEMENT = "disbursement"
    COMPLETED = "completed"


class EvaluationType(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"
    HYBRID = "hybrid"


class RiskCategory(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFERRED = "referred"
    ON_HOLD = "on_hold"


class LoanStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    NPA = "npa"
    WRITTEN_OFF = "written_off"


class DisbursementMode(str, Enum):
    CASH = "cash"
    NEFT = "neft"
    IMPS = "imps"
    RTGS = "rtgs"
    UPI = "upi"
    CHEQUE = "cheque"


class DisbursementStatus(str, Enum):
    INITIATED = "initiated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# LOAN APPLICATION SCHEMAS
# ============================================================================

class ApplicationOrnamentCreate(BaseModel):
    ornament_id: str
    packet_id: Optional[str] = None


class ApplicationOrnamentResponse(BaseModel):
    id: str
    application_id: str
    ornament_id: str
    packet_id: Optional[str]
    ornament_type: str
    gross_weight: Decimal
    net_weight: Decimal
    purity: Decimal
    valuation_amount: Decimal
    market_rate: Optional[Decimal]
    lien_marked: bool
    lien_marked_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoanApplicationCreate(BaseModel):
    customer_id: str
    product_id: str
    journey_session_id: Optional[str] = None
    appraisal_session_id: Optional[str] = None
    branch_id: Optional[str] = None
    
    loan_amount: Decimal = Field(..., gt=0)
    requested_tenure: int = Field(..., gt=0)
    purpose: Optional[str] = None
    
    # Customer details
    customer_name: str
    customer_mobile: str
    customer_email: Optional[str] = None
    customer_pan: Optional[str] = None
    customer_address: Optional[str] = None
    
    # Ornament summary
    total_ornaments: int
    total_gross_weight: Decimal
    total_net_weight: Decimal
    total_valuation: Decimal
    ltv_percentage: Decimal = Field(..., ge=0, le=100)
    
    # Ornaments to link
    ornament_ids: List[str]


class LoanApplicationUpdate(BaseModel):
    loan_amount: Optional[Decimal] = Field(None, gt=0)
    requested_tenure: Optional[int] = Field(None, gt=0)
    purpose: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    stage: Optional[ApplicationStage] = None


class LoanApplicationSubmit(BaseModel):
    submitted_by: str


class LoanApplicationResponse(BaseModel):
    id: str
    application_number: str
    customer_id: str
    product_id: str
    journey_session_id: Optional[str]
    appraisal_session_id: Optional[str]
    branch_id: Optional[str]
    
    loan_amount: Decimal
    requested_tenure: int
    purpose: Optional[str]
    
    customer_name: str
    customer_mobile: str
    customer_email: Optional[str]
    customer_pan: Optional[str]
    customer_address: Optional[str]
    
    total_ornaments: int
    total_gross_weight: Decimal
    total_net_weight: Decimal
    total_valuation: Decimal
    ltv_percentage: Decimal
    
    status: str
    stage: str
    
    submitted_at: Optional[datetime]
    submitted_by: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# CREDIT EVALUATION SCHEMAS
# ============================================================================

class CreditEvaluationCreate(BaseModel):
    application_id: str
    evaluation_type: EvaluationType
    
    cibil_score: Optional[int] = None
    internal_credit_score: Optional[Decimal] = None
    
    risk_category: Optional[RiskCategory] = None
    risk_score: Optional[Decimal] = None
    risk_factors: Optional[Dict[str, Any]] = None
    
    existing_loans_count: int = 0
    existing_loans_amount: Decimal = Decimal(0)
    repayment_history: Optional[str] = None
    bounce_count: int = 0
    
    recommended_amount: Optional[Decimal] = None
    recommended_tenure: Optional[int] = None
    recommended_interest_rate: Optional[Decimal] = None
    recommended_decision: Optional[str] = None
    decision_reason: Optional[str] = None
    
    ai_recommendation: Optional[str] = None
    ai_confidence_score: Optional[Decimal] = None
    ai_factors: Optional[Dict[str, Any]] = None


class CreditEvaluationResponse(BaseModel):
    id: str
    application_id: str
    evaluation_type: str
    evaluation_status: str
    
    cibil_score: Optional[int]
    cibil_fetched_at: Optional[datetime]
    internal_credit_score: Optional[Decimal]
    
    risk_category: Optional[str]
    risk_score: Optional[Decimal]
    risk_factors: Optional[Dict[str, Any]]
    
    existing_loans_count: int
    existing_loans_amount: Decimal
    repayment_history: Optional[str]
    bounce_count: int
    
    recommended_amount: Optional[Decimal]
    recommended_tenure: Optional[int]
    recommended_interest_rate: Optional[Decimal]
    recommended_decision: Optional[str]
    decision_reason: Optional[str]
    
    ai_recommendation: Optional[str]
    ai_confidence_score: Optional[Decimal]
    ai_factors: Optional[Dict[str, Any]]
    
    evaluated_by: Optional[str]
    evaluated_at: Optional[datetime]
    evaluation_duration: Optional[int]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# APPROVAL WORKFLOW SCHEMAS
# ============================================================================

class LoanApprovalCreate(BaseModel):
    application_id: str
    approval_level: int = Field(..., ge=1)
    approver_role: str
    approver_id: Optional[str] = None
    sequence_order: int = Field(..., ge=1)
    is_final_approval: bool = False
    sla_deadline: Optional[datetime] = None


class LoanApprovalDecision(BaseModel):
    decision: str  # approve, reject, refer, hold
    approved_amount: Optional[Decimal] = None
    approved_tenure: Optional[int] = None
    approved_interest_rate: Optional[Decimal] = None
    approved_conditions: Optional[str] = None
    remarks: Optional[str] = None
    rejection_reason: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None


class LoanApprovalResponse(BaseModel):
    id: str
    application_id: str
    approval_level: int
    approver_role: str
    approver_id: Optional[str]
    
    status: str
    decision: Optional[str]
    
    approved_amount: Optional[Decimal]
    approved_tenure: Optional[int]
    approved_interest_rate: Optional[Decimal]
    approved_conditions: Optional[str]
    
    remarks: Optional[str]
    rejection_reason: Optional[str]
    conditions: Optional[Dict[str, Any]]
    
    assigned_at: datetime
    responded_at: Optional[datetime]
    sla_deadline: Optional[datetime]
    is_overdue: bool
    
    sequence_order: int
    is_final_approval: bool
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# LOAN ACCOUNT SCHEMAS
# ============================================================================

class LoanAccountCreate(BaseModel):
    application_id: str
    customer_id: str
    product_id: str
    branch_id: Optional[str] = None
    
    principal_amount: Decimal = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    interest_rate: Decimal = Field(..., ge=0)
    interest_type: str
    
    processing_fee: Decimal = Decimal(0)
    documentation_charges: Decimal = Decimal(0)
    valuation_charges: Decimal = Decimal(0)
    other_charges: Decimal = Decimal(0)
    
    loan_date: date
    due_date: date
    maturity_date: date
    
    linked_packets: Optional[List[str]] = None
    linked_ornaments: Optional[List[str]] = None


class LoanAccountResponse(BaseModel):
    id: str
    loan_account_number: str
    application_id: str
    customer_id: str
    product_id: str
    branch_id: Optional[str]
    
    principal_amount: Decimal
    tenure_months: int
    interest_rate: Decimal
    interest_type: str
    
    processing_fee: Decimal
    documentation_charges: Decimal
    valuation_charges: Decimal
    other_charges: Decimal
    total_charges: Decimal
    
    status: str
    disbursement_status: str
    
    loan_date: date
    due_date: date
    maturity_date: date
    closed_date: Optional[date]
    
    outstanding_principal: Decimal
    outstanding_interest: Decimal
    total_outstanding: Decimal
    
    total_paid: Decimal
    last_payment_date: Optional[date]
    next_due_date: Optional[date]
    
    days_overdue: int
    overdue_interest: Decimal
    is_npa: bool
    npa_date: Optional[date]
    
    linked_packets: Optional[List[str]]
    linked_ornaments: Optional[List[str]]
    
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# DISBURSEMENT SCHEMAS
# ============================================================================

class DisbursementCreate(BaseModel):
    application_id: str
    loan_account_id: Optional[str] = None
    
    disbursement_amount: Decimal = Field(..., gt=0)
    disbursement_mode: DisbursementMode
    disbursement_date: date
    
    # Payment details (conditional based on mode)
    beneficiary_name: Optional[str] = None
    beneficiary_account: Optional[str] = None
    beneficiary_ifsc: Optional[str] = None
    beneficiary_bank: Optional[str] = None
    upi_id: Optional[str] = None
    cheque_number: Optional[str] = None
    
    payment_reference: Optional[str] = None


class DisbursementVerify(BaseModel):
    verified_by: str
    verification_notes: Optional[str] = None
    utr_number: Optional[str] = None
    transaction_id: Optional[str] = None
    bank_reference: Optional[str] = None


class DisbursementResponse(BaseModel):
    id: str
    disbursement_number: str
    application_id: str
    loan_account_id: Optional[str]
    
    disbursement_amount: Decimal
    disbursement_mode: str
    disbursement_date: date
    disbursement_time: datetime
    
    payment_reference: Optional[str]
    beneficiary_name: Optional[str]
    beneficiary_account: Optional[str]
    beneficiary_ifsc: Optional[str]
    beneficiary_bank: Optional[str]
    upi_id: Optional[str]
    cheque_number: Optional[str]
    
    status: str
    failure_reason: Optional[str]
    
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    
    utr_number: Optional[str]
    transaction_id: Optional[str]
    bank_reference: Optional[str]
    
    processed_by: Optional[str]
    processed_at: Optional[datetime]
    
    created_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# DOCUMENT SCHEMAS
# ============================================================================

class LoanDocumentCreate(BaseModel):
    application_id: Optional[str] = None
    loan_account_id: Optional[str] = None
    
    document_type: str
    document_category: str
    document_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    document_number: Optional[str] = None


class LoanDocumentResponse(BaseModel):
    id: str
    application_id: Optional[str]
    loan_account_id: Optional[str]
    
    document_type: str
    document_category: str
    document_name: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    
    document_number: Optional[str]
    is_signed: bool
    signed_at: Optional[datetime]
    signed_by: Optional[str]
    
    is_verified: bool
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    
    status: str
    created_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# CHARGE SCHEMAS
# ============================================================================

class LoanChargeCreate(BaseModel):
    loan_account_id: str
    charge_type: str
    charge_name: str
    charge_amount: Decimal = Field(..., gt=0)
    tax_type: Optional[str] = None
    tax_percentage: Optional[Decimal] = None
    tax_amount: Decimal = Decimal(0)
    total_amount: Decimal = Field(..., gt=0)


class LoanChargeResponse(BaseModel):
    id: str
    loan_account_id: str
    charge_type: str
    charge_name: str
    charge_amount: Decimal
    tax_type: Optional[str]
    tax_percentage: Optional[Decimal]
    tax_amount: Decimal
    total_amount: Decimal
    is_paid: bool
    paid_date: Optional[date]
    payment_mode: Optional[str]
    payment_reference: Optional[str]
    is_waived: bool
    waived_amount: Decimal
    waived_by: Optional[str]
    waived_at: Optional[datetime]
    waiver_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# STATUS HISTORY SCHEMAS
# ============================================================================

class LoanStatusHistoryCreate(BaseModel):
    application_id: Optional[str] = None
    loan_account_id: Optional[str] = None
    from_status: Optional[str] = None
    to_status: str
    stage: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    changed_by: Optional[str] = None


class LoanStatusHistoryResponse(BaseModel):
    id: str
    application_id: Optional[str]
    loan_account_id: Optional[str]
    from_status: Optional[str]
    to_status: str
    stage: Optional[str]
    changed_by: Optional[str]
    changed_at: datetime
    reason: Optional[str]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# SUMMARY/STATS SCHEMAS
# ============================================================================

class ApplicationSummary(BaseModel):
    total_applications: int
    draft: int
    submitted: int
    under_review: int
    approved: int
    rejected: int
    total_amount: Decimal
    avg_ltv: Decimal


class LoanPortfolioSummary(BaseModel):
    total_loans: int
    active_loans: int
    total_principal: Decimal
    total_outstanding: Decimal
    npa_count: int
    npa_amount: Decimal
    collection_efficiency: Decimal


# ============================================================================
# LMS INTEGRATION SCHEMAS
# ============================================================================

class LMSIntegrationCreate(BaseModel):
    application_id: Optional[str] = None
    loan_account_id: Optional[str] = None
    integration_type: str
    lms_system: str
    request_payload: Dict[str, Any]


class LMSIntegrationResponse(BaseModel):
    id: str
    application_id: Optional[str]
    loan_account_id: Optional[str]
    integration_type: str
    lms_system: str
    request_payload: Dict[str, Any]
    response_payload: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    lms_loan_id: Optional[str]
    lms_reference_number: Optional[str]
    initiated_at: datetime
    completed_at: Optional[datetime]
    next_retry_at: Optional[datetime]
    
    class Config:
        from_attributes = True
