"""
Collection Management Schemas
Pydantic models for request/response validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum

# Import enums from models
from backend.shared.database.collection_models import (
    ActionType,
    ActionStatus,
    TemplateType,
    VisitStatus,
    VisitDisposition,
    PromiseStatus,
    PromiseSource,
    LegalNoticeType,
    NoticeStage,
    DeliveryStatus,
    CaseType,
    CaseStatus,
    CaseOutcome,
    RecoveryActionType,
    SettlementType,
    SettlementStatus,
    PaymentTerms
)


# ============================================================================
# COLLECTION STRATEGY SCHEMAS
# ============================================================================

class CollectionStrategyCreate(BaseModel):
    """Create collection strategy"""
    strategy_name: str = Field(..., max_length=200)
    strategy_code: str = Field(..., max_length=50)
    description: Optional[str] = None
    dpd_min: int = Field(..., ge=0)
    dpd_max: int = Field(..., ge=0)
    action_type: ActionType
    frequency_days: int = Field(1, ge=1)
    max_attempts: int = Field(3, ge=1)
    template_id: Optional[int] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    escalate_after_days: Optional[int] = None
    escalate_to_strategy_id: Optional[int] = None
    priority: int = Field(1, ge=1)
    
    @field_validator('dpd_max')
    @classmethod
    def validate_dpd_range(cls, v, info):
        if 'dpd_min' in info.data and v < info.data['dpd_min']:
            raise ValueError('dpd_max must be greater than or equal to dpd_min')
        return v


class CollectionStrategyUpdate(BaseModel):
    """Update collection strategy"""
    strategy_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    frequency_days: Optional[int] = Field(None, ge=1)
    max_attempts: Optional[int] = Field(None, ge=1)
    template_id: Optional[int] = None
    priority: Optional[int] = Field(None, ge=1)


class CollectionStrategyResponse(BaseModel):
    """Collection strategy response"""
    id: int
    strategy_name: str
    strategy_code: str
    description: Optional[str]
    dpd_min: int
    dpd_max: int
    action_type: str
    frequency_days: int
    max_attempts: int
    template_id: Optional[int]
    is_active: bool
    priority: int
    created_at: str
    
    class Config:
        from_attributes = True


class CommunicationTemplateCreate(BaseModel):
    """Create communication template"""
    template_code: str = Field(..., max_length=50)
    template_name: str = Field(..., max_length=200)
    template_type: TemplateType
    content: str
    subject: Optional[str] = Field(None, max_length=500)
    language: str = Field("en", max_length=10)
    variables: Optional[List[str]] = None
    dpd_bucket: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=50)


class CommunicationTemplateResponse(BaseModel):
    """Communication template response"""
    id: int
    template_code: str
    template_name: str
    template_type: str
    content: str
    subject: Optional[str]
    language: str
    variables: Optional[List[str]]
    dpd_bucket: Optional[str]
    category: Optional[str]
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class CollectionActionResponse(BaseModel):
    """Collection action response"""
    id: int
    loan_account_id: int
    customer_id: int
    action_type: str
    action_date: str
    status: str
    response_received: bool
    response_details: Optional[str]
    next_action_date: Optional[str]
    notes: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class ExecuteStrategiesRequest(BaseModel):
    """Request to execute strategies"""
    loan_account_id: Optional[int] = None
    force_execution: bool = False


class UpdateActionStatusRequest(BaseModel):
    """Update action status"""
    status: ActionStatus
    response_details: Optional[str] = None
    next_action_date: Optional[datetime] = None
    next_action_type: Optional[ActionType] = None


# ============================================================================
# FIELD AGENT SCHEMAS
# ============================================================================

class TerritoryCreate(BaseModel):
    """Create territory"""
    territory_code: str = Field(..., max_length=50)
    territory_name: str = Field(..., max_length=200)
    state: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    pincode_list: Optional[List[str]] = None
    parent_territory_id: Optional[int] = None
    branch_id: Optional[int] = None


class TerritoryResponse(BaseModel):
    """Territory response"""
    id: int
    territory_code: str
    territory_name: str
    state: Optional[str]
    district: Optional[str]
    city: Optional[str]
    pincode_list: Optional[List[str]]
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class FieldAgentCreate(BaseModel):
    """Create field agent"""
    agent_code: str = Field(..., max_length=50)
    full_name: str = Field(..., max_length=200)
    mobile: str = Field(..., max_length=20)
    territory_id: int
    user_id: Optional[int] = None
    email: Optional[str] = Field(None, max_length=200)
    branch_id: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    employment_type: str = Field("permanent", max_length=50)
    joining_date: Optional[date] = None
    monthly_collection_target: Optional[Decimal] = None
    monthly_visit_target: Optional[int] = None


class FieldAgentResponse(BaseModel):
    """Field agent response"""
    id: int
    agent_code: str
    full_name: str
    mobile: str
    email: Optional[str]
    territory_id: int
    employment_type: str
    monthly_collection_target: float
    monthly_visit_target: int
    total_collection_amount: float
    total_visits_completed: int
    success_rate: float
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class FieldVisitCreate(BaseModel):
    """Create/schedule field visit"""
    loan_account_id: int
    customer_id: int
    agent_id: int
    visit_date: date
    scheduled_time: Optional[datetime] = None
    visit_type: str = Field("routine", max_length=50)


class FieldVisitUpdate(BaseModel):
    """Update field visit (from mobile app)"""
    visit_status: Optional[VisitStatus] = None
    disposition: Optional[VisitDisposition] = None
    amount_collected: Optional[Decimal] = None
    payment_mode: Optional[str] = Field(None, max_length=50)
    receipt_number: Optional[str] = Field(None, max_length=100)
    location_lat: Optional[Decimal] = None
    location_lng: Optional[Decimal] = None
    visit_notes: Optional[str] = None
    customer_remarks: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    next_visit_date: Optional[date] = None
    follow_up_required: bool = False


class FieldVisitResponse(BaseModel):
    """Field visit response"""
    id: int
    loan_account_id: int
    customer_id: int
    agent_id: int
    visit_date: str
    scheduled_time: Optional[str]
    visit_status: str
    visit_type: str
    disposition: Optional[str]
    amount_collected: float
    payment_mode: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]
    visit_notes: Optional[str]
    next_visit_date: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class VisitTargetCreate(BaseModel):
    """Set visit target"""
    agent_id: int
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)
    target_collection_amount: Decimal = Field(..., gt=0)
    target_visit_count: int = Field(..., gt=0)


class VisitTargetResponse(BaseModel):
    """Visit target response"""
    id: int
    agent_id: int
    month: int
    year: int
    target_collection_amount: float
    target_visit_count: int
    achieved_collection_amount: float
    achieved_visit_count: int
    achievement_percentage: float
    
    class Config:
        from_attributes = True


class AgentDashboardResponse(BaseModel):
    """Agent mobile dashboard"""
    agent: Dict[str, Any]
    today: Dict[str, Any]
    monthly_performance: Dict[str, Any]
    upcoming_visits: List[Dict[str, Any]]


class RecordPaymentFromVisitRequest(BaseModel):
    """Record payment during visit"""
    amount: Decimal = Field(..., gt=0)
    payment_mode: str = Field(..., max_length=50)
    promise_amount: Optional[Decimal] = Field(None, gt=0)
    promise_date: Optional[date] = None


# ============================================================================
# PAYMENT PROMISE SCHEMAS
# ============================================================================

class PaymentPromiseCreate(BaseModel):
    """Create payment promise"""
    loan_account_id: int
    customer_id: int
    promise_amount: Decimal = Field(..., gt=0)
    promise_date: date
    promised_by: PromiseSource
    agent_id: Optional[int] = None
    field_visit_id: Optional[int] = None
    collection_action_id: Optional[int] = None
    notes: Optional[str] = None
    customer_remarks: Optional[str] = None


class PaymentPromiseResponse(BaseModel):
    """Payment promise response"""
    id: int
    loan_account_id: int
    customer_id: int
    promise_amount: float
    promise_date: str
    promised_on_date: str
    promised_by: str
    promise_status: str
    actual_payment_amount: Optional[float]
    actual_payment_date: Optional[str]
    notes: Optional[str]
    reminder_sent: bool
    created_at: str
    
    class Config:
        from_attributes = True


class UpdatePromiseStatusRequest(BaseModel):
    """Update promise status"""
    new_status: PromiseStatus
    actual_payment_amount: Optional[Decimal] = Field(None, gt=0)
    actual_payment_date: Optional[date] = None
    payment_transaction_id: Optional[int] = None
    broken_reason: Optional[str] = None
    remarks: Optional[str] = None


class ReschedulePromiseRequest(BaseModel):
    """Reschedule promise"""
    new_promise_date: date
    new_promise_amount: Optional[Decimal] = Field(None, gt=0)
    remarks: Optional[str] = None


class PromiseAnalyticsResponse(BaseModel):
    """Promise analytics"""
    period: Dict[str, str]
    summary: Dict[str, Any]
    status_breakdown: Dict[str, Any]


# ============================================================================
# LEGAL & RECOVERY SCHEMAS
# ============================================================================

class LegalNoticeCreate(BaseModel):
    """Create legal notice"""
    loan_account_id: int
    customer_id: int
    notice_type: LegalNoticeType
    notice_stage: NoticeStage
    notice_amount_demanded: Decimal = Field(..., gt=0)
    template_id: Optional[int] = None
    dispatch_mode: str = Field("registered_post", max_length=50)


class LegalNoticeResponse(BaseModel):
    """Legal notice response"""
    id: int
    loan_account_id: int
    customer_id: int
    notice_type: str
    notice_stage: str
    notice_number: str
    notice_date: str
    notice_amount_demanded: float
    dispatch_mode: str
    delivery_status: str
    delivery_date: Optional[str]
    response_received: bool
    response_date: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class UpdateNoticeDeliveryRequest(BaseModel):
    """Update notice delivery"""
    delivery_status: DeliveryStatus
    delivery_date: Optional[date] = None
    delivered_to: Optional[str] = Field(None, max_length=200)
    tracking_number: Optional[str] = Field(None, max_length=100)


class RecordNoticeResponseRequest(BaseModel):
    """Record notice response"""
    response_details: str
    response_date: Optional[date] = None
    next_action: Optional[str] = Field(None, max_length=200)


class LegalCaseCreate(BaseModel):
    """File legal case"""
    loan_account_id: int
    customer_id: int
    case_type: CaseType
    claim_amount: Decimal = Field(..., gt=0)
    court_name: Optional[str] = Field(None, max_length=300)
    lawyer_id: Optional[int] = None
    lawyer_name: Optional[str] = Field(None, max_length=200)


class LegalCaseResponse(BaseModel):
    """Legal case response"""
    id: int
    loan_account_id: int
    customer_id: int
    case_number: str
    case_type: str
    court_name: Optional[str]
    filing_date: str
    claim_amount: float
    case_status: str
    next_hearing_date: Optional[str]
    total_hearings: int
    case_outcome: Optional[str]
    total_legal_cost: float
    created_at: str
    
    class Config:
        from_attributes = True


class UpdateCaseStatusRequest(BaseModel):
    """Update case status"""
    case_status: CaseStatus
    next_hearing_date: Optional[date] = None
    remarks: Optional[str] = None


class RecordJudgementRequest(BaseModel):
    """Record case judgement"""
    judgement_details: str
    judgement_amount: Optional[Decimal] = Field(None, gt=0)
    case_outcome: CaseOutcome = CaseOutcome.PENDING


class CaseHearingCreate(BaseModel):
    """Add case hearing"""
    case_id: int
    hearing_date: date
    hearing_time: Optional[str] = Field(None, max_length=20)
    judge_name: Optional[str] = Field(None, max_length=200)
    hearing_notes: Optional[str] = None
    next_hearing_date: Optional[date] = None


class CaseHearingResponse(BaseModel):
    """Case hearing response"""
    id: int
    case_id: int
    hearing_date: str
    hearing_time: Optional[str]
    judge_name: Optional[str]
    hearing_notes: Optional[str]
    next_hearing_date: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class RecoveryAgencyCreate(BaseModel):
    """Create recovery agency"""
    agency_code: str = Field(..., max_length=50)
    agency_name: str = Field(..., max_length=200)
    mobile: str = Field(..., max_length=20)
    commission_percentage: Decimal = Field(..., ge=0, le=100)
    contact_person: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = None


class RecoveryAgencyResponse(BaseModel):
    """Recovery agency response"""
    id: int
    agency_code: str
    agency_name: str
    contact_person: Optional[str]
    mobile: str
    email: Optional[str]
    commission_percentage: float
    total_cases_assigned: int
    total_amount_recovered: float
    performance_rating: Optional[float]
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class AssignToAgencyRequest(BaseModel):
    """Assign loan to agency"""
    agency_id: int
    loan_account_id: int
    customer_id: int
    outstanding_amount: Decimal = Field(..., gt=0)
    commission_agreed: Optional[Decimal] = Field(None, ge=0, le=100)


class RecordAgencyRecoveryRequest(BaseModel):
    """Record agency recovery"""
    recovery_amount: Decimal = Field(..., gt=0)
    commission_amount: Optional[Decimal] = Field(None, ge=0)


class RecoveryActionCreate(BaseModel):
    """Create recovery action"""
    loan_account_id: int
    customer_id: int
    action_type: RecoveryActionType
    assigned_to_internal: bool = True
    assigned_user_id: Optional[int] = None
    assigned_agency_id: Optional[int] = None
    remarks: Optional[str] = None


class RecoveryActionResponse(BaseModel):
    """Recovery action response"""
    id: int
    loan_account_id: int
    customer_id: int
    action_type: str
    action_date: str
    action_status: str
    recovery_amount: float
    recovery_cost: float
    net_recovery: float
    created_at: str
    
    class Config:
        from_attributes = True


class UpdateRecoveryActionRequest(BaseModel):
    """Update recovery action"""
    action_status: str = Field(..., max_length=50)
    recovery_amount: Optional[Decimal] = Field(None, ge=0)
    recovery_cost: Optional[Decimal] = Field(None, ge=0)
    remarks: Optional[str] = None


# ============================================================================
# SETTLEMENT/OTS SCHEMAS
# ============================================================================

class WaiverPolicyCreate(BaseModel):
    """Create waiver policy"""
    policy_code: str = Field(..., max_length=50)
    policy_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    min_dpd: int = Field(..., ge=0)
    max_dpd: int = Field(..., ge=0)
    max_waiver_percentage_interest: Decimal = Field(..., ge=0, le=100)
    max_waiver_percentage_penal: Decimal = Field(..., ge=0, le=100)
    min_recovery_percentage: Decimal = Field(..., ge=0, le=100)
    loan_product_ids: Optional[List[int]] = None
    approval_required: bool = True
    approval_authority: Optional[str] = Field(None, max_length=100)


class WaiverPolicyResponse(BaseModel):
    """Waiver policy response"""
    id: int
    policy_code: str
    policy_name: str
    description: Optional[str]
    min_dpd: int
    max_dpd: int
    max_waiver_percentage_interest: float
    max_waiver_percentage_penal: float
    min_recovery_percentage: float
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class SettlementProposalCreate(BaseModel):
    """Create settlement proposal"""
    loan_account_id: int
    customer_id: int
    proposal_type: SettlementType
    proposed_settlement_amount: Decimal = Field(..., gt=0)
    requested_by: str = Field("customer", max_length=50)
    waiver_policy_id: Optional[int] = None
    payment_terms: PaymentTerms = PaymentTerms.LUMP_SUM
    installment_count: Optional[int] = Field(None, ge=1)
    justification: Optional[str] = None
    financial_hardship_details: Optional[str] = None
    
    @field_validator('installment_count')
    @classmethod
    def validate_installments(cls, v, info):
        if 'payment_terms' in info.data:
            if info.data['payment_terms'] == PaymentTerms.INSTALLMENTS and not v:
                raise ValueError('installment_count required for installment payment terms')
        return v


class SettlementProposalResponse(BaseModel):
    """Settlement proposal response"""
    id: int
    loan_account_id: int
    customer_id: int
    proposal_number: str
    proposal_type: str
    total_outstanding: float
    outstanding_principal: float
    outstanding_interest: float
    penal_charges: float
    proposed_settlement_amount: float
    waiver_on_interest: float
    waiver_on_penal: float
    waiver_percentage: float
    payment_terms: str
    proposal_status: str
    request_date: str
    created_at: str
    
    class Config:
        from_attributes = True


class SettlementCalculationResponse(BaseModel):
    """Settlement calculation details"""
    proposal: SettlementProposalResponse
    calculation: Dict[str, Any]


class SettlementNPVResponse(BaseModel):
    """Settlement NPV analysis"""
    proposal_id: int
    settlement_amount: float
    estimated_recovery_amount: float
    present_value_recovery: float
    npv: float
    recommendation: str


class SubmitForApprovalRequest(BaseModel):
    """Submit proposal for approval"""
    approver_user_id: int
    approval_level: int = Field(1, ge=1)


class ApproveSettlementRequest(BaseModel):
    """Approve settlement"""
    remarks: Optional[str] = None
    forward_to_next_level: bool = False
    next_approver_user_id: Optional[int] = None


class RejectSettlementRequest(BaseModel):
    """Reject settlement"""
    remarks: str = Field(..., min_length=1)


class SettlementApprovalResponse(BaseModel):
    """Settlement approval response"""
    id: int
    proposal_id: int
    approval_level: int
    approver_user_id: int
    approval_status: str
    approval_date: Optional[str]
    approval_remarks: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class CreateSettlementAgreementRequest(BaseModel):
    """Create settlement agreement"""
    proposal_id: int
    payment_deadline: date
    terms_and_conditions: str
    breach_clause: Optional[str] = None
    breach_penalty: Optional[Decimal] = Field(None, ge=0)


class SettlementAgreementResponse(BaseModel):
    """Settlement agreement response"""
    id: int
    proposal_id: int
    agreement_number: str
    agreement_date: str
    settlement_amount: float
    payment_deadline: str
    payment_schedule: Optional[List[Dict[str, Any]]]
    agreement_status: str
    customer_signed_date: Optional[str]
    bank_signed_date: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class RecordSettlementPaymentRequest(BaseModel):
    """Record settlement payment"""
    installment_number: int = Field(..., ge=1)
    paid_amount: Decimal = Field(..., gt=0)
    payment_date: Optional[date] = None
    transaction_id: Optional[int] = None


class SettlementPaymentResponse(BaseModel):
    """Settlement payment response"""
    id: int
    agreement_id: int
    installment_number: int
    due_date: str
    due_amount: float
    paid_amount: float
    payment_date: Optional[str]
    payment_status: str
    
    class Config:
        from_attributes = True


class SettlementStatisticsResponse(BaseModel):
    """Settlement statistics"""
    period: Dict[str, str]
    summary: Dict[str, Any]
    status_breakdown: Dict[str, Any]


# ============================================================================
# COMMON SCHEMAS
# ============================================================================

class PaginationResponse(BaseModel):
    """Pagination metadata"""
    total: int
    skip: int
    limit: int
    pages: int


class ListResponse(BaseModel):
    """Generic list response with pagination"""
    items: List[Any]
    pagination: PaginationResponse


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
