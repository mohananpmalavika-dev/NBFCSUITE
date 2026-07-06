"""
Integration Models
Database models for third-party integration services

Includes:
- Bureau Reports (CIBIL, Equifax, Experian, CRIF)
- Bureau Consents
- Bank Statement Analyses
- OCR Results
- eKYC Records
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, JSON, DECIMAL, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class BureauReport(Base):
    """Bureau Credit Reports"""
    __tablename__ = "bureau_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    
    # Bureau Information
    bureau_name = Column(String(50), nullable=False, index=True)  # CIBIL, Equifax, Experian, CRIF
    report_type = Column(String(50))  # Consumer, Commercial
    
    # Score Information
    score = Column(Integer)  # Credit score (300-900)
    score_date = Column(Date)
    
    # Report Data
    report_date = Column(Date, nullable=False, index=True)
    report_json = Column(JSON)  # Complete parsed report
    report_pdf_url = Column(String(500))  # PDF report URL
    
    # Metadata
    consent_id = Column(Integer, ForeignKey('bureau_consents.id'))
    pulled_by = Column(Integer)  # User ID who pulled the report
    pulled_at = Column(DateTime, default=datetime.utcnow)
    
    # Analysis
    risk_factors = Column(JSON)  # Array of identified risk factors
    positive_factors = Column(JSON)  # Array of positive factors
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="bureau_reports")
    consent = relationship("BureauConsent", back_populates="reports")


class BureauConsent(Base):
    """Bureau Consent Management"""
    __tablename__ = "bureau_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    
    # Consent Details
    consent_type = Column(String(50))  # credit_report, monitoring, etc.
    consent_given = Column(Boolean, default=False)
    consent_date = Column(Date)
    consent_document_url = Column(String(500))  # Signed consent document
    
    # Validity
    valid_until = Column(Date)
    revoked = Column(Boolean, default=False)
    revoked_date = Column(Date)
    
    # Metadata
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="bureau_consents")
    reports = relationship("BureauReport", back_populates="consent")


class BankStatementAnalysis(Base):
    """Bank Statement Analysis Results"""
    __tablename__ = "bank_statement_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey('loan_applications.id'), index=True)
    
    # Bank Information
    bank_name = Column(String(200))
    account_number = Column(String(50))
    account_type = Column(String(50))  # Savings, Current, Salary
    ifsc_code = Column(String(20))
    
    # Statement Period
    statement_period_from = Column(Date)
    statement_period_to = Column(Date)
    number_of_months = Column(Integer)
    
    # Income Analysis
    avg_monthly_income = Column(DECIMAL(15, 2))
    total_credits = Column(DECIMAL(15, 2))
    salary_credits_count = Column(Integer)
    salary_credits_amount = Column(DECIMAL(15, 2))
    irregular_income = Column(Boolean, default=False)
    income_stability_score = Column(Integer)  # 0-100
    
    # Expense Analysis
    avg_monthly_expenses = Column(DECIMAL(15, 2))
    total_debits = Column(DECIMAL(15, 2))
    emi_obligations = Column(DECIMAL(15, 2))
    loan_payments = Column(DECIMAL(15, 2))
    credit_card_payments = Column(DECIMAL(15, 2))
    
    # Banking Behavior
    avg_balance = Column(DECIMAL(15, 2))
    min_balance = Column(DECIMAL(15, 2))
    max_balance = Column(DECIMAL(15, 2))
    bounced_transactions = Column(Integer, default=0)
    bounced_amount = Column(DECIMAL(15, 2))
    overdraft_instances = Column(Integer, default=0)
    
    # Cash Flow
    net_monthly_surplus = Column(DECIMAL(15, 2))
    disposable_income = Column(DECIMAL(15, 2))
    cash_deposit_frequency = Column(Integer)
    cash_deposit_amount = Column(DECIMAL(15, 2))
    
    # Risk Analysis
    risk_score = Column(Integer)  # 0-100
    risk_level = Column(String(50))  # Low, Medium, High
    red_flags = Column(JSON)  # Array of risk indicators
    
    # Detailed Analysis
    analysis_json = Column(JSON)  # Complete analysis data
    transaction_categories = Column(JSON)  # Categorized transactions
    
    # Source
    statement_file_url = Column(String(500))
    analyzed_by = Column(String(50))  # Perfios, FinBox, In-house
    analyzed_at = Column(DateTime)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="bank_analyses")
    application = relationship("LoanApplication", back_populates="bank_analyses")


class DocumentOCRResult(Base):
    """OCR Processing Results"""
    __tablename__ = "document_ocr_results"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), index=True)
    document_id = Column(Integer, ForeignKey('customer_documents.id'), nullable=False, index=True)
    
    # Document Information
    document_type = Column(String(100))  # Aadhaar, PAN, DL, Passport, etc.
    
    # OCR Results
    ocr_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    ocr_provider = Column(String(50))  # AWS Textract, Google Vision, etc.
    
    # Extracted Data
    extracted_data = Column(JSON)  # Complete extracted data
    
    # Common Fields
    full_name = Column(String(300))
    date_of_birth = Column(Date)
    document_number = Column(String(100))
    address = Column(Text)
    
    # Aadhaar Specific
    aadhaar_number = Column(String(20))
    gender = Column(String(20))
    
    # PAN Specific
    pan_number = Column(String(20))
    father_name = Column(String(300))
    
    # Passport/DL Specific
    issue_date = Column(Date)
    expiry_date = Column(Date)
    
    # Photo
    photo_url = Column(String(500))
    face_extracted = Column(Boolean, default=False)
    
    # Confidence & Verification
    confidence_score = Column(DECIMAL(5, 2))  # 0-100
    auto_verified = Column(Boolean, default=False)
    verification_status = Column(String(50))  # verified, failed, manual_review
    
    # Cross-Verification
    matches_customer_data = Column(Boolean)
    mismatch_fields = Column(JSON)  # Array of mismatched fields
    
    # Processing
    processed_at = Column(DateTime)
    processing_time_ms = Column(Integer)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer")
    document = relationship("CustomerDocument", back_populates="ocr_result")


class EKYCRecord(Base):
    """eKYC Verification Records"""
    __tablename__ = "ekyc_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    
    # eKYC Type
    kyc_type = Column(String(50))  # aadhaar_otp, aadhaar_biometric, digilocker
    
    # Aadhaar eKYC
    aadhaar_number = Column(String(20))
    transaction_id = Column(String(100))
    otp_sent = Column(Boolean, default=False)
    otp_verified = Column(Boolean, default=False)
    
    # Extracted Data
    kyc_data = Column(JSON)  # Complete eKYC response
    full_name = Column(String(300))
    date_of_birth = Column(Date)
    gender = Column(String(20))
    address = Column(Text)
    photo_base64 = Column(Text)
    
    # Verification
    verification_status = Column(String(50))  # success, failed, pending
    verification_timestamp = Column(DateTime)
    error_message = Column(Text)
    
    # Consent
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime)
    
    # Audit
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="ekyc_records")


class DigiLockerDocument(Base):
    """DigiLocker Fetched Documents"""
    __tablename__ = "digilocker_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    
    # DigiLocker Information
    digilocker_id = Column(String(100))  # DigiLocker document ID
    document_type = Column(String(100))  # Aadhaar, PAN, DL, etc.
    document_name = Column(String(300))
    
    # Document Data
    document_url = Column(String(500))  # Downloaded document URL
    document_data = Column(JSON)  # Extracted data
    
    # Issuer Information
    issuer_name = Column(String(200))
    issue_date = Column(Date)
    
    # Verification
    is_verified = Column(Boolean, default=True)  # DigiLocker docs are pre-verified
    verified_by_govt = Column(Boolean, default=True)
    
    # Fetch Information
    fetched_at = Column(DateTime, default=datetime.utcnow)
    access_token = Column(String(500))  # OAuth token (encrypted)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="digilocker_documents")
