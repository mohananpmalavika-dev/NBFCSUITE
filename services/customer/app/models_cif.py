"""
Comprehensive Customer Information File (CIF) System Models
Implements all 18 stages of enterprise customer onboarding
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Boolean, Date, Numeric, Text, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base


# ============================================================================
# ENHANCED BASE CUSTOMER MODEL (Stages 1-2)
# ============================================================================

class Customer(Base):
    """Central customer entity - the heart of the entire platform"""
    __tablename__ = "customers"

    # Identity
    id = Column(String(36), primary_key=True)
    cif_id = Column(String(15), unique=True, nullable=True, index=True)
    cif_generated_at = Column(DateTime, nullable=True)

    # Basic Info
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)

    # Identity Documents (searchable)
    pan = Column(String(20), unique=True, nullable=True, index=True)
    aadhar = Column(String(20), unique=True, nullable=True, index=True)
    passport = Column(String(50), unique=True, nullable=True)
    voter_id = Column(String(50), unique=True, nullable=True)
    driving_licence = Column(String(50), unique=True, nullable=True)
    gstin = Column(String(20), unique=True, nullable=True)
    cin = Column(String(21), unique=True, nullable=True)

    # Customer Classification
    customer_type = Column(String(50), default="individual")  # individual, company, etc
    customer_lifecycle = Column(String(50), default="lead", index=True)  # lead->prospect->pending_verification->kyc_in_progress->kyc_approved->active->dormant->closed
    kyc_status = Column(String(50), default="pending")
    approval_status = Column(String(50), default="pending", index=True)

    # Organization Hierarchy
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=True)

    # Completion & Risk
    onboarding_completion_percentage = Column(Integer, default=0)
    risk_level = Column(String(50), nullable=True)
    source_prospect_id = Column(String(36), nullable=True)
    preferred_language = Column(String(20), default="en")

    # Audit
    onboarding_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = relationship("BranchOffice", back_populates="customers")
    basic_details = relationship("CustomerBasicDetails", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    addresses = relationship("CustomerAddress", back_populates="customer", cascade="all, delete-orphan")
    contacts = relationship("CustomerContact", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    family_members = relationship("CustomerFamilyMember", back_populates="customer", cascade="all, delete-orphan")
    employment = relationship("CustomerEmployment", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    business_profile = relationship("CustomerBusinessProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    financial_profile = relationship("CustomerFinancialProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    banking_profile = relationship("CustomerBankingProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    compliance = relationship("CustomerCompliance", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    behavior_profile = relationship("CustomerBehaviorProfile", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    documents = relationship("CustomerDocument", back_populates="customer", cascade="all, delete-orphan")
    identity_documents = relationship("CustomerIdentityDocument", back_populates="customer", cascade="all, delete-orphan")
    approvals = relationship("CustomerApproval", back_populates="customer", cascade="all, delete-orphan")
    timeline = relationship("CustomerTimeline", back_populates="customer", cascade="all, delete-orphan")
    relationships = relationship("CustomerRelationship", foreign_keys="CustomerRelationship.primary_customer_id", back_populates="primary_customer")
    related_as = relationship("CustomerRelationship", foreign_keys="CustomerRelationship.related_customer_id", back_populates="related_customer")
    party = relationship("CustomerParty", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    consents = relationship("CustomerConsent", back_populates="customer", cascade="all, delete-orphan")


# ============================================================================
# STAGE 2: PROSPECT
# ============================================================================

class Prospect(Base):
    """Temporary prospect before customer creation"""
    __tablename__ = "prospects"

    id = Column(String(36), primary_key=True)
    
    # Status Journey
    status = Column(String(50), nullable=False, default="lead")  # lead->prospect->pending_verification->customer
    onboarding_stage = Column(Integer, default=1)
    conversion_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Source & Assignment
    source = Column(String(100), nullable=True)
    campaign = Column(String(100), nullable=True)
    branch_id = Column(String(36), nullable=True)
    assigned_rm = Column(String(36), nullable=True)

    # Identity Search Fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, unique=True)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    # Identity Documents
    pan_number = Column(String(20), nullable=True, unique=True)
    aadhar_number = Column(String(20), nullable=True, unique=True)
    passport_number = Column(String(50), nullable=True, unique=True)
    voter_id = Column(String(50), nullable=True, unique=True)
    driving_licence = Column(String(50), nullable=True, unique=True)
    gstin = Column(String(20), nullable=True, unique=True)
    cin = Column(String(21), nullable=True, unique=True)

    # Personal Info
    nationality = Column(String(50), nullable=True)
    resident_status = Column(String(50), nullable=True)
    customer_type = Column(String(50), nullable=True, default="individual")
    occupation = Column(String(100), nullable=True)
    marital_status = Column(String(50), nullable=True)
    education = Column(String(50), nullable=True)
    annual_income = Column(String(50), nullable=True)

    # Company Info (if applicable)
    company_name = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)

    # Profiles (stored as JSON for flexibility)
    contact_profile = Column(JSON, nullable=True)
    family_profile = Column(JSON, nullable=True)
    employment_profile = Column(JSON, nullable=True)
    business_profile = Column(JSON, nullable=True)
    financial_profile = Column(JSON, nullable=True)
    banking_profile = Column(JSON, nullable=True)
    compliance_profile = Column(JSON, nullable=True)
    behavior_profile = Column(JSON, nullable=True)
    relationship_profile = Column(JSON, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# STAGE 3: BASIC DETAILS
# ============================================================================

class CustomerBasicDetails(Base):
    """Stage 3 - Comprehensive personal and business details"""
    __tablename__ = "customer_basic_details"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)
    
    # Type
    customer_type = Column(String(20), nullable=False)  # individual, company

    # ===== Individual Fields =====
    first_name = Column(String(100))
    middle_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    marital_status = Column(String(50))
    occupation = Column(String(100))
    education_level = Column(String(50))
    nationality = Column(String(50))
    resident_status = Column(String(50))

    # ===== Company Fields =====
    company_name = Column(String(255))
    company_registration_date = Column(Date)
    company_type = Column(String(50))
    industry = Column(String(100))
    business_classification = Column(String(100))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="basic_details")


# ============================================================================
# STAGE 4: IDENTITY VERIFICATION
# ============================================================================

class CustomerIdentityDocument(Base):
    """Stage 4 - Identity documents with OCR and versioning"""
    __tablename__ = "customer_identity_documents"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    
    # Document Info
    document_type = Column(String(50), nullable=False)  # pan, aadhar, passport, driving_licence, voter_id, etc
    document_number = Column(String(100))
    document_value = Column(String(255))
    document_url = Column(String(500))
    document_file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(50))

    # OCR Processing
    ocr_extracted_data = Column(JSON)  # Auto-extracted fields from document
    ocr_confidence_score = Column(Numeric(5, 2))

    # Verification
    verification_status = Column(String(50), default="pending")
    verification_timestamp = Column(DateTime, nullable=True)
    verified_by = Column(String(36), nullable=True)
    expiry_date = Column(Date, nullable=True)

    # Versioning
    version = Column(Integer, default=1)
    is_primary = Column(Boolean, default=False)

    # Audit
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="identity_documents")

    __table_args__ = (
        Index('idx_customer_doctype', 'customer_id', 'document_type'),
    )


# ============================================================================
# STAGE 5: ADDRESS
# ============================================================================

class CustomerAddress(Base):
    """Stage 5 - Multiple addresses with proof and geo-coordinates"""
    __tablename__ = "customer_addresses"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    
    # Address Type
    address_type = Column(String(50), nullable=False)  # permanent, communication, office, branch, registered

    # Address Details
    street_line1 = Column(String(255))
    street_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))

    # Geo Location
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)

    # Proof
    address_proof_type = Column(String(50))
    address_proof_url = Column(String(500))
    address_proof_verification_status = Column(String(50), default="pending")

    # Metadata
    is_primary = Column(Boolean, default=False)
    years_at_residence = Column(Integer, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="addresses")

    __table_args__ = (
        Index('idx_customer_address_type', 'customer_id', 'address_type'),
    )


# ============================================================================
# STAGE 6: CONTACTS
# ============================================================================

class CustomerContact(Base):
    """Stage 6 - Contact information and preferences"""
    __tablename__ = "customer_contacts"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # Contact Methods
    mobile_primary = Column(String(20))
    mobile_alternate = Column(String(20), nullable=True)
    email_primary = Column(String(255))
    email_alternate = Column(String(255), nullable=True)
    whatsapp_number = Column(String(20), nullable=True)

    # Emergency Contact
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_mobile = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)

    # Preferences
    preferred_contact_method = Column(String(50))
    preferred_language = Column(String(20), default="en")
    communication_preference = Column(JSON)  # {email: true, sms: true, whatsapp: true, push: false, call: false}

    # Do Not Contact
    do_not_call = Column(Boolean, default=False)
    do_not_email = Column(Boolean, default=False)
    do_not_sms = Column(Boolean, default=False)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="contacts")


# ============================================================================
# STAGE 7: FAMILY
# ============================================================================

class CustomerFamilyMember(Base):
    """Stage 7 - Family member information"""
    __tablename__ = "customer_family_members"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)

    # Relationship
    relationship = Column(String(50), nullable=False)  # father, mother, spouse, child, sibling, dependent, nominee, guardian

    # Personal Info
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    occupation = Column(String(100), nullable=True)

    # Contact
    mobile = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)

    # Status
    is_dependent = Column(Boolean, default=False)
    is_nominee = Column(Boolean, default=False)
    is_guardian = Column(Boolean, default=False)

    # Identity
    pan_number = Column(String(20), nullable=True)
    aadhar_number = Column(String(20), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="family_members")


# ============================================================================
# STAGE 8: EMPLOYMENT
# ============================================================================

class CustomerEmployment(Base):
    """Stage 8 - Employment details and income verification"""
    __tablename__ = "customer_employment"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # Employment Type
    employment_type = Column(String(50))  # employed, self-employed, retired, student, unemployed, housewife

    # Employer Info
    employer_name = Column(String(255), nullable=True)
    employer_type = Column(String(50), nullable=True)
    designation = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)

    # Salary
    current_salary = Column(Numeric(15, 2), nullable=True)
    salary_frequency = Column(String(20))  # monthly, quarterly, annually
    salary_account_number = Column(String(30), nullable=True)
    salary_account_ifsc = Column(String(11), nullable=True)
    salary_account_bank = Column(String(100), nullable=True)

    # Experience
    years_in_current_job = Column(Numeric(5, 2), nullable=True)
    total_years_experience = Column(Numeric(5, 2), nullable=True)
    date_of_joining = Column(Date, nullable=True)

    # Employment Details
    employment_contract_type = Column(String(50), nullable=True)  # permanent, contract, temporary

    # Verification
    income_verification_status = Column(String(50), default="pending")
    income_verification_document_url = Column(String(500), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="employment")


# ============================================================================
# STAGE 9: BUSINESS PROFILE
# ============================================================================

class CustomerBusinessProfile(Base):
    """Stage 9 - Business details for business customers"""
    __tablename__ = "customer_business_profile"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # Business Type
    business_type = Column(String(50))  # sole_proprietorship, partnership, llp, company, trust, society, huf

    # Registration
    business_name = Column(String(255))
    business_registration_number = Column(String(100))
    gstin = Column(String(20), nullable=True)
    pan_number = Column(String(20), nullable=True)
    cin_number = Column(String(21), nullable=True)

    # Business Details
    business_start_date = Column(Date, nullable=True)
    nature_of_business = Column(String(255))
    business_category = Column(String(100))
    sub_category = Column(String(100), nullable=True)

    # Structure
    number_of_partners = Column(Integer, nullable=True)
    number_of_employees = Column(Integer, nullable=True)

    # Financials
    annual_turnover = Column(Numeric(15, 2), nullable=True)
    average_monthly_turnover = Column(Numeric(15, 2), nullable=True)
    cash_flow_pattern = Column(String(50), nullable=True)  # seasonal, steady, variable

    # Bank Accounts
    business_bank_accounts = Column(JSON)  # [{account_number, ifsc, bank_name, account_type}]

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="business_profile")


# ============================================================================
# STAGE 10: FINANCIAL PROFILE
# ============================================================================

class CustomerFinancialProfile(Base):
    """Stage 10 - Comprehensive financial information"""
    __tablename__ = "customer_financial_profile"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # Income
    annual_income = Column(Numeric(15, 2), nullable=True)
    monthly_income = Column(Numeric(15, 2), nullable=True)

    # Expenses
    monthly_expenses = Column(Numeric(15, 2), nullable=True)
    savings_per_month = Column(Numeric(15, 2), nullable=True)

    # Assets & Liabilities
    total_assets = Column(Numeric(15, 2), nullable=True)
    total_liabilities = Column(Numeric(15, 2), nullable=True)
    net_worth = Column(Numeric(15, 2), nullable=True)
    liquid_assets = Column(Numeric(15, 2), nullable=True)
    fixed_assets = Column(Numeric(15, 2), nullable=True)

    # Portfolios
    investments_portfolio = Column(JSON)  # [{type, value, instrument}]
    existing_loans = Column(JSON)  # [{lender, amount, emi, status}]
    credit_cards = Column(JSON)  # [{bank, limit, outstanding}]
    insurance_policies = Column(JSON)  # [{type, provider, sum_assured, premium}]

    # Credit
    credit_score = Column(Integer, nullable=True)
    credit_rating = Column(String(20), nullable=True)

    # Verification
    bureau_check_status = Column(String(50), default="pending")
    bureau_check_date = Column(DateTime, nullable=True)

    # Risk
    risk_rating = Column(String(20), nullable=True)
    financial_stress_indicator = Column(String(50), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="financial_profile")


# ============================================================================
# STAGE 11: BANKING PROFILE
# ============================================================================

class CustomerBankingProfile(Base):
    """Stage 11 - Banking relationship details"""
    __tablename__ = "customer_banking_profile"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # Primary Bank Account
    primary_bank_account_number = Column(String(30), nullable=True)
    primary_bank_ifsc = Column(String(11), nullable=True)
    primary_bank_name = Column(String(100), nullable=True)
    primary_account_type = Column(String(50), nullable=True)

    # All Accounts
    accounts = Column(JSON)  # [{account_number, ifsc, bank_name, account_type, is_salary_account}]

    # Relationship
    existing_relationship = Column(String(50), nullable=True)
    relationship_since = Column(Date, nullable=True)

    # Balance
    average_balance = Column(Numeric(15, 2), nullable=True)
    last_6month_avg_balance = Column(Numeric(15, 2), nullable=True)

    # Transactions
    monthly_debit_transactions = Column(Integer, nullable=True)
    monthly_credit_transactions = Column(Integer, nullable=True)
    average_transaction_value = Column(Numeric(15, 2), nullable=True)

    # Digital
    upi_handles = Column(JSON, nullable=True)  # array of upi ids
    net_banking_active = Column(Boolean, default=False)
    mobile_banking_active = Column(Boolean, default=False)

    # Standing Instructions
    standing_instructions = Column(JSON, nullable=True)
    last_bank_reconciliation_date = Column(DateTime, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="banking_profile")


# ============================================================================
# STAGE 12: COMPLIANCE
# ============================================================================

class CustomerCompliance(Base):
    """Stage 12 - Compliance checks and verifications"""
    __tablename__ = "customer_compliance"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # PAN Verification
    pan_verification_status = Column(String(50), default="pending")
    pan_verified_at = Column(DateTime, nullable=True)
    pan_verification_source = Column(String(100), nullable=True)

    # Aadhar Verification
    aadhar_verification_status = Column(String(50), default="pending")
    aadhar_verified_at = Column(DateTime, nullable=True)
    aadhar_verification_type = Column(String(50), nullable=True)  # online_otp, in_person_otp, video_kyc

    # CKYC
    ckyc_status = Column(String(50), default="pending")
    ckyc_reference_number = Column(String(100), nullable=True)
    ckyc_completed_at = Column(DateTime, nullable=True)

    # Video KYC
    video_kyc_status = Column(String(50), default="pending")
    video_kyc_url = Column(String(500), nullable=True)
    video_kyc_completed_at = Column(DateTime, nullable=True)

    # Compliance Checks
    aml_check_status = Column(String(50), default="pending")
    aml_check_result = Column(String(20), nullable=True)  # pass, fail
    aml_checked_at = Column(DateTime, nullable=True)

    pep_check_status = Column(String(50), default="pending")
    pep_check_result = Column(String(20), nullable=True)
    pep_checked_at = Column(DateTime, nullable=True)

    sanction_list_screening_status = Column(String(50), default="pending")
    sanction_list_result = Column(String(20), nullable=True)
    sanction_checked_at = Column(DateTime, nullable=True)

    negative_media_screening_status = Column(String(50), default="pending")
    negative_media_result = Column(String(20), nullable=True)
    negative_media_checked_at = Column(DateTime, nullable=True)

    fraud_check_status = Column(String(50), default="pending")
    fraud_check_result = Column(String(20), nullable=True)
    fraud_checked_at = Column(DateTime, nullable=True)

    watchlist_check_status = Column(String(50), default="pending")
    watchlist_result = Column(String(20), nullable=True)
    watchlist_checked_at = Column(DateTime, nullable=True)

    # Geo Risk
    geo_risk_assessment = Column(String(50), nullable=True)
    geo_risk_score = Column(Integer, nullable=True)

    # Documents Status
    kyc_documents_status = Column(JSON, nullable=True)
    compliance_notes = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="compliance")


# ============================================================================
# STAGE 13: BEHAVIOR PROFILE & FINDNA
# ============================================================================

class CustomerBehaviorProfile(Base):
    """Stage 13 - Behavioral profile and FinDNA"""
    __tablename__ = "customer_behavior_profile"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # Financial Behavior
    risk_appetite = Column(String(50), nullable=True)  # conservative, moderate, aggressive
    spending_pattern = Column(String(50), nullable=True)  # high, medium, low, erratic
    saving_pattern = Column(String(50), nullable=True)  # consistent, occasional, none
    decision_style = Column(String(50), nullable=True)  # impulsive, analytical, cautious

    # Scores
    financial_discipline_score = Column(Integer, nullable=True)  # 0-100
    impulse_buying_tendency = Column(String(50), nullable=True)  # high, medium, low
    income_stability_score = Column(Integer, nullable=True)  # 0-100
    income_trend = Column(String(50), nullable=True)  # increasing, stable, decreasing

    # Risk Indicators
    stress_indicators = Column(JSON, nullable=True)  # array of detected stress signals

    # Composite Scores
    behavior_score = Column(Integer, nullable=True)  # 0-100
    trust_score = Column(Integer, nullable=True)  # 0-100
    payment_discipline_score = Column(Integer, nullable=True)  # 0-100
    churn_risk_score = Column(Integer, nullable=True)  # 0-100

    # FinDNA - Competitive Advantage
    financial_dna = Column(String(100), nullable=True)  # e.g. "Conservative-Stable-High-Trust"

    # Affinity
    product_affinity = Column(JSON, nullable=True)  # predicted interest in products

    # Digital
    digital_savviness = Column(Integer, nullable=True)  # 0-100
    communication_preference_index = Column(String(50), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="behavior_profile")


# ============================================================================
# STAGE 14: RELATIONSHIPS (GRAPH MODEL)
# ============================================================================

class CustomerRelationship(Base):
    """Stage 14 - Relationship mapping for graph-based customer view"""
    __tablename__ = "customer_relationships"

    id = Column(String(36), primary_key=True)
    primary_customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    related_customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True)

    # Relationship
    relationship_type = Column(String(50), nullable=False)  # joint_holder, guarantor, family, business, introducer, rm, employee, agent, dealer, channel_partner
    relationship_strength = Column(String(50), nullable=True)  # strong, medium, weak
    primary_contact = Column(Boolean, default=False)

    # Shared
    shared_products = Column(JSON, nullable=True)
    shared_accounts = Column(JSON, nullable=True)
    relationship_since = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    primary_customer = relationship("Customer", foreign_keys=[primary_customer_id], back_populates="relationships")
    related_customer = relationship("Customer", foreign_keys=[related_customer_id], back_populates="related_as")

    __table_args__ = (
        Index('idx_customer_relationships', 'primary_customer_id', 'relationship_type'),
    )


# ============================================================================
# STAGE 15: DOCUMENT VAULT
# ============================================================================

class CustomerDocument(Base):
    """Stage 15 - Versioned document storage"""
    __tablename__ = "customer_documents"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)

    # Document Info
    document_category = Column(String(50), nullable=False)  # identity, address, income, business, kyc_video, agreement, other
    document_type = Column(String(100), nullable=True)
    document_description = Column(String(255), nullable=True)
    document_name = Column(String(255), nullable=False)

    # Storage
    document_url = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(50), nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA256

    # Upload Info
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(36), nullable=True)

    # Versioning
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    expiry_date = Column(Date, nullable=True)

    # Status
    document_status = Column(String(50), default="active")
    storage_location = Column(String(100))  # local, s3, azure_blob, etc

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="documents")

    __table_args__ = (
        Index('idx_customer_doc_category', 'customer_id', 'document_category'),
        Index('idx_doc_expiry', 'expiry_date'),
    )


# ============================================================================
# STAGE 16: APPROVAL WORKFLOW
# ============================================================================

class CustomerApproval(Base):
    """Stage 16 - Multi-level approval workflow"""
    __tablename__ = "customer_approvals"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)

    # Workflow
    workflow_stage = Column(Integer, nullable=True)
    approval_status = Column(String(50), default="pending")  # pending, approved, rejected, escalated

    # Initiation
    initiated_at = Column(DateTime, default=datetime.utcnow)
    initiated_by = Column(String(36), nullable=True)

    # Checker Level
    checker_id = Column(String(36), nullable=True)
    checker_approved_at = Column(DateTime, nullable=True)
    checker_comments = Column(Text, nullable=True)

    # Manager Level
    manager_id = Column(String(36), nullable=True)
    manager_approved_at = Column(DateTime, nullable=True)
    manager_comments = Column(Text, nullable=True)

    # Compliance Level
    compliance_officer_id = Column(String(36), nullable=True)
    compliance_approved_at = Column(DateTime, nullable=True)
    compliance_comments = Column(Text, nullable=True)

    # Final Approval
    final_approver_id = Column(String(36), nullable=True)
    final_approval_at = Column(DateTime, nullable=True)
    final_approval_comments = Column(Text, nullable=True)

    # Rejection/Escalation
    rejection_reason = Column(Text, nullable=True)
    escalation_reason = Column(Text, nullable=True)
    escalated_to = Column(String(36), nullable=True)

    # CIF Generation
    cif_generated_on = Column(DateTime, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="approvals")

    __table_args__ = (
        Index('idx_approval_status', 'customer_id', 'approval_status'),
    )


# ============================================================================
# STAGE 17-18: CUSTOMER 360 & TIMELINE
# ============================================================================

class CustomerTimeline(Base):
    """Stage 17-18 - Chronological audit trail of all customer interactions"""
    __tablename__ = "customer_timeline"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)

    # Event
    event_type = Column(String(100), nullable=False)  # kyc_update, product_opening, approval, branch_visit, call, complaint, transaction, etc
    event_description = Column(Text, nullable=True)
    event_timestamp = Column(DateTime, default=datetime.utcnow)

    # Who triggered it
    triggered_by = Column(String(36), nullable=True)

    # Metadata
    event_metadata = Column(JSON, nullable=True)
    document_reference_id = Column(String(36), nullable=True)
    related_product_id = Column(String(36), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="timeline")

    __table_args__ = (
        Index('idx_customer_timeline', 'customer_id', 'event_timestamp'),
    )


# ============================================================================
# ENTERPRISE ENHANCEMENTS
# ============================================================================

class CustomerHousehold(Base):
    """Family/Business householding for relationship-based servicing"""
    __tablename__ = "customer_households"

    id = Column(String(36), primary_key=True)
    household_name = Column(String(255))
    primary_customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    household_type = Column(String(50))  # family, business, joint_venture
    primary_contact_name = Column(String(100), nullable=True)
    total_relationship_value = Column(Numeric(15, 2), nullable=True)
    household_income = Column(Numeric(15, 2), nullable=True)
    household_status = Column(String(50))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('household_type', 'primary_customer_id', name='uk_household_primary'),
    )


class CustomerHouseholdMember(Base):
    """Members of a household"""
    __tablename__ = "customer_household_members"

    id = Column(String(36), primary_key=True)
    household_id = Column(String(36), ForeignKey("customer_households.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    member_role = Column(String(50), nullable=True)
    member_status = Column(String(50), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('household_id', 'customer_id', name='uk_household_member'),
    )


class CustomerParty(Base):
    """Party Model - support for various entity types"""
    __tablename__ = "customer_parties"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), unique=True, nullable=False)

    # Party Type
    party_type = Column(String(50), nullable=False)  # individual, sole_proprietor, partnership, llp, company, trust, society, government_entity, ngo
    party_name = Column(String(255), nullable=False)
    party_code = Column(String(50), unique=True, nullable=True)

    # Registration
    registration_number = Column(String(100), nullable=True)
    registration_authority = Column(String(100), nullable=True)
    party_status = Column(String(50), default="active")

    # Tax
    tax_id = Column(String(50), nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="party")


class CustomerConsent(Base):
    """Consent Management - Track all customer consents with versioning"""
    __tablename__ = "customer_consents"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)

    # Consent
    consent_type = Column(String(50), nullable=False)  # marketing, data_sharing, account_aggregation, digital_communications, credit_bureau
    consent_status = Column(String(20))  # given, withdrawn
    consent_date = Column(DateTime, nullable=False)
    consent_version = Column(String(20), nullable=True)
    consent_document_url = Column(String(500), nullable=True)
    consent_expiry_date = Column(Date, nullable=True)
    withdrawn_date = Column(DateTime, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="consents")

    __table_args__ = (
        Index('idx_customer_consent', 'customer_id', 'consent_type'),
    )


class OnboardingWorkflow(Base):
    """Configurable onboarding workflows for different products"""
    __tablename__ = "onboarding_workflows"

    id = Column(String(36), primary_key=True)
    workflow_name = Column(String(255), nullable=False)
    product_type = Column(String(100))  # savings_account, deposits, gold_loan, forex, corporate_customer
    customer_type = Column(String(50), nullable=True)
    workflow_stages = Column(JSON, nullable=True)
    required_documents = Column(JSON, nullable=True)
    required_compliance_checks = Column(JSON, nullable=True)
    approval_levels = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CIFSequence(Base):
    """CIF ID sequence generator"""
    __tablename__ = "cif_sequence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_cif_number = Column(Integer, default=1000000)
    created_at = Column(DateTime, default=datetime.utcnow)
