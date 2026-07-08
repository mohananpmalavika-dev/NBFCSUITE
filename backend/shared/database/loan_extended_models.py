"""
Loan Extended Models
NACH/eNACH Mandates, Restructuring, and Insurance Tracking
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, 
    DateTime, ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .models import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class MandateType(str, enum.Enum):
    """Mandate types"""
    NACH = "nach"
    EMANDATE = "emandate"


class MandateStatus(str, enum.Enum):
    """Mandate status"""
    PENDING = "pending"
    REGISTERED = "registered"
    APPROVED = "approved"
    ACTIVE = "active"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class DebitTransactionStatus(str, enum.Enum):
    """Debit transaction status"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    ACCOUNT_CLOSED = "account_closed"
    MANDATE_CANCELLED = "mandate_cancelled"


class RestructuringType(str, enum.Enum):
    """Restructuring types"""
    TENURE_EXTENSION = "tenure_extension"
    EMI_REDUCTION = "emi_reduction"
    MORATORIUM = "moratorium"
    RATE_REVISION = "rate_revision"
    COMBINATION = "combination"


class RestructuringStatus(str, enum.Enum):
    """Restructuring status"""
    REQUESTED = "requested"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class AssetClassification(str, enum.Enum):
    """Asset classification as per RBI"""
    STANDARD = "standard"
    SMA_0 = "sma_0"  # Special Mention Account 0
    SMA_1 = "sma_1"  # Special Mention Account 1
    SMA_2 = "sma_2"  # Special Mention Account 2
    SUB_STANDARD = "sub_standard"
    DOUBTFUL = "doubtful"
    LOSS = "loss"


class MoratoriumType(str, enum.Enum):
    """Moratorium types"""
    FULL_EMI = "full_emi"  # No payment required
    INTEREST_ONLY = "interest_only"  # Only interest, no principal
    PRINCIPAL_ONLY = "principal_only"  # Only principal, no interest


class InsurancePolicyType(str, enum.Enum):
    """Insurance policy types"""
    LIFE = "life"
    PROPERTY = "property"
    VEHICLE = "vehicle"
    HEALTH = "health"
    CREDIT_LIFE = "credit_life"
    FIRE = "fire"
    GENERAL = "general"


class InsurancePolicyStatus(str, enum.Enum):
    """Insurance policy status"""
    ACTIVE = "active"
    LAPSED = "lapsed"
    CLAIMED = "claimed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class PremiumFrequency(str, enum.Enum):
    """Premium payment frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"


class ClaimStatus(str, enum.Enum):
    """Insurance claim status"""
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"
    CLOSED = "closed"


# ============================================================================
# NACH/eNACH MANDATE MODELS
# ============================================================================

class LoanNACHMandate(BaseModel):
    """NACH/eNACH mandate for auto-debit"""
    __tablename__ = "loan_nach_mandates"
    
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Mandate Details
    umrn = Column(String(20), unique=True, index=True)  # Unique Mandate Reference Number
    mandate_type = Column(SQLEnum(MandateType), nullable=False)
    mandate_status = Column(SQLEnum(MandateStatus), default=MandateStatus.PENDING, index=True)
    
    # Bank Details
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("customer_bank_accounts.id"), nullable=False)
    bank_name = Column(String(200))
    account_number = Column(String(50))
    ifsc_code = Column(String(11))
    account_holder_name = Column(String(300))
    account_type = Column(String(20))  # savings, current
    
    # Mandate Configuration
    max_amount = Column(Numeric(15, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    frequency = Column(String(20), default='monthly')  # monthly, quarterly
    debit_type = Column(String(20), default='maximum')  # maximum, fixed
    
    # Registration Details
    registration_date = Column(DateTime)
    registration_mode = Column(String(50))  # online, offline, netbanking
    registration_reference = Column(String(100))
    sponsor_bank_code = Column(String(20))
    utility_code = Column(String(20))
    
    # Approval Details
    approval_date = Column(DateTime)
    approval_reference = Column(String(100))
    rejection_date = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Status Tracking
    is_active = Column(Boolean, default=True)
    cancellation_date = Column(DateTime)
    cancellation_reason = Column(Text)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Auto-debit Configuration
    auto_debit_enabled = Column(Boolean, default=True)
    debit_day = Column(Integer)  # 1-28
    retry_attempts = Column(Integer, default=0)
    max_retry_attempts = Column(Integer, default=3)
    
    # Integration
    npci_request_data = Column(JSON)
    npci_response_data = Column(JSON)
    last_debit_date = Column(Date)
    last_debit_status = Column(String(50))
    last_debit_reference = Column(String(100))
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    bank_account = relationship("CustomerBankAccount", foreign_keys=[bank_account_id])
    transactions = relationship("LoanMandateTransaction", back_populates="mandate", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_mandate_loan', 'tenant_id', 'loan_account_id'),
        Index('idx_mandate_customer', 'tenant_id', 'customer_id'),
        Index('idx_mandate_status', 'tenant_id', 'mandate_status'),
    )


class LoanMandateTransaction(BaseModel):
    """NACH mandate debit transactions"""
    __tablename__ = "loan_mandate_transactions"
    
    mandate_id = Column(UUID(as_uuid=True), ForeignKey("loan_nach_mandates.id"), nullable=False, index=True)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    # Transaction Details
    transaction_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(SQLEnum(DebitTransactionStatus), nullable=False, index=True)
    
    # NPCI Details
    npci_reference = Column(String(100), index=True)
    transaction_id = Column(String(100), unique=True)
    presentation_date = Column(Date)
    settlement_date = Column(Date)
    
    # Response
    response_code = Column(String(20))
    response_message = Column(Text)
    failure_reason = Column(Text)
    
    # Retry
    is_retry = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    original_transaction_id = Column(UUID(as_uuid=True))
    
    # EMI Link
    emi_schedule_id = Column(UUID(as_uuid=True), ForeignKey("loan_emi_schedule.id"))
    
    # Relationships
    mandate = relationship("LoanNACHMandate", back_populates="transactions")
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    
    __table_args__ = (
        Index('idx_transaction_mandate', 'mandate_id', 'transaction_date'),
        Index('idx_transaction_status', 'tenant_id', 'status'),
    )


# ============================================================================
# LOAN RESTRUCTURING MODELS
# ============================================================================

class LoanRestructuringRequest(BaseModel):
    """Loan restructuring requests"""
    __tablename__ = "loan_restructuring_requests"
    
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Request Details
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    request_date = Column(Date, nullable=False)
    request_type = Column(SQLEnum(RestructuringType), nullable=False)
    request_reason = Column(Text)
    
    # Current Loan Terms
    current_outstanding_principal = Column(Numeric(15, 2))
    current_outstanding_interest = Column(Numeric(15, 2))
    current_emi_amount = Column(Numeric(15, 2))
    current_interest_rate = Column(Numeric(5, 2))
    current_tenure_remaining = Column(Integer)
    
    # Proposed Terms
    proposed_tenure_months = Column(Integer)
    proposed_emi_amount = Column(Numeric(15, 2))
    proposed_interest_rate = Column(Numeric(5, 2))
    proposed_moratorium_months = Column(Integer, default=0)
    
    # Charges
    restructuring_charges = Column(Numeric(15, 2), default=0)
    processing_fee = Column(Numeric(15, 2), default=0)
    
    # Justification
    financial_hardship_reason = Column(Text)
    income_documents_provided = Column(Boolean, default=False)
    supporting_documents = Column(JSON)
    
    # Approval Workflow
    status = Column(SQLEnum(RestructuringStatus), default=RestructuringStatus.REQUESTED, index=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approval_date = Column(DateTime)
    approval_remarks = Column(Text)
    rejection_reason = Column(Text)
    
    # Implementation
    implementation_date = Column(Date)
    new_emi_start_date = Column(Date)
    revised_maturity_date = Column(Date)
    
    # RBI Compliance
    asset_classification_before = Column(SQLEnum(AssetClassification))
    asset_classification_after = Column(SQLEnum(AssetClassification))
    is_covid_related = Column(Boolean, default=False)
    restructuring_count = Column(Integer, default=1)
    
    # Impact
    additional_interest_cost = Column(Numeric(15, 2))
    total_cost_increase = Column(Numeric(15, 2))
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    moratorium_periods = relationship("LoanMoratoriumPeriod", back_populates="restructuring_request", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_restructuring_loan', 'tenant_id', 'loan_account_id'),
        Index('idx_restructuring_status', 'tenant_id', 'status'),
    )


class LoanMoratoriumPeriod(BaseModel):
    """Moratorium (EMI holiday) periods"""
    __tablename__ = "loan_moratorium_periods"
    
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), nullable=False, index=True)
    restructuring_id = Column(UUID(as_uuid=True), ForeignKey("loan_restructuring_requests.id"))
    
    # Moratorium Details
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    duration_months = Column(Integer, nullable=False)
    moratorium_type = Column(SQLEnum(MoratoriumType), nullable=False)
    
    # Interest Treatment
    interest_waived = Column(Boolean, default=False)
    interest_deferred = Column(Boolean, default=True)
    interest_accrued_during_period = Column(Numeric(15, 2))
    
    # Status
    status = Column(String(50), default='active')  # active, completed, cancelled
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    restructuring_request = relationship("LoanRestructuringRequest", back_populates="moratorium_periods")
    
    __table_args__ = (
        Index('idx_moratorium_loan', 'tenant_id', 'loan_account_id'),
    )


# ============================================================================
# INSURANCE TRACKING MODELS
# ============================================================================

class LoanInsurancePolicy(BaseModel):
    """Insurance policies linked to loans"""
    __tablename__ = "loan_insurance_policies"
    
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Policy Details
    policy_number = Column(String(100), unique=True, nullable=False, index=True)
    policy_type = Column(SQLEnum(InsurancePolicyType), nullable=False)
    insurance_provider_name = Column(String(200))
    
    # Coverage
    sum_assured = Column(Numeric(15, 2), nullable=False)
    coverage_amount = Column(Numeric(15, 2), nullable=False)
    coverage_start_date = Column(Date, nullable=False)
    coverage_end_date = Column(Date, nullable=False)
    
    # Premium
    premium_amount = Column(Numeric(15, 2), nullable=False)
    premium_frequency = Column(SQLEnum(PremiumFrequency), nullable=False)
    premium_paid_by = Column(String(20))  # customer, company, split
    next_premium_due_date = Column(Date, index=True)
    
    # Status
    policy_status = Column(SQLEnum(InsurancePolicyStatus), default=InsurancePolicyStatus.ACTIVE, index=True)
    is_mandatory = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verified_date = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Documents
    policy_document_url = Column(String(500))
    
    # Nominee/Beneficiary
    nominee_name = Column(String(300))
    nominee_relationship = Column(String(100))
    nominee_percentage = Column(Numeric(5, 2), default=100)
    
    # Renewal
    renewal_reminder_days = Column(Integer, default=30)
    last_renewal_date = Column(Date)
    next_renewal_date = Column(Date, index=True)
    auto_renewal_enabled = Column(Boolean, default=False)
    
    # Lien
    lien_marked = Column(Boolean, default=False)
    lien_marked_date = Column(Date)
    lien_amount = Column(Numeric(15, 2))
    lien_released_date = Column(Date)
    
    # Integration
    provider_api_reference = Column(String(100))
    policy_link_url = Column(String(500))
    
    # Relationships
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    customer = relationship("Customer", foreign_keys=[customer_id])
    premium_payments = relationship("InsurancePremiumPayment", back_populates="policy", cascade="all, delete-orphan")
    claims = relationship("LoanInsuranceClaim", back_populates="policy", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_policy_loan', 'tenant_id', 'loan_account_id'),
        Index('idx_policy_status', 'tenant_id', 'policy_status'),
        Index('idx_policy_renewal', 'next_renewal_date'),
    )


class InsurancePremiumPayment(BaseModel):
    """Insurance premium payment tracking"""
    __tablename__ = "insurance_premium_payments"
    
    policy_id = Column(UUID(as_uuid=True), ForeignKey("loan_insurance_policies.id"), nullable=False, index=True)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), nullable=False)
    
    # Payment Details
    receipt_number = Column(String(100), unique=True)
    payment_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    premium_amount = Column(Numeric(15, 2), nullable=False)
    late_fee = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment Method
    payment_mode = Column(String(50))  # cash, cheque, online, emi_deduction
    payment_reference = Column(String(100))
    paid_by = Column(String(20))  # customer, company
    
    # Status
    status = Column(String(50), default='pending', index=True)  # pending, paid, overdue, waived
    paid_at = Column(DateTime)
    
    # Relationships
    policy = relationship("LoanInsurancePolicy", back_populates="premium_payments")
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    
    __table_args__ = (
        Index('idx_premium_policy', 'policy_id', 'due_date'),
        Index('idx_premium_status', 'tenant_id', 'status'),
    )


class LoanInsuranceClaim(BaseModel):
    """Loan Insurance claim tracking"""
    __tablename__ = "loan_insurance_claims"
    
    policy_id = Column(UUID(as_uuid=True), ForeignKey("loan_insurance_policies.id"), nullable=False, index=True)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), nullable=False)
    
    # Claim Details
    claim_number = Column(String(100), unique=True, nullable=False, index=True)
    claim_date = Column(Date, nullable=False)
    claim_type = Column(String(50), nullable=False)  # death, disability, property_damage, theft
    claim_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    claim_status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.FILED, index=True)
    approved_amount = Column(Numeric(15, 2))
    settlement_date = Column(Date)
    settlement_amount = Column(Numeric(15, 2))
    
    # Documents
    supporting_documents = Column(JSON)
    
    # Remarks
    remarks = Column(Text)
    rejection_reason = Column(Text)
    
    # Relationships
    policy = relationship("LoanInsurancePolicy", back_populates="claims")
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    
    __table_args__ = (
        Index('idx_claim_policy', 'policy_id', 'claim_date'),
        Index('idx_claim_status', 'tenant_id', 'claim_status'),
    )
