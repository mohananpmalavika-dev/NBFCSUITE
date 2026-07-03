"""
Phase 7: Loan Servicing & Repayment - SQLAlchemy Models
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Numeric, Date, DateTime, Boolean, Text, 
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class EMISchedule(Base):
    """EMI schedule with payment tracking"""
    __tablename__ = "gold_emi_schedule"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    
    # EMI components
    principal_component = Column(Numeric(15, 2), nullable=False)
    interest_component = Column(Numeric(15, 2), nullable=False)
    total_emi_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment tracking
    payment_status = Column(String(50), nullable=False, default="pending")
    paid_amount = Column(Numeric(15, 2), default=0)
    paid_date = Column(Date)
    payment_mode = Column(String(50))
    transaction_reference = Column(String(100))
    
    # Outstanding
    outstanding_principal = Column(Numeric(15, 2))
    outstanding_interest = Column(Numeric(15, 2))
    
    # Overdue tracking
    days_overdue = Column(Integer, default=0)
    overdue_charges = Column(Numeric(15, 2), default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="emi_schedules")
    penalties = relationship("LoanPenalty", back_populates="emi_schedule")
    
    __table_args__ = (
        UniqueConstraint("loan_account_id", "installment_number", name="unique_loan_installment"),
        CheckConstraint("principal_component >= 0 AND interest_component >= 0", name="valid_emi_amounts"),
        CheckConstraint("payment_status IN ('pending', 'paid', 'partially_paid', 'overdue', 'waived')", name="valid_payment_status"),
        Index("idx_emi_schedule_loan", "loan_account_id"),
        Index("idx_emi_schedule_due_date", "due_date"),
        Index("idx_emi_schedule_status", "payment_status"),
        Index("idx_emi_loan_status_due", "loan_account_id", "payment_status", "due_date"),
    )


class RepaymentTransaction(Base):
    """All repayment transactions with allocation"""
    __tablename__ = "gold_repayment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    receipt_number = Column(String(50), unique=True, nullable=False)
    
    # Payment details
    payment_amount = Column(Numeric(15, 2), nullable=False)
    payment_mode = Column(String(50), nullable=False)
    transaction_reference = Column(String(100))
    bank_name = Column(String(100))
    cheque_number = Column(String(50))
    cheque_date = Column(Date)
    
    # Allocation breakdown
    principal_paid = Column(Numeric(15, 2), default=0)
    interest_paid = Column(Numeric(15, 2), default=0)
    overdue_interest_paid = Column(Numeric(15, 2), default=0)
    penalty_paid = Column(Numeric(15, 2), default=0)
    other_charges_paid = Column(Numeric(15, 2), default=0)
    
    # Status
    transaction_status = Column(String(50), nullable=False, default="completed")
    reversal_reason = Column(Text)
    reversed_at = Column(DateTime)
    reversed_by_user_id = Column(String(50))
    
    # Processing
    processed_by_user_id = Column(String(50), nullable=False)
    verified_by_user_id = Column(String(50))
    verification_date = Column(DateTime)
    branch_id = Column(String(50))
    
    # Metadata
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="repayment_transactions")
    prepayments = relationship("LoanPrepayment", back_populates="transaction")
    
    __table_args__ = (
        CheckConstraint("payment_amount > 0", name="valid_payment_amount"),
        CheckConstraint("transaction_status IN ('pending', 'completed', 'bounced', 'reversed', 'cancelled')", name="valid_transaction_status"),
        Index("idx_repayment_loan", "loan_account_id"),
        Index("idx_repayment_date", "transaction_date"),
        Index("idx_repayment_receipt", "receipt_number"),
        Index("idx_repayment_loan_date", "loan_account_id", "transaction_date"),
    )


class InterestAccrual(Base):
    """Daily interest accrual tracking"""
    __tablename__ = "gold_interest_accrual"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    accrual_date = Column(Date, nullable=False)
    accrual_period_start = Column(Date, nullable=False)
    accrual_period_end = Column(Date, nullable=False)
    
    # Principal and rate
    opening_principal = Column(Numeric(15, 2), nullable=False)
    closing_principal = Column(Numeric(15, 2), nullable=False)
    applicable_rate = Column(Numeric(8, 4), nullable=False)
    days_in_period = Column(Integer, nullable=False)
    
    # Interest calculation
    interest_accrued = Column(Numeric(15, 2), nullable=False)
    cumulative_interest = Column(Numeric(15, 2), nullable=False)
    
    # Status
    accrual_status = Column(String(50), nullable=False, default="posted")
    reversed_at = Column(DateTime)
    reversal_reason = Column(Text)
    
    # Metadata
    calculation_method = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="interest_accruals")
    
    __table_args__ = (
        UniqueConstraint("loan_account_id", "accrual_date", name="unique_loan_accrual_date"),
        CheckConstraint("accrual_status IN ('draft', 'posted', 'reversed')", name="valid_accrual_status"),
        CheckConstraint("interest_accrued >= 0", name="valid_interest_amount"),
        Index("idx_interest_accrual_loan", "loan_account_id"),
        Index("idx_interest_accrual_date", "accrual_date"),
        Index("idx_interest_loan_date", "loan_account_id", "accrual_date"),
    )


class LoanAdjustment(Base):
    """Loan account adjustments and waivers"""
    __tablename__ = "gold_loan_adjustments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    adjustment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    adjustment_type = Column(String(50), nullable=False)
    
    # Adjustment details
    adjustment_amount = Column(Numeric(15, 2), nullable=False)
    adjustment_category = Column(String(50), nullable=False)
    
    # Approval workflow
    requested_by_user_id = Column(String(50), nullable=False)
    approved_by_user_id = Column(String(50))
    approval_date = Column(DateTime)
    approval_status = Column(String(50), nullable=False, default="pending")
    
    # Justification
    reason = Column(Text, nullable=False)
    supporting_document_id = Column(String(100))
    branch_id = Column(String(50))
    
    # Accounting impact
    debit_account = Column(String(50))
    credit_account = Column(String(50))
    journal_entry_id = Column(String(100))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="adjustments")
    
    __table_args__ = (
        CheckConstraint("adjustment_type IN ('waiver', 'write_off', 'reversal', 'correction', 'penalty', 'rebate')", name="valid_adjustment_type"),
        CheckConstraint("adjustment_category IN ('principal', 'interest', 'penalty', 'charges')", name="valid_adjustment_category"),
        CheckConstraint("approval_status IN ('pending', 'approved', 'rejected')", name="valid_approval_status"),
        Index("idx_adjustments_loan", "loan_account_id"),
        Index("idx_adjustments_type", "adjustment_type"),
        Index("idx_adjustments_status", "approval_status"),
    )


class LoanPrepayment(Base):
    """Prepayment and foreclosure records"""
    __tablename__ = "gold_loan_prepayments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    prepayment_date = Column(Date, nullable=False)
    prepayment_type = Column(String(50), nullable=False)
    
    # Amount details
    prepayment_amount = Column(Numeric(15, 2), nullable=False)
    outstanding_principal_before = Column(Numeric(15, 2), nullable=False)
    outstanding_interest_before = Column(Numeric(15, 2), nullable=False)
    
    # Charges
    prepayment_charges = Column(Numeric(15, 2), default=0)
    prepayment_charge_percentage = Column(Numeric(5, 2))
    waived_charges = Column(Numeric(15, 2), default=0)
    
    # Impact
    principal_reduced = Column(Numeric(15, 2), nullable=False)
    interest_recalculated = Column(Boolean, default=False)
    tenure_reduced_months = Column(Integer, default=0)
    emi_recalculated = Column(Boolean, default=False)
    new_emi_amount = Column(Numeric(15, 2))
    
    # Status
    prepayment_status = Column(String(50), nullable=False, default="pending")
    approved_by_user_id = Column(String(50))
    approval_date = Column(DateTime)
    
    # NOC for foreclosure
    noc_issued = Column(Boolean, default=False)
    noc_issued_date = Column(Date)
    noc_number = Column(String(50))
    
    # Transaction
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("gold_repayment_transactions.id"))
    
    # Metadata
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="prepayments")
    transaction = relationship("RepaymentTransaction", back_populates="prepayments")
    
    __table_args__ = (
        CheckConstraint("prepayment_type IN ('part_payment', 'foreclosure', 'full_prepayment')", name="valid_prepayment_type"),
        CheckConstraint("prepayment_status IN ('pending', 'approved', 'completed', 'rejected')", name="valid_prepayment_status"),
        CheckConstraint("prepayment_amount > 0", name="valid_prepayment_amount"),
        Index("idx_prepayments_loan", "loan_account_id"),
        Index("idx_prepayments_type", "prepayment_type"),
    )


class LoanStatement(Base):
    """Loan account statements for customers"""
    __tablename__ = "gold_loan_statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    statement_date = Column(Date, nullable=False)
    statement_period_start = Column(Date, nullable=False)
    statement_period_end = Column(Date, nullable=False)
    statement_type = Column(String(50), nullable=False, default="monthly")
    
    # Opening balances
    opening_principal = Column(Numeric(15, 2), nullable=False)
    opening_interest = Column(Numeric(15, 2), nullable=False)
    
    # Transactions summary
    disbursements_amount = Column(Numeric(15, 2), default=0)
    repayments_amount = Column(Numeric(15, 2), default=0)
    interest_charged = Column(Numeric(15, 2), default=0)
    charges_applied = Column(Numeric(15, 2), default=0)
    adjustments_amount = Column(Numeric(15, 2), default=0)
    
    # Closing balances
    closing_principal = Column(Numeric(15, 2), nullable=False)
    closing_interest = Column(Numeric(15, 2), nullable=False)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    
    # Next EMI
    next_emi_due_date = Column(Date)
    next_emi_amount = Column(Numeric(15, 2))
    
    # Document
    statement_generated = Column(Boolean, default=False)
    statement_file_path = Column(String(500))
    generated_at = Column(DateTime)
    sent_to_customer = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    delivery_method = Column(String(50))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="statements")
    
    __table_args__ = (
        UniqueConstraint("loan_account_id", "statement_period_start", "statement_period_end", name="unique_loan_statement_period"),
        CheckConstraint("statement_type IN ('monthly', 'quarterly', 'annual', 'on_demand')", name="valid_statement_type"),
        Index("idx_statements_loan", "loan_account_id"),
        Index("idx_statements_date", "statement_date"),
    )


class AutoDebitMandate(Base):
    """Auto-debit mandate setup for EMI collection"""
    __tablename__ = "gold_auto_debit_mandates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    mandate_reference = Column(String(100), unique=True, nullable=False)
    
    # Bank details
    customer_account_number = Column(String(50), nullable=False)
    customer_ifsc_code = Column(String(20), nullable=False)
    customer_account_holder_name = Column(String(200), nullable=False)
    bank_name = Column(String(100))
    
    # Mandate details
    mandate_type = Column(String(50), nullable=False)
    mandate_amount = Column(Numeric(15, 2))
    mandate_frequency = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    
    # Status
    mandate_status = Column(String(50), nullable=False, default="pending")
    activation_date = Column(Date)
    cancellation_date = Column(Date)
    cancellation_reason = Column(Text)
    
    # Processing
    mandate_document_path = Column(String(500))
    bank_approval_reference = Column(String(100))
    bank_approval_date = Column(Date)
    
    # Debit tracking
    last_debit_date = Column(Date)
    last_debit_amount = Column(Numeric(15, 2))
    last_debit_status = Column(String(50))
    total_successful_debits = Column(Integer, default=0)
    total_failed_debits = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="auto_debit_mandates")
    
    __table_args__ = (
        CheckConstraint("mandate_type IN ('nach', 'emandate', 'standing_instruction')", name="valid_mandate_type"),
        CheckConstraint("mandate_frequency IN ('monthly', 'quarterly', 'one_time')", name="valid_mandate_frequency"),
        CheckConstraint("mandate_status IN ('pending', 'active', 'expired', 'cancelled', 'suspended')", name="valid_mandate_status"),
        Index("idx_mandate_loan", "loan_account_id"),
        Index("idx_mandate_reference", "mandate_reference"),
    )


class LoanPenalty(Base):
    """Penalty and additional charges tracking"""
    __tablename__ = "gold_loan_penalties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id", ondelete="CASCADE"), nullable=False)
    emi_schedule_id = Column(UUID(as_uuid=True), ForeignKey("gold_emi_schedule.id", ondelete="SET NULL"))
    
    # Penalty details
    penalty_date = Column(Date, nullable=False)
    penalty_type = Column(String(50), nullable=False)
    
    # Calculation
    base_amount = Column(Numeric(15, 2))
    penalty_rate = Column(Numeric(8, 4))
    penalty_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    penalty_status = Column(String(50), nullable=False, default="pending")
    waived_amount = Column(Numeric(15, 2), default=0)
    waived_by_user_id = Column(String(50))
    waiver_reason = Column(Text)
    waiver_date = Column(Date)
    
    # Payment
    paid_amount = Column(Numeric(15, 2), default=0)
    payment_date = Column(Date)
    
    # Approval for waiver
    waiver_approval_required = Column(Boolean, default=True)
    approved_by_user_id = Column(String(50))
    approval_date = Column(Date)
    
    # Metadata
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="penalties")
    emi_schedule = relationship("EMISchedule", back_populates="penalties")
    
    __table_args__ = (
        CheckConstraint("penalty_type IN ('late_payment', 'bounced_cheque', 'pre_closure', 'penal_interest', 'documentation')", name="valid_penalty_type"),
        CheckConstraint("penalty_status IN ('pending', 'applied', 'waived', 'paid')", name="valid_penalty_status"),
        CheckConstraint("penalty_amount >= 0", name="valid_penalty_amount"),
        Index("idx_penalties_loan", "loan_account_id"),
        Index("idx_penalties_type", "penalty_type"),
    )


class LoanRenewal(Base):
    """Loan renewal and extension records"""
    __tablename__ = "gold_loan_renewals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id"), nullable=False)
    new_loan_account_id = Column(UUID(as_uuid=True), ForeignKey("gold_loan_accounts.id"))
    
    # Renewal details
    renewal_date = Column(Date, nullable=False)
    renewal_type = Column(String(50), nullable=False)
    
    # Original loan details
    original_principal_outstanding = Column(Numeric(15, 2), nullable=False)
    original_interest_outstanding = Column(Numeric(15, 2), nullable=False)
    original_maturity_date = Column(Date, nullable=False)
    
    # Renewal terms
    extended_tenure_months = Column(Integer)
    new_maturity_date = Column(Date)
    additional_amount = Column(Numeric(15, 2), default=0)
    interest_settled_amount = Column(Numeric(15, 2), default=0)
    
    # Charges
    renewal_charges = Column(Numeric(15, 2), default=0)
    waived_renewal_charges = Column(Numeric(15, 2), default=0)
    
    # Status
    renewal_status = Column(String(50), nullable=False, default="pending")
    approved_by_user_id = Column(String(50))
    approval_date = Column(Date)
    
    # Documentation
    renewal_agreement_signed = Column(Boolean, default=False)
    renewal_agreement_date = Column(Date)
    renewal_agreement_path = Column(String(500))
    
    # Metadata
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    # Relationships
    original_loan = relationship("LoanAccount", foreign_keys=[original_loan_account_id], back_populates="renewal_as_original")
    new_loan = relationship("LoanAccount", foreign_keys=[new_loan_account_id], back_populates="renewal_as_new")
    
    __table_args__ = (
        CheckConstraint("renewal_type IN ('term_extension', 'interest_settlement', 'top_up')", name="valid_renewal_type"),
        CheckConstraint("renewal_status IN ('pending', 'approved', 'completed', 'rejected')", name="valid_renewal_status"),
        Index("idx_renewals_original_loan", "original_loan_account_id"),
        Index("idx_renewals_new_loan", "new_loan_account_id"),
    )


class RepaymentAllocationRule(Base):
    """Rules for payment allocation order"""
    __tablename__ = "gold_repayment_allocation_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(100), unique=True, nullable=False)
    rule_description = Column(Text)
    
    # Priority order
    allocation_priority_1 = Column(String(50), nullable=False)
    allocation_priority_2 = Column(String(50))
    allocation_priority_3 = Column(String(50))
    allocation_priority_4 = Column(String(50))
    allocation_priority_5 = Column(String(50))
    
    # Rule applicability
    is_default = Column(Boolean, default=False)
    product_type = Column(String(50))
    applicable_from_date = Column(Date)
    applicable_to_date = Column(Date)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(String(50))
    
    __table_args__ = (
        CheckConstraint("allocation_priority_1 IN ('penalty', 'overdue_interest', 'current_interest', 'principal', 'charges')", name="valid_allocation_priorities"),
        Index("idx_allocation_rules_default", "is_default"),
        Index("idx_allocation_rules_active", "is_active"),
    )
