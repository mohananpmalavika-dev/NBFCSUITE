"""
Phase 7: Loan Servicing & Repayment - Pydantic Schemas
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    WAIVED = "waived"


class PaymentMode(str, Enum):
    CASH = "cash"
    CHEQUE = "cheque"
    NEFT = "neft"
    IMPS = "imps"
    RTGS = "rtgs"
    UPI = "upi"
    AUTO_DEBIT = "auto_debit"
    ADJUSTMENT = "adjustment"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    BOUNCED = "bounced"
    REVERSED = "reversed"
    CANCELLED = "cancelled"


class AccrualStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"


class AdjustmentType(str, Enum):
    WAIVER = "waiver"
    WRITE_OFF = "write_off"
    REVERSAL = "reversal"
    CORRECTION = "correction"
    PENALTY = "penalty"
    REBATE = "rebate"


class AdjustmentCategory(str, Enum):
    PRINCIPAL = "principal"
    INTEREST = "interest"
    PENALTY = "penalty"
    CHARGES = "charges"


class PrepaymentType(str, Enum):
    PART_PAYMENT = "part_payment"
    FORECLOSURE = "foreclosure"
    FULL_PREPAYMENT = "full_prepayment"


class StatementType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ON_DEMAND = "on_demand"


class MandateType(str, Enum):
    NACH = "nach"
    EMANDATE = "emandate"
    STANDING_INSTRUCTION = "standing_instruction"


class MandateStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class PenaltyType(str, Enum):
    LATE_PAYMENT = "late_payment"
    BOUNCED_CHEQUE = "bounced_cheque"
    PRE_CLOSURE = "pre_closure"
    PENAL_INTEREST = "penal_interest"
    DOCUMENTATION = "documentation"


class RenewalType(str, Enum):
    TERM_EXTENSION = "term_extension"
    INTEREST_SETTLEMENT = "interest_settlement"
    TOP_UP = "top_up"


class AllocationPriority(str, Enum):
    PENALTY = "penalty"
    OVERDUE_INTEREST = "overdue_interest"
    CURRENT_INTEREST = "current_interest"
    PRINCIPAL = "principal"
    CHARGES = "charges"


# ============================================================================
# EMI Schedule Schemas
# ============================================================================

class EMIScheduleBase(BaseModel):
    loan_account_id: str
    installment_number: int
    due_date: date
    principal_component: Decimal
    interest_component: Decimal
    total_emi_amount: Decimal


class EMIScheduleCreate(EMIScheduleBase):
    created_by_user_id: Optional[str] = None


class EMIScheduleUpdate(BaseModel):
    payment_status: Optional[PaymentStatus] = None
    paid_amount: Optional[Decimal] = None
    paid_date: Optional[date] = None
    payment_mode: Optional[PaymentMode] = None
    transaction_reference: Optional[str] = None
    overdue_charges: Optional[Decimal] = None


class EMIScheduleResponse(EMIScheduleBase):
    id: str
    payment_status: PaymentStatus
    paid_amount: Decimal
    paid_date: Optional[date]
    payment_mode: Optional[PaymentMode]
    outstanding_principal: Optional[Decimal]
    outstanding_interest: Optional[Decimal]
    days_overdue: int
    overdue_charges: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Repayment Transaction Schemas
# ============================================================================

class RepaymentTransactionBase(BaseModel):
    loan_account_id: str
    payment_amount: Decimal = Field(..., gt=0)
    payment_mode: PaymentMode
    transaction_reference: Optional[str] = None
    bank_name: Optional[str] = None
    cheque_number: Optional[str] = None
    cheque_date: Optional[date] = None


class RepaymentTransactionCreate(RepaymentTransactionBase):
    processed_by_user_id: str
    branch_id: Optional[str] = None
    remarks: Optional[str] = None


class PaymentAllocation(BaseModel):
    principal_paid: Decimal = Field(default=Decimal(0))
    interest_paid: Decimal = Field(default=Decimal(0))
    overdue_interest_paid: Decimal = Field(default=Decimal(0))
    penalty_paid: Decimal = Field(default=Decimal(0))
    other_charges_paid: Decimal = Field(default=Decimal(0))


class RepaymentTransactionUpdate(BaseModel):
    transaction_status: Optional[TransactionStatus] = None
    verified_by_user_id: Optional[str] = None
    reversal_reason: Optional[str] = None


class RepaymentTransactionResponse(RepaymentTransactionBase):
    id: str
    transaction_date: datetime
    receipt_number: str
    principal_paid: Decimal
    interest_paid: Decimal
    overdue_interest_paid: Decimal
    penalty_paid: Decimal
    other_charges_paid: Decimal
    transaction_status: TransactionStatus
    processed_by_user_id: str
    verified_by_user_id: Optional[str]
    verification_date: Optional[datetime]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Interest Accrual Schemas
# ============================================================================

class InterestAccrualBase(BaseModel):
    loan_account_id: str
    accrual_date: date
    accrual_period_start: date
    accrual_period_end: date
    opening_principal: Decimal
    closing_principal: Decimal
    applicable_rate: Decimal
    days_in_period: int
    interest_accrued: Decimal
    cumulative_interest: Decimal


class InterestAccrualCreate(InterestAccrualBase):
    calculation_method: Optional[str] = None
    created_by_user_id: Optional[str] = None


class InterestAccrualResponse(InterestAccrualBase):
    id: str
    accrual_status: AccrualStatus
    calculation_method: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Loan Adjustment Schemas
# ============================================================================

class LoanAdjustmentBase(BaseModel):
    loan_account_id: str
    adjustment_type: AdjustmentType
    adjustment_amount: Decimal
    adjustment_category: AdjustmentCategory
    reason: str


class LoanAdjustmentCreate(LoanAdjustmentBase):
    requested_by_user_id: str
    branch_id: Optional[str] = None
    supporting_document_id: Optional[str] = None


class LoanAdjustmentApproval(BaseModel):
    approved_by_user_id: str
    approval_status: str  # approved, rejected


class LoanAdjustmentResponse(LoanAdjustmentBase):
    id: str
    adjustment_date: datetime
    requested_by_user_id: str
    approved_by_user_id: Optional[str]
    approval_date: Optional[datetime]
    approval_status: str
    branch_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Prepayment Schemas
# ============================================================================

class LoanPrepaymentBase(BaseModel):
    loan_account_id: str
    prepayment_type: PrepaymentType
    prepayment_amount: Decimal = Field(..., gt=0)
    outstanding_principal_before: Decimal
    outstanding_interest_before: Decimal


class LoanPrepaymentCreate(LoanPrepaymentBase):
    prepayment_date: date
    prepayment_charge_percentage: Optional[Decimal] = None
    remarks: Optional[str] = None
    created_by_user_id: Optional[str] = None


class LoanPrepaymentResponse(LoanPrepaymentBase):
    id: str
    prepayment_date: date
    prepayment_charges: Decimal
    waived_charges: Decimal
    principal_reduced: Decimal
    interest_recalculated: bool
    tenure_reduced_months: int
    emi_recalculated: bool
    new_emi_amount: Optional[Decimal]
    prepayment_status: str
    approved_by_user_id: Optional[str]
    noc_issued: bool
    noc_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Statement Schemas
# ============================================================================

class LoanStatementBase(BaseModel):
    loan_account_id: str
    statement_period_start: date
    statement_period_end: date
    statement_type: StatementType


class LoanStatementCreate(LoanStatementBase):
    statement_date: date
    opening_principal: Decimal
    opening_interest: Decimal
    closing_principal: Decimal
    closing_interest: Decimal
    total_outstanding: Decimal
    created_by_user_id: Optional[str] = None


class LoanStatementResponse(LoanStatementCreate):
    id: str
    disbursements_amount: Decimal
    repayments_amount: Decimal
    interest_charged: Decimal
    charges_applied: Decimal
    adjustments_amount: Decimal
    next_emi_due_date: Optional[date]
    next_emi_amount: Optional[Decimal]
    statement_generated: bool
    statement_file_path: Optional[str]
    sent_to_customer: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Auto Debit Mandate Schemas
# ============================================================================

class AutoDebitMandateBase(BaseModel):
    loan_account_id: str
    customer_account_number: str
    customer_ifsc_code: str
    customer_account_holder_name: str
    mandate_type: MandateType
    mandate_frequency: str
    start_date: date


class AutoDebitMandateCreate(AutoDebitMandateBase):
    bank_name: Optional[str] = None
    mandate_amount: Optional[Decimal] = None
    end_date: Optional[date] = None
    created_by_user_id: Optional[str] = None


class AutoDebitMandateUpdate(BaseModel):
    mandate_status: Optional[MandateStatus] = None
    cancellation_reason: Optional[str] = None


class AutoDebitMandateResponse(AutoDebitMandateBase):
    id: str
    mandate_reference: str
    bank_name: Optional[str]
    mandate_amount: Optional[Decimal]
    end_date: Optional[date]
    mandate_status: MandateStatus
    activation_date: Optional[date]
    last_debit_date: Optional[date]
    last_debit_amount: Optional[Decimal]
    total_successful_debits: int
    total_failed_debits: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Penalty Schemas
# ============================================================================

class LoanPenaltyBase(BaseModel):
    loan_account_id: str
    penalty_type: PenaltyType
    penalty_amount: Decimal = Field(..., ge=0)


class LoanPenaltyCreate(LoanPenaltyBase):
    penalty_date: date
    emi_schedule_id: Optional[str] = None
    base_amount: Optional[Decimal] = None
    penalty_rate: Optional[Decimal] = None
    remarks: Optional[str] = None
    created_by_user_id: Optional[str] = None


class LoanPenaltyWaiver(BaseModel):
    waived_amount: Decimal
    waived_by_user_id: str
    waiver_reason: str
    approved_by_user_id: Optional[str] = None


class LoanPenaltyResponse(LoanPenaltyBase):
    id: str
    penalty_date: date
    emi_schedule_id: Optional[str]
    base_amount: Optional[Decimal]
    penalty_rate: Optional[Decimal]
    penalty_status: str
    waived_amount: Decimal
    paid_amount: Decimal
    payment_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Renewal Schemas
# ============================================================================

class LoanRenewalBase(BaseModel):
    original_loan_account_id: str
    renewal_type: RenewalType
    original_principal_outstanding: Decimal
    original_interest_outstanding: Decimal
    original_maturity_date: date


class LoanRenewalCreate(LoanRenewalBase):
    renewal_date: date
    extended_tenure_months: Optional[int] = None
    new_maturity_date: Optional[date] = None
    additional_amount: Optional[Decimal] = Field(default=Decimal(0))
    interest_settled_amount: Optional[Decimal] = Field(default=Decimal(0))
    remarks: Optional[str] = None
    created_by_user_id: Optional[str] = None


class LoanRenewalResponse(LoanRenewalBase):
    id: str
    renewal_date: date
    new_loan_account_id: Optional[str]
    extended_tenure_months: Optional[int]
    new_maturity_date: Optional[date]
    additional_amount: Decimal
    interest_settled_amount: Decimal
    renewal_charges: Decimal
    waived_renewal_charges: Decimal
    renewal_status: str
    approved_by_user_id: Optional[str]
    renewal_agreement_signed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Allocation Rule Schemas
# ============================================================================

class RepaymentAllocationRuleBase(BaseModel):
    rule_name: str
    allocation_priority_1: AllocationPriority


class RepaymentAllocationRuleCreate(RepaymentAllocationRuleBase):
    rule_description: Optional[str] = None
    allocation_priority_2: Optional[AllocationPriority] = None
    allocation_priority_3: Optional[AllocationPriority] = None
    allocation_priority_4: Optional[AllocationPriority] = None
    allocation_priority_5: Optional[AllocationPriority] = None
    is_default: bool = False
    product_type: Optional[str] = None
    created_by_user_id: Optional[str] = None


class RepaymentAllocationRuleResponse(RepaymentAllocationRuleCreate):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Summary and Statistics Schemas
# ============================================================================

class EMISummary(BaseModel):
    total_emis: int
    paid_emis: int
    pending_emis: int
    overdue_emis: int
    total_emi_amount: Decimal
    total_paid: Decimal
    total_pending: Decimal
    total_overdue: Decimal


class RepaymentSummary(BaseModel):
    total_transactions: int
    total_amount_collected: Decimal
    total_principal_collected: Decimal
    total_interest_collected: Decimal
    total_penalty_collected: Decimal
    average_transaction_amount: Decimal


class LoanAccountSummary(BaseModel):
    loan_account_number: str
    outstanding_principal: Decimal
    outstanding_interest: Decimal
    total_outstanding: Decimal
    days_past_due: int
    next_emi_due_date: Optional[date]
    next_emi_amount: Optional[Decimal]
    total_payments_made: int
    last_payment_date: Optional[date]
    last_payment_amount: Optional[Decimal]


class OverdueEMISummary(BaseModel):
    loan_account_id: str
    loan_account_number: str
    customer_id: str
    overdue_count: int
    total_overdue_amount: Decimal
    max_days_overdue: int
    total_overdue_charges: Decimal
    earliest_overdue_date: date


class PortfolioHealthMetrics(BaseModel):
    branch_id: str
    product_id: str
    total_loans: int
    total_principal_disbursed: Decimal
    total_principal_outstanding: Decimal
    total_interest_outstanding: Decimal
    npa_count: int
    npa_amount: Decimal
    active_count: int
    closed_count: int
    avg_outstanding_principal: Decimal


# ============================================================================
# Bulk Operations Schemas
# ============================================================================

class BulkEMIGeneration(BaseModel):
    loan_account_ids: List[str]
    generation_date: date


class BulkInterestAccrual(BaseModel):
    loan_account_ids: List[str]
    accrual_date: date


class BulkStatementGeneration(BaseModel):
    loan_account_ids: List[str]
    statement_type: StatementType
    period_start: date
    period_end: date
