"""
Compliance & Regulatory Reporting Models
CRILC (Central Repository of Information on Large Credits) & SMA Reporting
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

class BorrowerType(str, enum.Enum):
    """Borrower classification"""
    INDIVIDUAL = "individual"
    SOLE_PROPRIETOR = "sole_proprietor"
    PARTNERSHIP = "partnership"
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    TRUST = "trust"
    SOCIETY = "society"
    GOVERNMENT = "government"
    HUF = "huf"


class ExposureType(str, enum.Enum):
    """Credit exposure types"""
    FUNDED = "funded"
    NON_FUNDED = "non_funded"


class FacilityType(str, enum.Enum):
    """Facility/Product types"""
    TERM_LOAN = "term_loan"
    CASH_CREDIT = "cash_credit"
    OVERDRAFT = "overdraft"
    WORKING_CAPITAL = "working_capital"
    BILL_DISCOUNTING = "bill_discounting"
    BANK_GUARANTEE = "bank_guarantee"
    LETTER_OF_CREDIT = "letter_of_credit"
    OTHER = "other"


class SMAStatus(str, enum.Enum):
    """Special Mention Account Status - As per RBI Guidelines"""
    STANDARD = "standard"  # 0 DPD
    SMA_0 = "sma_0"  # 1-30 DPD
    SMA_1 = "sma_1"  # 31-60 DPD
    SMA_2 = "sma_2"  # 61-90 DPD
    NPA_SUBSTANDARD = "npa_substandard"  # >90 DPD
    NPA_DOUBTFUL = "npa_doubtful"
    NPA_LOSS = "npa_loss"


class AssetClassification(str, enum.Enum):
    """Asset classification as per RBI"""
    STANDARD = "standard"
    SUB_STANDARD = "sub_standard"
    DOUBTFUL_1 = "doubtful_1"
    DOUBTFUL_2 = "doubtful_2"
    DOUBTFUL_3 = "doubtful_3"
    LOSS = "loss"


class ReportingFrequency(str, enum.Enum):
    """Reporting frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"


class ReportStatus(str, enum.Enum):
    """Report status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"


# ============================================================================
# CRILC LARGE CREDIT IDENTIFICATION
# ============================================================================

class CRILCBorrower(BaseModel):
    """Large Credit Borrowers - CRILC Reporting"""
    __tablename__ = "crilc_borrowers"
    
    # Borrower Identification
    borrower_code = Column(String(50), unique=True, nullable=False, index=True)
    borrower_name = Column(String(500), nullable=False)
    borrower_type = Column(SQLEnum(BorrowerType), nullable=False)
    
    # Company/Individual Details
    pan_number = Column(String(10), index=True)
    cin_number = Column(String(21))  # Corporate Identification Number
    gstin = Column(String(15))
    
    # Contact Details
    registered_address = Column(Text)
    city = Column(String(200))
    state = Column(String(100))
    pincode = Column(String(10))
    country = Column(String(100), default='India')
    
    # Business Details
    industry_code = Column(String(20))  # NIC Code
    industry_name = Column(String(200))
    nature_of_business = Column(String(500))
    year_of_incorporation = Column(Integer)
    
    # Financial Details
    annual_turnover = Column(Numeric(20, 2))
    net_worth = Column(Numeric(20, 2))
    financial_year = Column(String(10))  # FY2023-24
    
    # Large Credit Threshold
    total_credit_exposure = Column(Numeric(20, 2), nullable=False)  # Aggregate funded + non-funded
    funded_exposure = Column(Numeric(20, 2))
    non_funded_exposure = Column(Numeric(20, 2))
    
    # CRILC Criteria (₹5 Crore and above aggregate exposure)
    is_large_credit = Column(Boolean, default=False, index=True)
    large_credit_since = Column(Date)
    
    # Group/Related Party
    is_part_of_group = Column(Boolean, default=False)
    group_name = Column(String(300))
    group_exposure = Column(Numeric(20, 2))
    related_party_ids = Column(JSON)  # List of related borrower IDs
    
    # Risk Details
    current_sma_status = Column(SQLEnum(SMAStatus), default=SMAStatus.STANDARD, index=True)
    current_asset_classification = Column(SQLEnum(AssetClassification), default=AssetClassification.STANDARD)
    days_past_due = Column(Integer, default=0)
    
    # Rating
    internal_rating = Column(String(20))
    external_rating = Column(String(20))
    rating_agency = Column(String(100))
    rating_date = Column(Date)
    
    # Link to Customer
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_reported_quarter = Column(String(10))  # Q1FY24, Q2FY24, etc.
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    facilities = relationship("CRILCFacility", back_populates="borrower", cascade="all, delete-orphan")
    sma_tracking = relationship("SMATracking", back_populates="borrower", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_crilc_borrower_pan', 'tenant_id', 'pan_number'),
        Index('idx_crilc_large_credit', 'tenant_id', 'is_large_credit'),
        Index('idx_crilc_sma', 'tenant_id', 'current_sma_status'),
    )


class CRILCFacility(BaseModel):
    """Credit Facilities under CRILC Borrowers"""
    __tablename__ = "crilc_facilities"
    
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("crilc_borrowers.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), index=True)
    
    # Facility Details
    facility_id = Column(String(100), unique=True, nullable=False)
    facility_type = Column(SQLEnum(FacilityType), nullable=False)
    exposure_type = Column(SQLEnum(ExposureType), nullable=False)
    
    # Amounts
    sanctioned_amount = Column(Numeric(20, 2), nullable=False)
    outstanding_amount = Column(Numeric(20, 2), nullable=False)
    overdue_amount = Column(Numeric(20, 2), default=0)
    
    # Dates
    sanction_date = Column(Date, nullable=False)
    disbursement_date = Column(Date)
    maturity_date = Column(Date)
    
    # Security
    security_type = Column(String(100))  # secured, unsecured
    security_value = Column(Numeric(20, 2))
    collateral_details = Column(JSON)
    
    # Performance
    days_past_due = Column(Integer, default=0, index=True)
    asset_classification = Column(SQLEnum(AssetClassification), default=AssetClassification.STANDARD)
    
    # Interest
    interest_rate = Column(Numeric(5, 2))
    interest_overdue = Column(Numeric(15, 2), default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    closure_date = Column(Date)
    
    # Relationships
    borrower = relationship("CRILCBorrower", back_populates="facilities")
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    
    __table_args__ = (
        Index('idx_facility_borrower', 'tenant_id', 'borrower_id'),
        Index('idx_facility_dpd', 'tenant_id', 'days_past_due'),
    )


# ============================================================================
# SMA (SPECIAL MENTION ACCOUNT) TRACKING
# ============================================================================

class SMATracking(BaseModel):
    """SMA Status Tracking - Real-time monitoring"""
    __tablename__ = "sma_tracking"
    
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("crilc_borrowers.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    # As-on Date
    as_on_date = Column(Date, nullable=False, index=True)
    reporting_quarter = Column(String(10))  # Q1FY24, Q2FY24, etc.
    
    # Current Status
    current_sma_status = Column(SQLEnum(SMAStatus), nullable=False, index=True)
    days_past_due = Column(Integer, default=0)
    
    # Previous Status
    previous_sma_status = Column(SQLEnum(SMAStatus))
    status_change_date = Column(Date)
    days_in_current_status = Column(Integer, default=0)
    
    # Outstanding Details
    principal_outstanding = Column(Numeric(20, 2), nullable=False)
    interest_outstanding = Column(Numeric(20, 2), default=0)
    total_outstanding = Column(Numeric(20, 2), nullable=False)
    
    # Overdue Details
    principal_overdue = Column(Numeric(20, 2), default=0)
    interest_overdue = Column(Numeric(20, 2), default=0)
    total_overdue = Column(Numeric(20, 2), default=0)
    
    # EMI/Installment Details
    installment_amount = Column(Numeric(15, 2))
    last_payment_date = Column(Date)
    last_payment_amount = Column(Numeric(15, 2))
    next_due_date = Column(Date)
    
    # Asset Classification Impact
    asset_classification = Column(SQLEnum(AssetClassification), default=AssetClassification.STANDARD)
    provision_required = Column(Numeric(15, 2), default=0)
    provision_percentage = Column(Numeric(5, 2), default=0)
    
    # Alerts & Actions
    alert_triggered = Column(Boolean, default=False)
    alert_date = Column(DateTime)
    action_taken = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    
    # Relationships
    borrower = relationship("CRILCBorrower", back_populates="sma_tracking")
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    
    __table_args__ = (
        Index('idx_sma_loan_date', 'tenant_id', 'loan_account_id', 'as_on_date'),
        Index('idx_sma_status', 'tenant_id', 'current_sma_status', 'as_on_date'),
        Index('idx_sma_quarter', 'tenant_id', 'reporting_quarter'),
    )


class SMAStatusHistory(BaseModel):
    """Historical SMA status changes"""
    __tablename__ = "sma_status_history"
    
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("crilc_borrowers.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    # Status Change
    from_status = Column(SQLEnum(SMAStatus), nullable=False)
    to_status = Column(SQLEnum(SMAStatus), nullable=False)
    change_date = Column(Date, nullable=False, index=True)
    
    # DPD at change
    dpd_at_change = Column(Integer)
    
    # Outstanding at change
    outstanding_at_change = Column(Numeric(20, 2))
    overdue_at_change = Column(Numeric(20, 2))
    
    # Reason
    change_reason = Column(Text)
    triggered_by = Column(String(100))  # auto_calculation, manual_override, payment, etc.
    
    # Relationships
    borrower = relationship("CRILCBorrower", foreign_keys=[borrower_id])
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    
    __table_args__ = (
        Index('idx_history_loan', 'tenant_id', 'loan_account_id', 'change_date'),
    )


# ============================================================================
# CRILC QUARTERLY RETURNS
# ============================================================================

class CRILCQuarterlyReturn(BaseModel):
    """CRILC Quarterly Return Submission"""
    __tablename__ = "crilc_quarterly_returns"
    
    # Return Details
    return_number = Column(String(50), unique=True, nullable=False, index=True)
    reporting_quarter = Column(String(10), nullable=False, index=True)  # Q1FY24
    reporting_year = Column(String(10), nullable=False)  # FY2023-24
    as_on_date = Column(Date, nullable=False, index=True)
    
    # Status
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT, index=True)
    
    # Summary Statistics
    total_large_borrowers = Column(Integer, default=0)
    total_funded_exposure = Column(Numeric(20, 2), default=0)
    total_non_funded_exposure = Column(Numeric(20, 2), default=0)
    total_exposure = Column(Numeric(20, 2), default=0)
    
    # SMA Breakdown
    sma_0_count = Column(Integer, default=0)
    sma_0_amount = Column(Numeric(20, 2), default=0)
    sma_1_count = Column(Integer, default=0)
    sma_1_amount = Column(Numeric(20, 2), default=0)
    sma_2_count = Column(Integer, default=0)
    sma_2_amount = Column(Numeric(20, 2), default=0)
    npa_count = Column(Integer, default=0)
    npa_amount = Column(Numeric(20, 2), default=0)
    
    # Report Files
    report_file_path = Column(String(500))
    report_file_url = Column(String(500))
    report_format = Column(String(20))  # excel, csv, xml
    
    # Submission
    prepared_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    prepared_date = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_date = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_date = Column(DateTime)
    submitted_date = Column(DateTime)
    submission_reference = Column(String(100))
    
    # Remarks
    remarks = Column(Text)
    rejection_reason = Column(Text)
    
    # Data Snapshot
    data_snapshot = Column(JSON)  # Detailed data at the time of report generation
    
    __table_args__ = (
        Index('idx_return_quarter', 'tenant_id', 'reporting_quarter'),
        Index('idx_return_status', 'tenant_id', 'status'),
    )


class SMAQuarterlyReport(BaseModel):
    """SMA Quarterly Report for RBI"""
    __tablename__ = "sma_quarterly_reports"
    
    # Report Details
    report_number = Column(String(50), unique=True, nullable=False, index=True)
    reporting_quarter = Column(String(10), nullable=False, index=True)
    reporting_year = Column(String(10), nullable=False)
    as_on_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT, index=True)
    
    # SMA-0 (1-30 DPD)
    sma_0_accounts = Column(Integer, default=0)
    sma_0_amount = Column(Numeric(20, 2), default=0)
    sma_0_new_additions = Column(Integer, default=0)
    sma_0_regularized = Column(Integer, default=0)
    sma_0_upgraded_to_sma1 = Column(Integer, default=0)
    
    # SMA-1 (31-60 DPD)
    sma_1_accounts = Column(Integer, default=0)
    sma_1_amount = Column(Numeric(20, 2), default=0)
    sma_1_new_additions = Column(Integer, default=0)
    sma_1_regularized = Column(Integer, default=0)
    sma_1_upgraded_to_sma2 = Column(Integer, default=0)
    
    # SMA-2 (61-90 DPD)
    sma_2_accounts = Column(Integer, default=0)
    sma_2_amount = Column(Numeric(20, 2), default=0)
    sma_2_new_additions = Column(Integer, default=0)
    sma_2_regularized = Column(Integer, default=0)
    sma_2_slipped_to_npa = Column(Integer, default=0)
    
    # Sectoral Breakdown
    sectoral_breakdown = Column(JSON)  # Industry-wise SMA distribution
    
    # Geographic Breakdown
    geographic_breakdown = Column(JSON)  # State/Region-wise distribution
    
    # Report Files
    report_file_path = Column(String(500))
    report_file_url = Column(String(500))
    
    # Submission
    prepared_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    prepared_date = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_date = Column(DateTime)
    submitted_date = Column(DateTime)
    
    # Remarks
    remarks = Column(Text)
    
    __table_args__ = (
        Index('idx_sma_report_quarter', 'tenant_id', 'reporting_quarter'),
    )


class ComplianceAlert(BaseModel):
    """Compliance Alerts for SMA/CRILC"""
    __tablename__ = "compliance_alerts"
    
    # Alert Details
    alert_type = Column(String(50), nullable=False, index=True)
    # sma_status_change, large_credit_threshold, overdue_breach, npa_risk
    alert_category = Column(String(50), nullable=False)  # crilc, sma, regulatory
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Reference
    borrower_id = Column(UUID(as_uuid=True), ForeignKey("crilc_borrowers.id"), index=True)
    loan_account_id = Column(UUID(as_uuid=True), ForeignKey("loan_accounts.id"), index=True)
    
    # Alert Message
    alert_message = Column(Text, nullable=False)
    alert_details = Column(JSON)
    
    # Status
    status = Column(String(50), default='open', index=True)  # open, acknowledged, resolved, dismissed
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Due Date
    due_date = Column(Date, index=True)
    is_overdue = Column(Boolean, default=False)
    
    # Relationships
    borrower = relationship("CRILCBorrower", foreign_keys=[borrower_id])
    loan_account = relationship("LoanAccount", foreign_keys=[loan_account_id])
    
    __table_args__ = (
        Index('idx_alert_status', 'tenant_id', 'status'),
        Index('idx_alert_type', 'tenant_id', 'alert_type'),
    )
