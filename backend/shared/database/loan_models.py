"""
Loan Management Models
Complete loan lifecycle from products to repayments
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, 
    DateTime, ForeignKey, ARRAY, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class LoanProduct(Base):
    """Loan Product Configuration"""
    __tablename__ = "loan_products"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Product Identification
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    product_type = Column(String(50), nullable=False, index=True)
    # personal, business, gold, vehicle, home, education, agriculture
    loan_category = Column(String(50), nullable=False)  # secured, unsecured
    
    # Interest Configuration
    interest_rate_type = Column(String(50), nullable=False)  # flat, reducing, compound
    min_interest_rate = Column(Numeric(5, 2), nullable=False)
    max_interest_rate = Column(Numeric(5, 2), nullable=False)
    default_interest_rate = Column(Numeric(5, 2), nullable=False)
    
    # Loan Amount
    min_loan_amount = Column(Numeric(15, 2), nullable=False)
    max_loan_amount = Column(Numeric(15, 2), nullable=False)
    
    # Tenure
    min_tenure_months = Column(Integer, nullable=False)
    max_tenure_months = Column(Integer, nullable=False)
    allowed_tenures = Column(ARRAY(Integer))  # [6, 12, 18, 24, 36, 48, 60]
    
    # Fees & Charges
    processing_fee_type = Column(String(50), nullable=False)  # fixed, percentage
    processing_fee_value = Column(Numeric(15, 2), nullable=False)
    documentation_charges = Column(Numeric(15, 2))
    insurance_applicable = Column(Boolean, default=False)
    insurance_percentage = Column(Numeric(5, 2))
    
    # Penal Interest
    penal_interest_rate = Column(Numeric(5, 2), nullable=False)
    grace_period_days = Column(Integer, default=3)
    
    # Eligibility Criteria
    min_age = Column(Integer, default=21)
    max_age = Column(Integer, default=65)
    min_monthly_income = Column(Numeric(15, 2))
    min_cibil_score = Column(Integer, default=650)
    employment_types = Column(ARRAY(String))  # ['salaried', 'self_employed', 'business']
    
    # Documentation
    required_documents = Column(ARRAY(Integer))  # Document type IDs
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    # Description
    description = Column(Text)
    features = Column(ARRAY(String))
    terms_and_conditions = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    applications = relationship("LoanApplication", back_populates="loan_product")


class LoanApplication(Base):
    """Loan Application"""
    __tablename__ = "loan_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    application_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer & Product
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    loan_product_id = Column(Integer, ForeignKey("loan_products.id"), nullable=False)
    
    # Loan Details
    requested_amount = Column(Numeric(15, 2), nullable=False)
    approved_amount = Column(Numeric(15, 2))
    tenure_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    
    # EMI Calculation
    emi_amount = Column(Numeric(15, 2))
    total_interest = Column(Numeric(15, 2))
    total_repayment = Column(Numeric(15, 2))
    
    # Purpose
    loan_purpose_id = Column(Integer, ForeignKey("loan_purposes.id"))
    purpose_description = Column(Text)
    
    # Status
    status = Column(String(50), nullable=False, default="draft", index=True)
    # draft, submitted, under_review, credit_assessment, 
    # pending_approval, approved, rejected, disbursed, cancelled
    sub_status = Column(String(100))
    status_reason = Column(Text)
    
    # Workflow
    current_approver_id = Column(Integer)
    approval_level = Column(Integer, default=0)
    
    # Dates
    application_date = Column(Date, nullable=False, index=True)
    submission_date = Column(Date)
    approval_date = Column(Date)
    rejection_date = Column(Date)
    disbursement_date = Column(Date)
    
    # Credit Assessment
    credit_score = Column(Integer)
    debt_to_income_ratio = Column(Numeric(5, 2))
    monthly_income = Column(Numeric(15, 2))
    monthly_obligations = Column(Numeric(15, 2))
    risk_rating = Column(String(50))  # low, medium, high, very_high
    
    # Documents
    documents_verified = Column(Boolean, default=False)
    kyc_verified = Column(Boolean, default=False)
    
    # Fees
    processing_fee = Column(Numeric(15, 2))
    documentation_charges = Column(Numeric(15, 2))
    insurance_amount = Column(Numeric(15, 2))
    other_charges = Column(Numeric(15, 2))
    total_deductions = Column(Numeric(15, 2))
    net_disbursement = Column(Numeric(15, 2))
    
    # Disbursement Details
    disbursement_bank_account_id = Column(Integer, ForeignKey("customer_bank_accounts.id"))
    disbursement_mode = Column(String(50))  # neft, rtgs, imps, cheque
    disbursement_reference = Column(String(100))
    
    # Notes
    applicant_remarks = Column(Text)
    internal_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="loan_applications")
    loan_product = relationship("LoanProduct", back_populates="applications")
    co_applicants = relationship("LoanApplicationCoApplicant", back_populates="application")
    documents = relationship("LoanApplicationDocument", back_populates="application")
    workflows = relationship("LoanApprovalWorkflow", back_populates="application")
    loan_account = relationship("LoanAccount", back_populates="application", uselist=False)


class LoanApplicationCoApplicant(Base):
    """Loan Application Co-Applicants/Guarantors"""
    __tablename__ = "loan_application_co_applicants"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    family_member_id = Column(UUID(as_uuid=True), ForeignKey("customer_family.id"), nullable=False)  # UUID because CustomerFamily uses BaseModel
    
    co_applicant_type = Column(String(50), nullable=False)  # co_applicant, guarantor
    is_primary = Column(Boolean, default=False)
    family_relationship = Column(String(100))
    monthly_income = Column(Numeric(15, 2))
    occupation = Column(String(200))
    
    consent_given = Column(Boolean, default=False)
    consent_date = Column(Date)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="co_applicants")


class LoanApplicationDocument(Base):
    """Loan Application Documents"""
    __tablename__ = "loan_application_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), nullable=False)
    customer_document_id = Column(Integer, ForeignKey("customer_documents.id"))
    
    document_number = Column(String(100))
    file_path = Column(String(500))
    file_url = Column(String(500))
    
    status = Column(String(50), default="pending")  # pending, verified, rejected
    verified_by = Column(Integer)
    verified_at = Column(DateTime(timezone=True))
    remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="documents")


class LoanApprovalWorkflow(Base):
    """Loan Approval Workflow"""
    __tablename__ = "loan_approval_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)
    
    approval_level = Column(Integer, nullable=False)
    approver_role = Column(String(100), nullable=False)  # credit_officer, manager, senior_manager
    approver_id = Column(Integer, index=True)
    
    status = Column(String(50), nullable=False, default="pending", index=True)
    # pending, approved, rejected, returned, escalated
    
    action_date = Column(DateTime(timezone=True))
    decision = Column(String(50))  # approve, reject, return, request_more_info
    comments = Column(Text)
    conditions = Column(ARRAY(String))  # Approval conditions
    
    # Limits
    max_approval_amount = Column(Numeric(15, 2))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    application = relationship("LoanApplication", back_populates="workflows")


class LoanAccount(Base):
    """Active Loan Account"""
    __tablename__ = "loan_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    loan_account_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Application Link
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    loan_product_id = Column(Integer, ForeignKey("loan_products.id"), nullable=False)
    
    # Loan Details
    sanctioned_amount = Column(Numeric(15, 2), nullable=False)
    disbursed_amount = Column(Numeric(15, 2), nullable=False)
    outstanding_principal = Column(Numeric(15, 2), nullable=False)
    outstanding_interest = Column(Numeric(15, 2), nullable=False)
    outstanding_charges = Column(Numeric(15, 2), default=0)
    total_outstanding = Column(Numeric(15, 2), nullable=False)
    
    # Terms
    tenure_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    emi_amount = Column(Numeric(15, 2), nullable=False)
    emi_day = Column(Integer, nullable=False)  # Day of month for EMI
    
    # Dates
    disbursement_date = Column(Date, nullable=False)
    first_emi_date = Column(Date, nullable=False)
    last_emi_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    closure_date = Column(Date)
    
    # Status
    status = Column(String(50), nullable=False, default="active", index=True)
    # active, overdue, npa, closed, settled, written_off
    overdue_days = Column(Integer, default=0, index=True)
    dpd = Column(Integer, default=0)  # Days Past Due
    
    # Collections
    last_payment_date = Column(Date)
    last_payment_amount = Column(Numeric(15, 2))
    next_due_date = Column(Date)
    next_due_amount = Column(Numeric(15, 2))
    
    # NPA Classification
    npa_status = Column(String(50))  # standard, sub_standard, doubtful, loss
    npa_date = Column(Date)
    
    # Prepayment
    prepayment_allowed = Column(Boolean, default=True)
    prepayment_charges_percentage = Column(Numeric(5, 2))
    
    # Penal Interest
    penal_interest_outstanding = Column(Numeric(15, 2), default=0)
    
    # Accounting
    interest_accrued = Column(Numeric(15, 2), default=0)
    interest_received = Column(Numeric(15, 2), default=0)
    principal_received = Column(Numeric(15, 2), default=0)
    
    # Notes
    internal_notes = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    application = relationship("LoanApplication", back_populates="loan_account")
    customer = relationship("Customer", back_populates="loan_accounts")
    loan_product = relationship("LoanProduct")
    emi_schedules = relationship("LoanEMISchedule", back_populates="loan_account")
    repayments = relationship("LoanRepayment", back_populates="loan_account")


class LoanEMISchedule(Base):
    """EMI Schedule for Loan"""
    __tablename__ = "loan_emi_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    # EMI Details
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    
    # Amount Breakdown
    emi_amount = Column(Numeric(15, 2), nullable=False)
    principal_component = Column(Numeric(15, 2), nullable=False)
    interest_component = Column(Numeric(15, 2), nullable=False)
    
    # Balance
    opening_principal = Column(Numeric(15, 2), nullable=False)
    closing_principal = Column(Numeric(15, 2), nullable=False)
    
    # Payment Status
    status = Column(String(50), nullable=False, default="pending", index=True)
    # pending, paid, partially_paid, overdue, waived
    
    paid_amount = Column(Numeric(15, 2), default=0)
    paid_principal = Column(Numeric(15, 2), default=0)
    paid_interest = Column(Numeric(15, 2), default=0)
    payment_date = Column(Date)
    
    # Overdue
    overdue_days = Column(Integer, default=0, index=True)
    penal_interest = Column(Numeric(15, 2), default=0)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="emi_schedules")
    
    __table_args__ = (
        Index('idx_emi_loan_installment', 'loan_account_id', 'installment_number', unique=True),
    )


class LoanRepayment(Base):
    """Loan Repayment/Payment"""
    __tablename__ = "loan_repayments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Payment Details
    payment_date = Column(Date, nullable=False, index=True)
    payment_amount = Column(Numeric(15, 2), nullable=False)
    payment_mode = Column(String(50), nullable=False)  # cash, cheque, neft, rtgs, upi
    
    # Allocation
    allocated_to_principal = Column(Numeric(15, 2), nullable=False)
    allocated_to_interest = Column(Numeric(15, 2), nullable=False)
    allocated_to_penal_interest = Column(Numeric(15, 2), default=0)
    allocated_to_charges = Column(Numeric(15, 2), default=0)
    
    # Reference
    reference_number = Column(String(100))
    bank_name = Column(String(200))
    transaction_date = Column(Date)
    
    # Status
    status = Column(String(50), nullable=False, default="success")
    # success, pending, failed, reversed
    reversal_reason = Column(Text)
    reversed_at = Column(DateTime(timezone=True))
    reversed_by = Column(Integer)
    
    # Receipt
    receipt_generated = Column(Boolean, default=False)
    receipt_url = Column(String(500))
    
    # EMI Links
    emi_schedule_ids = Column(ARRAY(Integer))  # Which EMIs this payment covers
    
    # Notes
    remarks = Column(Text)
    collected_by = Column(Integer)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer)
    
    # Relationships
    loan_account = relationship("LoanAccount", back_populates="repayments")


# Create indexes
Index('idx_loan_products_tenant', LoanProduct.tenant_id)
Index('idx_loan_products_type', LoanProduct.product_type)
Index('idx_applications_tenant', LoanApplication.tenant_id)
Index('idx_applications_customer', LoanApplication.customer_id)
Index('idx_loan_accounts_tenant', LoanAccount.tenant_id)
Index('idx_loan_accounts_customer', LoanAccount.customer_id)
