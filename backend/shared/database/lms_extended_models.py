"""
LMS Extended Models
Database models for NACH, Loan Restructuring, and Insurance Tracking
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, 
    DateTime, ForeignKey, Enum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
import enum


# ============================================
# NACH/eNACH Models
# ============================================

class MandateType(str, enum.Enum):
    """Mandate types"""
    NACH = "nach"
    ENACH = "enach"
    SI = "standing_instruction"


class MandateStatus(str, enum.Enum):
    """Mandate status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class MandateFrequency(str, enum.Enum):
    """Mandate frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"
    AS_PRESENTED = "as_presented"


class DebitStatus(str, enum.Enum):
    """Auto-debit status"""
    PENDING = "pending"
    INITIATED = "initiated"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NACHMandate(Base):
    """NACH/eNACH Mandate Management"""
    __tablename__ = "nach_mandates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Mandate Details
    mandate_type = Column(Enum(MandateType), nullable=False, index=True)
    mandate_number = Column(String(100), unique=True, index=True)
    umrn = Column(String(50), unique=True, index=True)  # Unique Mandate Reference Number
    
    # Bank Details
    bank_name = Column(String(200), nullable=False)
    bank_account_number = Column(String(50), nullable=False)
    bank_ifsc = Column(String(11), nullable=False)
    bank_branch = Column(String(200))
    account_type = Column(String(50))  # savings, current
    
    # Mandate Configuration
    mandate_frequency = Column(Enum(MandateFrequency), nullable=False)
    max_amount = Column(Numeric(15, 2), nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    
    # EMI Configuration
    emi_amount = Column(Numeric(15, 2), nullable=False)
    emi_day = Column(Integer, nullable=False)  # Day of month (1-31)
    
    # Status
    status = Column(Enum(MandateStatus), default=MandateStatus.PENDING, index=True)
    
    # Registration Details
    sponsor_bank_code = Column(String(20))
    utility_code = Column(String(20))
    category_code = Column(String(10))
    
    # Physical NACH
    nach_form_number = Column(String(50))
    nach_form_date = Column(Date())
    physical_mandate_received = Column(Boolean, default=False)
    
    # eNACH
    enach_url = Column(String(500))
    enach_initiated_date = Column(DateTime())
    enach_authenticated_date = Column(DateTime())
    authentication_mode = Column(String(50))  # netbanking, debitcard, aadhaar
    
    # Submission & Approval
    submission_date = Column(Date())
    submission_reference = Column(String(100))
    approval_date = Column(Date())
    approval_reference = Column(String(100))
    rejection_date = Column(Date())
    rejection_reason = Column(Text())
    
    # Cancellation
    cancellation_date = Column(Date())
    cancellation_reason = Column(Text())
    cancellation_initiated_by = Column(UUID(as_uuid=True))
    
    # Auto-debit Configuration
    auto_debit_enabled = Column(Boolean, default=True)
    retry_on_failure = Column(Boolean, default=True)
    max_retry_attempts = Column(Integer, default=3)
    retry_interval_days = Column(Integer, default=2)
    
    # Statistics
    total_debits_attempted = Column(Integer, default=0)
    total_debits_success = Column(Integer, default=0)
    total_debits_failed = Column(Integer, default=0)
    total_amount_debited = Column(Numeric(15, 2), default=0)
    last_debit_date = Column(Date())
    last_debit_status = Column(String(50))
    consecutive_failures = Column(Integer, default=0)
    
    # Documents
    mandate_form_path = Column(String(500))
    bank_account_proof_path = Column(String(500))
    
    # Metadata
    additional_info = Column(JSONB())
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    loan_account = relationship("LoanAccount")
    customer = relationship("Customer")
    debit_transactions = relationship("NACHDebitTransaction", back_populates="mandate")
    
    # Indexes
    __table_args__ = (
        Index('idx_lms_mandate_tenant_loan', 'tenant_id', 'loan_account_id'),
        Index('idx_lms_mandate_status', 'tenant_id', 'status'),
        Index('idx_lms_mandate_dates', 'start_date', 'end_date'),
    )


class NACHDebitTransaction(Base):
    """NACH Auto-debit Transactions"""
    __tablename__ = "nach_debit_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    mandate_id = Column(Integer, ForeignKey("nach_mandates.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    # Transaction Details
    transaction_reference = Column(String(100), unique=True, nullable=False, index=True)
    presentation_date = Column(Date, nullable=False, index=True)
    debit_amount = Column(Numeric(15, 2), nullable=False)
    
    # Installment Details
    installment_number = Column(Integer)
    emi_due_date = Column(Date)
    
    # Status
    status = Column(Enum(DebitStatus), default=DebitStatus.PENDING, index=True)
    
    # Processing
    initiated_date = Column(DateTime())
    processed_date = Column(DateTime())
    settlement_date = Column(Date())
    
    # Response from Bank/NPCI
    npci_reference = Column(String(100))
    bank_reference = Column(String(100))
    response_code = Column(String(20))
    response_message = Column(Text())
    
    # Success Details
    utr_number = Column(String(50))  # Unique Transaction Reference
    payment_id = Column(Integer, ForeignKey("loan_repayments.id"))
    
    # Failure Details
    failure_reason = Column(Text())
    failure_category = Column(String(50))  # insufficient_funds, account_closed, etc.
    is_retry = Column(Boolean, default=False)
    retry_attempt = Column(Integer, default=0)
    original_transaction_id = Column(Integer)
    
    # Next Action
    retry_scheduled_date = Column(Date())
    can_retry = Column(Boolean, default=True)
    
    # Metadata
    additional_info = Column(JSONB())
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    mandate = relationship("NACHMandate", back_populates="debit_transactions")
    loan_account = relationship("LoanAccount")
    payment = relationship("LoanRepayment")
    
    # Indexes
    __table_args__ = (
        Index('idx_debit_tenant_mandate', 'tenant_id', 'mandate_id'),
        Index('idx_debit_status', 'tenant_id', 'status'),
        Index('idx_debit_presentation', 'tenant_id', 'presentation_date'),
    )



# ============================================
# Loan Restructuring Models
# ============================================

class RestructuringType(str, enum.Enum):
    """Restructuring types"""
    TENURE_EXTENSION = "tenure_extension"
    EMI_REDUCTION = "emi_reduction"
    MORATORIUM = "moratorium"
    INTEREST_RATE_REVISION = "interest_rate_revision"
    HYBRID = "hybrid"


class RestructuringStatus(str, enum.Enum):
    """Restructuring status"""
    REQUESTED = "requested"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class AssetClassification(str, enum.Enum):
    """Asset classification after restructuring"""
    STANDARD = "standard"
    SUB_STANDARD = "sub_standard"
    DOUBTFUL = "doubtful"
    LOSS = "loss"


class LoanRestructuring(Base):
    """Loan Restructuring Management"""
    __tablename__ = "loan_restructurings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Request Details
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    request_date = Column(Date, nullable=False, index=True)
    restructuring_type = Column(Enum(RestructuringType), nullable=False)
    
    # Current Loan Status
    current_outstanding = Column(Numeric(15, 2), nullable=False)
    current_emi = Column(Numeric(15, 2), nullable=False)
    current_tenure_months = Column(Integer, nullable=False)
    current_interest_rate = Column(Numeric(5, 2), nullable=False)
    remaining_tenure = Column(Integer, nullable=False)
    overdue_amount = Column(Numeric(15, 2))
    days_past_due = Column(Integer)
    
    # Restructuring Reason
    reason = Column(Text, nullable=False)
    reason_category = Column(String(50))  # financial_hardship, job_loss, medical, business_loss
    supporting_documents = Column(JSONB())
    
    # Proposed Changes
    proposed_tenure_months = Column(Integer)
    proposed_emi = Column(Numeric(15, 2))
    proposed_interest_rate = Column(Numeric(5, 2))
    moratorium_period_months = Column(Integer)
    moratorium_interest_treatment = Column(String(50))  # waived, capitalized, deferred
    
    # New Terms (After Approval)
    new_tenure_months = Column(Integer)
    new_emi = Column(Numeric(15, 2))
    new_interest_rate = Column(Numeric(5, 2))
    new_maturity_date = Column(Date)
    total_interest_impact = Column(Numeric(15, 2))
    
    # Charges & Fees
    restructuring_charges = Column(Numeric(15, 2))
    processing_fee = Column(Numeric(15, 2))
    legal_charges = Column(Numeric(15, 2))
    total_charges = Column(Numeric(15, 2))
    
    # Status
    status = Column(Enum(RestructuringStatus), default=RestructuringStatus.REQUESTED, index=True)
    
    # Workflow
    reviewed_by = Column(UUID(as_uuid=True))
    reviewed_date = Column(Date())
    review_comments = Column(Text())
    
    approved_by = Column(UUID(as_uuid=True))
    approved_date = Column(Date())
    approval_comments = Column(Text())
    
    rejected_by = Column(UUID(as_uuid=True))
    rejected_date = Column(Date())
    rejection_reason = Column(Text())
    
    # Implementation
    implemented_date = Column(Date())
    effective_date = Column(Date())
    implementation_reference = Column(String(100))
    
    # RBI Compliance
    is_covid_related = Column(Boolean, default=False)
    asset_classification_before = Column(Enum(AssetClassification))
    asset_classification_after = Column(Enum(AssetClassification))
    reporting_required = Column(Boolean, default=True)
    reported_to_rbi = Column(Boolean, default=False)
    reporting_date = Column(Date())
    
    # Customer Consent
    customer_consent_received = Column(Boolean, default=False)
    consent_date = Column(Date())
    consent_document_path = Column(String(500))
    
    # Monitoring (Post-Restructuring)
    is_performing = Column(Boolean, default=True)
    payments_on_time = Column(Integer, default=0)
    payments_delayed = Column(Integer, default=0)
    last_monitoring_date = Column(Date())
    
    # Documents
    request_letter_path = Column(String(500))
    supporting_docs_path = Column(JSONB())
    sanction_letter_path = Column(String(500))
    
    # Metadata
    additional_info = Column(JSONB())
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    loan_account = relationship("LoanAccount")
    customer = relationship("Customer")
    
    # Indexes
    __table_args__ = (
        Index('idx_lms_restructuring_tenant_loan', 'tenant_id', 'loan_account_id'),
        Index('idx_lms_restructuring_status', 'tenant_id', 'status'),
        Index('idx_lms_restructuring_date', 'tenant_id', 'request_date'),
    )


# ============================================
# Insurance Tracking Models
# ============================================

class InsurancePolicyType(str, enum.Enum):
    """Insurance policy types"""
    LIFE = "life"
    PROPERTY = "property"
    VEHICLE = "vehicle"
    HEALTH = "health"
    CREDIT_PROTECTION = "credit_protection"


class InsurancePolicyStatus(str, enum.Enum):
    """Insurance policy status"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    CLAIMED = "claimed"
    LAPSED = "lapsed"



class LoanInsurancePolicy(Base):
    """Loan Insurance Policy Tracking"""
    __tablename__ = "loan_insurance_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Policy Details
    policy_number = Column(String(100), unique=True, nullable=False, index=True)
    policy_type = Column(Enum(InsurancePolicyType), nullable=False, index=True)
    insurance_company = Column(String(200), nullable=False)
    insurance_company_code = Column(String(50))
    
    # Coverage
    sum_assured = Column(Numeric(15, 2), nullable=False)
    coverage_amount = Column(Numeric(15, 2))
    outstanding_loan_covered = Column(Numeric(15, 2))
    
    # Premium
    premium_amount = Column(Numeric(15, 2), nullable=False)
    premium_frequency = Column(String(50))  # monthly, quarterly, yearly, single
    total_premium_paid = Column(Numeric(15, 2), default=0)
    
    # Dates
    policy_start_date = Column(Date, nullable=False, index=True)
    policy_end_date = Column(Date, nullable=False, index=True)
    policy_issue_date = Column(Date)
    
    # Beneficiary
    beneficiary_name = Column(String(200))
    beneficiary_relationship = Column(String(50))
    nominee_name = Column(String(200))
    nominee_relationship = Column(String(50))
    
    # Lien Marking (for lender)
    lien_marked = Column(Boolean, default=False)
    lien_marked_date = Column(Date())
    lien_holder_name = Column(String(200))
    lien_removed_date = Column(Date())
    
    # Status
    status = Column(Enum(InsurancePolicyStatus), default=InsurancePolicyStatus.PENDING, index=True)
    
    # Renewal
    is_renewable = Column(Boolean, default=True)
    renewal_due_date = Column(Date())
    renewal_notice_sent = Column(Boolean, default=False)
    renewal_notice_date = Column(Date())
    auto_renewal = Column(Boolean, default=False)
    
    # Cancellation
    cancellation_date = Column(Date())
    cancellation_reason = Column(Text())
    refund_amount = Column(Numeric(15, 2))
    
    # Claims
    claims_count = Column(Integer, default=0)
    total_claim_amount = Column(Numeric(15, 2), default=0)
    last_claim_date = Column(Date())
    
    # Commission (if applicable)
    commission_rate = Column(Numeric(5, 2))
    commission_amount = Column(Numeric(15, 2))
    commission_paid = Column(Boolean, default=False)
    
    # Alerts
    expiry_alert_sent = Column(Boolean, default=False)
    expiry_alert_date = Column(Date())
    days_to_expiry = Column(Integer)
    
    # Documents
    policy_document_path = Column(String(500))
    premium_receipt_path = Column(String(500))
    claim_form_path = Column(String(500))
    
    # Metadata
    additional_info = Column(JSONB())
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    loan_account = relationship("LoanAccount")
    customer = relationship("Customer")
    claims = relationship("LoanInsuranceClaim", back_populates="policy")
    premiums = relationship("InsurancePremiumPayment", back_populates="policy")
    
    # Indexes
    __table_args__ = (
        Index('idx_insurance_tenant_loan', 'tenant_id', 'loan_account_id'),
        Index('idx_insurance_status', 'tenant_id', 'status'),
        Index('idx_insurance_expiry', 'tenant_id', 'policy_end_date', 'status'),
    )


class InsurancePremiumPayment(Base):
    """Insurance Premium Payment Tracking"""
    __tablename__ = "insurance_premium_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    policy_id = Column(Integer, ForeignKey("loan_insurance_policies.id"), nullable=False, index=True)
    
    # Payment Details
    payment_reference = Column(String(100), unique=True, nullable=False)
    premium_amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    payment_date = Column(Date())
    
    # Status
    is_paid = Column(Boolean, default=False)
    payment_status = Column(String(50), default='pending')  # pending, paid, overdue, waived
    
    # Payment Method
    payment_mode = Column(String(50))
    payment_transaction_id = Column(String(100))
    receipt_number = Column(String(100))
    
    # Grace Period
    grace_period_days = Column(Integer, default=15)
    grace_period_end_date = Column(Date())
    is_in_grace_period = Column(Boolean, default=False)
    
    # Late Payment
    days_overdue = Column(Integer, default=0)
    late_payment_charges = Column(Numeric(10, 2))
    
    # Metadata
    additional_info = Column(JSONB())
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    policy = relationship("LoanInsurancePolicy", back_populates="premiums")
    
    # Indexes
    __table_args__ = (
        Index('idx_premium_tenant_policy', 'tenant_id', 'policy_id'),
        Index('idx_premium_due_date', 'tenant_id', 'due_date', 'is_paid'),
    )


class LoanInsuranceClaim(Base):
    """Loan Insurance Claim Tracking"""
    __tablename__ = "loan_insurance_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    policy_id = Column(Integer, ForeignKey("loan_insurance_policies.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    # Claim Details
    claim_number = Column(String(100), unique=True, nullable=False, index=True)
    claim_date = Column(Date, nullable=False, index=True)
    claim_type = Column(String(50), nullable=False)  # death, disability, critical_illness, loss
    
    # Event Details
    event_date = Column(Date, nullable=False)
    event_description = Column(Text, nullable=False)
    event_location = Column(String(200))
    
    # Claim Amount
    claimed_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2))
    settled_amount = Column(Numeric(15, 2))
    outstanding_loan_at_claim = Column(Numeric(15, 2))
    
    # Status
    claim_status = Column(String(50), default='submitted', index=True)
    # submitted, under_review, documents_pending, approved, rejected, settled, closed
    
    # Processing
    submitted_date = Column(Date())
    acknowledged_date = Column(Date())
    surveyor_assigned = Column(Boolean, default=False)
    surveyor_name = Column(String(200))
    surveyor_contact = Column(String(20))
    survey_date = Column(Date())
    survey_report_received = Column(Boolean, default=False)
    
    # Approval
    approved_by_insurer = Column(Boolean, default=False)
    approval_date = Column(Date())
    approval_reference = Column(String(100))
    
    # Rejection
    rejection_date = Column(Date())
    rejection_reason = Column(Text())
    
    # Settlement
    settlement_date = Column(Date())
    settlement_mode = Column(String(50))
    settlement_reference = Column(String(100))
    settlement_bank_account = Column(String(50))
    
    # Loan Impact
    loan_settled = Column(Boolean, default=False)
    loan_settlement_date = Column(Date())
    loan_settlement_amount = Column(Numeric(15, 2))
    
    # Documents
    claim_form_path = Column(String(500))
    death_certificate_path = Column(String(500))
    medical_reports_path = Column(JSONB())
    fir_copy_path = Column(String(500))
    supporting_documents = Column(JSONB())
    
    # Metadata
    additional_info = Column(JSONB())
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    
    # Relationships
    policy = relationship("LoanInsurancePolicy", back_populates="claims")
    loan_account = relationship("LoanAccount")
    
    # Indexes
    __table_args__ = (
        Index('idx_lms_insurance_claim_tenant_policy', 'tenant_id', 'policy_id'),
        Index('idx_lms_insurance_claim_status', 'tenant_id', 'claim_status'),
        Index('idx_lms_insurance_claim_date', 'tenant_id', 'claim_date'),
    )
