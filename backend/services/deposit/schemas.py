"""
Deposit Management Pydantic Schemas

Comprehensive schemas for all deposit operations including:
- Product management
- Account operations
- Transaction handling
- Interest calculations
- Maturity processing
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ==================== ENUMS ====================

class DepositType(str, Enum):
    """Deposit account types"""
    SAVINGS = "savings"
    FIXED_DEPOSIT = "fd"
    RECURRING_DEPOSIT = "rd"
    MONTHLY_INCOME_SCHEME = "mis"


class InterestCalculationMethod(str, Enum):
    """Interest calculation methods"""
    SIMPLE = "simple"
    COMPOUND = "compound"


class InterestCalculationFrequency(str, Enum):
    """Interest calculation frequencies"""
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


class InterestPayoutFrequency(str, Enum):
    """Interest payout frequencies"""
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    MATURITY = "maturity"
    ON_DEMAND = "on_demand"


class AccountStatus(str, Enum):
    """Account status values"""
    ACTIVE = "active"
    MATURED = "matured"
    CLOSED = "closed"
    PREMATURE_CLOSED = "premature_closed"
    DORMANT = "dormant"


class TransactionType(str, Enum):
    """Transaction types"""
    OPENING = "opening"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    INTEREST_CREDIT = "interest_credit"
    INTEREST_TDS = "interest_tds"
    PENALTY = "penalty"
    CHARGE = "charge"
    INSTALLMENT = "installment"
    CLOSURE = "closure"


class PaymentMode(str, Enum):
    """Payment modes"""
    CASH = "cash"
    CHEQUE = "cheque"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    INTERNAL_TRANSFER = "internal_transfer"


# ==================== DEPOSIT PRODUCT SCHEMAS ====================

class DepositProductBase(BaseModel):
    """Base schema for deposit product"""
    product_code: str = Field(..., min_length=2, max_length=50)
    product_name: str = Field(..., min_length=3, max_length=200)
    product_type: DepositType
    description: Optional[str] = None
    
    # Interest Configuration
    interest_rate: Decimal = Field(..., ge=0, le=100)
    interest_calculation_method: InterestCalculationMethod
    interest_calculation_frequency: InterestCalculationFrequency
    interest_payout_frequency: Optional[InterestPayoutFrequency] = None
    
    # Tenure Configuration
    min_tenure_days: Optional[int] = Field(None, ge=1)
    max_tenure_days: Optional[int] = Field(None, ge=1)
    tenure_unit: Optional[str] = Field(None, pattern="^(days|months|years)$")
    
    # Amount Configuration
    min_deposit_amount: Decimal = Field(..., gt=0)
    max_deposit_amount: Optional[Decimal] = Field(None, gt=0)
    
    # Savings Specific
    min_balance: Optional[Decimal] = Field(None, ge=0)
    min_balance_penalty: Optional[Decimal] = Field(None, ge=0)
    
    # RD Specific
    installment_amount: Optional[Decimal] = Field(None, gt=0)
    installment_frequency: Optional[str] = Field(None, pattern="^(monthly|quarterly)$")
    missed_installment_penalty: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Withdrawal Rules
    premature_withdrawal_allowed: bool = False
    premature_withdrawal_penalty: Optional[Decimal] = Field(None, ge=0, le=100)
    max_withdrawals_per_month: Optional[int] = Field(None, ge=1)
    withdrawal_charge: Optional[Decimal] = Field(None, ge=0)
    
    # Renewal
    auto_renewal_allowed: bool = False
    
    # Tax
    tds_applicable: bool = True
    tds_rate: Decimal = Field(10.0, ge=0, le=100)
    tds_threshold: Decimal = Field(40000.0, ge=0)
    
    # Status
    is_active: bool = True


class DepositProductCreate(DepositProductBase):
    """Schema for creating deposit product"""
    pass


class DepositProductUpdate(BaseModel):
    """Schema for updating deposit product"""
    product_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    interest_calculation_method: Optional[InterestCalculationMethod] = None
    interest_calculation_frequency: Optional[InterestCalculationFrequency] = None
    interest_payout_frequency: Optional[InterestPayoutFrequency] = None
    min_deposit_amount: Optional[Decimal] = Field(None, gt=0)
    max_deposit_amount: Optional[Decimal] = Field(None, gt=0)
    premature_withdrawal_allowed: Optional[bool] = None
    premature_withdrawal_penalty: Optional[Decimal] = Field(None, ge=0, le=100)
    auto_renewal_allowed: Optional[bool] = None
    is_active: Optional[bool] = None


class DepositProductResponse(DepositProductBase):
    """Schema for deposit product response"""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ==================== CALCULATION SCHEMAS ====================

class MaturityCalculationRequest(BaseModel):
    """Request for maturity calculation"""
    product_id: int
    principal_amount: Decimal = Field(..., gt=0)
    tenure_days: Optional[int] = Field(None, ge=1)
    installment_amount: Optional[Decimal] = Field(None, gt=0)
    total_installments: Optional[int] = Field(None, ge=1)


class MaturityCalculationResponse(BaseModel):
    """Response for maturity calculation"""
    principal: float
    interest: float
    maturity_amount: float
    rate: float
    product_code: str
    product_name: str
    calculation_method: Optional[str] = None
    total_days: Optional[int] = None
    total_installments: Optional[int] = None


class EligibilityCheckRequest(BaseModel):
    """Request for eligibility check"""
    product_id: int
    amount: Decimal = Field(..., gt=0)
    tenure_days: Optional[int] = Field(None, ge=1)


class EligibilityCheckResponse(BaseModel):
    """Response for eligibility check"""
    eligible: bool
    errors: List[str]
    product_code: str
    product_name: str


class PrematureClosureRequest(BaseModel):
    """Request for premature closure calculation"""
    product_id: int
    principal_amount: Decimal = Field(..., gt=0)
    days_held: int = Field(..., ge=1)
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)


class PrematureClosureResponse(BaseModel):
    """Response for premature closure calculation"""
    principal: float
    days_held: int
    original_rate: float
    reduced_rate: float
    penalty_percent: float
    penalty_amount: float
    interest_earned: float
    closure_amount: float
    product_code: str


# ==================== DEPOSIT ACCOUNT SCHEMAS ====================

class NomineeDetails(BaseModel):
    """Nominee details"""
    nominee_name: str = Field(..., min_length=2, max_length=200)
    nominee_relationship: str = Field(..., min_length=2, max_length=100)
    nominee_dob: date
    nominee_percentage: Decimal = Field(100.0, ge=0, le=100)
    nominee_address: Optional[str] = None
    nominee_id_proof: Optional[str] = None


class DepositAccountCreate(BaseModel):
    """Schema for creating deposit account"""
    customer_id: int = Field(..., gt=0)
    deposit_product_id: int = Field(..., gt=0)
    principal_amount: Decimal = Field(..., gt=0)
    tenure_days: Optional[int] = Field(None, ge=1)
    opening_date: Optional[date] = None
    
    # RD Specific
    installment_amount: Optional[Decimal] = Field(None, gt=0)
    total_installments: Optional[int] = Field(None, ge=1)
    next_installment_date: Optional[date] = None
    
    # Renewal
    auto_renewal: bool = False
    
    # Nomination
    nominee_name: Optional[str] = Field(None, max_length=200)
    nominee_relationship: Optional[str] = Field(None, max_length=100)
    nominee_dob: Optional[date] = None
    nominee_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    nominee_address: Optional[str] = None
    nominee_id_proof: Optional[str] = None
    
    # Payment Details
    payment_mode: Optional[PaymentMode] = PaymentMode.CASH
    reference_number: Optional[str] = Field(None, max_length=100)
    
    # Linked Account
    linked_account_number: Optional[str] = Field(None, max_length=50)


class DepositAccountUpdate(BaseModel):
    """Schema for updating deposit account"""
    auto_renewal: Optional[bool] = None
    nominee_name: Optional[str] = Field(None, max_length=200)
    nominee_relationship: Optional[str] = Field(None, max_length=100)
    nominee_dob: Optional[date] = None
    nominee_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    nominee_address: Optional[str] = None
    nominee_id_proof: Optional[str] = None
    linked_account_number: Optional[str] = Field(None, max_length=50)


class DepositAccountResponse(BaseModel):
    """Schema for deposit account response"""
    id: int
    tenant_id: int
    account_number: str
    customer_id: int
    deposit_product_id: int
    account_type: str
    principal_amount: float
    current_balance: float
    interest_earned: float
    total_deposits: float
    total_withdrawals: float
    interest_rate: float
    opening_date: date
    maturity_date: Optional[date]
    maturity_amount: Optional[float]
    tenure_days: Optional[int]
    status: str
    auto_renewal: bool
    installment_amount: Optional[float]
    installments_paid: Optional[int]
    total_installments: Optional[int]
    next_installment_date: Optional[date]
    nominee_name: Optional[str]
    nominee_relationship: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountSummaryResponse(BaseModel):
    """Comprehensive account summary"""
    account: Dict[str, Any]
    balances: Dict[str, float]
    transactions: Dict[str, Any]
    product: Dict[str, Any]


# ==================== TRANSACTION SCHEMAS ====================

class DepositRequest(BaseModel):
    """Request for making deposit"""
    account_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    payment_mode: PaymentMode = PaymentMode.CASH
    reference_number: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None


class WithdrawalRequest(BaseModel):
    """Request for making withdrawal"""
    account_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    payment_mode: PaymentMode = PaymentMode.CASH
    reference_number: Optional[str] = Field(None, max_length=100)
    remarks: Optional[str] = None


class RDInstallmentRequest(BaseModel):
    """Request for RD installment payment"""
    account_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    payment_mode: PaymentMode = PaymentMode.CASH
    reference_number: Optional[str] = Field(None, max_length=100)


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    transaction_number: str
    transaction_type: str
    amount: float
    balance_before: float
    balance_after: float
    transaction_date: date
    payment_mode: Optional[str]
    reference_number: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """List of transactions"""
    transactions: List[TransactionResponse]
    total_count: int
    skip: int
    limit: int


# ==================== ACCOUNT CLOSURE SCHEMAS ====================

class PrematureClosureRequest(BaseModel):
    """Request for premature account closure"""
    account_id: int = Field(..., gt=0)
    closure_reason: Optional[str] = Field(None, max_length=200)


class ClosureResponse(BaseModel):
    """Response for account closure"""
    account_number: str
    status: str
    closure_amount: float
    closure_date: date
    days_held: Optional[int] = None
    penalty_amount: Optional[float] = None


# ==================== INTEREST CALCULATION SCHEMAS ====================

class InterestCalculationRequest(BaseModel):
    """Request for interest calculation"""
    account_id: int = Field(..., gt=0)
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class InterestCalculationResponse(BaseModel):
    """Response for interest calculation"""
    interest: float
    days: int
    rate: float
    method: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    tds_details: Dict[str, Any]
    net_interest: float
    average_balance: Optional[float] = None


class InterestPostRequest(BaseModel):
    """Request for posting interest"""
    account_id: int = Field(..., gt=0)
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class InterestPostResponse(BaseModel):
    """Response for posting interest"""
    account_number: str
    interest_posted: float
    tds_deducted: float
    net_interest: float
    period_start: date
    period_end: date
    new_balance: float
    calculation_id: int


class BatchInterestRequest(BaseModel):
    """Request for batch interest calculation"""
    account_type: Optional[DepositType] = None
    product_id: Optional[int] = Field(None, gt=0)


class BatchInterestResponse(BaseModel):
    """Response for batch interest calculation"""
    total_accounts: int
    successful: int
    failed: int
    total_interest: float
    total_tds: float
    errors: List[Dict[str, str]]


class InterestCertificateRequest(BaseModel):
    """Request for interest certificate"""
    account_id: int = Field(..., gt=0)
    financial_year: Optional[str] = Field(None, pattern="^\\d{4}-\\d{4}$")


class InterestCertificateResponse(BaseModel):
    """Interest certificate response"""
    account: Dict[str, Any]
    financial_year: str
    period: Dict[str, str]
    summary: Dict[str, float]
    calculations: List[Dict[str, Any]]
    certificate_date: date


class InterestHistoryItem(BaseModel):
    """Interest history item"""
    id: int
    period_start: date
    period_end: date
    days: int
    interest_rate: float
    interest_amount: float
    tds_amount: float
    net_interest: float
    posted_date: Optional[date]
    calculation_method: str


class InterestHistoryResponse(BaseModel):
    """Interest history response"""
    history: List[InterestHistoryItem]
    total_count: int


# ==================== PASSBOOK & STATEMENT SCHEMAS ====================

class PassbookEntryResponse(BaseModel):
    """Passbook entry response"""
    entry_date: date
    particulars: str
    withdrawal_amount: float
    deposit_amount: float
    balance: float


class PassbookResponse(BaseModel):
    """Passbook response"""
    account_number: str
    account_type: str
    customer_name: str
    entries: List[PassbookEntryResponse]
    from_date: date
    to_date: date


class StatementRequest(BaseModel):
    """Request for account statement"""
    account_id: int = Field(..., gt=0)
    from_date: date
    to_date: date


class StatementResponse(BaseModel):
    """Account statement response"""
    account: Dict[str, Any]
    period: Dict[str, str]
    opening_balance: float
    closing_balance: float
    total_deposits: float
    total_withdrawals: float
    total_interest: float
    transactions: List[TransactionResponse]


# ==================== MATURITY QUEUE SCHEMAS ====================

class MaturityQueueItem(BaseModel):
    """Maturity queue item"""
    id: int
    account_number: str
    account_type: str
    customer_id: int
    maturity_date: date
    maturity_amount: float
    principal_amount: float
    interest_amount: float
    status: str
    auto_renewal: bool


class MaturityQueueResponse(BaseModel):
    """Maturity queue response"""
    items: List[MaturityQueueItem]
    total_count: int


class ProcessMaturityRequest(BaseModel):
    """Request to process maturity"""
    maturity_queue_id: int = Field(..., gt=0)
    payout_mode: PaymentMode = PaymentMode.CASH
    payout_account: Optional[str] = Field(None, max_length=50)


# ==================== PRODUCT STATISTICS SCHEMAS ====================

class ProductStatistics(BaseModel):
    """Product statistics"""
    product: Dict[str, Any]
    statistics: Dict[str, Any]
    status_breakdown: Dict[str, int]


# ==================== SEARCH & FILTER SCHEMAS ====================

class DepositAccountFilter(BaseModel):
    """Filter for deposit accounts"""
    customer_id: Optional[int] = Field(None, gt=0)
    account_type: Optional[DepositType] = None
    status: Optional[AccountStatus] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class DepositProductFilter(BaseModel):
    """Filter for deposit products"""
    product_type: Optional[DepositType] = None
    is_active: Optional[bool] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class TransactionFilter(BaseModel):
    """Filter for transactions"""
    account_id: int = Field(..., gt=0)
    transaction_type: Optional[TransactionType] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


# ==================== COMMON RESPONSE SCHEMAS ====================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total: int
    skip: int
    limit: int
    has_more: bool


# ==================== VALIDATORS ====================

@validator('to_date')
def validate_date_range(cls, v, values):
    """Validate date range"""
    if 'from_date' in values and values['from_date'] and v:
        if v <= values['from_date']:
            raise ValueError('to_date must be after from_date')
    return v


# ==================== NEW SCHEMAS FOR ADVANCED FEATURES ====================

# Notification Schemas
class NotificationRequest(BaseModel):
    """Request to send custom notification"""
    account_ids: List[int] = Field(..., min_items=1)
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    channels: List[str] = Field(['email', 'sms'], min_items=1)


class NotificationResponse(BaseModel):
    """Notification response"""
    notification_type: str
    accounts_notified: int
    notifications: List[Dict[str, Any]]


# Standing Instruction Schemas
class StandingInstructionCreate(BaseModel):
    """Create standing instruction"""
    account_id: int = Field(..., gt=0)
    instruction_type: str = Field(..., pattern="^(auto_debit|sweep_in|sweep_out)$")
    debit_account_number: Optional[str] = Field(None, max_length=50)
    debit_amount: Optional[Decimal] = Field(None, gt=0)
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|quarterly)$")
    start_date: date
    end_date: Optional[date] = None
    threshold_amount: Optional[Decimal] = Field(None, ge=0)
    sweep_to_account: Optional[str] = Field(None, max_length=50)


class StandingInstructionResponse(BaseModel):
    """Standing instruction response"""
    instruction_id: int
    account_number: str
    instruction_type: str
    status: str
    debit_amount: Optional[float]
    frequency: Optional[str]
    threshold_amount: Optional[float]
    next_execution: Optional[date]


# Account Freeze Schemas
class AccountFreezeRequest(BaseModel):
    """Request to freeze account"""
    account_id: int = Field(..., gt=0)
    freeze_type: str = Field(..., pattern="^(debit|credit|full)$")
    reason: str = Field(..., min_length=5, max_length=500)


class AccountFreezeResponse(BaseModel):
    """Account freeze response"""
    freeze_id: int
    account_number: str
    freeze_type: str
    freeze_date: date
    reason: str
    status: str


class AccountUnfreezeRequest(BaseModel):
    """Request to unfreeze account"""
    freeze_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=5, max_length=500)


# Account Lien Schemas
class AccountLienRequest(BaseModel):
    """Request to mark lien"""
    account_id: int = Field(..., gt=0)
    lien_amount: Decimal = Field(..., gt=0)
    reason: str = Field(..., min_length=5, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)


class AccountLienResponse(BaseModel):
    """Account lien response"""
    lien_id: int
    account_number: str
    lien_amount: float
    total_lien: float
    current_balance: float
    available_balance: float
    marked_date: date


class LienReleaseRequest(BaseModel):
    """Request to release lien"""
    lien_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=5, max_length=500)


# Account Transfer Schemas
class AccountTransferRequest(BaseModel):
    """Request to transfer account"""
    account_id: int = Field(..., gt=0)
    new_customer_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=5, max_length=500)
    transfer_date: Optional[date] = None


class AccountTransferResponse(BaseModel):
    """Account transfer response"""
    account_number: str
    old_customer_id: int
    new_customer_id: int
    transfer_date: date
    reason: str
    status: str


# Joint Account Schemas
class JointHolderRequest(BaseModel):
    """Request to add joint holder"""
    account_id: int = Field(..., gt=0)
    customer_id: int = Field(..., gt=0)
    holder_type: str = Field(..., pattern="^(primary|joint|either_or_survivor)$")
    operation_mode: str = Field("joint", pattern="^(single|joint|either_or)$")


class JointHolderResponse(BaseModel):
    """Joint holder response"""
    holder_id: int
    account_number: str
    customer_id: int
    holder_type: str
    operation_mode: str
    added_date: date


# Batch Operation Schemas
class BatchMaturityRequest(BaseModel):
    """Request for batch maturity processing"""
    maturity_date: Optional[date] = None
    days_ahead: int = Field(0, ge=0, le=30)


class BatchTDSRequest(BaseModel):
    """Request for batch TDS calculation"""
    financial_year: str = Field(..., pattern="^\\d{4}-\\d{4}$")
    quarter: int = Field(..., ge=1, le=4)


class BatchDormancyRequest(BaseModel):
    """Request for dormancy check"""
    inactive_months: int = Field(24, ge=12, le=60)


class BatchPenaltyRequest(BaseModel):
    """Request for penalty application"""
    penalty_type: str = Field(..., pattern="^(rd_missed|min_balance|late_payment)$")


class BatchOperationResponse(BaseModel):
    """Batch operation response"""
    total_count: int
    processed: int
    success_count: int
    failed_count: int
    errors: List[Dict[str, str]]


# Report Schemas
class DashboardResponse(BaseModel):
    """Dashboard response"""
    summary: Dict[str, Any]
    by_type: List[Dict[str, Any]]
    maturity_alerts: Dict[str, int]
    today_transactions: Dict[str, Any]
    as_of_date: date


class DepositSummaryRequest(BaseModel):
    """Request for deposit summary"""
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    account_type: Optional[str] = None


class MaturityCalendarRequest(BaseModel):
    """Request for maturity calendar"""
    from_date: date
    to_date: date


class MaturityCalendarResponse(BaseModel):
    """Maturity calendar response"""
    period: Dict[str, str]
    total_accounts: int
    total_maturity_amount: float
    accounts: List[Dict[str, Any]]


class InterestAccrualRequest(BaseModel):
    """Request for interest accrual report"""
    from_date: date
    to_date: date
    account_type: Optional[str] = None


class InterestAccrualResponse(BaseModel):
    """Interest accrual response"""
    period: Dict[str, str]
    summary: Dict[str, float]
    by_type: List[Dict[str, Any]]


class AgingAnalysisResponse(BaseModel):
    """Aging analysis response"""
    as_of_date: date
    buckets: Dict[str, Dict[str, Any]]


class ProductPerformanceRequest(BaseModel):
    """Request for product performance"""
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class ProductPerformanceResponse(BaseModel):
    """Product performance response"""
    period: Dict[str, str]
    products: List[Dict[str, Any]]


class DormancyReportResponse(BaseModel):
    """Dormancy report response"""
    dormant_accounts: Dict[str, Any]
    near_dormant_accounts: Dict[str, Any]


class TDSSummaryRequest(BaseModel):
    """Request for TDS summary"""
    financial_year: str = Field(..., pattern="^\\d{4}-\\d{4}$")
    quarter: Optional[int] = Field(None, ge=1, le=4)


class TDSSummaryResponse(BaseModel):
    """TDS summary response"""
    financial_year: str
    quarter: Optional[int]
    period: Dict[str, str]
    total_interest: float
    total_tds: float
    calculation_count: int


class TransactionVolumeRequest(BaseModel):
    """Request for transaction volume report"""
    from_date: date
    to_date: date
    group_by: str = Field("day", pattern="^(day|week|month)$")


class TransactionVolumeResponse(BaseModel):
    """Transaction volume response"""
    period: Dict[str, str]
    group_by: str
    data: List[Dict[str, Any]]


# Regulatory Compliance Schemas
class RBIReturnRequest(BaseModel):
    """Request for RBI return"""
    return_date: date
    return_type: str = Field("quarterly", pattern="^(monthly|quarterly|annual)$")


class RBIReturnResponse(BaseModel):
    """RBI return response"""
    return_type: str
    return_date: date
    reporting_entity: Dict[str, str]
    summary: Dict[str, Any]
    by_deposit_type: List[Dict[str, Any]]
    maturity_profile: Dict[str, float]
    rate_wise_classification: List[Dict[str, Any]]
    top_depositors: List[Dict[str, Any]]


class DICGCReportRequest(BaseModel):
    """Request for DICGC report"""
    reporting_date: date


class DICGCReportResponse(BaseModel):
    """DICGC report response"""
    reporting_date: date
    insurance_limit: float
    summary: Dict[str, Any]
    depositor_classification: Dict[str, int]


class ConcentrationReportRequest(BaseModel):
    """Request for concentration report"""
    as_of_date: Optional[date] = None


class ConcentrationReportResponse(BaseModel):
    """Concentration report response"""
    as_of_date: date
    total_deposits: float
    concentration_metrics: Dict[str, Any]
    risk_assessment: Dict[str, str]


class KYCComplianceResponse(BaseModel):
    """KYC compliance response"""
    as_of_date: date
    summary: Dict[str, Any]
    pending_kyc: List[Dict[str, Any]]


class ComplianceDashboardResponse(BaseModel):
    """Compliance dashboard response"""
    as_of_date: date
    overall_metrics: Dict[str, Any]
    risk_indicators: Dict[str, Any]
    compliance_areas: Dict[str, Any]


# Scheduled Job Schemas
class ScheduledJobResponse(BaseModel):
    """Scheduled job response"""
    job_date: date
    tenant_id: int
    jobs: List[Dict[str, Any]]


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    message: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
