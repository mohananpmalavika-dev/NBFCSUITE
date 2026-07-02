"""
Loan Origination & Disbursement Models
Phase 6: Complete loan lifecycle management
"""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class LoanApplication(Base):
    """Loan application from customer"""
    __tablename__ = "gold_loan_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_number = Column(String(100), unique=True, nullable=False)
    
    # References
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('gold_products.id'), nullable=False)
    journey_session_id = Column(UUID(as_uuid=True), ForeignKey('gold_journey_sessions.id'))
    appraisal_session_id = Column(UUID(as_uuid=True), ForeignKey('gold_appraisal_sessions.id'))
    branch_id = Column(UUID(as_uuid=True), ForeignKey('branches.id'))
    
    # Application details
    loan_amount = Column(Numeric(15, 2), nullable=False)
    requested_tenure = Column(Integer, nullable=False)
    purpose = Column(Text)
    
    # Customer snapshot
    customer_name = Column(String(200), nullable=False)
    customer_mobile = Column(String(15), nullable=False)
    customer_email = Column(String(100))
    customer_pan = Column(String(10))
    customer_address = Column(Text)
    
    # Ornament summary
    total_ornaments = Column(Integer, nullable=False)
    total_gross_weight = Column(Numeric(10, 3), nullable=False)
    total_net_weight = Column(Numeric(10, 3), nullable=False)
    total_valuation = Column(Numeric(15, 2), nullable=False)
    ltv_percentage = Column(Numeric(5, 2), nullable=False)
    
    # Status
    status = Column(String(50), default='draft')
    stage = Column(String(50), default='application')
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True))
    submitted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Metadata
    metadata = Column(JSONB)
    
    # Relationships
    ornaments = relationship("ApplicationOrnament", back_populates="application", cascade="all, delete-orphan")
    credit_evaluation = relationship("CreditEvaluation", back_populates="application", uselist=False)
    approvals = relationship("LoanApproval", back_populates="application")
    loan_account = relationship("LoanAccount", back_populates="application", uselist=False)
    disbursements = relationship("Disbursement", back_populates="application")
    documents = relationship("LoanDocument", back_populates="application")
    status_history = relationship("LoanStatusHistory", back_populates="application")
    
    __table_args__ = (
        CheckConstraint('loan_amount > 0', name='check_loan_amount'),
        CheckConstraint('requested_tenure > 0', name='check_tenure'),
        CheckConstraint('ltv_percentage >= 0 AND ltv_percentage <= 100', name='check_ltv'),
    )


class ApplicationOrnament(Base):
    """Ornaments linked to loan application"""
    __tablename__ = "gold_application_ornaments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id', ondelete='CASCADE'), nullable=False)
    ornament_id = Column(UUID(as_uuid=True), ForeignKey('gold_ornaments.id'), nullable=False)
    packet_id = Column(UUID(as_uuid=True), ForeignKey('gold_packets.id'))
    
    # Ornament snapshot
    ornament_type = Column(String(100), nullable=False)
    gross_weight = Column(Numeric(10, 3), nullable=False)
    net_weight = Column(Numeric(10, 3), nullable=False)
    purity = Column(Numeric(5, 2), nullable=False)
    valuation_amount = Column(Numeric(15, 2), nullable=False)
    market_rate = Column(Numeric(10, 2))
    
    # Lien status
    lien_marked = Column(Boolean, default=False)
    lien_marked_at = Column(DateTime(timezone=True))
    lien_marked_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    application = relationship("LoanApplication", back_populates="ornaments")


class CreditEvaluation(Base):
    """Credit assessment and risk evaluation"""
    __tablename__ = "gold_credit_evaluations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id', ondelete='CASCADE'), nullable=False)
    
    # Evaluation details
    evaluation_type = Column(String(50), nullable=False)
    evaluation_status = Column(String(50), default='pending')
    
    # Credit scores
    cibil_score = Column(Integer)
    cibil_fetched_at = Column(DateTime(timezone=True))
    internal_credit_score = Column(Numeric(5, 2))
    
    # Risk assessment
    risk_category = Column(String(50))
    risk_score = Column(Numeric(5, 2))
    risk_factors = Column(JSONB)
    
    # Borrower assessment
    existing_loans_count = Column(Integer, default=0)
    existing_loans_amount = Column(Numeric(15, 2), default=0)
    repayment_history = Column(String(50))
    bounce_count = Column(Integer, default=0)
    
    # Decisioning
    recommended_amount = Column(Numeric(15, 2))
    recommended_tenure = Column(Integer)
    recommended_interest_rate = Column(Numeric(5, 2))
    recommended_decision = Column(String(50))
    decision_reason = Column(Text)
    
    # AI insights
    ai_recommendation = Column(String(50))
    ai_confidence_score = Column(Numeric(5, 2))
    ai_factors = Column(JSONB)
    
    # Metadata
    evaluated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    evaluated_at = Column(DateTime(timezone=True))
    evaluation_duration = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    application = relationship("LoanApplication", back_populates="credit_evaluation")


class LoanApproval(Base):
    """Multi-level approval workflow"""
    __tablename__ = "gold_loan_approvals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id', ondelete='CASCADE'), nullable=False)
    
    # Approval level
    approval_level = Column(Integer, nullable=False)
    approver_role = Column(String(100), nullable=False)
    approver_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Approval details
    status = Column(String(50), default='pending')
    decision = Column(String(50))
    
    # Approved terms
    approved_amount = Column(Numeric(15, 2))
    approved_tenure = Column(Integer)
    approved_interest_rate = Column(Numeric(5, 2))
    approved_conditions = Column(Text)
    
    # Remarks
    remarks = Column(Text)
    rejection_reason = Column(Text)
    conditions = Column(JSONB)
    
    # Timestamps
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True))
    sla_deadline = Column(DateTime(timezone=True))
    is_overdue = Column(Boolean, default=False)
    
    # Sequence
    sequence_order = Column(Integer, nullable=False)
    is_final_approval = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    application = relationship("LoanApplication", back_populates="approvals")


class LoanAccount(Base):
    """Active loan account"""
    __tablename__ = "gold_loan_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_number = Column(String(100), unique=True, nullable=False)
    
    # References
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('gold_products.id'), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey('branches.id'))
    
    # Loan terms
    principal_amount = Column(Numeric(15, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    interest_type = Column(String(50), nullable=False)
    
    # Charges
    processing_fee = Column(Numeric(15, 2), default=0)
    documentation_charges = Column(Numeric(15, 2), default=0)
    valuation_charges = Column(Numeric(15, 2), default=0)
    other_charges = Column(Numeric(15, 2), default=0)
    total_charges = Column(Numeric(15, 2), default=0)
    
    # Status
    status = Column(String(50), default='active')
    disbursement_status = Column(String(50), default='pending')
    
    # Important dates
    loan_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    closed_date = Column(Date)
    
    # Outstanding
    outstanding_principal = Column(Numeric(15, 2), nullable=False)
    outstanding_interest = Column(Numeric(15, 2), default=0)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    
    # Payments
    total_paid = Column(Numeric(15, 2), default=0)
    last_payment_date = Column(Date)
    next_due_date = Column(Date)
    
    # Overdue tracking
    days_overdue = Column(Integer, default=0)
    overdue_interest = Column(Numeric(15, 2), default=0)
    is_npa = Column(Boolean, default=False)
    npa_date = Column(Date)
    
    # Linked entities
    linked_packets = Column(JSONB)
    linked_ornaments = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Metadata
    metadata = Column(JSONB)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="loan_account")
    disbursements = relationship("Disbursement", back_populates="loan_account")
    charges = relationship("LoanCharge", back_populates="loan_account", cascade="all, delete-orphan")
    documents = relationship("LoanDocument", back_populates="loan_account")
    status_history = relationship("LoanStatusHistory", back_populates="loan_account")
    
    __table_args__ = (
        CheckConstraint('principal_amount > 0', name='check_principal'),
        CheckConstraint('interest_rate >= 0', name='check_interest_rate'),
        CheckConstraint('outstanding_principal >= 0', name='check_outstanding'),
    )


class Disbursement(Base):
    """Loan disbursement record"""
    __tablename__ = "gold_disbursements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disbursement_number = Column(String(100), unique=True, nullable=False)
    
    # References
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id'), nullable=False)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_accounts.id'))
    
    # Disbursement details
    disbursement_amount = Column(Numeric(15, 2), nullable=False)
    disbursement_mode = Column(String(50), nullable=False)
    disbursement_date = Column(Date, nullable=False)
    disbursement_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Payment details
    payment_reference = Column(String(200))
    beneficiary_name = Column(String(200))
    beneficiary_account = Column(String(100))
    beneficiary_ifsc = Column(String(20))
    beneficiary_bank = Column(String(200))
    upi_id = Column(String(100))
    cheque_number = Column(String(50))
    
    # Status
    status = Column(String(50), default='initiated')
    failure_reason = Column(Text)
    
    # Verification
    verified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    verified_at = Column(DateTime(timezone=True))
    verification_notes = Column(Text)
    
    # Transaction details
    utr_number = Column(String(100))
    transaction_id = Column(String(100))
    bank_reference = Column(String(100))
    
    # Processed by
    processed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    processed_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    metadata = Column(JSONB)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="disbursements")
    loan_account = relationship("LoanAccount", back_populates="disbursements")


class LoanDocument(Base):
    """Application and loan documents"""
    __tablename__ = "gold_loan_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id'))
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_accounts.id'))
    
    # Document details
    document_type = Column(String(100), nullable=False)
    document_category = Column(String(50), nullable=False)
    document_name = Column(String(200), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Document metadata
    document_number = Column(String(100))
    is_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime(timezone=True))
    signed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    verified_at = Column(DateTime(timezone=True))
    
    # Status
    status = Column(String(50), default='pending')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    application = relationship("LoanApplication", back_populates="documents")
    loan_account = relationship("LoanAccount", back_populates="documents")


class LoanCharge(Base):
    """Detailed breakdown of loan charges"""
    __tablename__ = "gold_loan_charges"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_accounts.id', ondelete='CASCADE'), nullable=False)
    
    # Charge details
    charge_type = Column(String(100), nullable=False)
    charge_name = Column(String(200), nullable=False)
    charge_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tax details
    tax_type = Column(String(50))
    tax_percentage = Column(Numeric(5, 2))
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment status
    is_paid = Column(Boolean, default=False)
    paid_date = Column(Date)
    payment_mode = Column(String(50))
    payment_reference = Column(String(100))
    
    # Waiver
    is_waived = Column(Boolean, default=False)
    waived_amount = Column(Numeric(15, 2), default=0)
    waived_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    waived_at = Column(DateTime(timezone=True))
    waiver_reason = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="charges")


class LoanStatusHistory(Base):
    """Complete status change audit trail"""
    __tablename__ = "gold_loan_status_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Can track application OR loan account
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id'))
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_accounts.id'))
    
    # Status change
    from_status = Column(String(50))
    to_status = Column(String(50), nullable=False)
    stage = Column(String(50))
    
    # Change details
    changed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(Text)
    notes = Column(Text)
    
    # Metadata
    metadata = Column(JSONB)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="status_history")
    loan_account = relationship("LoanAccount", back_populates="status_history")


class LMSIntegrationLog(Base):
    """Integration log with external LMS systems"""
    __tablename__ = "gold_lms_integration_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    application_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_applications.id'))
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey('gold_loan_accounts.id'))
    
    # Integration details
    integration_type = Column(String(50), nullable=False)
    lms_system = Column(String(50), nullable=False)
    
    # Request/Response
    request_payload = Column(JSONB, nullable=False)
    response_payload = Column(JSONB)
    
    # Status
    status = Column(String(50), default='pending')
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # External references
    lms_loan_id = Column(String(100))
    lms_reference_number = Column(String(100))
    
    # Timestamps
    initiated_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    next_retry_at = Column(DateTime(timezone=True))
