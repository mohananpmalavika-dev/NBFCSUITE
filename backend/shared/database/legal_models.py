"""
Legal Contract Management Models
Database models for contract repository, lifecycle management, renewal tracking, and version control
"""

from sqlalchemy import Column, String, Text, DateTime, Date, Numeric, Boolean, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, date
from decimal import Decimal
import uuid
import enum

from backend.shared.database.connection import Base


class ContractType(str, enum.Enum):
    """Contract type enumeration"""
    VENDOR = "vendor"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    PARTNERSHIP = "partnership"
    LEASE = "lease"
    LICENSE = "license"
    SERVICE = "service"
    NDA = "nda"
    SLA = "sla"
    OTHER = "other"


class ContractStatus(str, enum.Enum):
    """Contract status enumeration"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"
    CANCELLED = "cancelled"


class RenewalStatus(str, enum.Enum):
    """Renewal status enumeration"""
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class PartyType(str, enum.Enum):
    """Contract party type enumeration"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    WITNESS = "witness"
    GUARANTOR = "guarantor"
    LEGAL_REPRESENTATIVE = "legal_representative"


class Contract(Base):
    """
    Contract Model
    Stores master contract information with lifecycle tracking
    """
    __tablename__ = "legal_contracts"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(String(100), nullable=False, index=True)
    
    # Contract Identification
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    contract_type = Column(SQLEnum(ContractType), nullable=False, index=True)
    description = Column(Text)
    
    # Contract Status & Lifecycle
    status = Column(SQLEnum(ContractStatus), nullable=False, default=ContractStatus.DRAFT, index=True)
    
    # Contract Dates
    effective_date = Column(Date, nullable=False, index=True)
    expiry_date = Column(Date, index=True)
    execution_date = Column(Date)
    termination_date = Column(Date)
    
    # Contract Value
    contract_value = Column(Numeric(20, 2))
    currency = Column(String(10), default="INR")
    
    # Renewal Information
    is_renewable = Column(Boolean, default=False)
    auto_renewal = Column(Boolean, default=False)
    renewal_notice_days = Column(Integer, default=90)  # Days before expiry to send renewal notice
    renewal_status = Column(SQLEnum(RenewalStatus), default=RenewalStatus.NOT_REQUIRED)
    
    # Version Control
    current_version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True, index=True)
    parent_contract_id = Column(UUID(as_uuid=True), ForeignKey('legal_contracts.id'), nullable=True)
    
    # Document Storage
    document_url = Column(String(1000))  # S3 or file system URL
    document_hash = Column(String(256))  # SHA-256 hash for integrity
    
    # Metadata
    tags = Column(JSONB, default=list)  # ["urgent", "confidential", etc.]
    custom_fields = Column(JSONB, default=dict)  # Flexible custom attributes
    
    # Audit & Tracking
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Alert Configuration
    alert_before_expiry_days = Column(Integer, default=30)
    last_alert_sent = Column(DateTime)
    
    # Notes & Comments
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan")
    renewals = relationship("ContractRenewal", back_populates="contract", cascade="all, delete-orphan")
    documents = relationship("ContractDocument", back_populates="contract", cascade="all, delete-orphan")
    parties = relationship("ContractParty", back_populates="contract", cascade="all, delete-orphan")
    
    # Self-referential for parent contract
    amendments = relationship("Contract", backref="parent_contract", remote_side=[id])
    
    def __repr__(self):
        return f"<Contract {self.contract_number}: {self.title}>"


class ContractVersion(Base):
    """
    Contract Version Model
    Tracks all versions of a contract for full audit trail
    """
    __tablename__ = "legal_contract_versions"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    contract_id = Column(UUID(as_uuid=True), ForeignKey('legal_contracts.id'), nullable=False, index=True)
    
    # Version Information
    version_number = Column(Integer, nullable=False)
    version_name = Column(String(200))  # e.g., "Initial Draft", "Amendment 1"
    
    # Version Content
    title = Column(String(500), nullable=False)
    description = Column(Text)
    contract_value = Column(Numeric(20, 2))
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    
    # Document Storage
    document_url = Column(String(1000), nullable=False)
    document_hash = Column(String(256))
    
    # Change Tracking
    changes_summary = Column(Text)  # Summary of what changed
    change_reason = Column(Text)  # Reason for the change
    
    # Metadata
    custom_fields = Column(JSONB, default=dict)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="versions")
    
    def __repr__(self):
        return f"<ContractVersion {self.version_number}: {self.version_name}>"


class ContractRenewal(Base):
    """
    Contract Renewal Model
    Tracks renewal history and upcoming renewals
    """
    __tablename__ = "legal_contract_renewals"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    contract_id = Column(UUID(as_uuid=True), ForeignKey('legal_contracts.id'), nullable=False, index=True)
    
    # Renewal Information
    renewal_number = Column(Integer, nullable=False)  # 1st renewal, 2nd renewal, etc.
    renewal_status = Column(SQLEnum(RenewalStatus), nullable=False, default=RenewalStatus.PENDING)
    
    # Renewal Dates
    renewal_due_date = Column(Date, nullable=False, index=True)
    renewal_initiated_date = Column(Date)
    renewal_completed_date = Column(Date)
    new_expiry_date = Column(Date)
    
    # Renewal Terms
    new_contract_value = Column(Numeric(20, 2))
    value_change_percentage = Column(Numeric(5, 2))  # % increase/decrease
    terms_modified = Column(Boolean, default=False)
    modification_summary = Column(Text)
    
    # Alerts
    alert_sent_date = Column(DateTime)
    reminder_count = Column(Integer, default=0)
    
    # Approval Workflow
    requested_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approval_date = Column(DateTime)
    approval_notes = Column(Text)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contract = relationship("Contract", back_populates="renewals")
    
    def __repr__(self):
        return f"<ContractRenewal #{self.renewal_number} for {self.contract_id}>"


class ContractDocument(Base):
    """
    Contract Document Model
    Stores supporting documents, attachments, and related files
    """
    __tablename__ = "legal_contract_documents"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    contract_id = Column(UUID(as_uuid=True), ForeignKey('legal_contracts.id'), nullable=False, index=True)
    
    # Document Information
    document_name = Column(String(500), nullable=False)
    document_type = Column(String(100))  # "agreement", "amendment", "addendum", "supporting"
    description = Column(Text)
    
    # File Information
    file_name = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(100))  # MIME type
    file_url = Column(String(1000), nullable=False)
    file_hash = Column(String(256))  # SHA-256 hash
    
    # Version
    version = Column(Integer, default=1)
    
    # Metadata
    tags = Column(JSONB, default=list)
    is_confidential = Column(Boolean, default=False)
    
    # Audit
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Relationships
    contract = relationship("Contract", back_populates="documents")
    
    def __repr__(self):
        return f"<ContractDocument {self.document_name}>"


class ContractParty(Base):
    """
    Contract Party Model
    Stores information about parties involved in a contract
    """
    __tablename__ = "legal_contract_parties"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    contract_id = Column(UUID(as_uuid=True), ForeignKey('legal_contracts.id'), nullable=False, index=True)
    
    # Party Information
    party_type = Column(SQLEnum(PartyType), nullable=False)
    party_name = Column(String(500), nullable=False)
    party_designation = Column(String(200))  # Title/Position
    organization_name = Column(String(500))
    
    # Contact Information
    email = Column(String(200))
    phone = Column(String(50))
    address = Column(Text)
    
    # Legal Information
    legal_entity_type = Column(String(100))  # "individual", "company", "llp", etc.
    registration_number = Column(String(200))  # Company registration, PAN, etc.
    
    # Signature Information
    is_signatory = Column(Boolean, default=False)
    signature_date = Column(Date)
    signature_url = Column(String(1000))  # Digital signature or scan
    
    # Metadata
    custom_fields = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contract = relationship("Contract", back_populates="parties")
    
    def __repr__(self):
        return f"<ContractParty {self.party_name} ({self.party_type})>"


class ContractTemplate(Base):
    """
    Contract Template Model
    Pre-defined contract templates for quick contract creation
    """
    __tablename__ = "legal_contract_templates"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(String(100), nullable=False, index=True)
    
    # Template Information
    template_name = Column(String(500), nullable=False)
    template_code = Column(String(100), unique=True, nullable=False)
    contract_type = Column(SQLEnum(ContractType), nullable=False)
    description = Column(Text)
    
    # Template Content
    template_content = Column(Text)  # Rich text or HTML template
    template_url = Column(String(1000))  # Document template file
    
    # Configuration
    default_values = Column(JSONB, default=dict)  # Default field values
    required_fields = Column(JSONB, default=list)  # List of required fields
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ContractTemplate {self.template_name}>"


# ============================================================================
# LITIGATION MANAGEMENT MODELS
# Case Tracking, Hearing Management, Legal Expense Tracking
# ============================================================================

class CaseType(str, enum.Enum):
    """Case type enumeration"""
    CIVIL = "civil"
    CRIMINAL = "criminal"
    ARBITRATION = "arbitration"
    RECOVERY = "recovery"
    CONSUMER = "consumer"
    LABOR = "labor"
    TAX = "tax"
    CORPORATE = "corporate"
    PROPERTY = "property"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    BANKING = "banking"
    REGULATORY = "regulatory"
    WRIT = "writ"
    APPEAL = "appeal"
    OTHER = "other"


class CaseStatus(str, enum.Enum):
    """Case status enumeration"""
    FILED = "filed"
    ADMITTED = "admitted"
    IN_PROGRESS = "in_progress"
    EVIDENCE_STAGE = "evidence_stage"
    ARGUMENT_STAGE = "argument_stage"
    JUDGMENT_RESERVED = "judgment_reserved"
    JUDGMENT_DELIVERED = "judgment_delivered"
    DISPOSED = "disposed"
    WON = "won"
    LOST = "lost"
    SETTLED = "settled"
    WITHDRAWN = "withdrawn"
    DISMISSED = "dismissed"
    APPEALED = "appealed"
    STAYED = "stayed"


class CasePriority(str, enum.Enum):
    """Case priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class PartyRole(str, enum.Enum):
    """Party role in litigation"""
    PETITIONER = "petitioner"
    RESPONDENT = "respondent"
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    APPELLANT = "appellant"
    RESPONDENT_APPELLANT = "respondent_appellant"
    WITNESS = "witness"
    ADVOCATE = "advocate"
    THIRD_PARTY = "third_party"


class HearingType(str, enum.Enum):
    """Hearing type enumeration"""
    FIRST_HEARING = "first_hearing"
    REGULAR_HEARING = "regular_hearing"
    INTERIM_APPLICATION = "interim_application"
    EVIDENCE_RECORDING = "evidence_recording"
    CROSS_EXAMINATION = "cross_examination"
    ARGUMENT = "argument"
    FINAL_ARGUMENT = "final_argument"
    JUDGMENT = "judgment"
    EXECUTION = "execution"
    OTHER = "other"


class HearingStatus(str, enum.Enum):
    """Hearing status enumeration"""
    SCHEDULED = "scheduled"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    ADJOURNED = "adjourned"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ExpenseCategory(str, enum.Enum):
    """Legal expense category"""
    COURT_FEES = "court_fees"
    ADVOCATE_FEES = "advocate_fees"
    CONSULTATION_FEES = "consultation_fees"
    DOCUMENTATION = "documentation"
    TRAVEL = "travel"
    EXPERT_WITNESS = "expert_witness"
    INVESTIGATION = "investigation"
    STAMP_DUTY = "stamp_duty"
    NOTARY = "notary"
    TRANSLATION = "translation"
    PHOTOCOPYING = "photocopying"
    MISC = "misc"


class LitigationCase(Base):
    """
    Litigation Case Model
    Master case tracking with complete lifecycle management
    """
    __tablename__ = "legal_litigation_cases"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(String(100), nullable=False, index=True)
    
    # Case Identification
    case_number = Column(String(200), unique=True, nullable=False, index=True)
    case_title = Column(String(1000), nullable=False)
    case_type = Column(SQLEnum(CaseType), nullable=False, index=True)
    case_sub_type = Column(String(200))  # More specific classification
    
    # Case Status & Priority
    status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.FILED, index=True)
    priority = Column(SQLEnum(CasePriority), nullable=False, default=CasePriority.MEDIUM)
    
    # Court Information
    court_name = Column(String(500), nullable=False)
    court_location = Column(String(500))
    bench = Column(String(200))  # Single bench, Division bench, etc.
    judge_name = Column(String(500))
    
    # Case Details
    description = Column(Text)
    subject_matter = Column(Text)  # Subject matter of the case
    relief_sought = Column(Text)  # Relief or remedy sought
    
    # Financial Information
    claim_amount = Column(Numeric(20, 2))  # Amount claimed
    disputed_amount = Column(Numeric(20, 2))  # Amount in dispute
    awarded_amount = Column(Numeric(20, 2))  # Amount awarded
    currency = Column(String(10), default="INR")
    
    # Important Dates
    filing_date = Column(Date, nullable=False, index=True)
    admission_date = Column(Date)
    first_hearing_date = Column(Date, index=True)
    next_hearing_date = Column(Date, index=True)
    expected_closure_date = Column(Date)
    closure_date = Column(Date)
    limitation_date = Column(Date)  # Limitation period expiry
    
    # Related Cases
    parent_case_id = Column(UUID(as_uuid=True), ForeignKey('legal_litigation_cases.id'))
    related_case_numbers = Column(JSONB, default=list)  # List of related case numbers
    
    # Case Outcome
    judgment_date = Column(Date)
    judgment_summary = Column(Text)
    judgment_document_url = Column(String(1000))
    is_favorable = Column(Boolean)
    
    # Legal Team
    primary_advocate = Column(String(500))
    primary_advocate_contact = Column(String(100))
    advocate_firm = Column(String(500))
    internal_counsel_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Risk & Impact Assessment
    risk_level = Column(String(50))  # Low, Medium, High
    business_impact = Column(Text)
    potential_liability = Column(Numeric(20, 2))
    
    # Alerts & Reminders
    alert_before_hearing_days = Column(Integer, default=7)
    last_alert_sent = Column(DateTime)
    
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
    hearings = relationship("CaseHearing", back_populates="case", cascade="all, delete-orphan")
    expenses = relationship("LegalExpense", back_populates="case", cascade="all, delete-orphan")
    parties = relationship("CaseParty", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("CaseDocument", back_populates="case", cascade="all, delete-orphan")
    
    # Self-referential for parent case
    related_cases = relationship("LitigationCase", backref="parent_case", remote_side=[id])
    
    def __repr__(self):
        return f"<LitigationCase {self.case_number}: {self.case_title}>"


class CaseHearing(Base):
    """
    Case Hearing Model
    Tracks all hearings and court appearances
    """
    __tablename__ = "legal_case_hearings"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    case_id = Column(UUID(as_uuid=True), ForeignKey('legal_litigation_cases.id'), nullable=False, index=True)
    
    # Hearing Details
    hearing_number = Column(Integer, nullable=False)  # Sequential hearing number
    hearing_type = Column(SQLEnum(HearingType), nullable=False)
    hearing_status = Column(SQLEnum(HearingStatus), nullable=False, default=HearingStatus.SCHEDULED)
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    actual_date = Column(DateTime)
    duration_minutes = Column(Integer)  # Actual duration
    
    # Court Information
    court_room = Column(String(100))
    judge_name = Column(String(500))
    
    # Hearing Purpose & Outcome
    purpose = Column(Text)  # Purpose of hearing
    agenda = Column(Text)  # Agenda items
    proceedings = Column(Text)  # What happened in court
    orders_passed = Column(Text)  # Orders/directions by court
    next_action_required = Column(Text)
    
    # Next Hearing
    next_hearing_date = Column(DateTime, index=True)
    adjournment_reason = Column(String(500))
    
    # Attendance
    advocate_attended = Column(Boolean, default=True)
    advocate_name = Column(String(500))
    client_attended = Column(Boolean, default=False)
    opposing_party_attended = Column(Boolean)
    
    # Documents Submitted
    documents_submitted = Column(JSONB, default=list)  # List of document names
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_date = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Relationships
    case = relationship("LitigationCase", back_populates="hearings")
    
    def __repr__(self):
        return f"<CaseHearing #{self.hearing_number} on {self.scheduled_date}>"


class LegalExpense(Base):
    """
    Legal Expense Model
    Tracks all legal expenses and costs
    """
    __tablename__ = "legal_expenses"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant isolation
    tenant_id = Column(String(100), nullable=False, index=True)
    
    # Foreign Keys
    case_id = Column(UUID(as_uuid=True), ForeignKey('legal_litigation_cases.id'), nullable=False, index=True)
    
    # Expense Details
    expense_number = Column(String(100), unique=True, nullable=False, index=True)
    expense_category = Column(SQLEnum(ExpenseCategory), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Amount Information
    amount = Column(Numeric(20, 2), nullable=False)
    currency = Column(String(10), default="INR")
    tax_amount = Column(Numeric(20, 2))
    total_amount = Column(Numeric(20, 2), nullable=False)
    
    # Date & Payment
    expense_date = Column(Date, nullable=False, index=True)
    payment_date = Column(Date)
    payment_mode = Column(String(100))  # Cash, Cheque, NEFT, UPI, etc.
    payment_reference = Column(String(200))
    
    # Vendor/Payee Information
    payee_name = Column(String(500), nullable=False)
    payee_contact = Column(String(100))
    payee_pan = Column(String(50))
    payee_bank_details = Column(JSONB, default=dict)
    
    # Invoice Details
    invoice_number = Column(String(200))
    invoice_date = Column(Date)
    invoice_url = Column(String(1000))  # Invoice document
    
    # Approval & Status
    is_approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approval_date = Column(DateTime)
    approval_remarks = Column(Text)
    
    is_paid = Column(Boolean, default=False)
    paid_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Reimbursement
    is_reimbursable = Column(Boolean, default=False)
    reimbursed_amount = Column(Numeric(20, 2))
    reimbursement_date = Column(Date)
    
    # Budgeting
    budget_head = Column(String(200))
    cost_center = Column(String(200))
    
    # Metadata
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Relationships
    case = relationship("LitigationCase", back_populates="expenses")
    
    def __repr__(self):
        return f"<LegalExpense {self.expense_number}: {self.amount}>"


class CaseParty(Base):
    """
    Case Party Model
    Parties involved in litigation (petitioner, respondent, advocates, etc.)
    """
    __tablename__ = "legal_case_parties"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    case_id = Column(UUID(as_uuid=True), ForeignKey('legal_litigation_cases.id'), nullable=False, index=True)
    
    # Party Information
    party_role = Column(SQLEnum(PartyRole), nullable=False, index=True)
    party_name = Column(String(500), nullable=False)
    party_designation = Column(String(200))
    organization_name = Column(String(500))
    
    # Contact Information
    email = Column(String(200))
    phone = Column(String(50))
    address = Column(Text)
    
    # Legal Representation
    is_represented = Column(Boolean, default=False)
    advocate_name = Column(String(500))
    advocate_firm = Column(String(500))
    advocate_contact = Column(String(100))
    advocate_email = Column(String(200))
    
    # Additional Details
    party_type = Column(String(100))  # Individual, Company, Government, etc.
    identification_number = Column(String(200))  # PAN, CIN, etc.
    
    # Metadata
    custom_fields = Column(JSONB, default=dict)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    case = relationship("LitigationCase", back_populates="parties")
    
    def __repr__(self):
        return f"<CaseParty {self.party_name} ({self.party_role})>"


class CaseDocument(Base):
    """
    Case Document Model
    Documents related to litigation cases
    """
    __tablename__ = "legal_case_documents"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    case_id = Column(UUID(as_uuid=True), ForeignKey('legal_litigation_cases.id'), nullable=False, index=True)
    hearing_id = Column(UUID(as_uuid=True), ForeignKey('legal_case_hearings.id'))  # Optional link to hearing
    
    # Document Information
    document_name = Column(String(500), nullable=False)
    document_type = Column(String(200))  # Plaint, Written Statement, Affidavit, Evidence, etc.
    document_category = Column(String(200))  # Pleading, Evidence, Order, Judgment, etc.
    description = Column(Text)
    
    # File Information
    file_name = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(100))  # MIME type
    file_url = Column(String(1000), nullable=False)
    file_hash = Column(String(256))  # SHA-256 hash
    
    # Document Details
    document_date = Column(Date)  # Date on the document
    filing_date = Column(Date)  # Date when filed in court
    is_confidential = Column(Boolean, default=False)
    
    # Metadata
    tags = Column(JSONB, default=list)
    version = Column(Integer, default=1)
    
    # Audit
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Soft Delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    
    # Relationships
    case = relationship("LitigationCase", back_populates="documents")
    
    def __repr__(self):
        return f"<CaseDocument {self.document_name}>"
