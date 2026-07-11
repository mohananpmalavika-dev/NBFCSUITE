"""
HRMS Loan & Advances Database Models
Employee loans, advances, EMI schedule, and repayment tracking
"""
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, Text, ForeignKey, Numeric, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
from decimal import Decimal
import enum

from backend.shared.database.models import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class LoanType(str, enum.Enum):
    """Loan type"""
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


class LoanStatus(str, enum.Enum):
    """Loan application status"""
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


class RepaymentFrequency(str, enum.Enum):
    """Repayment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"
    BULLET = "bullet"  # One-time repayment


class EMIStatus(str, enum.Enum):
    """EMI payment status"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"
    WAIVED = "waived"


class TransactionType(str, enum.Enum):
    """Loan transaction type"""
    DISBURSEMENT = "disbursement"
    EMI_PAYMENT = "emi_payment"
    PREPAYMENT = "prepayment"
    FORECLOSURE = "foreclosure"
    WAIVER = "waiver"
    ADJUSTMENT = "adjustment"
    REVERSAL = "reversal"


# ============================================================================
# LOAN POLICY CONFIGURATION
# ============================================================================

class LoanPolicy(BaseModel):
    """
    Loan Policy Configuration
    Defines eligibility criteria and limits for different loan types
    """
    __tablename__ = "hrms_loan_policies"
    
    # Policy Identification
    policy_code = Column(String(50), nullable=False, index=True)
    policy_name = Column(String(200), nullable=False)
    loan_type = Column(SQLEnum(LoanType), nullable=False, index=True)
    
    # Eligibility Criteria
    min_service_months = Column(Integer, nullable=False, default=6)  # Minimum service required
    min_employment_type = Column(String(50), nullable=True)  # permanent, contract
    allowed_employment_statuses = Column(Text, nullable=True)  # JSON array: ["active"]
    allowed_designations = Column(Text, nullable=True)  # JSON array of designation IDs
    allowed_departments = Column(Text, nullable=True)  # JSON array of department IDs
    
    # Loan Limits
    min_loan_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("10000.00"))
    max_loan_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("500000.00"))
    
    # Salary-based limits
    max_loan_as_salary_multiple = Column(Numeric(5, 2), nullable=True)  # e.g., 3x of monthly salary
    max_emi_as_salary_percentage = Column(Numeric(5, 2), nullable=False, default=Decimal("40.00"))  # 40% of salary
    
    # Interest & Tenure
    interest_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))  # Annual rate
    min_tenure_months = Column(Integer, nullable=False, default=6)
    max_tenure_months = Column(Integer, nullable=False, default=60)
    
    # Repayment Configuration
    repayment_frequency = Column(SQLEnum(RepaymentFrequency), nullable=False, default=RepaymentFrequency.MONTHLY)
    processing_fee_percentage = Column(Numeric(5, 2), default=Decimal("0.00"))
    prepayment_allowed = Column(Boolean, default=True)
    prepayment_penalty_percentage = Column(Numeric(5, 2), default=Decimal("0.00"))
    
    # Restrictions
    max_active_loans_per_employee = Column(Integer, default=1)
    min_gap_between_loans_months = Column(Integer, default=0)
    
    # Approval Workflow
    requires_manager_approval = Column(Boolean, default=True)
    requires_hr_approval = Column(Boolean, default=True)
    requires_finance_approval = Column(Boolean, default=True)
    auto_approve_below_amount = Column(Numeric(15, 2), nullable=True)
    
    # Documents Required
    required_documents = Column(Text, nullable=True)  # JSON array: ["salary_slip", "id_proof"]
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    loans = relationship("EmployeeLoan", back_populates="policy", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_loan_policy_code', 'tenant_id', 'policy_code', unique=True),
        Index('idx_loan_policy_type', 'tenant_id', 'loan_type', 'is_active'),
    )
    
    def __repr__(self):
        return f"<LoanPolicy(code={self.policy_code}, type={self.loan_type})>"


# ============================================================================
# EMPLOYEE LOAN APPLICATION
# ============================================================================

class EmployeeLoan(BaseModel):
    """
    Employee Loan Application & Management
    Tracks complete lifecycle from application to closure
    """
    __tablename__ = "hrms_employee_loans"
    
    # Loan Identification
    loan_code = Column(String(50), nullable=False, index=True)
    
    # Employee & Policy
    employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="CASCADE"), nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("hrms_loan_policies.id", ondelete="RESTRICT"), nullable=False)
    loan_type = Column(SQLEnum(LoanType), nullable=False, index=True)
    
    # Loan Details
    loan_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    tenure_months = Column(Integer, nullable=False)
    repayment_frequency = Column(SQLEnum(RepaymentFrequency), nullable=False, default=RepaymentFrequency.MONTHLY)
    
    # EMI Calculation
    emi_amount = Column(Numeric(15, 2), nullable=False)
    total_interest = Column(Numeric(15, 2), default=Decimal("0.00"))
    total_repayment_amount = Column(Numeric(15, 2), nullable=False)
    processing_fee = Column(Numeric(15, 2), default=Decimal("0.00"))
    
    # Application Details
    application_date = Column(Date, nullable=False, default=date.today)
    purpose = Column(Text, nullable=False)
    reason_for_loan = Column(Text, nullable=True)
    attachment_urls = Column(Text, nullable=True)  # JSON array of document URLs
    
    # Disbursement Details
    disbursement_date = Column(Date, nullable=True)
    disbursement_mode = Column(String(20), nullable=True)  # bank_transfer, cheque, cash
    disbursement_reference = Column(String(100), nullable=True)
    disbursed_amount = Column(Numeric(15, 2), nullable=True)
    
    # Repayment Details
    repayment_start_date = Column(Date, nullable=True)
    first_emi_date = Column(Date, nullable=True)
    last_emi_date = Column(Date, nullable=True)
    
    # Outstanding Balance
    principal_outstanding = Column(Numeric(15, 2), default=Decimal("0.00"))
    interest_outstanding = Column(Numeric(15, 2), default=Decimal("0.00"))
    total_outstanding = Column(Numeric(15, 2), default=Decimal("0.00"))
    
    # Repayment Summary
    principal_paid = Column(Numeric(15, 2), default=Decimal("0.00"))
    interest_paid = Column(Numeric(15, 2), default=Decimal("0.00"))
    total_paid = Column(Numeric(15, 2), default=Decimal("0.00"))
    
    # Status & Workflow
    status = Column(SQLEnum(LoanStatus), nullable=False, default=LoanStatus.DRAFT, index=True)
    submitted_date = Column(DateTime, nullable=True)
    
    # Manager Approval
    manager_approver_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    manager_approval_status = Column(String(20), nullable=True)  # pending, approved, rejected
    manager_approval_date = Column(DateTime, nullable=True)
    manager_comments = Column(Text, nullable=True)
    
    # HR Approval
    hr_approver_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    hr_approval_status = Column(String(20), nullable=True)
    hr_approval_date = Column(DateTime, nullable=True)
    hr_comments = Column(Text, nullable=True)
    
    # Finance Approval
    finance_approver_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    finance_approval_status = Column(String(20), nullable=True)
    finance_approval_date = Column(DateTime, nullable=True)
    finance_comments = Column(Text, nullable=True)
    
    # Final Approval/Rejection
    approved_date = Column(DateTime, nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    rejected_date = Column(DateTime, nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Closure Details
    closure_date = Column(Date, nullable=True)
    closure_reason = Column(String(50), nullable=True)  # fully_paid, foreclosed, written_off
    closure_remarks = Column(Text, nullable=True)
    
    # Prepayment
    prepayment_allowed_after_months = Column(Integer, default=0)
    prepayment_penalty_percentage = Column(Numeric(5, 2), default=Decimal("0.00"))
    
    # Bank Details (for disbursement)
    bank_name = Column(String(100), nullable=True)
    bank_account_number = Column(String(30), nullable=True)
    bank_ifsc_code = Column(String(11), nullable=True)
    
    # Guarantor Information (optional)
    guarantor_employee_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employees.id", ondelete="SET NULL"), nullable=True)
    guarantor_name = Column(String(200), nullable=True)
    guarantor_relation = Column(String(50), nullable=True)
    guarantor_contact = Column(String(20), nullable=True)
    
    # Flags
    is_deducting_from_salary = Column(Boolean, default=True)
    is_overdue = Column(Boolean, default=False)
    days_overdue = Column(Integer, default=0)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="loans")
    policy = relationship("LoanPolicy", back_populates="loans")
    manager_approver = relationship("Employee", foreign_keys=[manager_approver_id])
    hr_approver = relationship("Employee", foreign_keys=[hr_approver_id])
    finance_approver = relationship("Employee", foreign_keys=[finance_approver_id])
    guarantor = relationship("Employee", foreign_keys=[guarantor_employee_id])
    
    emi_schedule = relationship("LoanEMISchedule", back_populates="loan", cascade="all, delete-orphan")
    transactions = relationship("LoanTransaction", back_populates="loan", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_loan_code', 'tenant_id', 'loan_code', unique=True),
        Index('idx_tenant_loan_emp', 'tenant_id', 'employee_id', 'status'),
        Index('idx_loan_status', 'tenant_id', 'status', 'is_deleted'),
        Index('idx_loan_type', 'tenant_id', 'loan_type', 'status'),
        Index('idx_loan_disbursement', 'tenant_id', 'disbursement_date'),
    )
    
    def __repr__(self):
        return f"<EmployeeLoan(code={self.loan_code}, employee_id={self.employee_id}, amount={self.loan_amount})>"


# ============================================================================
# EMI SCHEDULE
# ============================================================================

class LoanEMISchedule(BaseModel):
    """
    Loan EMI Schedule
    Detailed repayment schedule for each installment
    """
    __tablename__ = "hrms_loan_emi_schedule"
    
    # Loan Reference
    loan_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employee_loans.id", ondelete="CASCADE"), nullable=False)
    
    # EMI Details
    emi_number = Column(Integer, nullable=False)  # 1, 2, 3, ...
    emi_due_date = Column(Date, nullable=False, index=True)
    
    # Amount Breakdown
    emi_amount = Column(Numeric(15, 2), nullable=False)
    principal_component = Column(Numeric(15, 2), nullable=False)
    interest_component = Column(Numeric(15, 2), nullable=False)
    
    # Outstanding Before Payment
    opening_principal_balance = Column(Numeric(15, 2), nullable=False)
    closing_principal_balance = Column(Numeric(15, 2), nullable=False)
    
    # Payment Details
    payment_date = Column(Date, nullable=True)
    amount_paid = Column(Numeric(15, 2), default=Decimal("0.00"))
    principal_paid = Column(Numeric(15, 2), default=Decimal("0.00"))
    interest_paid = Column(Numeric(15, 2), default=Decimal("0.00"))
    
    # Status
    status = Column(SQLEnum(EMIStatus), nullable=False, default=EMIStatus.PENDING, index=True)
    is_overdue = Column(Boolean, default=False)
    days_overdue = Column(Integer, default=0)
    penalty_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    
    # Payment Reference
    payment_reference = Column(String(100), nullable=True)
    payroll_run_id = Column(UUID(as_uuid=True), nullable=True)  # Link to payroll if deducted from salary
    transaction_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Waiver
    is_waived = Column(Boolean, default=False)
    waived_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    waiver_reason = Column(Text, nullable=True)
    waived_by = Column(UUID(as_uuid=True), nullable=True)
    waived_date = Column(DateTime, nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    
    # Relationships
    loan = relationship("EmployeeLoan", back_populates="emi_schedule")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_emi_loan', 'tenant_id', 'loan_id', 'emi_number'),
        Index('idx_emi_due_date', 'tenant_id', 'emi_due_date', 'status'),
        Index('idx_emi_status', 'tenant_id', 'status', 'is_overdue'),
    )
    
    def __repr__(self):
        return f"<LoanEMISchedule(loan_id={self.loan_id}, emi_number={self.emi_number}, due_date={self.emi_due_date})>"


# ============================================================================
# LOAN TRANSACTIONS
# ============================================================================

class LoanTransaction(BaseModel):
    """
    Loan Transaction History
    Records all financial transactions related to the loan
    """
    __tablename__ = "hrms_loan_transactions"
    
    # Transaction Identification
    transaction_code = Column(String(50), nullable=False, index=True)
    
    # Loan Reference
    loan_id = Column(UUID(as_uuid=True), ForeignKey("hrms_employee_loans.id", ondelete="CASCADE"), nullable=False)
    emi_schedule_id = Column(UUID(as_uuid=True), ForeignKey("hrms_loan_emi_schedule.id", ondelete="SET NULL"), nullable=True)
    
    # Transaction Details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    
    # Amount Details
    transaction_amount = Column(Numeric(15, 2), nullable=False)
    principal_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    interest_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    penalty_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    
    # Balances After Transaction
    principal_outstanding = Column(Numeric(15, 2), nullable=False)
    interest_outstanding = Column(Numeric(15, 2), nullable=False)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    
    # Payment Details
    payment_mode = Column(String(20), nullable=True)  # salary_deduction, bank_transfer, cash, cheque
    payment_reference = Column(String(100), nullable=True)
    payroll_run_id = Column(UUID(as_uuid=True), nullable=True)  # If deducted from payroll
    
    # Reversal
    is_reversed = Column(Boolean, default=False)
    reversed_by_transaction_id = Column(UUID(as_uuid=True), nullable=True)
    reversal_reason = Column(Text, nullable=True)
    reversal_date = Column(DateTime, nullable=True)
    
    # Remarks
    remarks = Column(Text, nullable=True)
    processed_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    loan = relationship("EmployeeLoan", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_txn_code', 'tenant_id', 'transaction_code', unique=True),
        Index('idx_txn_loan', 'tenant_id', 'loan_id', 'transaction_date'),
        Index('idx_txn_type', 'tenant_id', 'transaction_type', 'transaction_date'),
    )
    
    def __repr__(self):
        return f"<LoanTransaction(code={self.transaction_code}, type={self.transaction_type}, amount={self.transaction_amount})>"
