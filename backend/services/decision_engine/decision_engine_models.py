"""
Instant Decision Framework Models
Real-time decisioning with parallel checks and automated scoring
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from backend.core.database import Base


# =====================================================================
# ENUMS
# =====================================================================

class DecisionStatus(str, Enum):
    """Decision request status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class DecisionOutcome(str, Enum):
    """Final decision outcome"""
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    CONDITIONAL_APPROVAL = "CONDITIONAL_APPROVAL"


class CheckStatus(str, Enum):
    """Individual check status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"


class CheckResult(str, Enum):
    """Individual check result"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    REFER = "REFER"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class BureauProvider(str, Enum):
    """Credit bureau providers"""
    CIBIL = "CIBIL"
    EXPERIAN = "EXPERIAN"
    EQUIFAX = "EQUIFAX"
    CRIF = "CRIF"


class FraudRiskLevel(str, Enum):
    """Fraud risk levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DeclineReason(str, Enum):
    """Decline reasons"""
    LOW_CREDIT_SCORE = "LOW_CREDIT_SCORE"
    INSUFFICIENT_INCOME = "INSUFFICIENT_INCOME"
    HIGH_DTI = "HIGH_DTI"
    ADVERSE_CREDIT = "ADVERSE_CREDIT"
    FRAUD_DETECTED = "FRAUD_DETECTED"
    KYC_FAILURE = "KYC_FAILURE"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    INCOMPLETE_DATA = "INCOMPLETE_DATA"
    DUPLICATE_APPLICATION = "DUPLICATE_APPLICATION"
    BLACKLISTED = "BLACKLISTED"


# =====================================================================
# DATABASE MODELS
# =====================================================================

class DecisionRequest(Base):
    """Main decision request"""
    __tablename__ = "decision_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Application details
    application_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    customer_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Request data
    loan_amount = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    purpose = Column(String(100))
    
    # Applicant data (for decision making)
    applicant_data = Column(JSON, nullable=False)  # Age, income, employment, etc.
    
    # Decision status
    status = Column(SQLEnum(DecisionStatus), default=DecisionStatus.PENDING, index=True)
    decision_outcome = Column(SQLEnum(DecisionOutcome))
    
    # Decision details
    decision_score = Column(Float)  # Overall score (0-100)
    confidence_score = Column(Float)  # Confidence in decision (0-100)
    
    approved_amount = Column(Float)
    approved_tenure = Column(Integer)
    approved_rate = Column(Float)
    
    decline_reasons = Column(JSON)  # List of decline reasons
    conditions = Column(JSON)  # Conditions for approval
    
    # Timing
    request_time = Column(DateTime, default=datetime.utcnow)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_duration_ms = Column(Integer)  # Total time in milliseconds
    
    # Checks summary
    total_checks = Column(Integer, default=0)
    passed_checks = Column(Integer, default=0)
    failed_checks = Column(Integer, default=0)
    warning_checks = Column(Integer, default=0)
    
    # Fraud indicators
    fraud_score = Column(Float)  # 0-100, higher is more fraudulent
    fraud_risk_level = Column(SQLEnum(FraudRiskLevel))
    fraud_indicators = Column(JSON)  # List of fraud indicators
    
    # Manual review
    requires_manual_review = Column(Boolean, default=False)
    manual_review_reason = Column(Text)
    reviewed_by = Column(PGUUID(as_uuid=True))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    
    # Relationships
    bureau_checks = relationship("BureauCheck", back_populates="decision_request", cascade="all, delete-orphan")
    bank_statement_analysis = relationship("BankStatementAnalysis", back_populates="decision_request", uselist=False, cascade="all, delete-orphan")
    kyc_verification = relationship("KYCVerification", back_populates="decision_request", uselist=False, cascade="all, delete-orphan")
    fraud_check = relationship("FraudCheck", back_populates="decision_request", uselist=False, cascade="all, delete-orphan")
    eligibility_check = relationship("EligibilityCheck", back_populates="decision_request", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("DecisionAudit", back_populates="decision_request", cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))


class BureauCheck(Base):
    """Credit bureau check"""
    __tablename__ = "bureau_checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_request_id = Column(PGUUID(as_uuid=True), ForeignKey("decision_requests.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Bureau details
    bureau_provider = Column(SQLEnum(BureauProvider), nullable=False)
    bureau_reference = Column(String(100))  # Bureau transaction ID
    
    # Check status
    status = Column(SQLEnum(CheckStatus), default=CheckStatus.PENDING)
    result = Column(SQLEnum(CheckResult))
    
    # Credit score
    credit_score = Column(Integer)
    score_version = Column(String(50))
    
    # Bureau data
    total_accounts = Column(Integer)
    active_accounts = Column(Integer)
    closed_accounts = Column(Integer)
    total_credit_limit = Column(Float)
    total_outstanding = Column(Float)
    credit_utilization = Column(Float)  # Percentage
    
    # Delinquency
    total_dpd = Column(Integer)  # Total days past due
    max_dpd_last_12m = Column(Integer)
    max_dpd_last_24m = Column(Integer)
    dpd_30_count = Column(Integer)
    dpd_60_count = Column(Integer)
    dpd_90_count = Column(Integer)
    
    # Enquiries
    enquiries_last_3m = Column(Integer)
    enquiries_last_6m = Column(Integer)
    enquiries_last_12m = Column(Integer)
    
    # Account types
    secured_accounts = Column(Integer)
    unsecured_accounts = Column(Integer)
    
    # Adverse items
    written_off_count = Column(Integer)
    settled_count = Column(Integer)
    restructured_count = Column(Integer)
    
    # Full bureau response
    bureau_response = Column(JSON)
    
    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_ms = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    
    # Relationship
    decision_request = relationship("DecisionRequest", back_populates="bureau_checks")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class BankStatementAnalysis(Base):
    """Bank statement AI analysis"""
    __tablename__ = "bank_statement_analysis"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_request_id = Column(PGUUID(as_uuid=True), ForeignKey("decision_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Check status
    status = Column(SQLEnum(CheckStatus), default=CheckStatus.PENDING)
    result = Column(SQLEnum(CheckResult))
    
    # Statement details
    statement_period_months = Column(Integer)
    bank_name = Column(String(100))
    account_type = Column(String(50))
    
    # Income analysis
    average_monthly_credit = Column(Float)
    salary_credits_count = Column(Integer)
    salary_amount = Column(Float)
    salary_regularity_score = Column(Float)  # 0-100
    
    other_income = Column(Float)
    bonus_amount = Column(Float)
    
    # Spending analysis
    average_monthly_debit = Column(Float)
    emi_deductions = Column(Float)
    loan_repayments = Column(Float)
    bill_payments = Column(Float)
    
    # Balance analysis
    average_balance = Column(Float)
    min_balance = Column(Float)
    max_balance = Column(Float)
    balance_volatility = Column(Float)  # Standard deviation
    
    # Red flags
    bounced_cheques_count = Column(Integer)
    insufficient_funds_count = Column(Integer)
    overdraft_usage_count = Column(Integer)
    gambling_transactions = Column(Boolean, default=False)
    
    # Banking behavior score
    banking_behavior_score = Column(Float)  # 0-100
    
    # DTI calculation
    calculated_monthly_income = Column(Float)
    calculated_monthly_obligations = Column(Float)
    calculated_dti = Column(Float)  # Percentage
    
    # Full analysis
    analysis_details = Column(JSON)
    
    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_ms = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    
    # Relationship
    decision_request = relationship("DecisionRequest", back_populates="bank_statement_analysis")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class KYCVerification(Base):
    """KYC verification (Aadhaar, PAN, etc.)"""
    __tablename__ = "kyc_verifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_request_id = Column(PGUUID(as_uuid=True), ForeignKey("decision_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Check status
    status = Column(SQLEnum(CheckStatus), default=CheckStatus.PENDING)
    result = Column(SQLEnum(CheckResult))
    
    # Aadhaar verification
    aadhaar_verified = Column(Boolean, default=False)
    aadhaar_name_match = Column(Boolean)
    aadhaar_address_match = Column(Boolean)
    aadhaar_dob_match = Column(Boolean)
    aadhaar_verification_method = Column(String(50))  # OTP, Biometric, Offline
    
    # PAN verification
    pan_verified = Column(Boolean, default=False)
    pan_name_match = Column(Boolean)
    pan_dob_match = Column(Boolean)
    pan_status = Column(String(50))  # Active, Inactive
    
    # Address verification
    address_verified = Column(Boolean, default=False)
    address_proof_type = Column(String(50))
    address_match_score = Column(Float)  # 0-100
    
    # Employment verification
    employment_verified = Column(Boolean, default=False)
    employer_name = Column(String(200))
    employment_type = Column(String(50))
    employment_proof_type = Column(String(50))
    
    # Document verification
    documents_verified = Column(JSON)  # List of verified documents
    
    # Biometric verification
    biometric_verified = Column(Boolean, default=False)
    biometric_score = Column(Float)
    
    # Overall KYC score
    kyc_score = Column(Float)  # 0-100
    
    # Verification details
    verification_details = Column(JSON)
    
    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_ms = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    
    # Relationship
    decision_request = relationship("DecisionRequest", back_populates="kyc_verification")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class FraudCheck(Base):
    """Fraud detection check"""
    __tablename__ = "fraud_checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_request_id = Column(PGUUID(as_uuid=True), ForeignKey("decision_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Check status
    status = Column(SQLEnum(CheckStatus), default=CheckStatus.PENDING)
    result = Column(SQLEnum(CheckResult))
    
    # Device fingerprinting
    device_id = Column(String(100))
    device_type = Column(String(50))
    device_os = Column(String(50))
    device_browser = Column(String(50))
    device_risk_score = Column(Float)
    
    # Geolocation
    ip_address = Column(String(50))
    geo_country = Column(String(50))
    geo_state = Column(String(50))
    geo_city = Column(String(100))
    geo_lat = Column(Float)
    geo_lon = Column(Float)
    geo_risk_score = Column(Float)
    
    # Velocity checks
    applications_last_24h = Column(Integer)
    applications_last_7d = Column(Integer)
    applications_last_30d = Column(Integer)
    velocity_risk_score = Column(Float)
    
    # Duplicate detection
    duplicate_applications = Column(Integer)
    duplicate_phone = Column(Boolean, default=False)
    duplicate_email = Column(Boolean, default=False)
    duplicate_pan = Column(Boolean, default=False)
    duplicate_aadhaar = Column(Boolean, default=False)
    
    # Blacklist check
    blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(String(200))
    
    # Behavior analysis
    time_to_complete = Column(Integer)  # Time to complete application (seconds)
    unusual_behavior = Column(Boolean, default=False)
    behavior_risk_score = Column(Float)
    
    # Email/Phone verification
    email_verified = Column(Boolean, default=False)
    email_risk_score = Column(Float)
    phone_verified = Column(Boolean, default=False)
    phone_risk_score = Column(Float)
    
    # Social media signals (optional)
    social_media_verified = Column(Boolean, default=False)
    social_media_score = Column(Float)
    
    # Overall fraud score
    fraud_score = Column(Float)  # 0-100, higher = more fraudulent
    fraud_risk_level = Column(SQLEnum(FraudRiskLevel))
    
    # Fraud indicators
    fraud_indicators = Column(JSON)  # List of detected fraud indicators
    
    # Full fraud analysis
    fraud_details = Column(JSON)
    
    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_ms = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    
    # Relationship
    decision_request = relationship("DecisionRequest", back_populates="fraud_check")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class EligibilityCheck(Base):
    """Eligibility and business rules check"""
    __tablename__ = "eligibility_checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_request_id = Column(PGUUID(as_uuid=True), ForeignKey("decision_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Check status
    status = Column(SQLEnum(CheckStatus), default=CheckStatus.PENDING)
    result = Column(SQLEnum(CheckResult))
    
    # Age check
    age = Column(Integer)
    age_eligible = Column(Boolean)
    min_age = Column(Integer)
    max_age = Column(Integer)
    
    # Income check
    monthly_income = Column(Float)
    income_eligible = Column(Boolean)
    min_income = Column(Float)
    
    # DTI check
    monthly_obligations = Column(Float)
    dti_ratio = Column(Float)
    dti_eligible = Column(Boolean)
    max_dti = Column(Float)
    
    # Employment check
    employment_type = Column(String(50))
    employment_duration_months = Column(Integer)
    employment_eligible = Column(Boolean)
    min_employment_months = Column(Integer)
    
    # Credit score check
    credit_score = Column(Integer)
    credit_score_eligible = Column(Boolean)
    min_credit_score = Column(Integer)
    
    # Loan amount check
    requested_amount = Column(Float)
    amount_eligible = Column(Boolean)
    min_loan_amount = Column(Float)
    max_loan_amount = Column(Float)
    
    # LTV check (if applicable)
    collateral_value = Column(Float)
    ltv_ratio = Column(Float)
    ltv_eligible = Column(Boolean)
    max_ltv = Column(Float)
    
    # Residence check
    residence_type = Column(String(50))
    residence_duration_months = Column(Integer)
    residence_eligible = Column(Boolean)
    
    # Geography check
    state = Column(String(50))
    city = Column(String(100))
    geography_eligible = Column(Boolean)
    
    # Product-specific rules
    product_rules_passed = Column(Boolean)
    product_rules_details = Column(JSON)
    
    # Policy rules
    policy_rules_passed = Column(Boolean)
    policy_rules_details = Column(JSON)
    
    # Overall eligibility
    overall_eligible = Column(Boolean)
    eligibility_score = Column(Float)  # 0-100
    
    # Failed criteria
    failed_criteria = Column(JSON)  # List of failed eligibility criteria
    
    # Timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_ms = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    
    # Relationship
    decision_request = relationship("DecisionRequest", back_populates="eligibility_check")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class DecisionAudit(Base):
    """Decision audit trail"""
    __tablename__ = "decision_audit"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    decision_request_id = Column(PGUUID(as_uuid=True), ForeignKey("decision_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # REQUEST_RECEIVED, CHECK_STARTED, CHECK_COMPLETED, DECISION_MADE, etc.
    event_description = Column(Text)
    event_data = Column(JSON)
    
    # Timing
    event_time = Column(DateTime, default=datetime.utcnow, index=True)
    
    # User tracking
    user_id = Column(PGUUID(as_uuid=True))
    ip_address = Column(String(50))
    
    # Relationship
    decision_request = relationship("DecisionRequest", back_populates="audit_logs")


# =====================================================================
# PYDANTIC SCHEMAS
# =====================================================================

class DecisionRequestCreate(BaseModel):
    """Create decision request schema"""
    application_id: UUID
    customer_id: UUID
    product_id: UUID
    loan_amount: float
    tenure_months: int
    purpose: Optional[str] = None
    applicant_data: Dict[str, Any]  # Age, income, employment, etc.


class DecisionRequestResponse(BaseModel):
    """Decision request response schema"""
    id: UUID
    tenant_id: UUID
    application_id: UUID
    customer_id: UUID
    product_id: UUID
    loan_amount: float
    tenure_months: int
    status: DecisionStatus
    decision_outcome: Optional[DecisionOutcome]
    decision_score: Optional[float]
    confidence_score: Optional[float]
    approved_amount: Optional[float]
    approved_tenure: Optional[int]
    approved_rate: Optional[float]
    decline_reasons: Optional[List[str]]
    conditions: Optional[List[str]]
    request_time: datetime
    total_duration_ms: Optional[int]
    total_checks: int
    passed_checks: int
    failed_checks: int
    fraud_score: Optional[float]
    fraud_risk_level: Optional[FraudRiskLevel]
    requires_manual_review: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CheckStatusSummary(BaseModel):
    """Check status summary"""
    check_name: str
    status: CheckStatus
    result: Optional[CheckResult]
    duration_ms: Optional[int]
    error_message: Optional[str] = None


class DecisionDetailResponse(BaseModel):
    """Detailed decision response with all checks"""
    decision_request: DecisionRequestResponse
    bureau_checks: List[Dict[str, Any]]
    bank_statement: Optional[Dict[str, Any]]
    kyc_verification: Optional[Dict[str, Any]]
    fraud_check: Optional[Dict[str, Any]]
    eligibility_check: Optional[Dict[str, Any]]
    audit_logs: List[Dict[str, Any]]
