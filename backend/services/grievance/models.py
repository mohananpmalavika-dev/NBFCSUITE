"""
Grievance & Complaint Management - Database Models
"""

from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.orm import relationship
from backend.database import Base


class ComplaintStatus(str, Enum):
    """Complaint status enumeration"""
    REGISTERED = "REGISTERED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"
    ESCALATED = "ESCALATED"
    REJECTED = "REJECTED"


class ComplaintPriority(str, Enum):
    """Complaint priority levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    URGENT = "URGENT"


class ComplaintCategory(str, Enum):
    """Complaint category types"""
    PRODUCT_SERVICE = "PRODUCT_SERVICE"
    ACCOUNT_MANAGEMENT = "ACCOUNT_MANAGEMENT"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    COLLECTION_HARASSMENT = "COLLECTION_HARASSMENT"
    INTEREST_CHARGES = "INTEREST_CHARGES"
    DOCUMENT_ISSUES = "DOCUMENT_ISSUES"
    BRANCH_SERVICE = "BRANCH_SERVICE"
    DIGITAL_BANKING = "DIGITAL_BANKING"
    STAFF_BEHAVIOR = "STAFF_BEHAVIOR"
    FRAUD_SECURITY = "FRAUD_SECURITY"
    REGULATORY = "REGULATORY"
    OTHER = "OTHER"


class ChannelType(str, Enum):
    """Communication channel types"""
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    WEB_PORTAL = "WEB_PORTAL"
    MOBILE_APP = "MOBILE_APP"
    BRANCH_VISIT = "BRANCH_VISIT"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    LETTER = "LETTER"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    CHATBOT = "CHATBOT"


class EscalationLevel(str, Enum):
    """Escalation hierarchy levels"""
    LEVEL_0 = "LEVEL_0"  # Initial assignment
    LEVEL_1 = "LEVEL_1"  # Team Lead
    LEVEL_2 = "LEVEL_2"  # Manager
    LEVEL_3 = "LEVEL_3"  # Senior Manager
    LEVEL_4 = "LEVEL_4"  # Head of Department
    LEVEL_5 = "LEVEL_5"  # Executive Management
    OMBUDSMAN = "OMBUDSMAN"  # Banking Ombudsman


class OmbudsmanStatus(str, Enum):
    """Ombudsman case status"""
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    HEARING_SCHEDULED = "HEARING_SCHEDULED"
    AWARD_ISSUED = "AWARD_ISSUED"
    CLOSED = "CLOSED"
    WITHDRAWN = "WITHDRAWN"


class Complaint(Base):
    """Main complaint/grievance entity"""
    __tablename__ = "complaints"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    complaint_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer and reference information
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    customer_name = Column(String(200))
    customer_email = Column(String(100))
    customer_phone = Column(String(20))
    
    # Related entity (optional)
    related_entity_type = Column(String(50))  # loan, deposit, account, etc.
    related_entity_id = Column(Integer)
    
    # Complaint details
    category = Column(SQLEnum(ComplaintCategory), nullable=False, index=True)
    sub_category = Column(String(100))
    subject = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    
    # Channel and source
    channel = Column(SQLEnum(ChannelType), nullable=False, index=True)
    source_reference = Column(String(200))  # Email ID, Phone number, etc.
    
    # Status and priority
    status = Column(SQLEnum(ComplaintStatus), default=ComplaintStatus.REGISTERED, index=True)
    priority = Column(SQLEnum(ComplaintPriority), default=ComplaintPriority.MEDIUM, index=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), index=True)
    assigned_department = Column(String(100))
    assigned_at = Column(DateTime)
    
    # Dates and timeline
    registered_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_date = Column(DateTime)
    target_resolution_date = Column(DateTime)
    actual_resolution_date = Column(DateTime)
    closed_date = Column(DateTime)
    
    # SLA tracking
    sla_hours = Column(Integer, default=48)  # Default 48 hours
    sla_breach = Column(Boolean, default=False)
    sla_breach_hours = Column(Integer, default=0)
    
    # Resolution
    resolution = Column(Text)
    resolution_remarks = Column(Text)
    customer_satisfaction = Column(Integer)  # 1-5 rating
    
    # Financial impact (if any)
    compensation_amount = Column(Numeric(15, 2), default=0)
    compensation_paid = Column(Boolean, default=False)
    
    # Escalation tracking
    escalation_level = Column(SQLEnum(EscalationLevel), default=EscalationLevel.LEVEL_0)
    escalated_to_ombudsman = Column(Boolean, default=False)
    
    # Additional information
    is_regulatory = Column(Boolean, default=False)
    is_repeat = Column(Boolean, default=False)
    previous_complaint_id = Column(Integer, ForeignKey("complaints.id"))
    
    tags = Column(String(500))  # Comma-separated tags
    attachments = Column(Text)  # JSON array of file paths
    
    # Audit fields
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    escalations = relationship("ComplaintEscalation", back_populates="complaint", cascade="all, delete-orphan")
    channels_log = relationship("ComplaintChannel", back_populates="complaint", cascade="all, delete-orphan")
    ombudsman_case = relationship("OmbudsmanCase", back_populates="complaint", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_complaint_customer_status', 'customer_id', 'status'),
        Index('idx_complaint_assigned_status', 'assigned_to', 'status'),
        Index('idx_complaint_category_status', 'category', 'status'),
        Index('idx_complaint_sla_breach', 'sla_breach', 'status'),
        Index('idx_complaint_registered_date', 'registered_date'),
    )


class ComplaintChannel(Base):
    """Track all communication channels used for a complaint"""
    __tablename__ = "complaint_channels"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Channel details
    channel_type = Column(SQLEnum(ChannelType), nullable=False)
    communication_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    direction = Column(String(20))  # INBOUND, OUTBOUND
    
    # Communication content
    subject = Column(String(300))
    message = Column(Text)
    response = Column(Text)
    
    # Contact details
    from_address = Column(String(200))  # Email, phone, etc.
    to_address = Column(String(200))
    
    # Status
    is_customer_initiated = Column(Boolean, default=True)
    requires_response = Column(Boolean, default=False)
    response_sent = Column(Boolean, default=False)
    
    # Attachments
    attachments = Column(Text)  # JSON array
    
    # Metadata
    handled_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    complaint = relationship("Complaint", back_populates="channels_log")


class ComplaintEscalation(Base):
    """Track complaint escalations through hierarchy"""
    __tablename__ = "complaint_escalations"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Escalation details
    escalation_level = Column(SQLEnum(EscalationLevel), nullable=False, index=True)
    escalation_number = Column(Integer, default=1)  # Track how many times escalated
    
    # Reason and trigger
    escalation_reason = Column(String(50))  # SLA_BREACH, CUSTOMER_REQUEST, MANUAL, AUTO
    reason_details = Column(Text)
    is_auto_escalated = Column(Boolean, default=False)
    
    # Assignment
    escalated_from = Column(Integer, ForeignKey("users.id"))
    escalated_to = Column(Integer, ForeignKey("users.id"), index=True)
    escalated_to_department = Column(String(100))
    
    # Dates
    escalated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # SLA for escalation
    escalation_sla_hours = Column(Integer, default=24)  # Shorter SLA after escalation
    escalation_sla_breach = Column(Boolean, default=False)
    
    # Status and outcome
    status = Column(String(50), default="PENDING")  # PENDING, ACKNOWLEDGED, RESOLVED, REJECTED
    resolution_notes = Column(Text)
    action_taken = Column(Text)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    complaint = relationship("Complaint", back_populates="escalations")
    
    # Indexes
    __table_args__ = (
        Index('idx_escalation_complaint_level', 'complaint_id', 'escalation_level'),
        Index('idx_escalation_assigned_to', 'escalated_to', 'status'),
    )


class ComplaintSLA(Base):
    """SLA configuration for different complaint categories and priorities"""
    __tablename__ = "complaint_sla"

    id = Column(Integer, primary_key=True, index=True)
    
    # SLA criteria
    category = Column(SQLEnum(ComplaintCategory), index=True)
    priority = Column(SQLEnum(ComplaintPriority), index=True)
    channel = Column(SQLEnum(ChannelType))
    
    # SLA timelines (in hours)
    acknowledgement_hours = Column(Integer, default=2)
    resolution_hours = Column(Integer, default=48)
    escalation_hours = Column(Integer, default=24)
    
    # Escalation rules
    auto_escalate = Column(Boolean, default=True)
    escalation_level_1_hours = Column(Integer, default=24)
    escalation_level_2_hours = Column(Integer, default=48)
    escalation_level_3_hours = Column(Integer, default=72)
    
    # Notification settings
    send_reminder_before_hours = Column(Integer, default=4)
    notify_customer = Column(Boolean, default=True)
    notify_manager = Column(Boolean, default=True)
    
    # Regulatory requirements
    is_regulatory_complaint = Column(Boolean, default=False)
    regulatory_timeline_days = Column(Integer)  # RBI guidelines: 30 days
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_sla_category_priority', 'category', 'priority', 'is_active'),
    )


class OmbudsmanCase(Base):
    """Track cases escalated to Banking Ombudsman"""
    __tablename__ = "ombudsman_cases"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), unique=True, nullable=False)
    
    # Case identification
    ombudsman_case_number = Column(String(100), unique=True, index=True)
    ombudsman_office = Column(String(200))  # RBI Ombudsman office location
    
    # Submission details
    submitted_date = Column(DateTime)
    submission_reference = Column(String(100))
    grounds_of_complaint = Column(Text)  # Grounds under Banking Ombudsman Scheme
    
    # Documents
    documents_submitted = Column(Text)  # JSON array
    supporting_evidence = Column(Text)
    
    # Status and timeline
    status = Column(SQLEnum(OmbudsmanStatus), default=OmbudsmanStatus.PENDING, index=True)
    acknowledgement_date = Column(DateTime)
    hearing_date = Column(DateTime)
    award_date = Column(DateTime)
    closure_date = Column(DateTime)
    
    # Outcome
    award_details = Column(Text)
    compensation_awarded = Column(Numeric(15, 2))
    compensation_paid = Column(Boolean, default=False)
    compensation_paid_date = Column(DateTime)
    
    # Bank's response
    bank_response = Column(Text)
    bank_response_date = Column(DateTime)
    bank_representative = Column(String(200))
    
    # Appeal
    is_appealed = Column(Boolean, default=False)
    appeal_filed_by = Column(String(50))  # CUSTOMER, BANK
    appeal_date = Column(DateTime)
    appeal_outcome = Column(Text)
    
    # Compliance
    rbi_guidelines_followed = Column(Boolean, default=True)
    resolution_within_30_days = Column(Boolean)
    
    # Notes and remarks
    notes = Column(Text)
    internal_remarks = Column(Text)
    
    # Audit
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    complaint = relationship("Complaint", back_populates="ombudsman_case")
    
    # Indexes
    __table_args__ = (
        Index('idx_ombudsman_status', 'status'),
        Index('idx_ombudsman_submitted_date', 'submitted_date'),
    )
