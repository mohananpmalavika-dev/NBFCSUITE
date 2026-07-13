"""
Legal - Litigation Management Schemas
Pydantic models for case tracking, hearing management, and legal expense tracking
"""

from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class CaseTypeEnum(str, Enum):
    """Case type enumeration"""
    CIVIL = "civil"
    CRIMINAL = "criminal"
    ARBITRATION = "arbitration"
    RECOVERY = "recovery"
    CONSUMER = "consumer"
    LABOR = "labor"
    TAX = "tax"
    CORPORATE = "corporate"
    PROPERTY = "property"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    BANKING = "banking"
    REGULATORY = "regulatory"
    WRIT = "writ"
    APPEAL = "appeal"
    OTHER = "other"


class CaseStatusEnum(str, Enum):
    """Case status enumeration"""
    FILED = "filed"
    ADMITTED = "admitted"
    IN_PROGRESS = "in_progress"
    EVIDENCE_STAGE = "evidence_stage"
    ARGUMENT_STAGE = "argument_stage"
    JUDGMENT_RESERVED = "judgment_reserved"
    JUDGMENT_DELIVERED = "judgment_delivered"
    DISPOSED = "disposed"
    WON = "won"
    LOST = "lost"
    SETTLED = "settled"
    WITHDRAWN = "withdrawn"
    DISMISSED = "dismissed"
    APPEALED = "appealed"
    STAYED = "stayed"


class CasePriorityEnum(str, Enum):
    """Case priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class PartyRoleEnum(str, Enum):
    """Party role in litigation"""
    PETITIONER = "petitioner"
    RESPONDENT = "respondent"
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    APPELLANT = "appellant"
    RESPONDENT_APPELLANT = "respondent_appellant"
    WITNESS = "witness"
    ADVOCATE = "advocate"
    THIRD_PARTY = "third_party"


class HearingTypeEnum(str, Enum):
    """Hearing type enumeration"""
    FIRST_HEARING = "first_hearing"
    REGULAR_HEARING = "regular_hearing"
    INTERIM_APPLICATION = "interim_application"
    EVIDENCE_RECORDING = "evidence_recording"
    CROSS_EXAMINATION = "cross_examination"
    ARGUMENT = "argument"
    FINAL_ARGUMENT = "final_argument"
    JUDGMENT = "judgment"
    EXECUTION = "execution"
    OTHER = "other"


class HearingStatusEnum(str, Enum):
    """Hearing status enumeration"""
    SCHEDULED = "scheduled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    ADJOURNED = "adjourned"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ExpenseCategoryEnum(str, Enum):
    """Legal expense category"""
    COURT_FEES = "court_fees"
    ADVOCATE_FEES = "advocate_fees"
    CONSULTATION_FEES = "consultation_fees"
    DOCUMENTATION = "documentation"
    TRAVEL = "travel"
    EXPERT_WITNESS = "expert_witness"
    INVESTIGATION = "investigation"
    STAMP_DUTY = "stamp_duty"
    NOTARY = "notary"
    TRANSLATION = "translation"
    PHOTOCOPYING = "photocopying"
    MISC = "misc"


# ============================================================================
# CASE PARTY SCHEMAS
# ============================================================================

class CasePartyBase(BaseModel):
    """Base schema for case party"""
    party_role: PartyRoleEnum
    party_name: str = Field(..., max_length=500)
    party_designation: Optional[str] = Field(None, max_length=200)
    organization_name: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    is_represented: bool = False
    advocate_name: Optional[str] = Field(None, max_length=500)
    advocate_firm: Optional[str] = Field(None, max_length=500)
    advocate_contact: Optional[str] = Field(None, max_length=100)
    advocate_email: Optional[str] = Field(None, max_length=200)
    party_type: Optional[str] = Field(None, max_length=100)
    identification_number: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class CasePartyCreate(CasePartyBase):
    """Schema for creating a case party"""
    case_id: UUID


class CasePartyUpdate(BaseModel):
    """Schema for updating a case party"""
    party_role: Optional[PartyRoleEnum] = None
    party_name: Optional[str] = Field(None, max_length=500)
    party_designation: Optional[str] = Field(None, max_length=200)
    organization_name: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    is_represented: Optional[bool] = None
    advocate_name: Optional[str] = Field(None, max_length=500)
    advocate_firm: Optional[str] = Field(None, max_length=500)
    advocate_contact: Optional[str] = Field(None, max_length=100)
    advocate_email: Optional[str] = Field(None, max_length=200)
    party_type: Optional[str] = Field(None, max_length=100)
    identification_number: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class CasePartyResponse(CasePartyBase):
    """Schema for case party response"""
    id: UUID
    case_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# LITIGATION CASE SCHEMAS
# ============================================================================

class LitigationCaseBase(BaseModel):
    """Base schema for litigation case"""
    case_number: str = Field(..., max_length=200)
    case_title: str = Field(..., max_length=1000)
    case_type: CaseTypeEnum
    case_sub_type: Optional[str] = Field(None, max_length=200)
    priority: CasePriorityEnum = CasePriorityEnum.MEDIUM
    court_name: str = Field(..., max_length=500)
    court_location: Optional[str] = Field(None, max_length=500)
    bench: Optional[str] = Field(None, max_length=200)
    judge_name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    subject_matter: Optional[str] = None
    relief_sought: Optional[str] = None
    claim_amount: Optional[Decimal] = None
    disputed_amount: Optional[Decimal] = None
    awarded_amount: Optional[Decimal] = None
    currency: str = "INR"
    filing_date: date
    admission_date: Optional[date] = None
    first_hearing_date: Optional[date] = None
    next_hearing_date: Optional[date] = None
    expected_closure_date: Optional[date] = None
    limitation_date: Optional[date] = None
    primary_advocate: Optional[str] = Field(None, max_length=500)
    primary_advocate_contact: Optional[str] = Field(None, max_length=100)
    advocate_firm: Optional[str] = Field(None, max_length=500)
    risk_level: Optional[str] = Field(None, max_length=50)
    business_impact: Optional[str] = None
    potential_liability: Optional[Decimal] = None
    alert_before_hearing_days: int = 7
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    internal_remarks: Optional[str] = None


class LitigationCaseCreate(LitigationCaseBase):
    """Schema for creating a litigation case"""
    pass


class LitigationCaseUpdate(BaseModel):
    """Schema for updating a litigation case"""
    case_title: Optional[str] = Field(None, max_length=1000)
    case_type: Optional[CaseTypeEnum] = None
    case_sub_type: Optional[str] = Field(None, max_length=200)
    status: Optional[CaseStatusEnum] = None
    priority: Optional[CasePriorityEnum] = None
    court_name: Optional[str] = Field(None, max_length=500)
    court_location: Optional[str] = Field(None, max_length=500)
    bench: Optional[str] = Field(None, max_length=200)
    judge_name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    subject_matter: Optional[str] = None
    relief_sought: Optional[str] = None
    claim_amount: Optional[Decimal] = None
    disputed_amount: Optional[Decimal] = None
    awarded_amount: Optional[Decimal] = None
    admission_date: Optional[date] = None
    first_hearing_date: Optional[date] = None
    next_hearing_date: Optional[date] = None
    expected_closure_date: Optional[date] = None
    closure_date: Optional[date] = None
    limitation_date: Optional[date] = None
    judgment_date: Optional[date] = None
    judgment_summary: Optional[str] = None
    judgment_document_url: Optional[str] = Field(None, max_length=1000)
    is_favorable: Optional[bool] = None
    primary_advocate: Optional[str] = Field(None, max_length=500)
    primary_advocate_contact: Optional[str] = Field(None, max_length=100)
    advocate_firm: Optional[str] = Field(None, max_length=500)
    risk_level: Optional[str] = Field(None, max_length=50)
    business_impact: Optional[str] = None
    potential_liability: Optional[Decimal] = None
    alert_before_hearing_days: Optional[int] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    internal_remarks: Optional[str] = None


class LitigationCaseResponse(LitigationCaseBase):
    """Schema for litigation case response"""
    id: UUID
    tenant_id: str
    status: CaseStatusEnum
    closure_date: Optional[date] = None
    judgment_date: Optional[date] = None
    judgment_summary: Optional[str] = None
    judgment_document_url: Optional[str] = None
    is_favorable: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    
    # Summary counts
    total_hearings: Optional[int] = 0
    total_expenses: Optional[Decimal] = 0
    total_parties: Optional[int] = 0

    class Config:
        from_attributes = True


# ============================================================================
# CASE HEARING SCHEMAS
# ============================================================================

class CaseHearingBase(BaseModel):
    """Base schema for case hearing"""
    hearing_type: HearingTypeEnum
    scheduled_date: datetime
    court_room: Optional[str] = Field(None, max_length=100)
    judge_name: Optional[str] = Field(None, max_length=500)
    purpose: Optional[str] = None
    agenda: Optional[str] = None
    advocate_name: Optional[str] = Field(None, max_length=500)
    client_attended: bool = False


class CaseHearingCreate(CaseHearingBase):
    """Schema for creating a case hearing"""
    case_id: UUID


class CaseHearingUpdate(BaseModel):
    """Schema for updating a case hearing"""
    hearing_type: Optional[HearingTypeEnum] = None
    hearing_status: Optional[HearingStatusEnum] = None
    scheduled_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    court_room: Optional[str] = Field(None, max_length=100)
    judge_name: Optional[str] = Field(None, max_length=500)
    purpose: Optional[str] = None
    agenda: Optional[str] = None
    proceedings: Optional[str] = None
    orders_passed: Optional[str] = None
    next_action_required: Optional[str] = None
    next_hearing_date: Optional[datetime] = None
    adjournment_reason: Optional[str] = Field(None, max_length=500)
    advocate_attended: Optional[bool] = None
    advocate_name: Optional[str] = Field(None, max_length=500)
    client_attended: Optional[bool] = None
    opposing_party_attended: Optional[bool] = None
    documents_submitted: Optional[List[str]] = None
    notes: Optional[str] = None


class CaseHearingResponse(CaseHearingBase):
    """Schema for case hearing response"""
    id: UUID
    case_id: UUID
    hearing_number: int
    hearing_status: HearingStatusEnum
    actual_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    proceedings: Optional[str] = None
    orders_passed: Optional[str] = None
    next_action_required: Optional[str] = None
    next_hearing_date: Optional[datetime] = None
    adjournment_reason: Optional[str] = None
    advocate_attended: bool
    opposing_party_attended: Optional[bool] = None
    documents_submitted: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    reminder_sent: bool
    reminder_sent_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


# ============================================================================
# LEGAL EXPENSE SCHEMAS
# ============================================================================

class LegalExpenseBase(BaseModel):
    """Base schema for legal expense"""
    expense_category: ExpenseCategoryEnum
    description: str
    amount: Decimal = Field(..., gt=0)
    currency: str = "INR"
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    expense_date: date
    payment_mode: Optional[str] = Field(None, max_length=100)
    payment_reference: Optional[str] = Field(None, max_length=200)
    payee_name: str = Field(..., max_length=500)
    payee_contact: Optional[str] = Field(None, max_length=100)
    payee_pan: Optional[str] = Field(None, max_length=50)
    invoice_number: Optional[str] = Field(None, max_length=200)
    invoice_date: Optional[date] = None
    invoice_url: Optional[str] = Field(None, max_length=1000)
    is_reimbursable: bool = False
    budget_head: Optional[str] = Field(None, max_length=200)
    cost_center: Optional[str] = Field(None, max_length=200)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    @computed_field
    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount"""
        return self.amount + (self.tax_amount or Decimal(0))


class LegalExpenseCreate(LegalExpenseBase):
    """Schema for creating a legal expense"""
    case_id: UUID


class LegalExpenseUpdate(BaseModel):
    """Schema for updating a legal expense"""
    expense_category: Optional[ExpenseCategoryEnum] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    expense_date: Optional[date] = None
    payment_date: Optional[date] = None
    payment_mode: Optional[str] = Field(None, max_length=100)
    payment_reference: Optional[str] = Field(None, max_length=200)
    payee_name: Optional[str] = Field(None, max_length=500)
    payee_contact: Optional[str] = Field(None, max_length=100)
    payee_pan: Optional[str] = Field(None, max_length=50)
    invoice_number: Optional[str] = Field(None, max_length=200)
    invoice_date: Optional[date] = None
    invoice_url: Optional[str] = Field(None, max_length=1000)
    is_approved: Optional[bool] = None
    approval_remarks: Optional[str] = None
    is_paid: Optional[bool] = None
    is_reimbursable: Optional[bool] = None
    reimbursed_amount: Optional[Decimal] = None
    reimbursement_date: Optional[date] = None
    budget_head: Optional[str] = Field(None, max_length=200)
    cost_center: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class LegalExpenseResponse(LegalExpenseBase):
    """Schema for legal expense response"""
    id: UUID
    tenant_id: str
    case_id: UUID
    expense_number: str
    # total_amount is computed in base class
    payment_date: Optional[date] = None
    is_approved: bool
    approved_by: Optional[UUID] = None
    approval_date: Optional[datetime] = None
    approval_remarks: Optional[str] = None
    is_paid: bool
    paid_by: Optional[UUID] = None
    reimbursed_amount: Optional[Decimal] = None
    reimbursement_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID

    class Config:
        from_attributes = True


# ============================================================================
# CASE DOCUMENT SCHEMAS
# ============================================================================

class CaseDocumentBase(BaseModel):
    """Base schema for case document"""
    document_name: str = Field(..., max_length=500)
    document_type: Optional[str] = Field(None, max_length=200)
    document_category: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    document_date: Optional[date] = None
    filing_date: Optional[date] = None
    is_confidential: bool = False
    tags: List[str] = Field(default_factory=list)


class CaseDocumentCreate(CaseDocumentBase):
    """Schema for creating a case document"""
    case_id: UUID
    hearing_id: Optional[UUID] = None
    file_name: str = Field(..., max_length=500)
    file_size: Optional[int] = None
    file_type: Optional[str] = Field(None, max_length=100)
    file_url: str = Field(..., max_length=1000)
    file_hash: Optional[str] = Field(None, max_length=256)


class CaseDocumentUpdate(BaseModel):
    """Schema for updating a case document"""
    document_name: Optional[str] = Field(None, max_length=500)
    document_type: Optional[str] = Field(None, max_length=200)
    document_category: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    document_date: Optional[date] = None
    filing_date: Optional[date] = None
    is_confidential: Optional[bool] = None
    tags: Optional[List[str]] = None


class CaseDocumentResponse(CaseDocumentBase):
    """Schema for case document response"""
    id: UUID
    case_id: UUID
    hearing_id: Optional[UUID] = None
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    file_url: str
    file_hash: Optional[str] = None
    version: int
    uploaded_by: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# STATISTICS & ANALYTICS SCHEMAS
# ============================================================================

class CaseStatistics(BaseModel):
    """Case statistics schema"""
    total_cases: int
    active_cases: int
    won_cases: int
    lost_cases: int
    settled_cases: int
    pending_cases: int
    total_claim_amount: Decimal
    total_awarded_amount: Decimal
    total_legal_expenses: Decimal
    cases_by_type: Dict[str, int]
    cases_by_status: Dict[str, int]
    cases_by_priority: Dict[str, int]
    upcoming_hearings: int


class ExpenseStatistics(BaseModel):
    """Expense statistics schema"""
    total_expenses: Decimal
    approved_expenses: Decimal
    paid_expenses: Decimal
    pending_approvals: Decimal
    expenses_by_category: Dict[str, Decimal]
    expenses_by_month: Dict[str, Decimal]
    top_payees: List[Dict[str, Any]]


class HearingStatistics(BaseModel):
    """Hearing statistics schema"""
    total_hearings: int
    completed_hearings: int
    scheduled_hearings: int
    adjourned_hearings: int
    hearings_this_week: int
    hearings_this_month: int
    hearings_by_type: Dict[str, int]
