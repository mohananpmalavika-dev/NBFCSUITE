"""
HRMS Loan & Advances Schemas
Request/Response models for loan operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class LoanTypeEnum(str, Enum):
    PERSONAL = "personal"
    VEHICLE = "vehicle"
    HOME = "home"
    EDUCATION = "education"
    MEDICAL = "medical"
    MARRIAGE = "marriage"
    SALARY_ADVANCE = "salary_advance"
    EMERGENCY = "emergency"
    FESTIVAL_ADVANCE = "festival_advance"
    OTHER = "other"


class LoanStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class RepaymentFrequencyEnum(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"
    BULLET = "bullet"


class EMIStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"
    WAIVED = "waived"


# ============================================================================
# LOAN ELIGIBILITY
# ============================================================================

class LoanEligibilityRequest(BaseModel):
    """Request to check loan eligibility"""
    loan_type: LoanTypeEnum
    requested_amount: Decimal = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0, le=360)


class LoanEligibilityResponse(BaseModel):
    """Loan eligibility check response"""
    is_eligible: bool
    eligible_amount: Decimal
    max_loan_amount: Decimal
    max_emi_amount: Decimal
    suggested_tenure_months: int
    interest_rate: Decimal
    reasons: List[str] = []
    policy_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# EMI CALCULATION
# ============================================================================

class EMICalculationRequest(BaseModel):
    """Request for EMI calculation"""
    principal_amount: Decimal = Field(..., gt=0)
    interest_rate: Decimal = Field(..., ge=0, le=100)
    tenure_months: int = Field(..., gt=0, le=360)
    repayment_frequency: RepaymentFrequencyEnum = RepaymentFrequencyEnum.MONTHLY


class EMICalculationResponse(BaseModel):
    """EMI calculation response"""
    emi_amount: Decimal
    total_interest: Decimal
    total_repayment_amount: Decimal
    monthly_emi: Decimal
    effective_rate: Decimal
    
    class Config:
        from_attributes = True


class EMIScheduleItem(BaseModel):
    """Single EMI schedule item"""
    emi_number: int
    emi_due_date: date
    emi_amount: Decimal
    principal_component: Decimal
    interest_component: Decimal
    opening_balance: Decimal
    closing_balance: Decimal
    status: EMIStatusEnum
    payment_date: Optional[date] = None
    amount_paid: Decimal = Decimal("0.00")
    is_overdue: bool = False
    days_overdue: int = 0
    
    class Config:
        from_attributes = True


class EMIScheduleResponse(BaseModel):
    """Complete EMI schedule"""
    loan_id: str
    loan_code: str
    total_emis: int
    schedule: List[EMIScheduleItem] = []
    total_principal: Decimal
    total_interest: Decimal
    total_amount: Decimal
    paid_emis: int
    pending_emis: int
    overdue_emis: int
    
    class Config:
        from_attributes = True


# ============================================================================
# LOAN APPLICATION
# ============================================================================

class LoanApplicationCreate(BaseModel):
    """Create loan application"""
    loan_type: LoanTypeEnum
    loan_amount: Decimal = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0, le=360)
    purpose: str = Field(..., min_length=10, max_length=500)
    reason_for_loan: Optional[str] = Field(None, max_length=1000)
    repayment_frequency: RepaymentFrequencyEnum = RepaymentFrequencyEnum.MONTHLY
    
    # Bank details for disbursement
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    
    # Guarantor (optional)
    guarantor_employee_id: Optional[str] = None
    guarantor_name: Optional[str] = None
    guarantor_relation: Optional[str] = None
    guarantor_contact: Optional[str] = None
    
    # Documents
    attachment_urls: Optional[List[str]] = []
    
    @validator('tenure_months')
    def validate_tenure(cls, v):
        if v <= 0:
            raise ValueError('Tenure must be greater than 0')
        if v > 360:
            raise ValueError('Maximum tenure is 360 months')
        return v


class LoanApplicationUpdate(BaseModel):
    """Update loan application (draft only)"""
    loan_amount: Optional[Decimal] = None
    tenure_months: Optional[int] = None
    purpose: Optional[str] = None
    reason_for_loan: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc_code: Optional[str] = None
    guarantor_name: Optional[str] = None
    guarantor_contact: Optional[str] = None


class LoanApprovalAction(BaseModel):
    """Approve or reject loan"""
    action: str = Field(..., pattern="^(approve|reject)$")
    comments: Optional[str] = Field(None, max_length=1000)
    approved_amount: Optional[Decimal] = None  # Can approve lesser amount
    approved_tenure: Optional[int] = None  # Can modify tenure


class LoanDisbursementRequest(BaseModel):
    """Disburse approved loan"""
    disbursement_date: date
    disbursement_mode: str = Field(..., pattern="^(bank_transfer|cheque|cash)$")
    disbursement_reference: Optional[str] = None
    disbursed_amount: Optional[Decimal] = None  # If different from approved
    repayment_start_date: date
    
    @validator('repayment_start_date')
    def validate_repayment_date(cls, v, values):
        if 'disbursement_date' in values and v < values['disbursement_date']:
            raise ValueError('Repayment start date cannot be before disbursement date')
        return v


class LoanResponse(BaseModel):
    """Loan application response"""
    id: str
    loan_code: str
    employee_id: str
    employee_code: str
    employee_name: str
    loan_type: LoanTypeEnum
    loan_amount: Decimal
    interest_rate: Decimal
    tenure_months: int
    emi_amount: Decimal
    total_interest: Decimal
    total_repayment_amount: Decimal
    processing_fee: Decimal
    
    application_date: date
    purpose: str
    status: LoanStatusEnum
    
    # Disbursement
    disbursement_date: Optional[date] = None
    disbursed_amount: Optional[Decimal] = None
    
    # Repayment
    repayment_start_date: Optional[date] = None
    first_emi_date: Optional[date] = None
    last_emi_date: Optional[date] = None
    
    # Outstanding
    principal_outstanding: Decimal
    interest_outstanding: Decimal
    total_outstanding: Decimal
    
    # Paid
    principal_paid: Decimal
    interest_paid: Decimal
    total_paid: Decimal
    
    # Approval status
    manager_approval_status: Optional[str] = None
    hr_approval_status: Optional[str] = None
    finance_approval_status: Optional[str] = None
    
    approved_date: Optional[datetime] = None
    rejected_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Flags
    is_deducting_from_salary: bool
    is_overdue: bool
    days_overdue: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoanListItem(BaseModel):
    """Simplified loan for lists"""
    id: str
    loan_code: str
    employee_code: str
    employee_name: str
    loan_type: LoanTypeEnum
    loan_amount: Decimal
    emi_amount: Decimal
    total_outstanding: Decimal
    status: LoanStatusEnum
    application_date: date
    disbursement_date: Optional[date] = None
    is_overdue: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# LOAN TRANSACTIONS
# ============================================================================

class LoanTransactionCreate(BaseModel):
    """Create loan transaction (prepayment, adjustment)"""
    transaction_type: str = Field(..., pattern="^(prepayment|adjustment|waiver)$")
    transaction_amount: Decimal = Field(..., gt=0)
    transaction_date: date
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    remarks: Optional[str] = None


class LoanTransactionResponse(BaseModel):
    """Loan transaction response"""
    id: str
    transaction_code: str
    loan_id: str
    loan_code: str
    transaction_type: str
    transaction_date: date
    transaction_amount: Decimal
    principal_amount: Decimal
    interest_amount: Decimal
    penalty_amount: Decimal
    principal_outstanding: Decimal
    interest_outstanding: Decimal
    total_outstanding: Decimal
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# LOAN CLOSURE
# ============================================================================

class LoanClosureRequest(BaseModel):
    """Close loan (foreclosure)"""
    closure_date: date
    closure_reason: str = Field(..., pattern="^(fully_paid|foreclosed|written_off)$")
    settlement_amount: Optional[Decimal] = None
    waiver_amount: Optional[Decimal] = None
    closure_remarks: Optional[str] = None


# ============================================================================
# LOAN POLICY
# ============================================================================

class LoanPolicyResponse(BaseModel):
    """Loan policy response"""
    id: str
    policy_code: str
    policy_name: str
    loan_type: LoanTypeEnum
    min_service_months: int
    min_loan_amount: Decimal
    max_loan_amount: Decimal
    max_loan_as_salary_multiple: Optional[Decimal] = None
    max_emi_as_salary_percentage: Decimal
    interest_rate: Decimal
    min_tenure_months: int
    max_tenure_months: int
    repayment_frequency: RepaymentFrequencyEnum
    processing_fee_percentage: Decimal
    prepayment_allowed: bool
    max_active_loans_per_employee: int
    is_active: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD & REPORTS
# ============================================================================

class LoanDashboardStats(BaseModel):
    """Loan dashboard statistics"""
    total_active_loans: int
    total_disbursed_amount: Decimal
    total_outstanding_amount: Decimal
    total_collected_amount: Decimal
    pending_approvals: int
    overdue_loans: int
    total_overdue_amount: Decimal
    loans_this_month: int
    disbursements_this_month: Decimal
    collections_this_month: Decimal


class EmployeeLoanSummary(BaseModel):
    """Employee's loan summary"""
    total_loans: int
    active_loans: int
    closed_loans: int
    total_borrowed: Decimal
    total_outstanding: Decimal
    total_paid: Decimal
    current_monthly_emi: Decimal
    next_emi_date: Optional[date] = None
    next_emi_amount: Decimal = Decimal("0.00")
    overdue_emis: int
    overdue_amount: Decimal = Decimal("0.00")


# ============================================================================
# APPROVAL WORKFLOW
# ============================================================================

class LoanApprovalListItem(BaseModel):
    """Loan pending approval"""
    id: str
    loan_code: str
    employee_code: str
    employee_name: str
    department: Optional[str] = None
    loan_type: LoanTypeEnum
    loan_amount: Decimal
    tenure_months: int
    emi_amount: Decimal
    purpose: str
    application_date: date
    current_approval_stage: str  # manager, hr, finance
    submitted_date: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# LOAN STATEMENT
# ============================================================================

class LoanStatementRequest(BaseModel):
    """Request loan statement"""
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class LoanStatementResponse(BaseModel):
    """Loan statement"""
    loan_id: str
    loan_code: str
    employee_name: str
    loan_type: LoanTypeEnum
    loan_amount: Decimal
    disbursement_date: date
    
    # Summary
    total_emi_paid: int
    total_amount_paid: Decimal
    principal_paid: Decimal
    interest_paid: Decimal
    principal_outstanding: Decimal
    interest_outstanding: Decimal
    total_outstanding: Decimal
    
    # Transactions
    transactions: List[LoanTransactionResponse] = []
    
    # EMI Schedule
    emi_schedule: List[EMIScheduleItem] = []
    
    class Config:
        from_attributes = True
