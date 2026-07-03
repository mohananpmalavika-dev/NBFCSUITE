"""
Deposit Operating System - Database Models
Enterprise-grade deposit management with FD/RD/CASA support
"""

from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime, 
    ForeignKey, Text, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()


# ==================== ENUMS ====================

class DepositType(str, enum.Enum):
    """Deposit product types"""
    FIXED_DEPOSIT = "FIXED_DEPOSIT"
    RECURRING_DEPOSIT = "RECURRING_DEPOSIT"
    CASA = "CASA"
    FLEXI_DEPOSIT = "FLEXI_DEPOSIT"


class InterestMethod(str, enum.Enum):
    """Interest calculation methods"""
    SIMPLE = "SIMPLE"
    COMPOUND_MONTHLY = "COMPOUND_MONTHLY"
    COMPOUND_QUARTERLY = "COMPOUND_QUARTERLY"
    COMPOUND_HALF_YEARLY = "COMPOUND_HALF_YEARLY"
    COMPOUND_YEARLY = "COMPOUND_YEARLY"


class PayoutFrequency(str, enum.Enum):
    """Interest payout frequency"""
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    YEARLY = "YEARLY"
    ON_MATURITY = "ON_MATURITY"
    CUMULATIVE = "CUMULATIVE"


class DepositAccountStatus(str, enum.Enum):
    """Deposit account lifecycle status"""
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    MATURED = "MATURED"
    PREMATURELY_CLOSED = "PREMATURELY_CLOSED"
    RENEWED = "RENEWED"
    CLOSED = "CLOSED"
    SUSPENDED = "SUSPENDED"


class RDInstallmentStatus(str, enum.Enum):
    """RD installment status"""
    SCHEDULED = "SCHEDULED"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"


# ==================== PRODUCT ENGINE ====================

class DepositProduct(Base):
    """
    Configurable Deposit Products
    Supports FD, RD, CASA with flexible configurations
    """
    __tablename__ = "deposit_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    deposit_type = Column(SQLEnum(DepositType), nullable=False)
    
    # Amount constraints
    min_amount = Column(Numeric(15, 2), nullable=False)
    max_amount = Column(Numeric(15, 2))
    
    # Tenure constraints (in days)
    min_tenure_days = Column(Integer)
    max_tenure_days = Column(Integer)
    
    # Interest configuration
    interest_method = Column(SQLEnum(InterestMethod), nullable=False)
    default_interest_rate = Column(Numeric(5, 2))  # Annual percentage
    senior_citizen_rate_bonus = Column(Numeric(5, 2), default=0.5)
    
    # Payout options
    payout_frequency = Column(SQLEnum(PayoutFrequency), nullable=False)
    
    # Features
    premature_allowed = Column(Boolean, default=True)
    premature_penalty_percentage = Column(Numeric(5, 2), default=1.0)
    auto_renewal_allowed = Column(Boolean, default=True)
    loan_against_deposit_allowed = Column(Boolean, default=True)
    nomination_mandatory = Column(Boolean, default=False)
    
    # Tax
    tds_applicable = Column(Boolean, default=True)
    tds_rate = Column(Numeric(5, 2), default=10.0)
    
    # Business rules
    business_rules = Column(JSONB)  # Flexible rules engine
    
    # Status
    status = Column(String(20), default="ACTIVE")
    effective_from = Column(Date)
    effective_to = Column(Date)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(100))
    
    # Relationships
    accounts = relationship("DepositAccount", back_populates="product")
    interest_slabs = relationship("InterestSlab", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_product_type_status', 'deposit_type', 'status'),
    )


class InterestSlab(Base):
    """
    Interest rate slabs based on amount and tenure
    Supports dynamic rate calculation
    """
    __tablename__ = "interest_slabs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("deposit_products.id"), nullable=False)
    
    # Slab criteria
    min_amount = Column(Numeric(15, 2))
    max_amount = Column(Numeric(15, 2))
    min_tenure_days = Column(Integer)
    max_tenure_days = Column(Integer)
    
    # Rate
    interest_rate = Column(Numeric(5, 2), nullable=False)
    senior_citizen_rate = Column(Numeric(5, 2))
    
    # Special rates
    special_rate_applicable = Column(Boolean, default=False)
    special_rate_conditions = Column(JSONB)
    
    effective_from = Column(Date)
    effective_to = Column(Date)
    
    # Relationships
    product = relationship("DepositProduct", back_populates="interest_slabs")

    __table_args__ = (
        Index('idx_slab_product_effective', 'product_id', 'effective_from', 'effective_to'),
    )


# ==================== DEPOSIT ACCOUNTS ====================

class DepositAccount(Base):
    """
    Core Deposit Account
    Supports FD, RD, and all deposit types
    """
    __tablename__ = "deposit_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer linkage
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    cif_number = Column(String(50), nullable=False, index=True)
    
    # Product
    product_id = Column(UUID(as_uuid=True), ForeignKey("deposit_products.id"), nullable=False)
    deposit_type = Column(SQLEnum(DepositType), nullable=False)
    
    # Account details
    principal_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    is_senior_citizen = Column(Boolean, default=False)
    
    # Dates
    open_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    actual_closure_date = Column(Date)
    
    # Maturity
    maturity_amount = Column(Numeric(15, 2))
    maturity_instruction = Column(String(50))  # RENEW, PAYOUT, PARTIAL_RENEW
    
    # Interest configuration
    interest_method = Column(SQLEnum(InterestMethod))
    payout_frequency = Column(SQLEnum(PayoutFrequency))
    interest_payout_account = Column(String(50))  # For periodic interest
    
    # Features
    auto_renewal = Column(Boolean, default=False)
    loan_facility = Column(Boolean, default=False)
    
    # Status
    status = Column(SQLEnum(DepositAccountStatus), nullable=False, default=DepositAccountStatus.DRAFT)
    
    # Financial summary
    total_interest_earned = Column(Numeric(15, 2), default=0)
    total_interest_paid = Column(Numeric(15, 2), default=0)
    total_tds_deducted = Column(Numeric(15, 2), default=0)
    last_interest_calculated_date = Column(Date)
    
    # Branch & maker-checker
    branch_code = Column(String(20))
    created_by = Column(String(100))
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Metadata
    metadata = Column(JSONB)  # Flexible storage
    
    # Relationships
    product = relationship("DepositProduct", back_populates="accounts")
    nominees = relationship("Nominee", back_populates="account", cascade="all, delete-orphan")
    interest_postings = relationship("InterestPosting", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("DepositTransaction", back_populates="account", cascade="all, delete-orphan")
    rd_schedule = relationship("RDSchedule", back_populates="account", cascade="all, delete-orphan")
    certificates = relationship("DepositCertificate", back_populates="account", cascade="all, delete-orphan")
    renewal_history = relationship("RenewalHistory", back_populates="account", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_account_customer_status', 'customer_id', 'status'),
        Index('idx_account_maturity', 'maturity_date', 'status'),
        Index('idx_account_branch', 'branch_code', 'status'),
    )


# ==================== NOMINEE MANAGEMENT ====================

class Nominee(Base):
    """
    Nominee/Beneficiary management
    Banking-grade nominee tracking
    """
    __tablename__ = "nominees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("deposit_accounts.id"), nullable=False)
    
    # Nominee details
    name = Column(String(200), nullable=False)
    relationship = Column(String(50), nullable=False)
    date_of_birth = Column(Date)
    age = Column(Integer)
    
    # Contact
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    
    # Identification
    id_proof_type = Column(String(50))
    id_proof_number = Column(String(100))
    
    # Allocation
    allocation_percentage = Column(Numeric(5, 2), default=100.00)
    is_minor = Column(Boolean, default=False)
    guardian_name = Column(String(200))
    guardian_relationship = Column(String(50))
    
    # Priority
    nominee_order = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount", back_populates="nominees")


# ==================== INTEREST ENGINE ====================

class InterestPosting(Base):
    """
    Interest calculation and posting records
    Supports all interest methods and payout frequencies
    """
    __tablename__ = "interest_postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("deposit_accounts.id"), nullable=False)
    
    # Period
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    days = Column(Integer, nullable=False)
    
    # Calculation
    principal_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    interest_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tax
    tds_amount = Column(Numeric(15, 2), default=0)
    tds_rate = Column(Numeric(5, 2))
    net_interest = Column(Numeric(15, 2))
    
    # Posting
    posting_date = Column(Date)
    is_paid = Column(Boolean, default=False)
    payment_date = Column(Date)
    payment_reference = Column(String(100))
    
    # Accounting
    journal_entry_id = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount", back_populates="interest_postings")

    __table_args__ = (
        Index('idx_interest_account_period', 'account_id', 'from_date', 'to_date'),
        Index('idx_interest_posting_date', 'posting_date', 'is_paid'),
    )


# ==================== RD ENGINE ====================

class RDSchedule(Base):
    """
    Recurring Deposit Installment Schedule
    Manages monthly installments, penalties, and collections
    """
    __tablename__ = "rd_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("deposit_accounts.id"), nullable=False)
    
    # Installment details
    installment_number = Column(Integer, nullable=False)
    installment_amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(RDInstallmentStatus), default=RDInstallmentStatus.SCHEDULED)
    
    # Payment
    paid_amount = Column(Numeric(15, 2), default=0)
    paid_date = Column(Date)
    payment_mode = Column(String(50))
    payment_reference = Column(String(100))
    
    # Penalty
    penalty_amount = Column(Numeric(15, 2), default=0)
    penalty_waived = Column(Boolean, default=False)
    waiver_reason = Column(Text)
    
    # Grace period
    grace_period_days = Column(Integer, default=7)
    overdue_days = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount", back_populates="rd_schedule")

    __table_args__ = (
        Index('idx_rd_account_due', 'account_id', 'due_date', 'status'),
    )


# ==================== TRANSACTIONS ====================

class DepositTransaction(Base):
    """
    All deposit-related transactions
    Opening, closure, interest payout, penalty, etc.
    """
    __tablename__ = "deposit_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("deposit_accounts.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # OPENING, INTEREST_PAYOUT, CLOSURE, etc.
    transaction_date = Column(Date, nullable=False)
    value_date = Column(Date)
    
    # Amount
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2))
    
    # Reference
    reference_number = Column(String(100), unique=True)
    payment_mode = Column(String(50))
    narration = Column(Text)
    
    # Accounting
    journal_entry_id = Column(String(100))
    
    # Maker-checker
    created_by = Column(String(100))
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount", back_populates="transactions")

    __table_args__ = (
        Index('idx_txn_account_date', 'account_id', 'transaction_date'),
        Index('idx_txn_type_date', 'transaction_type', 'transaction_date'),
    )


# ==================== CERTIFICATES ====================

class DepositCertificate(Base):
    """
    FD Certificates and documents
    Generated for opening, renewal, interest, TDS
    """
    __tablename__ = "deposit_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("deposit_accounts.id"), nullable=False)
    
    certificate_type = Column(String(50), nullable=False)  # FD_CERTIFICATE, INTEREST_STATEMENT, TDS_CERTIFICATE
    certificate_number = Column(String(100), unique=True)
    
    # Document reference
    document_id = Column(String(100))  # Reference to document service
    document_url = Column(String(500))
    
    # Period
    from_date = Column(Date)
    to_date = Column(Date)
    financial_year = Column(String(10))
    
    # Status
    status = Column(String(20), default="GENERATED")
    generated_date = Column(DateTime, default=datetime.utcnow)
    sent_date = Column(DateTime)
    
    # Metadata
    metadata = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("DepositAccount", back_populates="certificates")


# ==================== RENEWAL ENGINE ====================

class RenewalHistory(Base):
    """
    Track deposit renewals and maturity actions
    """
    __tablename__ = "renewal_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    old_account_id = Column(UUID(as_uuid=True), ForeignKey("deposit_accounts.id"), nullable=False)
    new_account_id = Column(UUID(as_uuid=True))
    
    # Renewal details
    renewal_date = Column(Date, nullable=False)
    renewal_type = Column(String(50))  # AUTO, MANUAL, PARTIAL
    
    # Amounts
    maturity_amount = Column(Numeric(15, 2))
    renewed_principal = Column(Numeric(15, 2))
    interest_paid_out = Column(Numeric(15, 2))
    
    # New terms
    new_interest_rate = Column(Numeric(5, 2))
    new_tenure_days = Column(Integer)
    new_maturity_date = Column(Date)
    
    # AI recommendation
    ai_recommended = Column(Boolean, default=False)
    ai_confidence_score = Column(Numeric(5, 2))
    ai_reasoning = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    
    # Relationships
    account = relationship("DepositAccount", back_populates="renewal_history")


# ==================== PREMATURE CLOSURE ====================

class PrematureClosure(Base):
    """
    Premature closure requests and processing
    """
    __tablename__ = "premature_closures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Request
    request_date = Column(Date, nullable=False)
    requested_by = Column(String(100))
    closure_reason = Column(Text)
    
    # Calculation
    principal_amount = Column(Numeric(15, 2))
    days_completed = Column(Integer)
    applicable_interest_rate = Column(Numeric(5, 2))
    interest_earned = Column(Numeric(15, 2))
    penalty_percentage = Column(Numeric(5, 2))
    penalty_amount = Column(Numeric(15, 2))
    tds_amount = Column(Numeric(15, 2))
    net_payout = Column(Numeric(15, 2))
    
    # Approval
    status = Column(String(20), default="PENDING")
    approved_by = Column(String(100))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Closure
    closure_date = Column(Date)
    payment_mode = Column(String(50))
    payment_reference = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_closure_status', 'status', 'request_date'),
    )


# ==================== AI INTELLIGENCE ====================

class DepositIntelligence(Base):
    """
    AI-powered deposit insights and predictions
    Customer behavior, renewal probability, churn risk
    """
    __tablename__ = "deposit_intelligence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True))
    
    # Analysis type
    analysis_type = Column(String(50), nullable=False)  # RENEWAL_PREDICTION, CHURN_RISK, PRODUCT_RECOMMENDATION
    
    # Prediction
    prediction = Column(String(100))
    confidence_score = Column(Numeric(5, 2))
    probability = Column(Numeric(5, 2))
    
    # Insights
    insights = Column(JSONB)
    behavioral_patterns = Column(JSONB)
    recommendations = Column(JSONB)
    
    # Context
    data_points_analyzed = Column(Integer)
    model_version = Column(String(50))
    
    # Validity
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_intelligence_customer_type', 'customer_id', 'analysis_type'),
    )


# ==================== MATURITY PIPELINE ====================

class MaturityPipeline(Base):
    """
    Track upcoming maturities for proactive management
    """
    __tablename__ = "maturity_pipeline"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    
    maturity_date = Column(Date, nullable=False)
    maturity_amount = Column(Numeric(15, 2))
    
    # Customer preference
    customer_instruction = Column(String(50))
    contact_attempted = Column(Boolean, default=False)
    contact_date = Column(Date)
    contact_method = Column(String(50))
    
    # AI recommendation
    ai_recommended_action = Column(String(50))
    renewal_probability = Column(Numeric(5, 2))
    
    # Status
    status = Column(String(20), default="UPCOMING")
    processed_date = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_maturity_date_status', 'maturity_date', 'status'),
    )
