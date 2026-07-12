"""
Legal License Management Models
Database models for license register, renewal tracking, and compliance management
"""

from sqlalchemy import Column, String, Text, DateTime, Date, Numeric, Boolean, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from backend.shared.database.connection import Base


class LicenseType(str, enum.Enum):
    """License type enumeration"""
    NBFC_REGISTRATION = "nbfc_registration"
    RBI_LICENSE = "rbi_license"
    SEBI_LICENSE = "sebi_license"
    BUSINESS_LICENSE = "business_license"
    TRADE_LICENSE = "trade_license"
    PROFESSIONAL_LICENSE = "professional_license"
    ENVIRONMENTAL_LICENSE = "environmental_license"
    FIRE_SAFETY = "fire_safety"
    POLLUTION_CONTROL = "pollution_control"
    LABOR_LICENSE = "labor_license"
    GST_REGISTRATION = "gst_registration"
    IMPORT_EXPORT_LICENSE = "import_export_license"
    SOFTWARE_LICENSE = "software_license"
    DATA_PROTECTION = "data_protection"
    REGULATORY = "regulatory"
    OPERATIONAL = "operational"
    OTHER = "other"


class LicenseStatus(str, enum.Enum):
    """License status enumeration"""
    ACTIVE = "active"
    PENDING_RENEWAL = "pending_renewal"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    REVOKED = "revoked"
    UNDER_REVIEW = "under_review"
    APPLIED = "applied"
    REJECTED = "rejected"


class RenewalStatus(str, enum.Enum):
    """Renewal status enumeration"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ComplianceStatus(str, enum.Enum):
    """Compliance status enumeration"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    REVIEW_REQUIRED = "review_required"
    NOT_APPLICABLE = "not_applicable"


class ReminderFrequency(str, enum.Enum):
    """Reminder frequency enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


class License(Base):
    """
    License Model
    Master license register with renewal tracking and compliance management
    """
    __tablename__ = "legal_licenses"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(String(100), nullable=False, index=True)
    
    # License Identification
    license_number = Column(String(200), nullable=False, index=True)
    license_name = Column(String(500), nullable=False)
    license_type = Column(SQLEnum(LicenseType), nullable=False, index=True)
    license_category = Column(String(200))  # Additional categorization
    description = Column(Text)
    
    # Status
    status = Column(SQLEnum(LicenseStatus), nullable=False, default=LicenseStatus.ACTIVE, index=True)
    
    # Issuing Authority
    issuing_authority = Column(String(500), nullable=False)
    authority_contact_person = Column(String(200))
    authority_email = Column(String(200))
    authority_phone = Column(String(50))
    authority_website = Column(String(500))
    authority_address = Column(Text)
    
    # Important Dates
    application_date = Column(Date, index=True)
    issue_date = Column(Date, nullable=False, index=True)
    effective_date = Column(Date, index=True)
    expiry_date = Column(Date, index=True)  # Null if perpetual
    last_renewal_date = Column(Date)
    next_renewal_date = Column(Date, index=True)
    
    # License Duration
    validity_period_months = Column(Integer)  # License validity in months
    is_perpetual = Column(Boolean, default=False)  # No expiry
    
    # Renewal Configuration
    is_renewable = Column(Boolean, default=True)
    auto_renewal_enabled = Column(Boolean, default=False)
    renewal_status = Column(SQLEnum(RenewalStatus), default=RenewalStatus.NOT_REQUIRED)
    renewal_notice_days = Column(Integer, default=60)  # Days before expiry to start renewal
    renewal_submission_deadline_days = Column(Integer, default=30)  # Days before expiry to submit renewal
    
    # Compliance Tracking
    compliance_status = Column(SQLEnum(ComplianceStatus), nullable=False, default=ComplianceStatus.COMPLIANT, index=True)
    last_compliance_check_date = Column(Date)
    next_compliance_check_date = Column(Date, index=True)
    compliance_requirements = Column(JSONB, default=list)  # List of compliance requirements
    compliance_notes = Column(Text)
    
    # Financial Information
    application_fee = Column(Numeric(20, 2))
    renewal_fee = Column(Numeric(20, 2))
    annual_fee = Column(Numeric(20, 2))
    penalty_for_late_renewal = Column(Numeric(20, 2))
    currency = Column(String(10), default="INR")
    
    # Responsible Personnel
    license_holder_name = Column(String(500))  # Person/Entity holding the license
    responsible_department = Column(String(200))
    responsible_person_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    backup_person_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Document Management
    license_document_url = Column(String(1000))  # License certificate
    application_document_url = Column(String(1000))
    supporting_documents = Column(JSONB, default=list)  # List of supporting document URLs
    
    # Conditions & Restrictions
    license_conditions = Column(JSONB, default=list)  # List of license conditions
    restrictions = Column(Text)
    scope_of_license = Column(Text)
    geographical_coverage = Column(String(500))  # State, National, International
    
    # Alert & Reminder Configuration
    alert_enabled = Column(Boolean, default=True)
    alert_days_before_expiry = Column(JSONB, default=list)  # e.g., [90, 60, 30, 15, 7]
    reminder_frequency = Column(SQLEnum(ReminderFrequency), default=ReminderFrequency.WEEKLY)
    last_alert_sent = Column(DateTime)
    alert_recipients = Column(JSONB, default=list)  # List of email addresses
    
    # Tracking
    total_reminders_sent = Column(Integer, default=0)
    escalation_triggered = Column(Boolean, default=False)
    escalation_date = Column(DateTime)
    escalation_to = Column(JSONB, default=list)  # List of escalation recipients
    
    # Risk Assessment
    criticality_level = Column(String(50))  # Low, Medium, High, Critical
    business_impact = Column(Text)  # Impact if license expires/revoked
    risk_of_non_compliance = Column(Text)
    
    # Audit Trail
    audit_log = Column(JSONB, default=list)  # Log of important changes
    
    # Metadata
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Notes
    notes = Column(Text)
    internal_remarks = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    renewals = relationship("LicenseRenewal", back_populates="license", cascade="all, delete-orphan")
    compliance_checks = relationship("LicenseComplianceCheck", back_populates="license", cascade="all, delete-orphan")
    documents = relationship("LicenseDocument", back_populates="license", cascade="all, delete-orphan")
    reminders = relationship("LicenseReminder", back_populates="license", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<License {self.license_number}: {self.license_name}>"


class LicenseRenewal(Base):
    """
    License Renewal Model
    Tracks renewal history and upcoming renewals
    """
    __tablename__ = "legal_license_renewals"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    license_id = Column(UUID(as_uuid=True), ForeignKey('legal_licenses.id'), nullable=False, index=True)
    
    # Renewal Information
    renewal_number = Column(Integer, nullable=False)  # 1st, 2nd, 3rd renewal
    renewal_status = Column(SQLEnum(RenewalStatus), nullable=False, default=RenewalStatus.PENDING)
    
    # Important Dates
    renewal_due_date = Column(Date, nullable=False, index=True)
    renewal_initiated_date = Column(Date)
    application_submitted_date = Column(Date)
    approval_received_date = Column(Date)
    renewal_completed_date = Column(Date)
    new_expiry_date = Column(Date)
    
    # Application Details
    application_number = Column(String(200))
    application_document_url = Column(String(1000))
    
    # Financial
    renewal_fee_paid = Column(Numeric(20, 2))
    late_fee_paid = Column(Numeric(20, 2))
    total_amount_paid = Column(Numeric(20, 2))
    payment_date = Column(Date)
    payment_reference = Column(String(200))
    payment_receipt_url = Column(String(1000))
    
    # Processing
    processing_days = Column(Integer)  # Days taken to complete renewal
    authority_reference_number = Column(String(200))
    
    # Changes
    terms_modified = Column(Boolean, default=False)
    modification_summary = Column(Text)
    conditions_changed = Column(Boolean, default=False)
    conditions_summary = Column(Text)
    
    # Approval Workflow
    submitted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approval_notes = Column(Text)
    rejection_reason = Column(Text)
    
    # Reminders
    reminder_sent_dates = Column(JSONB, default=list)  # List of dates when reminders were sent
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Relationships
    license = relationship("License", back_populates="renewals")
    
    def __repr__(self):
        return f"<LicenseRenewal #{self.renewal_number} for {self.license_id}>"


class LicenseComplianceCheck(Base):
    """
    License Compliance Check Model
    Periodic compliance verification and audit
    """
    __tablename__ = "legal_license_compliance_checks"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    license_id = Column(UUID(as_uuid=True), ForeignKey('legal_licenses.id'), nullable=False, index=True)
    
    # Check Information
    check_number = Column(Integer, nullable=False)
    check_date = Column(Date, nullable=False, index=True)
    check_type = Column(String(200))  # Routine, Audit, Inspection, Self-Assessment
    
    # Status
    compliance_status = Column(SQLEnum(ComplianceStatus), nullable=False, default=ComplianceStatus.COMPLIANT)
    overall_score = Column(Numeric(5, 2))  # Percentage or score
    
    # Checklist
    checklist_items = Column(JSONB, default=list)  # List of compliance items checked
    compliant_items = Column(Integer, default=0)
    non_compliant_items = Column(Integer, default=0)
    
    # Findings
    findings = Column(Text)  # Detailed findings
    non_compliance_issues = Column(JSONB, default=list)  # List of issues found
    recommendations = Column(Text)
    
    # Action Items
    action_required = Column(Boolean, default=False)
    action_items = Column(JSONB, default=list)  # List of corrective actions
    action_deadline = Column(Date)
    actions_completed = Column(Boolean, default=False)
    
    # Inspector/Auditor
    conducted_by = Column(String(500))  # Internal or external auditor
    inspector_name = Column(String(500))
    inspector_designation = Column(String(200))
    inspector_organization = Column(String(500))
    
    # Documentation
    report_document_url = Column(String(1000))
    evidence_documents = Column(JSONB, default=list)  # Supporting documents
    
    # Next Check
    next_check_due_date = Column(Date, index=True)
    check_frequency_months = Column(Integer, default=12)
    
    # Notes
    notes = Column(Text)
    internal_remarks = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Relationships
    license = relationship("License", back_populates="compliance_checks")
    
    def __repr__(self):
        return f"<LicenseComplianceCheck #{self.check_number} on {self.check_date}>"


class LicenseDocument(Base):
    """
    License Document Model
    All documents related to a license
    """
    __tablename__ = "legal_license_documents"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    license_id = Column(UUID(as_uuid=True), ForeignKey('legal_licenses.id'), nullable=False, index=True)
    renewal_id = Column(UUID(as_uuid=True), ForeignKey('legal_license_renewals.id'))  # Optional
    
    # Document Information
    document_name = Column(String(500), nullable=False)
    document_type = Column(String(200))  # Certificate, Application, Approval, Supporting, etc.
    description = Column(Text)
    
    # File Information
    file_name = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(100))  # MIME type
    file_url = Column(String(1000), nullable=False)
    file_hash = Column(String(256))  # SHA-256 hash
    
    # Document Details
    document_date = Column(Date)
    valid_from = Column(Date)
    valid_until = Column(Date)
    
    # Classification
    is_confidential = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    
    # Metadata
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Audit
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Relationships
    license = relationship("License", back_populates="documents")
    
    def __repr__(self):
        return f"<LicenseDocument {self.document_name}>"


class LicenseReminder(Base):
    """
    License Reminder Model
    Tracks all reminders sent for license renewals and compliance
    """
    __tablename__ = "legal_license_reminders"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    license_id = Column(UUID(as_uuid=True), ForeignKey('legal_licenses.id'), nullable=False, index=True)
    
    # Reminder Information
    reminder_type = Column(String(100), nullable=False)  # renewal, compliance, expiry, etc.
    reminder_date = Column(DateTime, nullable=False, index=True)
    days_before_due = Column(Integer)  # How many days before due date
    
    # Status
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    send_attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime)
    
    # Recipients
    recipients = Column(JSONB, default=list)  # List of email addresses
    cc_recipients = Column(JSONB, default=list)
    
    # Message
    subject = Column(String(500))
    message_body = Column(Text)
    
    # Response Tracking
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    acknowledged_at = Column(DateTime)
    
    # Escalation
    is_escalated = Column(Boolean, default=False)
    escalated_to = Column(JSONB, default=list)
    escalated_at = Column(DateTime)
    
    # Delivery Status
    delivery_status = Column(String(100))  # sent, delivered, failed, bounced
    error_message = Column(Text)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    license = relationship("License", back_populates="reminders")
    
    def __repr__(self):
        return f"<LicenseReminder for {self.license_id} on {self.reminder_date}>"
