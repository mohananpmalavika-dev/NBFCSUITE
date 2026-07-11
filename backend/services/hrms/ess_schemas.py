"""
HRMS Employee Self-Service (ESS) Schemas
Request/Response models for ESS features
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class LeaveTypeEnum(str, Enum):
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    COMPENSATORY_OFF = "compensatory_off"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    BEREAVEMENT = "bereavement"
    MARRIAGE = "marriage"
    UNPAID = "unpaid"
    SABBATICAL = "sabbatical"
    WORK_FROM_HOME = "work_from_home"


class LeaveStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"


class InvestmentSectionEnum(str, Enum):
    SECTION_80C = "80C"
    SECTION_80D = "80D"
    SECTION_80E = "80E"
    SECTION_80G = "80G"
    SECTION_24 = "24"
    SECTION_80CCD = "80CCD"
    HRA = "HRA"
    LTA = "LTA"
    OTHER = "OTHER"


class InvestmentStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    APPROVED = "approved"


class ReimbursementTypeEnum(str, Enum):
    TRAVEL = "travel"
    MEDICAL = "medical"
    TELEPHONE = "telephone"
    INTERNET = "internet"
    FUEL = "fuel"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    TRAINING = "training"
    UNIFORM = "uniform"
    RELOCATION = "relocation"
    OTHER = "other"


class ReimbursementStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"
    PAID = "paid"


# ============================================================================
# PAYSLIP SCHEMAS
# ============================================================================

class PayslipComponentSchema(BaseModel):
    """Payslip component detail"""
    component_name: str
    component_type: str  # earning, deduction, employer_contribution
    amount: Decimal
    
    class Config:
        from_attributes = True


class PayslipDownloadRequest(BaseModel):
    """Request for payslip download"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)


class PayslipResponse(BaseModel):
    """Payslip response"""
    id: str
    payslip_number: str
    employee_code: str
    employee_name: str
    department_name: Optional[str] = None
    designation_name: Optional[str] = None
    month: int
    year: int
    days_in_month: int
    days_worked: int
    basic_salary: Decimal
    gross_earnings: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    earnings: List[PayslipComponentSchema] = []
    deductions: List[PayslipComponentSchema] = []
    employer_contributions: List[PayslipComponentSchema] = []
    generated_date: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# LEAVE MANAGEMENT SCHEMAS
# ============================================================================

class LeaveBalanceResponse(BaseModel):
    """Leave balance response"""
    leave_type: LeaveTypeEnum
    financial_year: str
    opening_balance: Decimal
    accrued: Decimal
    used: Decimal
    current_balance: Decimal
    
    class Config:
        from_attributes = True


class LeaveApplicationCreate(BaseModel):
    """Create leave application"""
    leave_type: LeaveTypeEnum
    from_date: date
    to_date: date
    is_half_day: bool = False
    half_day_session: Optional[str] = None  # first_half, second_half
    reason: str = Field(..., min_length=10, max_length=500)
    contact_number_during_leave: Optional[str] = None
    contact_address_during_leave: Optional[str] = None
    
    @validator('to_date')
    def validate_dates(cls, v, values):
        if 'from_date' in values and v < values['from_date']:
            raise ValueError('to_date must be greater than or equal to from_date')
        return v


class LeaveApplicationUpdate(BaseModel):
    """Update leave application"""
    reason: Optional[str] = None
    contact_number_during_leave: Optional[str] = None
    contact_address_during_leave: Optional[str] = None


class LeaveApplicationResponse(BaseModel):
    """Leave application response"""
    id: str
    application_code: str
    employee_code: str
    employee_name: str
    leave_type: LeaveTypeEnum
    from_date: date
    to_date: date
    number_of_days: Decimal
    is_half_day: bool
    reason: str
    status: LeaveStatusEnum
    submitted_date: Optional[datetime] = None
    approver1_name: Optional[str] = None
    approver1_status: Optional[str] = None
    approved_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeaveApplicationListItem(BaseModel):
    """Simplified leave application for lists"""
    id: str
    application_code: str
    leave_type: LeaveTypeEnum
    from_date: date
    to_date: date
    number_of_days: Decimal
    status: LeaveStatusEnum
    submitted_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# INVESTMENT DECLARATION SCHEMAS
# ============================================================================

class InvestmentDeclarationItemCreate(BaseModel):
    """Create investment declaration item"""
    section: InvestmentSectionEnum
    investment_type: str
    description: Optional[str] = None
    declared_amount: Decimal = Field(..., gt=0)
    policy_number: Optional[str] = None
    proof_document_name: Optional[str] = None
    proof_document_url: Optional[str] = None


class InvestmentDeclarationItemResponse(BaseModel):
    """Investment declaration item response"""
    id: str
    section: InvestmentSectionEnum
    investment_type: str
    description: Optional[str] = None
    declared_amount: Decimal
    approved_amount: Optional[Decimal] = None
    policy_number: Optional[str] = None
    proof_document_url: Optional[str] = None
    is_verified: bool
    verification_remarks: Optional[str] = None
    
    class Config:
        from_attributes = True


class InvestmentDeclarationCreate(BaseModel):
    """Create investment declaration"""
    financial_year: str
    tax_regime: str = "old"  # old, new
    items: List[InvestmentDeclarationItemCreate] = []


class InvestmentDeclarationUpdate(BaseModel):
    """Update investment declaration"""
    tax_regime: Optional[str] = None
    items: Optional[List[InvestmentDeclarationItemCreate]] = None


class InvestmentDeclarationResponse(BaseModel):
    """Investment declaration response"""
    id: str
    declaration_code: str
    employee_code: str
    employee_name: str
    financial_year: str
    tax_regime: str
    status: InvestmentStatusEnum
    total_declared_amount: Decimal
    total_approved_amount: Decimal
    submitted_date: Optional[datetime] = None
    verified_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    is_locked: bool
    items: List[InvestmentDeclarationItemResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvestmentDeclarationListItem(BaseModel):
    """Simplified investment declaration for lists"""
    id: str
    declaration_code: str
    financial_year: str
    status: InvestmentStatusEnum
    total_declared_amount: Decimal
    submitted_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# REIMBURSEMENT CLAIM SCHEMAS
# ============================================================================

class ReimbursementClaimCreate(BaseModel):
    """Create reimbursement claim"""
    claim_title: str = Field(..., min_length=5, max_length=200)
    reimbursement_type: ReimbursementTypeEnum
    claim_description: str = Field(..., min_length=10, max_length=1000)
    expense_date: date
    claim_amount: Decimal = Field(..., gt=0)
    bill_number: Optional[str] = None
    vendor_name: Optional[str] = None
    attachment_urls: Optional[List[str]] = None


class ReimbursementClaimUpdate(BaseModel):
    """Update reimbursement claim"""
    claim_title: Optional[str] = None
    claim_description: Optional[str] = None
    claim_amount: Optional[Decimal] = None
    bill_number: Optional[str] = None
    vendor_name: Optional[str] = None


class ReimbursementClaimResponse(BaseModel):
    """Reimbursement claim response"""
    id: str
    claim_code: str
    claim_title: str
    employee_code: str
    employee_name: str
    reimbursement_type: ReimbursementTypeEnum
    claim_description: str
    expense_date: date
    claim_amount: Decimal
    approved_amount: Optional[Decimal] = None
    bill_number: Optional[str] = None
    vendor_name: Optional[str] = None
    status: ReimbursementStatusEnum
    submitted_date: Optional[datetime] = None
    approver_name: Optional[str] = None
    approved_date: Optional[datetime] = None
    is_paid: bool
    payment_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReimbursementClaimListItem(BaseModel):
    """Simplified reimbursement claim for lists"""
    id: str
    claim_code: str
    claim_title: str
    reimbursement_type: ReimbursementTypeEnum
    claim_amount: Decimal
    expense_date: date
    status: ReimbursementStatusEnum
    submitted_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# PROFILE UPDATE SCHEMAS
# ============================================================================

class EmployeeProfileUpdateRequest(BaseModel):
    """Employee profile update request (limited fields)"""
    # Contact Information
    personal_email: Optional[str] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    
    # Current Address
    current_address_line1: Optional[str] = None
    current_address_line2: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None
    
    # Banking
    salary_bank_name: Optional[str] = None
    salary_account_number: Optional[str] = None
    salary_ifsc_code: Optional[str] = None


class EmployeeProfileResponse(BaseModel):
    """Employee profile response"""
    id: str
    employee_code: str
    full_name: str
    official_email: Optional[str] = None
    personal_email: Optional[str] = None
    mobile: str
    alternate_mobile: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    marital_status: Optional[str] = None
    department_name: Optional[str] = None
    designation_name: Optional[str] = None
    reporting_manager_name: Optional[str] = None
    date_of_joining: date
    current_address_line1: Optional[str] = None
    current_address_line2: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None
    salary_bank_name: Optional[str] = None
    salary_account_number: Optional[str] = None
    salary_ifsc_code: Optional[str] = None
    photo_url: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class ESSDashboardStats(BaseModel):
    """Employee Self-Service Dashboard Statistics"""
    # Leave Summary
    total_leave_balance: Decimal = Decimal("0")
    pending_leave_applications: int = 0
    approved_leaves_this_month: int = 0
    
    # Investment Declaration
    has_active_declaration: bool = False
    declaration_status: Optional[str] = None
    total_declared_amount: Decimal = Decimal("0")
    
    # Reimbursement
    pending_reimbursement_claims: int = 0
    approved_claims_pending_payment: int = 0
    total_pending_amount: Decimal = Decimal("0")
    
    # Profile
    profile_completion_percentage: int = 0
    profile_update_required: bool = False


# ============================================================================
# PAGINATION
# ============================================================================

class PaginatedLeaveApplicationResponse(BaseModel):
    """Paginated leave application response"""
    items: List[LeaveApplicationListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedInvestmentDeclarationResponse(BaseModel):
    """Paginated investment declaration response"""
    items: List[InvestmentDeclarationListItem]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedReimbursementClaimResponse(BaseModel):
    """Paginated reimbursement claim response"""
    items: List[ReimbursementClaimListItem]
    total: int
    page: int
    page_size: int
    pages: int
