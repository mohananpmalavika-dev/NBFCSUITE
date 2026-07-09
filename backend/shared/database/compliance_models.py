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
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), index=True)
    
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
        Index('idx_compliance_alert_status', 'tenant_id', 'status'),
        Index('idx_compliance_alert_type', 'tenant_id', 'alert_type'),
    )


# ============================================================================
# RBI RETURNS AUTOMATION - NBS-7 & STATUTORY RETURNS
# ============================================================================

class RBIReturnType(str, enum.Enum):
    """RBI Return Types"""
    NBS_7_MONTHLY = "nbs_7_monthly"
    NBS_7_QUARTERLY = "nbs_7_quarterly"
    ALM_RETURN = "alm_return"
    NPA_RETURN = "npa_return"
    EXPOSURE_RETURN = "exposure_return"
    CRILC_RETURN = "crilc_return"
    SMA_RETURN = "sma_return"
    PRUDENTIAL_NORMS = "prudential_norms"
    CAPITAL_ADEQUACY = "capital_adequacy"
    LIQUIDITY_RETURN = "liquidity_return"
    SECTORAL_DEPLOYMENT = "sectoral_deployment"
    OTHER = "other"


class XBRLTaxonomy(str, enum.Enum):
    """XBRL Taxonomy Versions"""
    RBI_NBFC_2023 = "rbi_nbfc_2023"
    RBI_NBFC_2024 = "rbi_nbfc_2024"
    RBI_NBFC_ND_SI = "rbi_nbfc_nd_si"  # Non-Deposit taking - Systemically Important
    RBI_NBFC_D = "rbi_nbfc_d"  # Deposit taking
    CUSTOM = "custom"


class ReturnFrequency(str, enum.Enum):
    """Return submission frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    ANNUAL = "annual"
    ON_DEMAND = "on_demand"


class SubmissionStatus(str, enum.Enum):
    """Submission status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    REVISED = "revised"


class ComplianceEventType(str, enum.Enum):
    """Compliance calendar event types"""
    RETURN_DUE = "return_due"
    AUDIT_SCHEDULED = "audit_scheduled"
    BOARD_MEETING = "board_meeting"
    REGULATORY_FILING = "regulatory_filing"
    LICENSE_RENEWAL = "license_renewal"
    INSPECTION = "inspection"
    OTHER = "other"


class EventPriority(str, enum.Enum):
    """Event priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# RBI RETURN MASTER
# ============================================================================

class RBIReturnMaster(BaseModel):
    """Master data for RBI returns configuration"""
    __tablename__ = "rbi_return_master"
    
    # Return Details
    return_code = Column(String(50), unique=True, nullable=False, index=True)
    return_name = Column(String(300), nullable=False)
    return_type = Column(SQLEnum(RBIReturnType), nullable=False, index=True)
    description = Column(Text)
    
    # Applicability
    applicable_to = Column(JSON)  # List of entity types: ["nbfc_d", "nbfc_nd_si", etc.]
    is_mandatory = Column(Boolean, default=True)
    effective_from = Column(Date)
    effective_to = Column(Date)
    
    # Frequency & Deadlines
    frequency = Column(SQLEnum(ReturnFrequency), nullable=False)
    due_day_of_month = Column(Integer)  # Day of month when due
    due_days_after_period = Column(Integer)  # Days after period end
    grace_period_days = Column(Integer, default=0)
    
    # Format & Requirements
    file_formats = Column(JSON)  # ["excel", "csv", "xml", "xbrl"]
    has_xbrl = Column(Boolean, default=False)
    xbrl_taxonomy = Column(SQLEnum(XBRLTaxonomy))
    
    # Submission Details
    submission_portal = Column(String(500))  # URL or portal name
    submission_method = Column(String(100))  # online, email, physical
    
    # Template & Instructions
    template_file_path = Column(String(500))
    template_file_url = Column(String(500))
    instructions_file_path = Column(String(500))
    instructions_url = Column(String(500))
    
    # Validation Rules
    validation_rules = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    __table_args__ = (
        Index('idx_return_type_active', 'tenant_id', 'return_type', 'is_active'),
        Index('idx_return_frequency', 'tenant_id', 'frequency'),
    )


# ============================================================================
# NBS-7 RETURN DATA
# ============================================================================

class NBS7Return(BaseModel):
    """NBS-7 Return Data - Monthly/Quarterly Financial Returns"""
    __tablename__ = "nbs7_returns"
    
    # Return Identification
    return_number = Column(String(50), unique=True, nullable=False, index=True)
    return_master_id = Column(UUID(as_uuid=True), ForeignKey("rbi_return_master.id"))
    
    # Period Details
    reporting_period = Column(String(20), nullable=False, index=True)  # "2024-01", "Q1-FY2024"
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    as_on_date = Column(Date, nullable=False)
    
    # Financial Year
    financial_year = Column(String(10), nullable=False, index=True)  # FY2024-25
    quarter = Column(String(5))  # Q1, Q2, Q3, Q4
    
    # Status
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.DRAFT, index=True)
    
    # ========== ASSET SIDE DATA ==========
    
    # Loans & Advances
    term_loans = Column(Numeric(20, 2), default=0)
    hire_purchase = Column(Numeric(20, 2), default=0)
    leasing = Column(Numeric(20, 2), default=0)
    bills_discounted = Column(Numeric(20, 2), default=0)
    other_loans = Column(Numeric(20, 2), default=0)
    total_loans = Column(Numeric(20, 2), default=0)
    
    # Provisions
    provision_standard_assets = Column(Numeric(20, 2), default=0)
    provision_npa = Column(Numeric(20, 2), default=0)
    total_provisions = Column(Numeric(20, 2), default=0)
    
    # Net Loans
    net_loans_advances = Column(Numeric(20, 2), default=0)
    
    # Investments
    government_securities = Column(Numeric(20, 2), default=0)
    corporate_bonds = Column(Numeric(20, 2), default=0)
    mutual_funds = Column(Numeric(20, 2), default=0)
    shares_equity = Column(Numeric(20, 2), default=0)
    other_investments = Column(Numeric(20, 2), default=0)
    total_investments = Column(Numeric(20, 2), default=0)
    
    # Fixed Assets
    fixed_assets_gross = Column(Numeric(20, 2), default=0)
    accumulated_depreciation = Column(Numeric(20, 2), default=0)
    fixed_assets_net = Column(Numeric(20, 2), default=0)
    
    # Other Assets
    cash_bank_balances = Column(Numeric(20, 2), default=0)
    other_assets = Column(Numeric(20, 2), default=0)
    
    # Total Assets
    total_assets = Column(Numeric(20, 2), default=0)
    
    # ========== LIABILITY SIDE DATA ==========
    
    # Capital & Reserves
    share_capital = Column(Numeric(20, 2), default=0)
    reserves_surplus = Column(Numeric(20, 2), default=0)
    total_capital_reserves = Column(Numeric(20, 2), default=0)
    
    # Borrowings
    bank_borrowings = Column(Numeric(20, 2), default=0)
    debentures = Column(Numeric(20, 2), default=0)
    commercial_paper = Column(Numeric(20, 2), default=0)
    subordinated_debt = Column(Numeric(20, 2), default=0)
    other_borrowings = Column(Numeric(20, 2), default=0)
    total_borrowings = Column(Numeric(20, 2), default=0)
    
    # Public Deposits (for NBFC-D)
    public_deposits = Column(Numeric(20, 2), default=0)
    
    # Other Liabilities
    other_liabilities = Column(Numeric(20, 2), default=0)
    provisions_liabilities = Column(Numeric(20, 2), default=0)
    
    # Total Liabilities
    total_liabilities = Column(Numeric(20, 2), default=0)
    
    # ========== INCOME STATEMENT DATA ==========
    
    # Income
    interest_income = Column(Numeric(20, 2), default=0)
    other_income = Column(Numeric(20, 2), default=0)
    total_income = Column(Numeric(20, 2), default=0)
    
    # Expenditure
    interest_expenditure = Column(Numeric(20, 2), default=0)
    operating_expenses = Column(Numeric(20, 2), default=0)
    provisions_write_offs = Column(Numeric(20, 2), default=0)
    total_expenditure = Column(Numeric(20, 2), default=0)
    
    # Profit
    profit_before_tax = Column(Numeric(20, 2), default=0)
    tax_provision = Column(Numeric(20, 2), default=0)
    profit_after_tax = Column(Numeric(20, 2), default=0)
    
    # ========== NPA & PRUDENTIAL DATA ==========
    
    # NPAs
    gross_npa = Column(Numeric(20, 2), default=0)
    net_npa = Column(Numeric(20, 2), default=0)
    npa_ratio = Column(Numeric(10, 4), default=0)  # Percentage
    
    # Capital Adequacy
    crar_percentage = Column(Numeric(10, 4), default=0)  # Capital to Risk-weighted Assets Ratio
    tier1_capital = Column(Numeric(20, 2), default=0)
    tier2_capital = Column(Numeric(20, 2), default=0)
    total_capital = Column(Numeric(20, 2), default=0)
    risk_weighted_assets = Column(Numeric(20, 2), default=0)
    
    # Sectoral Deployment
    sectoral_deployment = Column(JSON)  # Industry-wise loan distribution
    
    # Geographic Distribution
    geographic_distribution = Column(JSON)  # State-wise distribution
    
    # ========== ADDITIONAL DATA ==========
    
    # Detailed breakdown in JSON
    detailed_data = Column(JSON)
    
    # ========== SUBMISSION TRACKING ==========
    
    # File Attachments
    excel_file_path = Column(String(500))
    excel_file_url = Column(String(500))
    pdf_file_path = Column(String(500))
    pdf_file_url = Column(String(500))
    
    # Workflow
    prepared_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    prepared_date = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_date = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_date = Column(DateTime)
    
    # Submission
    submitted_date = Column(DateTime, index=True)
    submission_reference = Column(String(100))
    acknowledgement_number = Column(String(100))
    acknowledgement_date = Column(DateTime)
    
    # Due Date Tracking
    due_date = Column(Date, nullable=False, index=True)
    is_overdue = Column(Boolean, default=False, index=True)
    days_overdue = Column(Integer, default=0)
    
    # Remarks & Notes
    remarks = Column(Text)
    rejection_reason = Column(Text)
    internal_notes = Column(Text)
    
    # Relationships
    return_master = relationship("RBIReturnMaster", foreign_keys=[return_master_id])
    
    __table_args__ = (
        Index('idx_nbs7_period', 'tenant_id', 'reporting_period'),
        Index('idx_nbs7_status', 'tenant_id', 'status'),
        Index('idx_nbs7_fy', 'tenant_id', 'financial_year'),
        Index('idx_nbs7_due', 'tenant_id', 'due_date', 'is_overdue'),
    )


# ============================================================================
# STATUTORY RETURNS
# ============================================================================

class StatutoryReturn(BaseModel):
    """Generic Statutory Returns (ALM, Exposure, Prudential Norms, etc.)"""
    __tablename__ = "statutory_returns"
    
    # Return Identification
    return_number = Column(String(50), unique=True, nullable=False, index=True)
    return_master_id = Column(UUID(as_uuid=True), ForeignKey("rbi_return_master.id"))
    return_type = Column(SQLEnum(RBIReturnType), nullable=False, index=True)
    
    # Period Details
    reporting_period = Column(String(20), nullable=False, index=True)
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    as_on_date = Column(Date, nullable=False)
    financial_year = Column(String(10), nullable=False)
    
    # Status
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.DRAFT, index=True)
    
    # Return Data (flexible JSON structure)
    return_data = Column(JSON, nullable=False)  # Main return data
    schedules = Column(JSON)  # Additional schedules/annexures
    summary_data = Column(JSON)  # Summary for quick view
    
    # Validation
    validation_status = Column(String(50), default='pending')  # pending, passed, failed
    validation_errors = Column(JSON)
    validation_warnings = Column(JSON)
    
    # File Attachments
    excel_file_path = Column(String(500))
    excel_file_url = Column(String(500))
    pdf_file_path = Column(String(500))
    pdf_file_url = Column(String(500))
    
    # Workflow
    prepared_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    prepared_date = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_date = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_date = Column(DateTime)
    
    # Submission
    submitted_date = Column(DateTime, index=True)
    submission_reference = Column(String(100))
    acknowledgement_number = Column(String(100))
    acknowledgement_date = Column(DateTime)
    
    # Due Date Tracking
    due_date = Column(Date, nullable=False, index=True)
    is_overdue = Column(Boolean, default=False, index=True)
    days_overdue = Column(Integer, default=0)
    
    # Remarks
    remarks = Column(Text)
    rejection_reason = Column(Text)
    internal_notes = Column(Text)
    
    # Revision Tracking
    revision_number = Column(Integer, default=1)
    parent_return_id = Column(UUID(as_uuid=True), ForeignKey("statutory_returns.id"))
    
    # Relationships
    return_master = relationship("RBIReturnMaster", foreign_keys=[return_master_id])
    parent_return = relationship("StatutoryReturn", remote_side="StatutoryReturn.id", foreign_keys=[parent_return_id])
    
    __table_args__ = (
        Index('idx_statutory_period', 'tenant_id', 'reporting_period'),
        Index('idx_statutory_type_status', 'tenant_id', 'return_type', 'status'),
        Index('idx_statutory_due', 'tenant_id', 'due_date', 'is_overdue'),
    )


# ============================================================================
# XBRL DOCUMENTS
# ============================================================================

class XBRLDocument(BaseModel):
    """XBRL Document Generation & Storage"""
    __tablename__ = "xbrl_documents"
    
    # Document Identification
    document_number = Column(String(50), unique=True, nullable=False, index=True)
    document_name = Column(String(300), nullable=False)
    
    # Linked Return
    return_type = Column(SQLEnum(RBIReturnType), nullable=False)
    nbs7_return_id = Column(UUID(as_uuid=True), ForeignKey("nbs7_returns.id"))
    statutory_return_id = Column(UUID(as_uuid=True), ForeignKey("statutory_returns.id"))
    
    # XBRL Details
    taxonomy_version = Column(SQLEnum(XBRLTaxonomy), nullable=False)
    taxonomy_url = Column(String(500))
    schema_version = Column(String(50))
    
    # Period
    reporting_period = Column(String(20), nullable=False)
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    # XBRL Content
    xbrl_content = Column(Text)  # Full XBRL XML content
    instance_document = Column(Text)  # Instance document
    
    # Validation
    is_valid = Column(Boolean, default=False)
    validation_errors = Column(JSON)
    validation_date = Column(DateTime)
    
    # File Storage
    xbrl_file_path = Column(String(500))
    xbrl_file_url = Column(String(500))
    xbrl_file_size = Column(Integer)  # bytes
    
    # Metadata
    entity_identifier = Column(String(100))  # Company/Entity ID
    entity_name = Column(String(300))
    
    # Status
    status = Column(String(50), default='draft', index=True)  # draft, validated, submitted
    
    # Generation Details
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    generated_date = Column(DateTime)
    
    # Submission
    submitted_date = Column(DateTime)
    submission_reference = Column(String(100))
    
    # Remarks
    remarks = Column(Text)
    
    # Relationships
    nbs7_return = relationship("NBS7Return", foreign_keys=[nbs7_return_id])
    statutory_return = relationship("StatutoryReturn", foreign_keys=[statutory_return_id])
    
    __table_args__ = (
        Index('idx_xbrl_period', 'tenant_id', 'reporting_period'),
        Index('idx_xbrl_status', 'tenant_id', 'status'),
        Index('idx_xbrl_return_type', 'tenant_id', 'return_type'),
    )


# ============================================================================
# COMPLIANCE CALENDAR
# ============================================================================

class ComplianceCalendar(BaseModel):
    """Compliance Calendar - Track all regulatory deadlines and events"""
    __tablename__ = "compliance_calendar"
    
    # Event Identification
    event_code = Column(String(50), index=True)
    event_title = Column(String(300), nullable=False)
    event_type = Column(SQLEnum(ComplianceEventType), nullable=False, index=True)
    
    # Description
    description = Column(Text)
    requirements = Column(Text)  # What needs to be done
    
    # Date & Time
    event_date = Column(Date, nullable=False, index=True)
    event_time = Column(String(20))  # Optional time
    due_date = Column(Date, index=True)
    
    # Priority & Category
    priority = Column(SQLEnum(EventPriority), default=EventPriority.MEDIUM, index=True)
    category = Column(String(100))  # RBI, SEBI, Tax, Audit, etc.
    
    # Linked Entities
    return_master_id = Column(UUID(as_uuid=True), ForeignKey("rbi_return_master.id"))
    nbs7_return_id = Column(UUID(as_uuid=True), ForeignKey("nbs7_returns.id"))
    statutory_return_id = Column(UUID(as_uuid=True), ForeignKey("statutory_returns.id"))
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # monthly, quarterly, annually
    recurrence_day = Column(Integer)  # Day of month/quarter
    
    # Status
    status = Column(String(50), default='pending', index=True)  # pending, in_progress, completed, cancelled
    completion_date = Column(DateTime)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_date = Column(DateTime)
    
    # Reminders
    reminder_enabled = Column(Boolean, default=True)
    reminder_days_before = Column(JSON)  # [30, 15, 7, 3, 1] days before
    last_reminder_sent = Column(DateTime)
    
    # Notifications
    notification_sent = Column(Boolean, default=False)
    notification_date = Column(DateTime)
    
    # Attachments
    attachments = Column(JSON)  # List of file paths/URLs
    
    # Notes & Comments
    notes = Column(Text)
    internal_comments = Column(Text)
    
    # Tracking
    start_date = Column(DateTime)
    estimated_effort_hours = Column(Numeric(10, 2))
    actual_effort_hours = Column(Numeric(10, 2))
    
    # Relationships
    return_master = relationship("RBIReturnMaster", foreign_keys=[return_master_id])
    nbs7_return = relationship("NBS7Return", foreign_keys=[nbs7_return_id])
    statutory_return = relationship("StatutoryReturn", foreign_keys=[statutory_return_id])
    
    __table_args__ = (
        Index('idx_calendar_date', 'tenant_id', 'event_date'),
        Index('idx_calendar_due', 'tenant_id', 'due_date'),
        Index('idx_calendar_status', 'tenant_id', 'status'),
        Index('idx_calendar_priority', 'tenant_id', 'priority'),
        Index('idx_calendar_assigned', 'tenant_id', 'assigned_to'),
    )


# ============================================================================
# RETURN SUBMISSION HISTORY
# ============================================================================

class ReturnSubmissionHistory(BaseModel):
    """Track submission history and audit trail"""
    __tablename__ = "return_submission_history"
    
    # Linked Return
    return_type = Column(String(50), nullable=False, index=True)
    nbs7_return_id = Column(UUID(as_uuid=True), ForeignKey("nbs7_returns.id"))
    statutory_return_id = Column(UUID(as_uuid=True), ForeignKey("statutory_returns.id"))
    xbrl_document_id = Column(UUID(as_uuid=True), ForeignKey("xbrl_documents.id"))
    
    # Action
    action = Column(String(50), nullable=False)  # created, submitted, approved, rejected, revised
    previous_status = Column(String(50))
    new_status = Column(String(50))
    
    # User & Timestamp
    action_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Details
    action_details = Column(JSON)
    comments = Column(Text)
    
    # IP & Session
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Relationships
    nbs7_return = relationship("NBS7Return", foreign_keys=[nbs7_return_id])
    statutory_return = relationship("StatutoryReturn", foreign_keys=[statutory_return_id])
    xbrl_document = relationship("XBRLDocument", foreign_keys=[xbrl_document_id])
    
    __table_args__ = (
        Index('idx_history_return', 'tenant_id', 'return_type', 'action_date'),
        Index('idx_history_user', 'tenant_id', 'action_by'),
    )
