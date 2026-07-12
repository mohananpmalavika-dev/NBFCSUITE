"""
NBFC Loan Management System - Database Models
Core loan models for NBFC operations

Note: This is a minimal implementation to prevent import errors.
Full NBFC loan models need to be implemented based on business requirements.
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

class LoanStatus(str, enum.Enum):
    """Loan status"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    CLOSED = "closed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class ApplicationStatus(str, enum.Enum):
    """Application status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class RepaymentFrequency(str, enum.Enum):
    """Repayment frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"
    BULLET = "bullet"


class EMIStatus(str, enum.Enum):
    """EMI payment status"""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIALLY_PAID = "partially_paid"
    WAIVED = "waived"


# ============================================================================
# LOAN PRODUCT
# ============================================================================

class LoanProduct(BaseModel):
    """
    Loan Product Configuration
    Defines different types of loan products offered
    """
    __tablename__ = "loan_products"
    
    # Product Identification
    product_code = Column(String(50), nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    product_type = Column(String(50), nullable=False)  # personal, business, gold, vehicle, property
    description = Column(Text, nullable=True)
    
    # Loan Limits
    min_loan_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("10000.00"))
    max_loan_amount = Column(Numeric(15, 2), nullable=False, default=Decimal("10000000.00"))
    
    # Interest Configuration
    min_interest_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("8.00"))
    max_interest_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("24.00"))
    default_interest_rate = Column(Numeric(5, 2), nullable=False)
    
    # Tenure Configuration
    min_tenure_months = Column(Integer, nullable=False, default=6)
    max_tenure_months = Column(Integer, nullable=False, default=60)
    
    # Repayment Configuration
    repayment_frequency = Column(SQLEnum(RepaymentFrequency), nullable=False, default=RepaymentFrequency.MONTHLY)
    processing_fee_percentage = Column(Numeric(5, 2), default=Decimal("0.00"))
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    applications = relationship("LoanApplication", back_populates="product", lazy="select")
    accounts = relationship("LoanAccount", back_populates="product", lazy="select")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_product_code', 'tenant_id', 'product_code', unique=True),
        Index('idx_product_type', 'tenant_id', 'product_type', 'is_active'),
    )
    
    def __repr__(self):
        return f"<LoanProduct(code={self.product_code}, name={self.product_name})>"


# ============================================================================
# LOAN APPLICATION
# ============================================================================

class LoanApplication(BaseModel):
    """
    Loan Application
    Tracks customer loan applications from submission to approval/rejection
    """
    __tablename__ = "loan_applications"
    
    # Application Identification
    application_number = Column(String(50), nullable=False, index=True)
    
    # Customer & Product
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("loan_products.id", ondelete="RESTRICT"), nullable=False)
    
    # Loan Request Details
    requested_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2), nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    
    # EMI Calculation
    emi_amount = Column(Numeric(15, 2), nullable=True)
    total_repayment_amount = Column(Numeric(15, 2), nullable=True)
    processing_fee = Column(Numeric(15, 2), default=Decimal("0.00"))
    
    # Application Details
    application_date = Column(Date, nullable=False, default=date.today)
    purpose = Column(Text, nullable=False)
    
    # Status & Workflow
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.DRAFT, index=True)
    submitted_date = Column(DateTime, nullable=True)
    approved_date = Column(DateTime, nullable=True)
    rejected_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="loan_applications")
    product = relationship("LoanProduct", back_populates="applications")
    co_applicants = relationship("LoanApplicationCoApplicant", back_populates="application", cascade="all, delete-orphan")
    documents = relationship("LoanApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_app_number', 'tenant_id', 'application_number', unique=True),
        Index('idx_app_customer', 'tenant_id', 'customer_id', 'status'),
        Index('idx_app_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<LoanApplication(number={self.application_number}, customer_id={self.customer_id})>"


# ============================================================================
# LOAN APPLICATION CO-APPLICANT
# ============================================================================

class LoanApplicationCoApplicant(BaseModel):
    """
    Loan Application Co-Applicant
    Additional applicants for joint loans
    """
    __tablename__ = "loan_application_co_applicants"
    
    # Application Reference
    application_id = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id", ondelete="CASCADE"), nullable=False)
    
    # Co-Applicant Details
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=True)
    name = Column(String(200), nullable=False)
    relation_type = Column(String(50), nullable=False)  # renamed from 'relationship' to avoid shadowing SQLAlchemy function
    contact_number = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    
    # Income Details
    occupation = Column(String(100), nullable=True)
    annual_income = Column(Numeric(15, 2), nullable=True)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="co_applicants")
    customer = relationship("Customer")
    
    # Indexes
    __table_args__ = (
        Index('idx_co_applicant_app', 'tenant_id', 'application_id'),
    )
    
    def __repr__(self):
        return f"<LoanApplicationCoApplicant(name={self.name}, application_id={self.application_id})>"


# ============================================================================
# LOAN APPLICATION DOCUMENT
# ============================================================================

class LoanApplicationDocument(BaseModel):
    """
    Loan Application Document
    Documents submitted with loan application
    """
    __tablename__ = "loan_application_documents"
    
    # Application Reference
    application_id = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id", ondelete="CASCADE"), nullable=False)
    
    # Document Details
    document_type = Column(String(100), nullable=False)
    document_name = Column(String(200), nullable=False)
    document_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    verification_remarks = Column(Text, nullable=True)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="documents")
    
    # Indexes
    __table_args__ = (
        Index('idx_app_document', 'tenant_id', 'application_id', 'document_type'),
    )
    
    def __repr__(self):
        return f"<LoanApplicationDocument(type={self.document_type}, application_id={self.application_id})>"


# ============================================================================
# LOAN ACCOUNT
# ============================================================================

class LoanAccount(BaseModel):
    """
    Loan Account
    Active loan account after disbursement
    """
    __tablename__ = "loan_accounts"
    
    # Account Identification
    account_number = Column(String(50), nullable=False, index=True)
    
    # Customer & Product
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("loan_products.id", ondelete="RESTRICT"), nullable=False)
    application_id = Column(UUID(as_uuid=True), ForeignKey("loan_applications.id", ondelete="SET NULL"), nullable=True)
    
    # Loan Details
    loan_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    repayment_frequency = Column(SQLEnum(RepaymentFrequency), nullable=False, default=RepaymentFrequency.MONTHLY)
    
    # EMI Calculation
    emi_amount = Column(Numeric(15, 2), nullable=False)
    total_interest = Column(Numeric(15, 2), default=Decimal("0.00"))
    total_repayment_amount = Column(Numeric(15, 2), nullable=False)
    
    # Disbursement Details
    disbursement_date = Column(Date, nullable=True)
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
    
    # Status
    status = Column(SQLEnum(LoanStatus), nullable=False, default=LoanStatus.ACTIVE, index=True)
    closure_date = Column(Date, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="loan_accounts")
    product = relationship("LoanProduct", back_populates="accounts")
    application = relationship("LoanApplication")
    emi_schedule = relationship("LoanEMISchedule", back_populates="loan_account", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_account_number', 'tenant_id', 'account_number', unique=True),
        Index('idx_account_customer', 'tenant_id', 'customer_id', 'status'),
        Index('idx_account_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<LoanAccount(number={self.account_number}, customer_id={self.customer_id})>"


# ============================================================================
# EMI SCHEDULE
# ============================================================================

class LoanEMISchedule(BaseModel):
    """
    Loan EMI Schedule
    Detailed repayment schedule for each installment
    """
    __tablename__ = "loan_emi_schedules"
    
    # Loan Reference
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id", ondelete="CASCADE"), nullable=False)
    
    # EMI Details
    emi_number = Column(Integer, nullable=False)
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
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="emi_schedule")
    
    # Indexes
    __table_args__ = (
        Index('idx_tenant_emi_loan', 'tenant_id', 'loan_account_id', 'emi_number'),
        Index('idx_emi_due_date', 'tenant_id', 'emi_due_date', 'status'),
        Index('idx_emi_status', 'tenant_id', 'status', 'is_overdue'),
    )
    
    def __repr__(self):
        return f"<LoanEMISchedule(loan_id={self.loan_account_id}, emi_number={self.emi_number})>"
