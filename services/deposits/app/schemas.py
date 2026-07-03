"""
Deposit Operating System - Pydantic Schemas
Request/Response models for all deposit operations
"""

from pydantic import BaseModel, Field, validator, constr, condecimal
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ==================== ENUMS ====================

class DepositTypeEnum(str, Enum):
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    RECURRING_DEPOSIT = "RECURRING_DEPOSIT"
    CASA = "CASA"
    FLEXI_DEPOSIT = "FLEXI_DEPOSIT"


class InterestMethodEnum(str, Enum):
    SIMPLE = "SIMPLE"
    COMPOUND_MONTHLY = "COMPOUND_MONTHLY"
    COMPOUND_QUARTERLY = "COMPOUND_QUARTERLY"
    COMPOUND_HALF_YEARLY = "COMPOUND_HALF_YEARLY"
    COMPOUND_YEARLY = "COMPOUND_YEARLY"


class PayoutFrequencyEnum(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    YEARLY = "YEARLY"
    ON_MATURITY = "ON_MATURITY"
    CUMULATIVE = "CUMULATIVE"


class DepositAccountStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    MATURED = "MATURED"
    PREMATURELY_CLOSED = "PREMATURELY_CLOSED"
    RENEWED = "RENEWED"
    CLOSED = "CLOSED"
    SUSPENDED = "SUSPENDED"


# ==================== PRODUCT SCHEMAS ====================

class InterestSlabCreate(BaseModel):
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    min_tenure_days: Optional[int] = None
    max_tenure_days: Optional[int] = None
    interest_rate: Decimal = Field(..., description="Annual interest rate percentage")
    senior_citizen_rate: Optional[Decimal] = None
    special_rate_applicable: bool = False
    special_rate_conditions: Optional[Dict[str, Any]] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class InterestSlabResponse(InterestSlabCreate):
    id: str
    product_id: str

    class Config:
        from_attributes = True


class DepositProductCreate(BaseModel):
    code: constr(max_length=50)
    name: constr(max_length=200)
    deposit_type: DepositTypeEnum
    min_amount: Decimal
    max_amount: Optional[Decimal] = None
    min_tenure_days: Optional[int] = None
    max_tenure_days: Optional[int] = None
    interest_method: InterestMethodEnum
    default_interest_rate: Optional[Decimal] = None
    senior_citizen_rate_bonus: Decimal = Field(default=0.5, description="Additional rate for senior citizens")
    payout_frequency: PayoutFrequencyEnum
    premature_allowed: bool = True
    premature_penalty_percentage: Decimal = Field(default=1.0)
    auto_renewal_allowed: bool = True
    loan_against_deposit_allowed: bool = True
    nomination_mandatory: bool = False
    tds_applicable: bool = True
    tds_rate: Decimal = Field(default=10.0)
    business_rules: Optional[Dict[str, Any]] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    @validator('code')
    def validate_code(cls, v):
        if not v.isupper():
            raise ValueError('Product code must be uppercase')
        return v


class DepositProductUpdate(BaseModel):
    name: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    default_interest_rate: Optional[Decimal] = None
    status: Optional[str] = None
    business_rules: Optional[Dict[str, Any]] = None


class DepositProductResponse(BaseModel):
    id: str
    code: str
    name: str
    deposit_type: DepositTypeEnum
    min_amount: Decimal
    max_amount: Optional[Decimal]
    min_tenure_days: Optional[int]
    max_tenure_days: Optional[int]
    interest_method: InterestMethodEnum
    default_interest_rate: Optional[Decimal]
    senior_citizen_rate_bonus: Decimal
    payout_frequency: PayoutFrequencyEnum
    premature_allowed: bool
    auto_renewal_allowed: bool
    status: str
    created_at: datetime
    interest_slabs: Optional[List[InterestSlabResponse]] = []

    class Config:
        from_attributes = True


# ==================== NOMINEE SCHEMAS ====================

class NomineeCreate(BaseModel):
    name: constr(max_length=200)
    relationship: constr(max_length=50)
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    phone: Optional[constr(max_length=20)] = None
    email: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    allocation_percentage: Decimal = Field(default=100.00, le=100, ge=0)
    is_minor: bool = False
    guardian_name: Optional[str] = None
    guardian_relationship: Optional[str] = None
    nominee_order: int = 1


class NomineeResponse(NomineeCreate):
    id: str
    account_id: str
    age: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== DEPOSIT ACCOUNT SCHEMAS ====================

class DepositAccountCreate(BaseModel):
    customer_id: str
    cif_number: constr(max_length=50)
    product_id: str
    principal_amount: Decimal = Field(..., gt=0, description="Deposit amount")
    tenure_days: Optional[int] = Field(None, description="Tenure in days")
    is_senior_citizen: bool = False
    open_date: date = Field(default_factory=date.today)
    interest_payout_account: Optional[str] = None
    auto_renewal: bool = False
    branch_code: Optional[str] = None
    nominees: Optional[List[NomineeCreate]] = []
    metadata: Optional[Dict[str, Any]] = None

    @validator('nominees')
    def validate_nominee_allocation(cls, v):
        if v:
            total = sum(n.allocation_percentage for n in v)
            if total != 100:
                raise ValueError('Total nominee allocation must be 100%')
        return v


class DepositAccountUpdate(BaseModel):
    interest_payout_account: Optional[str] = None
    auto_renewal: Optional[bool] = None
    maturity_instruction: Optional[str] = None
    status: Optional[DepositAccountStatusEnum] = None


class DepositAccountResponse(BaseModel):
    id: str
    account_number: str
    customer_id: str
    cif_number: str
    product_id: str
    deposit_type: DepositTypeEnum
    principal_amount: Decimal
    interest_rate: Decimal
    is_senior_citizen: bool
    open_date: date
    maturity_date: date
    maturity_amount: Optional[Decimal]
    status: DepositAccountStatusEnum
    total_interest_earned: Decimal
    total_interest_paid: Decimal
    total_tds_deducted: Decimal
    branch_code: Optional[str]
    created_at: datetime
    nominees: Optional[List[NomineeResponse]] = []

    class Config:
        from_attributes = True


class DepositAccountDetail(DepositAccountResponse):
    product: Optional[DepositProductResponse] = None
    interest_postings: Optional[List] = []
    transactions: Optional[List] = []

    class Config:
        from_attributes = True


# ==================== INTEREST CALCULATION SCHEMAS ====================

class InterestCalculationRequest(BaseModel):
    principal: Decimal = Field(..., gt=0)
    rate: Decimal = Field(..., gt=0, le=100)
    days: int = Field(..., gt=0)
    method: InterestMethodEnum = InterestMethodEnum.SIMPLE
    compounding_frequency: Optional[int] = None  # Times per year


class InterestCalculationResponse(BaseModel):
    principal: Decimal
    rate: Decimal
    days: int
    years: Decimal
    method: InterestMethodEnum
    interest: Decimal
    maturity_amount: Decimal
    calculation_details: Dict[str, Any]


class InterestPostingResponse(BaseModel):
    id: str
    account_id: str
    from_date: date
    to_date: date
    days: int
    principal_amount: Decimal
    interest_rate: Decimal
    interest_amount: Decimal
    tds_amount: Decimal
    net_interest: Decimal
    is_paid: bool
    posting_date: Optional[date]

    class Config:
        from_attributes = True


# ==================== RD SCHEMAS ====================

class RDAccountCreate(BaseModel):
    customer_id: str
    cif_number: str
    product_id: str
    installment_amount: Decimal = Field(..., gt=0)
    num_installments: int = Field(..., gt=0, description="Number of monthly installments")
    is_senior_citizen: bool = False
    open_date: date = Field(default_factory=date.today)
    auto_debit: bool = False
    debit_account: Optional[str] = None
    branch_code: Optional[str] = None
    nominees: Optional[List[NomineeCreate]] = []


class RDScheduleResponse(BaseModel):
    id: str
    account_id: str
    installment_number: int
    installment_amount: Decimal
    due_date: date
    status: str
    paid_amount: Decimal
    paid_date: Optional[date]
    penalty_amount: Decimal
    overdue_days: int

    class Config:
        from_attributes = True


class RDInstallmentPayment(BaseModel):
    schedule_id: str
    amount: Decimal = Field(..., gt=0)
    payment_date: date = Field(default_factory=date.today)
    payment_mode: str
    payment_reference: Optional[str] = None


# ==================== MATURITY SCHEMAS ====================

class MaturityCalculation(BaseModel):
    account_id: str
    principal: Decimal
    interest_rate: Decimal
    tenure_days: int
    interest_method: InterestMethodEnum
    payout_frequency: PayoutFrequencyEnum
    total_interest: Decimal
    maturity_amount: Decimal
    maturity_date: date


class MaturityAction(BaseModel):
    account_id: str
    action: str = Field(..., description="RENEW, PAYOUT, PARTIAL_RENEW")
    renewal_amount: Optional[Decimal] = None
    renewal_tenure_days: Optional[int] = None
    payout_account: Optional[str] = None


class MaturityPipelineResponse(BaseModel):
    account_id: str
    customer_id: str
    account_number: str
    customer_name: str
    maturity_date: date
    maturity_amount: Decimal
    days_to_maturity: int
    customer_instruction: Optional[str]
    ai_recommended_action: Optional[str]
    renewal_probability: Optional[Decimal]
    status: str

    class Config:
        from_attributes = True


# ==================== PREMATURE CLOSURE SCHEMAS ====================

class PrematureClosureRequest(BaseModel):
    account_id: str
    closure_reason: str
    requested_closure_date: date = Field(default_factory=date.today)


class PrematureClosureCalculation(BaseModel):
    account_id: str
    principal_amount: Decimal
    days_completed: int
    original_rate: Decimal
    applicable_rate: Decimal
    interest_earned: Decimal
    penalty_percentage: Decimal
    penalty_amount: Decimal
    tds_amount: Decimal
    net_payout: Decimal
    effective_yield: Decimal


class PrematureClosureApproval(BaseModel):
    closure_id: str
    approved: bool
    rejection_reason: Optional[str] = None
    payment_mode: Optional[str] = None
    payment_account: Optional[str] = None


# ==================== RENEWAL SCHEMAS ====================

class RenewalRequest(BaseModel):
    account_id: str
    renewal_type: str = Field(..., description="AUTO, MANUAL, PARTIAL")
    renewed_principal: Decimal
    interest_payout: Decimal
    new_tenure_days: int
    new_product_id: Optional[str] = None


class RenewalResponse(BaseModel):
    old_account_id: str
    new_account_id: str
    renewal_date: date
    maturity_amount: Decimal
    renewed_principal: Decimal
    interest_paid_out: Decimal
    new_interest_rate: Decimal
    new_maturity_date: date

    class Config:
        from_attributes = True


# ==================== CERTIFICATE SCHEMAS ====================

class CertificateGenerateRequest(BaseModel):
    account_id: str
    certificate_type: str = Field(..., description="FD_CERTIFICATE, INTEREST_STATEMENT, TDS_CERTIFICATE")
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    financial_year: Optional[str] = None


class CertificateResponse(BaseModel):
    id: str
    account_id: str
    certificate_type: str
    certificate_number: str
    document_id: Optional[str]
    document_url: Optional[str]
    generated_date: datetime
    status: str

    class Config:
        from_attributes = True


# ==================== AI INTELLIGENCE SCHEMAS ====================

class AIDepositPrediction(BaseModel):
    customer_id: str
    account_id: Optional[str] = None
    analysis_type: str = Field(..., description="RENEWAL_PREDICTION, CHURN_RISK, PRODUCT_RECOMMENDATION")


class AIInsightResponse(BaseModel):
    customer_id: str
    analysis_type: str
    prediction: str
    confidence_score: Decimal
    probability: Optional[Decimal]
    insights: Dict[str, Any]
    behavioral_patterns: Optional[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class DepositCopilotQuery(BaseModel):
    question: str = Field(..., description="Natural language question about deposits")
    context: Optional[Dict[str, Any]] = None


class DepositCopilotResponse(BaseModel):
    question: str
    answer: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = []
    confidence: Decimal


# ==================== DASHBOARD SCHEMAS ====================

class DepositDashboard(BaseModel):
    total_deposits: Decimal
    total_accounts: int
    active_accounts: int
    total_interest_liability: Decimal
    avg_interest_rate: Decimal
    deposits_today: Decimal
    maturities_next_30_days: int
    maturity_amount_next_30_days: Decimal
    renewals_this_month: int
    premature_closures_this_month: int


class TreasuryDepositView(BaseModel):
    total_deposit_base: Decimal
    cost_of_funds: Decimal
    liquidity_position: Decimal
    maturity_pipeline_7_days: Decimal
    maturity_pipeline_30_days: Decimal
    maturity_pipeline_90_days: Decimal
    branch_wise_deposits: Dict[str, Decimal]
    product_wise_deposits: Dict[str, Decimal]


class CustomerDepositPortfolio(BaseModel):
    customer_id: str
    cif_number: str
    customer_name: str
    total_deposits: Decimal
    num_accounts: int
    accounts: List[DepositAccountResponse]
    total_interest_earned: Decimal
    relationship_score: Optional[Decimal]
    ai_insights: Optional[AIInsightResponse]


# ==================== TRANSACTION SCHEMAS ====================

class DepositTransactionCreate(BaseModel):
    account_id: str
    transaction_type: str
    transaction_date: date = Field(default_factory=date.today)
    debit_amount: Decimal = Field(default=0)
    credit_amount: Decimal = Field(default=0)
    payment_mode: Optional[str] = None
    reference_number: Optional[str] = None
    narration: Optional[str] = None


class DepositTransactionResponse(BaseModel):
    id: str
    account_id: str
    transaction_type: str
    transaction_date: date
    debit_amount: Decimal
    credit_amount: Decimal
    balance: Decimal
    reference_number: Optional[str]
    narration: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== SEARCH & FILTER SCHEMAS ====================

class DepositAccountSearch(BaseModel):
    customer_id: Optional[str] = None
    cif_number: Optional[str] = None
    account_number: Optional[str] = None
    product_id: Optional[str] = None
    status: Optional[DepositAccountStatusEnum] = None
    branch_code: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    maturity_from: Optional[date] = None
    maturity_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, le=100)


# ==================== RATE ENGINE SCHEMAS ====================

class RateCalculationRequest(BaseModel):
    product_id: str
    amount: Decimal
    tenure_days: int
    is_senior_citizen: bool = False
    special_conditions: Optional[Dict[str, Any]] = None


class RateCalculationResponse(BaseModel):
    product_id: str
    amount: Decimal
    tenure_days: int
    base_rate: Decimal
    senior_citizen_bonus: Optional[Decimal] = None
    special_rate_adjustment: Optional[Decimal] = None
    applicable_rate: Decimal
    slab_details: Optional[Dict[str, Any]] = None
