"""
Loan Management Schemas
Pydantic models for loan products, applications, accounts
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ProductType(str, Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    GOLD = "gold"
    VEHICLE = "vehicle"
    HOME = "home"
    EDUCATION = "education"
    AGRICULTURE = "agriculture"


class LoanCategory(str, Enum):
    SECURED = "secured"
    UNSECURED = "unsecured"


class InterestRateType(str, Enum):
    FLAT = "flat"
    REDUCING = "reducing"
    COMPOUND = "compound"


class ProcessingFeeType(str, Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    CREDIT_ASSESSMENT = "credit_assessment"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"


class DisbursementMode(str, Enum):
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    CHEQUE = "cheque"
    UPI = "upi"


class LoanAccountStatus(str, Enum):
    ACTIVE = "active"
    OVERDUE = "overdue"
    NPA = "npa"
    CLOSED = "closed"
    SETTLED = "settled"
    WRITTEN_OFF = "written_off"


class EMIStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    WAIVED = "waived"
    CANCELLED = "cancelled"


class RiskRating(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DisbursementMode(str, Enum):
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    CHEQUE = "cheque"
    CASH = "cash"


# ============================================================================
# LOAN PRODUCT SCHEMAS
# ============================================================================

class LoanProductBase(BaseModel):
    product_name: str = Field(..., max_length=200)
    product_type: ProductType
    loan_category: LoanCategory
    
    # Interest Configuration
    interest_rate_type: InterestRateType
    min_interest_rate: Decimal = Field(..., ge=0, le=100)
    max_interest_rate: Decimal = Field(..., ge=0, le=100)
    default_interest_rate: Decimal = Field(..., ge=0, le=100)
    
    # Loan Amount
    min_loan_amount: Decimal = Field(..., gt=0)
    max_loan_amount: Decimal = Field(..., gt=0)
    
    # Tenure
    min_tenure_months: int = Field(..., ge=1, le=360)
    max_tenure_months: int = Field(..., ge=1, le=360)
    allowed_tenures: Optional[List[int]] = None
    
    # Fees & Charges
    processing_fee_type: ProcessingFeeType
    processing_fee_value: Decimal = Field(..., ge=0)
    documentation_charges: Optional[Decimal] = Field(None, ge=0)
    insurance_applicable: bool = False
    insurance_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Penal Interest
    penal_interest_rate: Decimal = Field(..., ge=0, le=100)
    grace_period_days: int = Field(default=3, ge=0, le=30)
    
    # Eligibility
    min_age: int = Field(default=21, ge=18, le=100)
    max_age: int = Field(default=65, ge=18, le=100)
    min_monthly_income: Optional[Decimal] = Field(None, ge=0)
    min_cibil_score: int = Field(default=650, ge=300, le=900)
    employment_types: Optional[List[str]] = None
    
    # Documentation
    required_documents: Optional[List[int]] = None
    
    # Description
    description: Optional[str] = None
    features: Optional[List[str]] = None
    terms_and_conditions: Optional[str] = None
    
    # Display
    is_active: bool = True
    is_featured: bool = False
    display_order: int = 0
    
    @validator('max_interest_rate')
    def validate_interest_rates(cls, v, values):
        if 'min_interest_rate' in values and v < values['min_interest_rate']:
            raise ValueError('max_interest_rate must be >= min_interest_rate')
        return v
    
    @validator('max_loan_amount')
    def validate_loan_amounts(cls, v, values):
        if 'min_loan_amount' in values and v < values['min_loan_amount']:
            raise ValueError('max_loan_amount must be >= min_loan_amount')
        return v
    
    @validator('max_tenure_months')
    def validate_tenures(cls, v, values):
        if 'min_tenure_months' in values and v < values['min_tenure_months']:
            raise ValueError('max_tenure_months must be >= min_tenure_months')
        return v
    
    @validator('max_age')
    def validate_ages(cls, v, values):
        if 'min_age' in values and v < values['min_age']:
            raise ValueError('max_age must be >= min_age')
        return v


class LoanProductCreate(LoanProductBase):
    product_code: str = Field(..., max_length=50)


class LoanProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, max_length=200)
    default_interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    processing_fee_value: Optional[Decimal] = Field(None, ge=0)
    documentation_charges: Optional[Decimal] = Field(None, ge=0)
    penal_interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    min_cibil_score: Optional[int] = Field(None, ge=300, le=900)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    terms_and_conditions: Optional[str] = None


class LoanProductResponse(LoanProductBase):
    id: int
    product_code: str
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class LoanProductListResponse(BaseModel):
    items: List[LoanProductResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# LOAN APPLICATION SCHEMAS
# ============================================================================

class CoApplicantBase(BaseModel):
    family_member_id: int
    co_applicant_type: str = Field(..., pattern="^(co_applicant|guarantor)$")
    is_primary: bool = False
    monthly_income: Optional[Decimal] = Field(None, ge=0)
    occupation: Optional[str] = Field(None, max_length=200)
    consent_given: bool = False
    consent_date: Optional[date] = None


class CoApplicantCreate(CoApplicantBase):
    pass


class CoApplicantResponse(CoApplicantBase):
    id: int
    relationship: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationDocumentBase(BaseModel):
    document_type_id: int
    customer_document_id: Optional[int] = None
    document_number: Optional[str] = Field(None, max_length=100)
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    remarks: Optional[str] = None


class ApplicationDocumentCreate(ApplicationDocumentBase):
    pass


class ApplicationDocumentResponse(ApplicationDocumentBase):
    id: int
    status: str
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoanApplicationBase(BaseModel):
    customer_id: int
    loan_product_id: int
    requested_amount: Decimal = Field(..., gt=0)
    tenure_months: int = Field(..., ge=1, le=360)
    
    # Purpose
    loan_purpose_id: Optional[int] = None
    purpose_description: Optional[str] = None
    
    # Disbursement
    disbursement_bank_account_id: Optional[int] = None
    disbursement_mode: Optional[DisbursementMode] = None
    
    # Notes
    applicant_remarks: Optional[str] = None


class LoanApplicationCreate(LoanApplicationBase):
    co_applicants: Optional[List[CoApplicantCreate]] = None
    documents: Optional[List[ApplicationDocumentCreate]] = None


class LoanApplicationUpdate(BaseModel):
    requested_amount: Optional[Decimal] = Field(None, gt=0)
    tenure_months: Optional[int] = Field(None, ge=1, le=360)
    loan_purpose_id: Optional[int] = None
    purpose_description: Optional[str] = None
    disbursement_bank_account_id: Optional[int] = None
    disbursement_mode: Optional[DisbursementMode] = None
    applicant_remarks: Optional[str] = None
    internal_notes: Optional[str] = None


class LoanApplicationResponse(LoanApplicationBase):
    id: int
    application_number: str
    tenant_id: int
    
    # Calculated fields
    interest_rate: Decimal
    emi_amount: Optional[Decimal] = None
    total_interest: Optional[Decimal] = None
    total_repayment: Optional[Decimal] = None
    
    # Status
    status: ApplicationStatus
    sub_status: Optional[str] = None
    status_reason: Optional[str] = None
    
    # Workflow
    current_approver_id: Optional[int] = None
    approval_level: int
    
    # Dates
    application_date: date
    submission_date: Optional[date] = None
    approval_date: Optional[date] = None
    rejection_date: Optional[date] = None
    disbursement_date: Optional[date] = None
    
    # Credit Assessment
    credit_score: Optional[int] = None
    debt_to_income_ratio: Optional[Decimal] = None
    monthly_income: Optional[Decimal] = None
    monthly_obligations: Optional[Decimal] = None
    risk_rating: Optional[RiskRating] = None
    
    # Verification
    documents_verified: bool
    kyc_verified: bool
    
    # Fees
    processing_fee: Optional[Decimal] = None
    documentation_charges: Optional[Decimal] = None
    insurance_amount: Optional[Decimal] = None
    other_charges: Optional[Decimal] = None
    total_deductions: Optional[Decimal] = None
    net_disbursement: Optional[Decimal] = None
    
    # Approved amount (if approved)
    approved_amount: Optional[Decimal] = None
    
    # Rejection
    rejection_reason: Optional[str] = None
    
    # Reference
    disbursement_reference: Optional[str] = None
    
    # Relations
    co_applicants: Optional[List[CoApplicantResponse]] = None
    documents: Optional[List[ApplicationDocumentResponse]] = None
    
    # Product details (joined)
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    
    # Customer details (joined)
    customer_name: Optional[str] = None
    customer_code: Optional[str] = None
    customer_mobile: Optional[str] = None
    customer_cibil_score: Optional[int] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class LoanApplicationListResponse(BaseModel):
    items: List[LoanApplicationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class LoanApplicationStats(BaseModel):
    total_applications: int
    draft: int
    submitted: int
    under_review: int
    pending_approval: int
    approved: int
    rejected: int
    disbursed: int
    total_requested_amount: Decimal
    total_approved_amount: Decimal
    average_loan_amount: Decimal
    average_processing_days: Optional[float] = None
    approval_rate: Optional[float] = None


# ============================================================================
# EMI CALCULATION SCHEMAS
# ============================================================================

class EMICalculationRequest(BaseModel):
    loan_amount: Decimal = Field(..., gt=0)
    interest_rate: Decimal = Field(..., ge=0, le=100)
    tenure_months: int = Field(..., ge=1, le=360)
    interest_rate_type: InterestRateType = InterestRateType.REDUCING


class EMICalculationResponse(BaseModel):
    loan_amount: Decimal
    interest_rate: Decimal
    tenure_months: int
    emi_amount: Decimal
    total_interest: Decimal
    total_repayment: Decimal
    processing_fee: Optional[Decimal] = None
    net_disbursement: Optional[Decimal] = None


class EMIScheduleRow(BaseModel):
    installment_number: int
    due_date: date
    emi_amount: Decimal
    principal_component: Decimal
    interest_component: Decimal
    opening_principal: Decimal
    closing_principal: Decimal


class EMIScheduleResponse(BaseModel):
    loan_amount: Decimal
    interest_rate: Decimal
    tenure_months: int
    emi_amount: Decimal
    total_interest: Decimal
    total_repayment: Decimal
    schedule: List[EMIScheduleRow]


# ============================================================================
# LOAN ACCOUNT SCHEMAS (for later)
# ============================================================================

class LoanAccountSummary(BaseModel):
    id: int
    loan_account_number: str
    customer_name: str
    product_name: str
    sanctioned_amount: Decimal
    outstanding_principal: Decimal
    outstanding_interest: Decimal
    total_outstanding: Decimal
    emi_amount: Decimal
    next_due_date: Optional[date] = None
    next_due_amount: Optional[Decimal] = None
    status: str
    overdue_days: int
    dpd: int
    
    class Config:
        from_attributes = True


# ============================================================================
# DISBURSEMENT SCHEMAS
# ============================================================================

class SanctionLetterResponse(BaseModel):
    """Sanction letter details"""
    sanction_number: str
    sanction_date: str
    application_number: str
    customer_name: str
    customer_id: str
    product_name: str
    sanctioned_amount: float
    tenure_months: int
    interest_rate: float
    emi_amount: float
    processing_fee: float
    documentation_charges: float
    insurance_amount: float
    total_deductions: float
    net_disbursement: float
    first_emi_date: Optional[str] = None
    last_emi_date: Optional[str] = None
    total_interest: float
    total_repayment: float
    terms_and_conditions: Optional[str] = None
    validity_days: int
    expiry_date: str


class DisbursementApprovalRequest(BaseModel):
    """Request schema for disbursement approval"""
    bank_account_id: int = Field(..., description="Customer's bank account ID for disbursement")
    disbursement_date: date = Field(..., description="Date of fund transfer")
    disbursement_mode: DisbursementMode = Field(..., description="Mode of disbursement")
    emi_start_day: int = Field(default=5, ge=1, le=28, description="Day of month for EMI deduction")
    remarks: Optional[str] = Field(None, max_length=500, description="Optional remarks")
    
    @validator('disbursement_date')
    def validate_disbursement_date(cls, v):
        if v > date.today():
            # Future disbursement allowed up to 7 days
            if (v - date.today()).days > 7:
                raise ValueError('Disbursement date cannot be more than 7 days in future')
        return v


class BankAccountInfo(BaseModel):
    """Bank account information for disbursement"""
    account_number: str
    bank_name: str
    ifsc_code: str
    account_holder_name: str


class EMIDetailsInfo(BaseModel):
    """EMI details information"""
    emi_amount: float
    first_emi_date: str
    last_emi_date: str
    emi_day: int
    total_emis: int


class DisbursementResponse(BaseModel):
    """Response after successful disbursement"""
    loan_account_number: str
    application_number: str
    customer_id: int
    disbursement_amount: float
    disbursement_date: str
    disbursement_mode: str
    disbursement_reference: str
    bank_account: BankAccountInfo
    emi_details: EMIDetailsInfo
    status: str
    message: str


class EMIScheduleItemResponse(BaseModel):
    """Single EMI schedule item"""
    installment_number: int
    due_date: str
    emi_amount: float
    principal_component: float
    interest_component: float
    opening_principal: float
    closing_principal: float
    status: str
    paid_amount: float
    paid_principal: float
    paid_interest: float
    payment_date: Optional[str] = None
    overdue_days: int
    penal_interest: float


class LoanAccountResponse(BaseModel):
    """Basic loan account response"""
    id: int
    loan_account_number: str
    customer_id: int
    sanctioned_amount: float
    disbursed_amount: float
    total_outstanding: float
    outstanding_principal: float
    outstanding_interest: float
    emi_amount: float
    tenure_months: int
    interest_rate: float
    disbursement_date: str
    next_due_date: Optional[str] = None
    status: str
    overdue_days: int
    dpd: int
    created_at: str


class LoanAccountDetailResponse(BaseModel):
    """Detailed loan account response"""
    id: int
    loan_account_number: str
    customer_id: int
    loan_product_id: int
    loan_application_id: int
    sanctioned_amount: float
    disbursed_amount: float
    outstanding_principal: float
    outstanding_interest: float
    outstanding_charges: float
    total_outstanding: float
    tenure_months: int
    interest_rate: float
    emi_amount: float
    emi_day: int
    disbursement_date: str
    first_emi_date: str
    last_emi_date: str
    maturity_date: str
    closure_date: Optional[str] = None
    status: str
    overdue_days: int
    dpd: int
    last_payment_date: Optional[str] = None
    last_payment_amount: Optional[float] = None
    next_due_date: Optional[str] = None
    next_due_amount: Optional[float] = None
    npa_status: Optional[str] = None
    npa_date: Optional[str] = None
    prepayment_allowed: bool
    prepayment_charges_percentage: Optional[float] = None
    penal_interest_outstanding: float
    interest_accrued: float
    interest_received: float
    principal_received: float
    internal_notes: Optional[str] = None
    created_at: str
    updated_at: str
    emi_schedule: Optional[List[EMIScheduleItemResponse]] = None


class LoanAccountListItem(BaseModel):
    """Loan account list item"""
    id: int
    loan_account_number: str
    customer_id: int
    sanctioned_amount: float
    disbursed_amount: float
    total_outstanding: float
    outstanding_principal: float
    outstanding_interest: float
    emi_amount: float
    tenure_months: int
    interest_rate: float
    disbursement_date: str
    next_due_date: Optional[str] = None
    status: str
    overdue_days: int
    dpd: int
    created_at: str


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    total: int
    skip: int
    limit: int
    pages: int


class LoanAccountListResponse(BaseModel):
    """Loan account list with pagination"""
    accounts: List[LoanAccountListItem]
    pagination: PaginationInfo


# ============================================================================
# REPAYMENT & COLLECTION SCHEMAS
# ============================================================================

class PaymentMode(str, Enum):
    """Payment mode options"""
    CASH = "cash"
    CHEQUE = "cheque"
    NEFT = "neft"
    RTGS = "rtgs"
    UPI = "upi"
    IMPS = "imps"


class PaymentRecordRequest(BaseModel):
    """Request schema for recording a payment"""
    account_id: Optional[int] = Field(None, description="Loan account ID")
    account_number: Optional[str] = Field(None, description="Loan account number")
    payment_amount: Decimal = Field(..., gt=0, description="Payment amount")
    payment_date: Optional[date] = Field(None, description="Payment date (default: today)")
    payment_mode: PaymentMode = Field(..., description="Mode of payment")
    reference_number: Optional[str] = Field(None, max_length=100, description="Transaction reference")
    bank_name: Optional[str] = Field(None, max_length=200, description="Bank name")
    transaction_date: Optional[date] = Field(None, description="Transaction date")
    remarks: Optional[str] = Field(None, max_length=500, description="Optional remarks")
    collected_by: Optional[int] = Field(None, description="User ID who collected payment")
    
    @root_validator
    def validate_account_identifier(cls, values):
        if not values.get('account_id') and not values.get('account_number'):
            raise ValueError('Either account_id or account_number must be provided')
        return values


class PaymentAllocation(BaseModel):
    """Payment allocation breakdown"""
    penal_interest: float
    interest: float
    principal: float
    charges: float
    total: float


class PaymentRecordResponse(BaseModel):
    """Response after recording payment"""
    payment_id: int
    receipt_number: str
    loan_account_number: str
    payment_amount: float
    payment_date: str
    payment_mode: str
    allocation: PaymentAllocation
    remaining_amount: float
    emis_updated: int
    status: str
    message: str


class PaymentHistoryItem(BaseModel):
    """Single payment history item"""
    id: int
    receipt_number: str
    payment_date: str
    payment_amount: float
    payment_mode: str
    allocated_to_principal: float
    allocated_to_interest: float
    allocated_to_penal_interest: float
    allocated_to_charges: float
    reference_number: Optional[str] = None
    bank_name: Optional[str] = None
    status: str
    receipt_generated: bool
    remarks: Optional[str] = None
    created_at: str


class PaymentHistoryResponse(BaseModel):
    """Payment history with pagination"""
    loan_account_number: str
    payments: List[PaymentHistoryItem]
    pagination: PaginationInfo


class ReceiptAllocation(BaseModel):
    """Receipt allocation details"""
    principal: float
    interest: float
    penal_interest: float
    charges: float
    total: float


class ReceiptResponse(BaseModel):
    """Payment receipt details"""
    receipt_number: str
    receipt_date: str
    loan_account_number: Optional[str] = None
    payment_date: str
    payment_amount: float
    payment_mode: str
    reference_number: Optional[str] = None
    bank_name: Optional[str] = None
    transaction_date: Optional[str] = None
    allocation: ReceiptAllocation
    status: str
    remarks: Optional[str] = None


class OverdueAccountItem(BaseModel):
    """Single overdue account item"""
    loan_account_id: int
    loan_account_number: str
    customer_id: int
    sanctioned_amount: float
    total_outstanding: float
    outstanding_principal: float
    outstanding_interest: float
    penal_interest_outstanding: float
    overdue_days: int
    dpd: int
    dpd_bucket: str
    npa_status: Optional[str] = None
    overdue_emis_count: int
    overdue_emi_amount: float
    last_payment_date: Optional[str] = None
    last_payment_amount: Optional[float] = None
    status: str
    disbursement_date: str


class OverdueAccountsResponse(BaseModel):
    """Overdue accounts list with pagination"""
    overdue_accounts: List[OverdueAccountItem]
    pagination: PaginationInfo


class CollectionQueueItem(BaseModel):
    """Single collection queue item"""
    loan_account_id: int
    loan_account_number: str
    customer_id: int
    dpd: int
    dpd_bucket: str
    npa_status: Optional[str] = None
    total_outstanding: float
    overdue_amount: float
    overdue_emis_count: int
    penal_interest: float
    last_payment_date: Optional[str] = None
    priority: str


class CollectionQueueSummary(BaseModel):
    """Collection queue summary"""
    total_accounts: int
    high_priority: int
    medium_priority: int
    low_priority: int
    total_overdue_amount: float
    total_penal_interest: float


class CollectionQueueResponse(BaseModel):
    """Collection queue with summary"""
    queue: List[CollectionQueueItem]
    summary: CollectionQueueSummary


class DPDBucketDistribution(BaseModel):
    """DPD bucket distribution"""
    current: int
    bucket_1_30: int
    bucket_31_60: int
    bucket_61_90: int
    bucket_91_180: int
    bucket_180_plus: int


class NPADistribution(BaseModel):
    """NPA classification distribution"""
    standard: int
    sub_standard: int
    doubtful: int
    loss: int


class CollectionStatisticsResponse(BaseModel):
    """Collection statistics and metrics"""
    total_accounts: int
    overdue_accounts: int
    overdue_percentage: float
    total_portfolio: float
    overdue_portfolio: float
    overdue_portfolio_percentage: float
    total_penal_interest: float
    collection_efficiency: float
    dpd_bucket_distribution: Dict[str, int]
    npa_distribution: Dict[str, int]


class PrepaymentCalculationResponse(BaseModel):
    """Prepayment calculation response"""
    loan_account_number: str
    prepayment_date: str
    outstanding_principal: float
    outstanding_interest: float
    outstanding_penal_interest: float
    outstanding_charges: float
    prepayment_charges: float
    prepayment_charges_percentage: float
    total_prepayment_amount: float
    interest_savings: float
    pending_emis_count: int
    tenure_remaining: int
    prepayment_allowed: bool
    message: str


class PartialPrepaymentRequest(BaseModel):
    """Request for partial prepayment calculation"""
    account_id: Optional[int] = Field(None, description="Loan account ID")
    account_number: Optional[str] = Field(None, description="Loan account number")
    prepayment_amount: Decimal = Field(..., gt=0, description="Amount to prepay")
    reduce_emi: bool = Field(True, description="True = reduce EMI, False = reduce tenure")
    
    @root_validator
    def validate_account_identifier(cls, values):
        if not values.get('account_id') and not values.get('account_number'):
            raise ValueError('Either account_id or account_number must be provided')
        return values


class CurrentValues(BaseModel):
    """Current loan values"""
    outstanding_principal: float
    emi_amount: float
    tenure_remaining: int


class NewValues(BaseModel):
    """New loan values after prepayment"""
    outstanding_principal: float
    emi_amount: float
    tenure_remaining: int


class PrepaymentImpact(BaseModel):
    """Impact of prepayment"""
    emi_reduction: float
    tenure_reduction_months: int
    interest_savings: float


class PartialPrepaymentResponse(BaseModel):
    """Partial prepayment calculation response"""
    loan_account_number: str
    prepayment_amount: float
    prepayment_charges: float
    net_prepayment_towards_principal: float
    current_values: CurrentValues
    new_values: NewValues
    impact: PrepaymentImpact
    option_selected: str
    recommendation: str


class ForeclosureRequest(BaseModel):
    """Request for loan foreclosure"""
    account_id: Optional[int] = Field(None, description="Loan account ID")
    account_number: Optional[str] = Field(None, description="Loan account number")
    foreclosure_amount: Decimal = Field(..., gt=0, description="Foreclosure payment amount")
    foreclosure_date: Optional[date] = Field(None, description="Date of foreclosure (default: today)")
    payment_mode: PaymentMode = Field(..., description="Mode of payment")
    reference_number: Optional[str] = Field(None, max_length=100, description="Payment reference")
    remarks: Optional[str] = Field(None, max_length=500, description="Optional remarks")
    
    @root_validator
    def validate_account_identifier(cls, values):
        if not values.get('account_id') and not values.get('account_number'):
            raise ValueError('Either account_id or account_number must be provided')
        return values


class ForeclosureResponse(BaseModel):
    """Foreclosure confirmation response"""
    loan_account_number: str
    customer_id: int
    foreclosure_date: str
    foreclosure_amount: float
    payment_mode: str
    reference_number: Optional[str] = None
    original_loan_amount: float
    disbursement_date: str
    total_emis_paid: int
    emis_cancelled: int
    interest_savings: float
    status: str
    noc_generated: bool
    message: str


class NOCResponse(BaseModel):
    """No Objection Certificate response"""
    noc_number: str
    noc_date: str
    loan_account_number: str
    customer_id: int
    loan_amount: float
    disbursement_date: str
    closure_date: Optional[str] = None
    total_amount_paid: float
    principal_paid: float
    interest_paid: float
    status: str
    outstanding_amount: float
    declaration: str
    generated_date: str
