"""
AML/CFT (Anti-Money Laundering / Combating Financing of Terrorism) Models
Transaction Monitoring, CTR/STR Reporting, PEP & Sanction List Screening
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

class TransactionRiskLevel(str, enum.Enum):
    """Transaction risk classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    """AML alert status"""
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    CLOSED_FALSE_POSITIVE = "closed_false_positive"
    CLOSED_REPORTED = "closed_reported"
    CLOSED_NO_ACTION = "closed_no_action"


class ReportStatus(str, enum.Enum):
    """Report submission status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"


class PEPCategory(str, enum.Enum):
    """Politically Exposed Person Categories"""
    DOMESTIC_PEP = "domestic_pep"
    FOREIGN_PEP = "foreign_pep"
    INTERNATIONAL_ORG = "international_org"
    FAMILY_MEMBER = "family_member"
    CLOSE_ASSOCIATE = "close_associate"


class ScreeningStatus(str, enum.Enum):
    """Screening result status"""
    CLEAR = "clear"
    POTENTIAL_MATCH = "potential_match"
    CONFIRMED_MATCH = "confirmed_match"
    FALSE_POSITIVE = "false_positive"
    PENDING_REVIEW = "pending_review"


class MonitoringRuleType(str, enum.Enum):
    """Types of monitoring rules"""
    THRESHOLD = "threshold"
    VELOCITY = "velocity"
    PATTERN = "pattern"
    GEOGRAPHIC = "geographic"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    RELATED_PARTY = "related_party"


# ============================================================================
# TRANSACTION MONITORING
# ============================================================================

class AMLTransactionMonitoring(BaseModel):
    """Real-time transaction monitoring for AML/CFT"""
    __tablename__ = "aml_transaction_monitoring"
    
    # Transaction Reference
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    # deposit, withdrawal, transfer, loan_disbursement, loan_repayment
    
    transaction_date = Column(DateTime, nullable=False, index=True)
    posting_date = Column(Date, nullable=False)
    
    # Parties
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    customer_name = Column(String(300))
    customer_type = Column(String(50))  # individual, business
    
    account_id = Column(String(100), index=True)
    account_number = Column(String(50))
    
    # Counterparty
    counterparty_name = Column(String(300))
    counterparty_account = Column(String(100))
    counterparty_bank = Column(String(200))
    counterparty_country = Column(String(100))
    
    # Amount
    transaction_amount = Column(Numeric(20, 2), nullable=False, index=True)
    transaction_currency = Column(String(3), default='INR')
    
    # Location
    branch_code = Column(String(50))
    channel = Column(String(50))  # branch, atm, internet, mobile, upi
    ip_address = Column(String(50))
    device_id = Column(String(100))
    
    # Risk Assessment
    risk_score = Column(Numeric(5, 2), default=0, index=True)
    risk_level = Column(SQLEnum(TransactionRiskLevel), default=TransactionRiskLevel.LOW, index=True)
    
    # Flags
    is_cash_transaction = Column(Boolean, default=False, index=True)
    is_cross_border = Column(Boolean, default=False, index=True)
    is_high_risk_country = Column(Boolean, default=False)
    is_structured_transaction = Column(Boolean, default=False)
    
    # Customer Profile
    customer_risk_rating = Column(String(20))  # low, medium, high
    customer_is_pep = Column(Boolean, default=False, index=True)
    customer_occupation = Column(String(200))
    
    # Monitoring Results
    rules_triggered = Column(JSON)  # List of rule IDs triggered
    alerts_generated = Column(Integer, default=0)
    requires_review = Column(Boolean, default=False, index=True)
    
    # Review Status
    review_status = Column(String(50), default='pending')  # pending, reviewed, escalated
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    
    # Additional Details
    transaction_purpose = Column(String(500))
    transaction_details = Column(JSON)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    alerts = relationship("AMLAlert", back_populates="transaction", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_aml_txn_date', 'tenant_id', 'transaction_date'),
        Index('idx_aml_txn_amount', 'tenant_id', 'transaction_amount'),
        Index('idx_aml_txn_risk', 'tenant_id', 'risk_level'),
        Index('idx_aml_txn_review', 'tenant_id', 'requires_review'),
    )


class AMLMonitoringRule(BaseModel):
    """AML monitoring rules configuration"""
    __tablename__ = "aml_monitoring_rules"
    
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(200), nullable=False)
    rule_type = Column(SQLEnum(MonitoringRuleType), nullable=False, index=True)
    
    description = Column(Text)
    
    # Rule Parameters
    threshold_amount = Column(Numeric(20, 2))
    threshold_count = Column(Integer)
    time_period_days = Column(Integer)  # For velocity checks
    
    # Risk Assignment
    risk_score_addition = Column(Numeric(5, 2), default=0)
    auto_risk_level = Column(SQLEnum(TransactionRiskLevel))
    
    # Configuration
    rule_config = Column(JSON)  # Detailed rule configuration
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=5)
    
    # Actions
    generate_alert = Column(Boolean, default=True)
    require_review = Column(Boolean, default=False)
    block_transaction = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_rule_active', 'tenant_id', 'is_active'),
    )


# ============================================================================
# AML ALERTS
# ============================================================================

class AMLAlert(BaseModel):
    """AML/CFT Alerts"""
    __tablename__ = "aml_alerts"
    
    alert_id = Column(String(50), unique=True, nullable=False, index=True)
    alert_type = Column(String(100), nullable=False, index=True)
    # large_cash, structured, velocity, pep, sanctions, geographic, etc.
    
    alert_category = Column(String(50), nullable=False)  # transaction, customer, relationship
    severity = Column(SQLEnum(TransactionRiskLevel), default=TransactionRiskLevel.MEDIUM, index=True)
    
    # References
    transaction_monitoring_id = Column(UUID(as_uuid=True), ForeignKey("aml_transaction_monitoring.id"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)
    
    # Alert Details
    alert_title = Column(String(500), nullable=False)
    alert_description = Column(Text)
    rule_triggered = Column(String(100))
    
    # Risk
    risk_score = Column(Numeric(5, 2), default=0)
    risk_indicators = Column(JSON)  # List of risk indicators
    
    # Status & Workflow
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN, index=True)
    
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    assigned_at = Column(DateTime)
    
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    
    closed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    closed_at = Column(DateTime)
    
    # Investigation
    investigation_notes = Column(Text)
    supporting_documents = Column(JSON)  # Document references
    
    # Outcome
    false_positive = Column(Boolean, default=False)
    str_filed = Column(Boolean, default=False, index=True)  # STR filed for this alert
    str_id = Column(UUID(as_uuid=True), ForeignKey("aml_str_reports.id"))
    
    # SLA
    due_date = Column(DateTime, index=True)
    is_overdue = Column(Boolean, default=False, index=True)
    escalation_level = Column(Integer, default=0)
    
    # Relationships
    transaction = relationship("AMLTransactionMonitoring", back_populates="alerts")
    customer = relationship("Customer", foreign_keys=[customer_id])
    str_report = relationship("AMLSTRReport", foreign_keys=[str_id])
    
    __table_args__ = (
        Index('idx_aml_alert_status', 'tenant_id', 'status'),
        Index('idx_aml_alert_assigned', 'tenant_id', 'assigned_to', 'status'),
    )


# ============================================================================
# CTR (CASH TRANSACTION REPORT)
# ============================================================================

class AMLCTRReport(BaseModel):
    """Cash Transaction Reports (₹10 Lakh threshold)"""
    __tablename__ = "aml_ctr_reports"
    
    ctr_number = Column(String(50), unique=True, nullable=False, index=True)
    reporting_month = Column(String(7), nullable=False, index=True)  # YYYY-MM
    reporting_date = Column(Date, nullable=False)
    
    # Transaction Details
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)  # cash_deposit, cash_withdrawal
    transaction_amount = Column(Numeric(20, 2), nullable=False)
    
    # Customer Details
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    customer_name = Column(String(300), nullable=False)
    customer_type = Column(String(50))  # individual, business
    
    pan_number = Column(String(10), index=True)
    aadhaar_number = Column(String(12))
    passport_number = Column(String(50))
    
    customer_address = Column(Text)
    customer_phone = Column(String(20))
    
    occupation = Column(String(200))
    nature_of_business = Column(String(300))
    
    # Account Details
    account_number = Column(String(50), nullable=False)
    account_type = Column(String(50))
    
    # Branch Details
    branch_code = Column(String(50))
    branch_name = Column(String(200))
    
    # Transaction Mode
    mode_of_transaction = Column(String(100))  # cash, bearer_cheque, demand_draft
    currency = Column(String(3), default='INR')
    
    # Verification
    identity_verified = Column(Boolean, default=False)
    verification_document_type = Column(String(100))
    verification_document_number = Column(String(100))
    
    # Reporting Status
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT, index=True)
    
    prepared_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    prepared_at = Column(DateTime)
    
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    
    submitted_to_fiu = Column(Boolean, default=False, index=True)
    fiu_submission_date = Column(DateTime)
    fiu_reference_number = Column(String(100))
    
    # Remarks
    remarks = Column(Text)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    
    __table_args__ = (
        Index('idx_ctr_month', 'tenant_id', 'reporting_month'),
        Index('idx_ctr_date', 'tenant_id', 'transaction_date'),
        Index('idx_ctr_customer', 'tenant_id', 'customer_id'),
    )


# ============================================================================
# STR (SUSPICIOUS TRANSACTION REPORT)
# ============================================================================

class AMLSTRReport(BaseModel):
    """Suspicious Transaction Reports to FIU-IND"""
    __tablename__ = "aml_str_reports"
    
    str_number = Column(String(50), unique=True, nullable=False, index=True)
    report_date = Column(Date, nullable=False, index=True)
    
    # Customer/Subject Details
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    customer_name = Column(String(300), nullable=False)
    customer_type = Column(String(50))
    
    pan_number = Column(String(10))
    aadhaar_number = Column(String(12))
    passport_number = Column(String(50))
    
    customer_address = Column(Text)
    customer_phone = Column(String(20))
    customer_email = Column(String(200))
    
    date_of_birth = Column(Date)
    nationality = Column(String(100))
    occupation = Column(String(200))
    
    # Account Details
    account_numbers = Column(JSON)  # List of involved account numbers
    
    # Suspicious Activity Details
    suspicious_activity_type = Column(String(100), nullable=False)
    # structuring, unusual_pattern, high_risk_country, pep_related, etc.
    
    activity_start_date = Column(Date)
    activity_end_date = Column(Date)
    
    total_amount_involved = Column(Numeric(20, 2), nullable=False)
    number_of_transactions = Column(Integer, default=1)
    
    # Description
    suspicious_activity_description = Column(Text, nullable=False)
    reason_for_suspicion = Column(Text, nullable=False)
    
    # Related Transactions
    transaction_ids = Column(JSON)  # List of transaction IDs
    
    # Related Alerts
    alert_ids = Column(JSON)  # List of alert IDs that led to this STR
    
    # Risk Assessment
    risk_level = Column(SQLEnum(TransactionRiskLevel), default=TransactionRiskLevel.HIGH)
    risk_indicators = Column(JSON)
    
    # Investigation
    investigation_summary = Column(Text)
    supporting_documents = Column(JSON)  # Document references
    
    # Related Parties
    related_parties = Column(JSON)  # Other involved parties
    
    # Status & Workflow
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT, index=True)
    
    prepared_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    prepared_at = Column(DateTime)
    
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_remarks = Column(Text)
    
    # FIU Submission
    submitted_to_fiu = Column(Boolean, default=False, index=True)
    fiu_submission_date = Column(DateTime, index=True)
    fiu_reference_number = Column(String(100))
    fiu_acknowledgment = Column(String(200))
    
    # Follow-up
    law_enforcement_notified = Column(Boolean, default=False)
    follow_up_actions = Column(JSON)
    
    # Confidentiality
    is_confidential = Column(Boolean, default=True)
    customer_notified = Column(Boolean, default=False)  # Should always be False as per regulations
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    
    __table_args__ = (
        Index('idx_str_date', 'tenant_id', 'report_date'),
        Index('idx_str_status', 'tenant_id', 'status'),
        Index('idx_str_customer', 'tenant_id', 'customer_id'),
    )


# ============================================================================
# PEP SCREENING
# ============================================================================

class AMLPEPScreening(BaseModel):
    """Politically Exposed Person Screening"""
    __tablename__ = "aml_pep_screening"
    
    screening_id = Column(String(50), unique=True, nullable=False, index=True)
    screening_date = Column(DateTime, nullable=False, index=True)
    
    # Subject Details
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    customer_name = Column(String(300), nullable=False)
    
    date_of_birth = Column(Date)
    nationality = Column(String(100))
    
    # Screening Type
    screening_type = Column(String(50), nullable=False)  # onboarding, periodic, transaction_based
    trigger_event = Column(String(100))  # new_customer, annual_review, high_value_transaction
    
    # Screening Result
    screening_status = Column(SQLEnum(ScreeningStatus), default=ScreeningStatus.PENDING_REVIEW, index=True)
    
    is_pep = Column(Boolean, default=False, index=True)
    pep_category = Column(SQLEnum(PEPCategory))
    
    # Match Details
    match_score = Column(Numeric(5, 2))  # 0-100
    match_details = Column(JSON)
    
    # PEP Information (if matched)
    pep_position = Column(String(300))
    pep_organization = Column(String(300))
    pep_country = Column(String(100))
    pep_start_date = Column(Date)
    pep_end_date = Column(Date)  # NULL if still active
    
    # Enhanced Due Diligence
    edd_required = Column(Boolean, default=False)
    edd_completed = Column(Boolean, default=False)
    edd_completion_date = Column(Date)
    edd_summary = Column(Text)
    
    # Source of Wealth (for PEPs)
    source_of_wealth = Column(Text)
    source_of_funds = Column(Text)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_remarks = Column(Text)
    
    # Risk Rating
    risk_rating = Column(String(20))  # low, medium, high, very_high
    
    # Review Schedule
    next_review_date = Column(Date, index=True)
    review_frequency_months = Column(Integer, default=12)
    
    # Screening Source
    screening_source = Column(String(100))  # internal_list, external_api, manual
    external_screening_reference = Column(String(200))
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    
    __table_args__ = (
        Index('idx_pep_customer', 'tenant_id', 'customer_id'),
        Index('idx_pep_status', 'tenant_id', 'screening_status'),
        Index('idx_pep_is_pep', 'tenant_id', 'is_pep'),
    )


# ============================================================================
# SANCTION LIST SCREENING
# ============================================================================

class AMLSanctionList(BaseModel):
    """Sanction Lists Master Data"""
    __tablename__ = "aml_sanction_lists"
    
    list_id = Column(String(50), unique=True, nullable=False, index=True)
    list_name = Column(String(200), nullable=False)
    list_type = Column(String(100), nullable=False, index=True)
    # UN, OFAC, EU, DFAT, HMT, domestic_terror, etc.
    
    list_source = Column(String(200))
    list_url = Column(String(500))
    
    # Subject Details
    entity_name = Column(String(500), nullable=False, index=True)
    entity_type = Column(String(50))  # individual, organization, vessel, aircraft
    
    aliases = Column(JSON)  # List of known aliases
    
    date_of_birth = Column(Date)
    place_of_birth = Column(String(200))
    nationality = Column(String(100))
    
    passport_numbers = Column(JSON)
    identification_numbers = Column(JSON)
    
    addresses = Column(JSON)
    
    # Sanction Details
    sanction_type = Column(String(100))  # financial, travel, arms, etc.
    sanction_reason = Column(Text)
    designation_date = Column(Date, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    removal_date = Column(Date)
    
    # Additional Information
    additional_info = Column(JSON)
    
    # Data Management
    last_updated = Column(DateTime, nullable=False)
    data_source_version = Column(String(50))
    
    __table_args__ = (
        Index('idx_sanction_name', 'tenant_id', 'entity_name'),
        Index('idx_sanction_type', 'tenant_id', 'list_type'),
        Index('idx_sanction_active', 'tenant_id', 'is_active'),
    )


class AMLSanctionScreening(BaseModel):
    """Sanction List Screening Results"""
    __tablename__ = "aml_sanction_screening"
    
    screening_id = Column(String(50), unique=True, nullable=False, index=True)
    screening_date = Column(DateTime, nullable=False, index=True)
    
    # Subject Details
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    customer_name = Column(String(300), nullable=False)
    
    screening_name = Column(String(300))  # Name used for screening (might be alias)
    date_of_birth = Column(Date)
    nationality = Column(String(100))
    
    # Screening Type
    screening_type = Column(String(50), nullable=False)  # onboarding, periodic, transaction_based, ad_hoc
    trigger_event = Column(String(100))
    
    # Screening Result
    screening_status = Column(SQLEnum(ScreeningStatus), default=ScreeningStatus.PENDING_REVIEW, index=True)
    
    is_match_found = Column(Boolean, default=False, index=True)
    match_type = Column(String(50))  # exact, fuzzy, partial
    match_score = Column(Numeric(5, 2))  # 0-100
    
    # Match Details
    matched_list_id = Column(UUID(as_uuid=True), ForeignKey("aml_sanction_lists.id"))
    matched_list_name = Column(String(200))
    match_details = Column(JSON)
    
    # Risk Assessment
    risk_level = Column(SQLEnum(TransactionRiskLevel), default=TransactionRiskLevel.CRITICAL)
    
    # Review & Decision
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    
    decision = Column(String(50))  # true_positive, false_positive, escalated
    decision_rationale = Column(Text)
    
    # Actions Taken
    account_blocked = Column(Boolean, default=False)
    transaction_blocked = Column(Boolean, default=False)
    authorities_notified = Column(Boolean, default=False)
    
    action_details = Column(JSON)
    
    # Next Review
    next_review_date = Column(Date, index=True)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    sanction_list = relationship("AMLSanctionList", foreign_keys=[matched_list_id])
    
    __table_args__ = (
        Index('idx_screening_customer', 'tenant_id', 'customer_id'),
        Index('idx_screening_status', 'tenant_id', 'screening_status'),
        Index('idx_screening_match', 'tenant_id', 'is_match_found'),
    )


# ============================================================================
# ALERT MANAGEMENT
# ============================================================================

class AMLAlertWorkflow(BaseModel):
    """Alert workflow and assignment tracking"""
    __tablename__ = "aml_alert_workflows"
    
    alert_id = Column(UUID(as_uuid=True), ForeignKey("aml_alerts.id"), nullable=False, index=True)
    
    # Workflow Step
    workflow_step = Column(String(50), nullable=False)  # l1_review, l2_review, investigation, closure
    step_sequence = Column(Integer, default=1)
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Status
    status = Column(String(50), default='pending')  # pending, in_progress, completed, rejected
    
    # Completion
    completed_at = Column(DateTime)
    completion_notes = Column(Text)
    
    # SLA
    sla_due_date = Column(DateTime)
    is_breached = Column(Boolean, default=False)
    
    # Relationships
    alert = relationship("AMLAlert", foreign_keys=[alert_id])
    
    __table_args__ = (
        Index('idx_workflow_alert', 'tenant_id', 'alert_id'),
        Index('idx_workflow_assigned', 'tenant_id', 'assigned_to', 'status'),
    )


class AMLAuditLog(BaseModel):
    """Comprehensive audit log for AML activities"""
    __tablename__ = "aml_audit_logs"
    
    # Event Details
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), nullable=False)  # screening, monitoring, reporting, alert
    
    event_date = Column(DateTime, nullable=False, index=True)
    
    # User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    user_name = Column(String(200))
    user_role = Column(String(100))
    
    # References
    reference_type = Column(String(50))  # transaction, alert, customer, report
    reference_id = Column(String(100), index=True)
    
    # Action
    action = Column(String(200), nullable=False)
    action_details = Column(JSON)
    
    # Changes (for updates)
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # Context
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Results
    result = Column(String(50))  # success, failure, partial
    error_message = Column(Text)
    
    __table_args__ = (
        Index('idx_aml_audit_event', 'tenant_id', 'event_type', 'event_date'),
        Index('idx_aml_audit_user', 'tenant_id', 'user_id', 'event_date'),
        Index('idx_aml_audit_reference', 'tenant_id', 'reference_type', 'reference_id'),
    )
