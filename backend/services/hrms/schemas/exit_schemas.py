"""
Exit Management Pydantic Schemas
Request/Response models for Exit Management API
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
import enum


# ============================================================================
# ENUMS
# ============================================================================

class ResignationType(str, enum.Enum):
    """Type of resignation"""
    VOLUNTARY = "voluntary"
    INVOLUNTARY = "involuntary"
    RETIREMENT = "retirement"
    ABSCONDING = "absconding"
    END_OF_CONTRACT = "end_of_contract"
    MUTUAL_CONSENT = "mutual_consent"


class ResignationStatus(str, enum.Enum):
    """Resignation status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClearanceStatus(str, enum.Enum):
    """Clearance status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NOT_APPLICABLE = "not_applicable"
    WAIVED = "waived"


class SettlementStatus(str, enum.Enum):
    """Settlement status"""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PROCESSING = "processing"
    PAID = "paid"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"


class SettlementComponentType(str, enum.Enum):
    """Settlement component type"""
    SALARY = "salary"
    LEAVE_ENCASHMENT = "leave_encashment"
    NOTICE_PAY = "notice_pay"
    BONUS = "bonus"
    GRATUITY = "gratuity"
    REIMBURSEMENT = "reimbursement"
    RECOVERY = "recovery"
    OTHER = "other"


class ExitDocumentType(str, enum.Enum):
    """Exit document type"""
    RESIGNATION_LETTER = "resignation_letter"
    ACCEPTANCE_LETTER = "acceptance_letter"
    EXPERIENCE_LETTER = "experience_letter"
    RELIEVING_LETTER = "relieving_letter"
    SERVICE_CERTIFICATE = "service_certificate"
    NOC = "noc"
    CLEARANCE_FORM = "clearance_form"
    FNF_STATEMENT = "fnf_statement"
    FORM_16 = "form_16"
    PF_WITHDRAWAL = "pf_withdrawal"
    GRATUITY_FORM = "gratuity_form"
    OTHER = "other"


# ============================================================================
# RESIGNATION SCHEMAS
# ============================================================================

class ResignationBase(BaseModel):
    """Base resignation schema"""
    resignation_type: ResignationType = Field(default=ResignationType.VOLUNTARY)
    resignation_date: date = Field(...)
    last_working_date: date = Field(...)
    notice_period_days: int = Field(default=30, ge=0, le=365)
    reason_category: Optional[str] = Field(None, max_length=100)
    reason_details: str = Field(..., min_length=10, max_length=2000)
    feedback: Optional[str] = Field(None, max_length=2000)
    
    @validator('last_working_date')
    def validate_last_working_date(cls, v, values):
        if 'resignation_date' in values and v < values['resignation_date']:
            raise ValueError('Last working date must be after resignation date')
        return v


class ResignationCreate(ResignationBase):
    """Schema for creating resignation"""
    employee_id: UUID = Field(...)
    resignation_letter_path: Optional[str] = Field(None, max_length=500)
    supporting_documents: Optional[str] = Field(None)  # JSON string


class ResignationUpdate(BaseModel):
    """Schema for updating resignation"""
    resignation_type: Optional[ResignationType] = None
    last_working_date: Optional[date] = None
    actual_last_working_date: Optional[date] = None
    notice_period_days: Optional[int] = Field(None, ge=0, le=365)
    notice_period_served: Optional[int] = Field(None, ge=0, le=365)
    is_notice_period_waived: Optional[bool] = None
    notice_waiver_reason: Optional[str] = Field(None, max_length=2000)
    reason_category: Optional[str] = Field(None, max_length=100)
    reason_details: Optional[str] = Field(None, min_length=10, max_length=2000)
    feedback: Optional[str] = Field(None, max_length=2000)
    resignation_letter_path: Optional[str] = Field(None, max_length=500)
    supporting_documents: Optional[str] = None


class ManagerReviewSchema(BaseModel):
    """Schema for manager review"""
    manager_comments: str = Field(..., min_length=10, max_length=2000)
    manager_recommendation: str = Field(..., max_length=50)  # approve, reject, counter_offer
    counter_offer_details: Optional[str] = Field(None, max_length=2000)


class HRReviewSchema(BaseModel):
    """Schema for HR review"""
    hr_comments: str = Field(..., min_length=10, max_length=2000)
    re_employment_eligible: bool = Field(default=True)
    blacklist_flag: bool = Field(default=False)
    blacklist_reason: Optional[str] = Field(None, max_length=2000)


class ResignationApprovalSchema(BaseModel):
    """Schema for resignation approval"""
    approval_comments: str = Field(..., min_length=10, max_length=2000)
    actual_last_working_date: date = Field(...)


class ResignationRejectionSchema(BaseModel):
    """Schema for resignation rejection"""
    rejection_reason: str = Field(..., min_length=10, max_length=2000)


class ResignationWithdrawalSchema(BaseModel):
    """Schema for resignation withdrawal"""
    withdrawal_reason: str = Field(..., min_length=10, max_length=2000)


class ExitInterviewSchema(BaseModel):
    """Schema for exit interview"""
    exit_interview_date: datetime = Field(...)
    exit_interview_notes: str = Field(..., min_length=10, max_length=5000)
    feedback: Optional[str] = Field(None, max_length=2000)


class HandoverSchema(BaseModel):
    """Schema for handover"""
    handover_to_employee_id: UUID = Field(...)
    handover_notes: str = Field(..., min_length=10, max_length=2000)
    handover_document_path: Optional[str] = Field(None, max_length=500)


class ResignationResponse(ResignationBase):
    """Schema for resignation response"""
    id: UUID
    resignation_code: str
    employee_id: UUID
    actual_last_working_date: Optional[date]
    notice_period_served: Optional[int]
    is_notice_period_waived: bool
    notice_waiver_reason: Optional[str]
    status: ResignationStatus
    
    # Workflow
    reporting_manager_id: Optional[UUID]
    manager_reviewed_date: Optional[datetime]
    manager_comments: Optional[str]
    manager_recommendation: Optional[str]
    
    hr_reviewer_id: Optional[UUID]
    hr_reviewed_date: Optional[datetime]
    hr_comments: Optional[str]
    
    approved_by_id: Optional[UUID]
    approved_date: Optional[datetime]
    approval_comments: Optional[str]
    
    rejected_date: Optional[datetime]
    rejection_reason: Optional[str]
    withdrawn_date: Optional[datetime]
    withdrawal_reason: Optional[str]
    
    # Counter offer
    counter_offer_made: bool
    counter_offer_details: Optional[str]
    counter_offer_accepted: Optional[bool]
    
    # Exit interview
    exit_interview_scheduled: bool
    exit_interview_date: Optional[datetime]
    exit_interview_conducted_by_id: Optional[UUID]
    exit_interview_notes: Optional[str]
    
    # Handover
    handover_completed: bool
    handover_to_employee_id: Optional[UUID]
    handover_notes: Optional[str]
    handover_document_path: Optional[str]
    
    # Additional
    re_employment_eligible: bool
    blacklist_flag: bool
    blacklist_reason: Optional[str]
    
    resignation_letter_path: Optional[str]
    supporting_documents: Optional[str]
    
    # Audit
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    
    class Config:
        orm_mode = True


# ============================================================================
# CLEARANCE SCHEMAS
# ============================================================================

class ClearanceBase(BaseModel):
    """Base clearance schema"""
    clearance_from: str = Field(..., min_length=2, max_length=100)
    clearance_type: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    checklist_items: Optional[str] = None  # JSON string
    is_mandatory: bool = Field(default=True)
    due_date: Optional[date] = None


class ClearanceCreate(ClearanceBase):
    """Schema for creating clearance"""
    resignation_id: UUID = Field(...)
    assigned_to_id: Optional[UUID] = None
    depends_on_clearance_id: Optional[UUID] = None


class ClearanceUpdate(BaseModel):
    """Schema for updating clearance"""
    clearance_from: Optional[str] = Field(None, min_length=2, max_length=100)
    clearance_type: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ClearanceStatus] = None
    checklist_items: Optional[str] = None
    pending_items: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[date] = None
    is_mandatory: Optional[bool] = None
    depends_on_clearance_id: Optional[UUID] = None


class ClearanceCompleteSchema(BaseModel):
    """Schema for completing clearance"""
    clearance_remarks: str = Field(..., min_length=10, max_length=2000)
    supporting_documents: Optional[str] = None  # JSON string


class ClearanceResponse(ClearanceBase):
    """Schema for clearance response"""
    id: UUID
    resignation_id: UUID
    status: ClearanceStatus
    
    assigned_to_id: Optional[UUID]
    assigned_date: Optional[datetime]
    
    pending_items: Optional[str]
    
    cleared_by_id: Optional[UUID]
    cleared_date: Optional[datetime]
    clearance_remarks: Optional[str]
    
    supporting_documents: Optional[str]
    
    depends_on_clearance_id: Optional[UUID]
    
    is_overdue: bool
    escalated: bool
    escalation_level: int
    
    # Audit
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ============================================================================
# SETTLEMENT SCHEMAS
# ============================================================================

class SettlementComponentBase(BaseModel):
    """Base settlement component schema"""
    component_type: SettlementComponentType = Field(...)
    component_name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    is_deduction: bool = Field(default=False)
    calculation_basis: Optional[str] = Field(None, max_length=2000)
    quantity: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    rate: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_taxable: bool = Field(default=True)
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    remarks: Optional[str] = Field(None, max_length=2000)


class SettlementComponentCreate(SettlementComponentBase):
    """Schema for creating settlement component"""
    settlement_id: UUID = Field(...)


class SettlementComponentUpdate(BaseModel):
    """Schema for updating settlement component"""
    component_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_deduction: Optional[bool] = None
    calculation_basis: Optional[str] = Field(None, max_length=2000)
    quantity: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    rate: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    is_taxable: Optional[bool] = None
    tax_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    remarks: Optional[str] = Field(None, max_length=2000)


class SettlementComponentResponse(SettlementComponentBase):
    """Schema for settlement component response"""
    id: UUID
    settlement_id: UUID
    
    # Audit
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class SettlementBase(BaseModel):
    """Base settlement schema"""
    settlement_from_date: date = Field(...)
    settlement_to_date: date = Field(...)
    
    @validator('settlement_to_date')
    def validate_settlement_to_date(cls, v, values):
        if 'settlement_from_date' in values and v < values['settlement_from_date']:
            raise ValueError('Settlement to date must be after from date')
        return v


class SettlementCreate(SettlementBase):
    """Schema for creating settlement"""
    resignation_id: UUID = Field(...)
    employee_id: UUID = Field(...)


class SettlementCalculationSchema(BaseModel):
    """Schema for settlement calculation"""
    # Salary
    basic_salary_days: Optional[int] = Field(None, ge=0, le=31)
    basic_salary_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    
    # Leave
    total_leave_balance: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    encashable_leaves: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    leave_encashment_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    
    # Notice period
    notice_period_shortfall_days: int = Field(default=0, ge=0, le=365)
    notice_pay_recovery: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    
    # Gratuity
    years_of_service: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    gratuity_eligible: bool = Field(default=False)
    gratuity_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    
    # Bonus
    bonus_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    incentive_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    
    # Reimbursements
    pending_reimbursement_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    
    # Recoveries
    loan_recovery: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    advance_recovery: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    asset_loss_recovery: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    other_recovery: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    recovery_remarks: Optional[str] = Field(None, max_length=2000)
    
    # Tax
    tds_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    professional_tax: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    
    calculation_remarks: Optional[str] = Field(None, max_length=2000)


class SettlementApprovalSchema(BaseModel):
    """Schema for settlement approval"""
    approval_remarks: str = Field(..., min_length=10, max_length=2000)


class SettlementPaymentSchema(BaseModel):
    """Schema for settlement payment"""
    payment_date: date = Field(...)
    payment_mode: str = Field(..., max_length=50)  # bank_transfer, cheque, cash
    payment_reference: str = Field(..., max_length=100)
    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=200)
    bank_ifsc_code: Optional[str] = Field(None, max_length=20)
    finance_remarks: Optional[str] = Field(None, max_length=2000)


class SettlementHoldSchema(BaseModel):
    """Schema for putting settlement on hold"""
    hold_reason: str = Field(..., min_length=10, max_length=2000)
    hold_until_date: Optional[date] = None


class SettlementResponse(SettlementBase):
    """Schema for settlement response"""
    id: UUID
    settlement_code: str
    resignation_id: UUID
    employee_id: UUID
    status: SettlementStatus
    
    # Calculation details
    basic_salary_days: Optional[int]
    basic_salary_amount: Decimal
    
    total_leave_balance: Decimal
    encashable_leaves: Decimal
    leave_encashment_amount: Decimal
    
    notice_period_shortfall_days: int
    notice_pay_recovery: Decimal
    
    years_of_service: Optional[Decimal]
    gratuity_eligible: bool
    gratuity_amount: Decimal
    
    bonus_amount: Decimal
    incentive_amount: Decimal
    
    pending_reimbursement_amount: Decimal
    
    loan_recovery: Decimal
    advance_recovery: Decimal
    asset_loss_recovery: Decimal
    other_recovery: Decimal
    recovery_remarks: Optional[str]
    
    gross_payable: Decimal
    total_deductions: Decimal
    net_payable: Decimal
    
    tds_amount: Decimal
    professional_tax: Decimal
    
    # Workflow
    calculated_by_id: Optional[UUID]
    calculated_date: Optional[datetime]
    calculation_remarks: Optional[str]
    
    approved_by_id: Optional[UUID]
    approved_date: Optional[datetime]
    approval_remarks: Optional[str]
    
    finance_processor_id: Optional[UUID]
    finance_processed_date: Optional[datetime]
    finance_remarks: Optional[str]
    
    # Payment
    payment_date: Optional[date]
    payment_mode: Optional[str]
    payment_reference: Optional[str]
    bank_account_number: Optional[str]
    bank_name: Optional[str]
    bank_ifsc_code: Optional[str]
    
    # Hold/Rejection
    hold_reason: Optional[str]
    hold_until_date: Optional[date]
    rejected_date: Optional[datetime]
    rejection_reason: Optional[str]
    
    fnf_statement_path: Optional[str]
    supporting_documents: Optional[str]
    
    # Audit
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ============================================================================
# DOCUMENT SCHEMAS
# ============================================================================

class DocumentBase(BaseModel):
    """Base document schema"""
    document_type: ExitDocumentType = Field(...)
    document_name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    template_name: Optional[str] = Field(None, max_length=200)


class DocumentCreate(DocumentBase):
    """Schema for creating document"""
    resignation_id: UUID = Field(...)
    employee_id: UUID = Field(...)
    document_content: Optional[str] = None
    document_path: Optional[str] = Field(None, max_length=500)
    document_url: Optional[str] = Field(None, max_length=500)


class DocumentGenerateSchema(BaseModel):
    """Schema for generating document"""
    document_type: ExitDocumentType = Field(...)
    template_name: Optional[str] = Field(None, max_length=200)
    template_version: Optional[str] = Field(None, max_length=20)
    document_number: Optional[str] = Field(None, max_length=100)
    issue_place: Optional[str] = Field(None, max_length=200)
    validity_date: Optional[date] = None


class DocumentApprovalSchema(BaseModel):
    """Schema for document approval"""
    approval_remarks: str = Field(..., min_length=10, max_length=2000)


class DocumentIssuanceSchema(BaseModel):
    """Schema for document issuance"""
    issue_remarks: str = Field(..., min_length=10, max_length=2000)
    delivery_mode: str = Field(..., max_length=50)  # email, hard_copy, courier, portal
    recipient_email: Optional[str] = Field(None, max_length=100)
    recipient_address: Optional[str] = Field(None, max_length=500)


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: UUID
    document_code: str
    resignation_id: UUID
    employee_id: UUID
    
    template_version: Optional[str]
    
    document_content: Optional[str]
    document_path: Optional[str]
    document_url: Optional[str]
    
    is_generated: bool
    is_approved: bool
    is_issued: bool
    
    generated_by_id: Optional[UUID]
    generated_date: Optional[datetime]
    
    approved_by_id: Optional[UUID]
    approved_date: Optional[datetime]
    approval_remarks: Optional[str]
    
    issued_by_id: Optional[UUID]
    issued_date: Optional[datetime]
    issue_remarks: Optional[str]
    
    document_number: Optional[str]
    issue_place: Optional[str]
    validity_date: Optional[date]
    
    is_digitally_signed: bool
    digital_signature_info: Optional[str]
    
    delivery_mode: Optional[str]
    delivered_date: Optional[datetime]
    recipient_email: Optional[str]
    recipient_address: Optional[str]
    tracking_number: Optional[str]
    
    acknowledged_by_employee: bool
    acknowledgment_date: Optional[datetime]
    
    # Audit
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ============================================================================
# FILTER AND PAGINATION SCHEMAS
# ============================================================================

class ResignationFilter(BaseModel):
    """Schema for filtering resignations"""
    employee_id: Optional[UUID] = None
    resignation_type: Optional[ResignationType] = None
    status: Optional[ResignationStatus] = None
    reporting_manager_id: Optional[UUID] = None
    resignation_date_from: Optional[date] = None
    resignation_date_to: Optional[date] = None
    last_working_date_from: Optional[date] = None
    last_working_date_to: Optional[date] = None
    search: Optional[str] = None  # Search in resignation_code, reason_details


class ClearanceFilter(BaseModel):
    """Schema for filtering clearances"""
    resignation_id: Optional[UUID] = None
    status: Optional[ClearanceStatus] = None
    assigned_to_id: Optional[UUID] = None
    clearance_from: Optional[str] = None
    is_overdue: Optional[bool] = None
    is_mandatory: Optional[bool] = None


class SettlementFilter(BaseModel):
    """Schema for filtering settlements"""
    employee_id: Optional[UUID] = None
    resignation_id: Optional[UUID] = None
    status: Optional[SettlementStatus] = None
    payment_date_from: Optional[date] = None
    payment_date_to: Optional[date] = None
    search: Optional[str] = None  # Search in settlement_code


class DocumentFilter(BaseModel):
    """Schema for filtering documents"""
    resignation_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    document_type: Optional[ExitDocumentType] = None
    is_generated: Optional[bool] = None
    is_approved: Optional[bool] = None
    is_issued: Optional[bool] = None


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = Field(default="created_at")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    """Schema for paginated response"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============================================================================
# DASHBOARD AND STATISTICS SCHEMAS
# ============================================================================

class ExitDashboardStats(BaseModel):
    """Schema for exit management dashboard statistics"""
    # Resignations
    total_resignations: int = 0
    pending_resignations: int = 0
    approved_resignations: int = 0
    rejected_resignations: int = 0
    
    # By type
    voluntary_resignations: int = 0
    involuntary_resignations: int = 0
    
    # This month
    resignations_this_month: int = 0
    exits_this_month: int = 0
    
    # Clearances
    pending_clearances: int = 0
    overdue_clearances: int = 0
    
    # Settlements
    pending_settlements: int = 0
    approved_settlements: int = 0
    total_settlement_amount: Decimal = Decimal('0.00')
    
    # Documents
    pending_documents: int = 0
    issued_documents: int = 0


class ExitAnalytics(BaseModel):
    """Schema for exit analytics"""
    period: str  # month, quarter, year
    total_exits: int
    voluntary_exits: int
    involuntary_exits: int
    avg_tenure_years: Decimal
    top_resignation_reasons: List[Dict[str, Any]]
    department_wise_exits: List[Dict[str, Any]]
    avg_settlement_amount: Decimal


# ============================================================================
# BULK OPERATIONS SCHEMAS
# ============================================================================

class BulkClearanceCreate(BaseModel):
    """Schema for creating multiple clearances"""
    resignation_id: UUID
    clearances: List[ClearanceCreate]


class BulkDocumentGenerate(BaseModel):
    """Schema for generating multiple documents"""
    resignation_id: UUID
    document_types: List[ExitDocumentType]


# ============================================================================
# NOTIFICATION SCHEMAS
# ============================================================================

class ExitNotification(BaseModel):
    """Schema for exit-related notifications"""
    notification_type: str  # resignation_submitted, clearance_assigned, settlement_ready, etc.
    recipient_ids: List[UUID]
    subject: str
    message: str
    data: Optional[Dict[str, Any]] = None
