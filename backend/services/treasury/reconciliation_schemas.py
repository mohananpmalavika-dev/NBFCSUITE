"""
Treasury - Bank Reconciliation Schemas
Pydantic models for bank reconciliation, statements, and matching
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Enums
class ReconciliationStatus(str, Enum):
    """Reconciliation status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    MATCHED = "matched"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReconciliationItemType(str, Enum):
    """Types of reconciliation items"""
    OUTSTANDING_CHEQUE = "outstanding_cheque"
    DEPOSIT_IN_TRANSIT = "deposit_in_transit"
    BANK_CHARGES = "bank_charges"
    INTEREST_EARNED = "interest_earned"
    DIRECT_DEBIT = "direct_debit"
    DIRECT_CREDIT = "direct_credit"
    ERROR_CORRECTION = "error_correction"
    OTHER = "other"


# Bank Statement Schemas
class BankStatementCreate(BaseModel):
    """Create bank statement entry"""
    bank_account_id: int = Field(..., description="Bank account ID")
    transaction_date: date = Field(..., description="Transaction date")
    value_date: Optional[date] = Field(None, description="Value date")
    transaction_reference: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., description="Transaction description")
    cheque_number: Optional[str] = Field(None, max_length=50)
    debit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    balance: Optional[Decimal] = Field(None, description="Balance after transaction")
    import_batch_id: Optional[str] = Field(None, max_length=50)

    @field_validator('debit_amount', 'credit_amount')
    @classmethod
    def validate_amounts(cls, v):
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v


class BankStatementUpdate(BaseModel):
    """Update bank statement entry"""
    transaction_date: Optional[date] = None
    value_date: Optional[date] = None
    transaction_reference: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cheque_number: Optional[str] = Field(None, max_length=50)
    debit_amount: Optional[Decimal] = Field(None, ge=0)
    credit_amount: Optional[Decimal] = Field(None, ge=0)
    balance: Optional[Decimal] = None


class BankStatementResponse(BaseModel):
    """Bank statement response"""
    id: int
    tenant_id: int
    bank_account_id: int
    transaction_date: date
    value_date: Optional[date]
    transaction_reference: Optional[str]
    description: str
    cheque_number: Optional[str]
    debit_amount: Decimal
    credit_amount: Decimal
    balance: Optional[Decimal]
    import_batch_id: Optional[str]
    import_date: datetime
    imported_by: int
    is_matched: bool
    matched_gl_entry_id: Optional[int]
    matched_at: Optional[datetime]
    matched_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class BankStatementBulkImport(BaseModel):
    """Bulk import bank statements"""
    bank_account_id: int
    import_batch_id: str = Field(..., max_length=50)
    statements: List[BankStatementCreate]


# Reconciliation Item Schemas
class ReconciliationItemCreate(BaseModel):
    """Create reconciliation item"""
    item_type: ReconciliationItemType
    item_date: date
    description: str = Field(..., description="Item description")
    reference_number: Optional[str] = Field(None, max_length=100)
    amount: Decimal = Field(..., gt=0, description="Item amount")
    is_debit: bool = Field(default=True, description="Is this a debit item?")
    bank_statement_id: Optional[int] = Field(None, description="Linked bank statement ID")
    gl_entry_id: Optional[int] = Field(None, description="Linked GL entry ID")
    notes: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than zero')
        return v


class ReconciliationItemUpdate(BaseModel):
    """Update reconciliation item"""
    item_type: Optional[ReconciliationItemType] = None
    item_date: Optional[date] = None
    description: Optional[str] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    amount: Optional[Decimal] = Field(None, gt=0)
    is_debit: Optional[bool] = None
    bank_statement_id: Optional[int] = None
    gl_entry_id: Optional[int] = None
    is_matched: Optional[bool] = None
    is_cleared: Optional[bool] = None
    cleared_date: Optional[date] = None
    notes: Optional[str] = None


class ReconciliationItemResponse(BaseModel):
    """Reconciliation item response"""
    id: int
    tenant_id: int
    reconciliation_id: int
    item_type: ReconciliationItemType
    item_date: date
    description: str
    reference_number: Optional[str]
    amount: Decimal
    is_debit: bool
    bank_statement_id: Optional[int]
    gl_entry_id: Optional[int]
    is_matched: bool
    is_cleared: bool
    cleared_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True


# Bank Reconciliation Schemas
class BankReconciliationCreate(BaseModel):
    """Create bank reconciliation"""
    bank_account_id: int = Field(..., description="Bank account ID")
    reconciliation_date: date = Field(..., description="Reconciliation date")
    period_start_date: date = Field(..., description="Period start date")
    period_end_date: date = Field(..., description="Period end date")
    book_balance: Decimal = Field(..., description="Book balance (GL)")
    bank_balance: Decimal = Field(..., description="Bank statement balance")
    notes: Optional[str] = None

    @field_validator('period_end_date')
    @classmethod
    def validate_dates(cls, v, info):
        if 'period_start_date' in info.data and v < info.data['period_start_date']:
            raise ValueError('End date must be after start date')
        return v


class BankReconciliationUpdate(BaseModel):
    """Update bank reconciliation"""
    reconciliation_date: Optional[date] = None
    period_start_date: Optional[date] = None
    period_end_date: Optional[date] = None
    book_balance: Optional[Decimal] = None
    bank_balance: Optional[Decimal] = None
    notes: Optional[str] = None
    approval_notes: Optional[str] = None


class BankReconciliationResponse(BaseModel):
    """Bank reconciliation response"""
    id: int
    tenant_id: int
    reconciliation_number: str
    reconciliation_date: date
    bank_account_id: int
    period_start_date: date
    period_end_date: date
    book_balance: Decimal
    bank_balance: Decimal
    difference: Decimal
    total_matched: int
    total_unmatched: int
    matched_amount: Decimal
    unmatched_amount: Decimal
    status: ReconciliationStatus
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    approval_notes: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class BankReconciliationDetail(BankReconciliationResponse):
    """Bank reconciliation with items"""
    items: List[ReconciliationItemResponse] = []


class BankReconciliationApprove(BaseModel):
    """Approve reconciliation"""
    approval_notes: Optional[str] = None


class BankReconciliationReject(BaseModel):
    """Reject reconciliation"""
    approval_notes: str = Field(..., description="Reason for rejection")


# Matching Schemas
class MatchTransactionRequest(BaseModel):
    """Request to match bank statement with GL entry"""
    bank_statement_id: int = Field(..., description="Bank statement ID")
    gl_entry_id: Optional[int] = Field(None, description="GL entry ID")


class UnmatchTransactionRequest(BaseModel):
    """Request to unmatch a transaction"""
    bank_statement_id: int = Field(..., description="Bank statement ID")


class AutoMatchRequest(BaseModel):
    """Request for automatic matching"""
    reconciliation_id: int = Field(..., description="Reconciliation ID")
    match_tolerance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Tolerance for amount matching"
    )
    match_days_range: int = Field(
        default=3,
        ge=0,
        le=30,
        description="Date range for matching (days)"
    )


# Statistics and Reports
class ReconciliationStatistics(BaseModel):
    """Reconciliation statistics"""
    total_reconciliations: int
    draft_count: int
    in_progress_count: int
    matched_count: int
    pending_approval_count: int
    approved_count: int
    rejected_count: int
    total_matched_amount: Decimal
    total_unmatched_amount: Decimal
    average_difference: Decimal
    oldest_unreconciled_date: Optional[date]


class BankStatementSummary(BaseModel):
    """Bank statement summary"""
    bank_account_id: int
    statement_count: int
    matched_count: int
    unmatched_count: int
    total_debit: Decimal
    total_credit: Decimal
    oldest_unmatched_date: Optional[date]


class ReconciliationDifference(BaseModel):
    """Reconciliation difference breakdown"""
    outstanding_cheques_amount: Decimal = Decimal("0.00")
    outstanding_cheques_count: int = 0
    deposits_in_transit_amount: Decimal = Decimal("0.00")
    deposits_in_transit_count: int = 0
    bank_charges_amount: Decimal = Decimal("0.00")
    bank_charges_count: int = 0
    interest_earned_amount: Decimal = Decimal("0.00")
    interest_earned_count: int = 0
    direct_debits_amount: Decimal = Decimal("0.00")
    direct_debits_count: int = 0
    direct_credits_amount: Decimal = Decimal("0.00")
    direct_credits_count: int = 0
    error_corrections_amount: Decimal = Decimal("0.00")
    error_corrections_count: int = 0
    other_amount: Decimal = Decimal("0.00")
    other_count: int = 0
    total_difference: Decimal = Decimal("0.00")
    total_items: int = 0


# List request/response
class BankReconciliationListRequest(BaseModel):
    """Request filters for listing reconciliations"""
    bank_account_id: Optional[int] = None
    status: Optional[ReconciliationStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)


class BankStatementListRequest(BaseModel):
    """Request filters for listing bank statements"""
    bank_account_id: Optional[int] = None
    is_matched: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    total: int
    items: List
    skip: int
    limit: int
