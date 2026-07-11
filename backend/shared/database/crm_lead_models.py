"""
CRM Lead Management Models
Database models for lead capture, scoring, assignment, and tracking
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date,
    Numeric, ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from .base import Base, TimestampMixin, TenantMixin


# ============================================================================
# ENUMS
# ============================================================================

class LeadSource(str, Enum):
    """Lead source channels"""
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    PHONE_CALL = "phone_call"
    WALK_IN = "walk_in"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    PARTNER = "partner"
    CAMPAIGN = "campaign"
    EVENT = "event"
    DIRECT = "direct"
    OTHER = "other"


class LeadStatus(str, Enum):
    """Lead lifecycle status"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    NURTURING = "nurturing"
    CONVERTED = "converted"
    LOST = "lost"
    DUPLICATE = "duplicate"
    INVALID = "invalid"


class LeadPriority(str, Enum):
    """Lead priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class LeadTemperature(str, Enum):
    """Lead temperature/engagement level"""
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"


class FollowUpStatus(str, Enum):
    """Follow-up status"""
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class FollowUpType(str, Enum):
    """Follow-up activity types"""
    PHONE_CALL = "phone_call"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    MEETING = "meeting"
    SITE_VISIT = "site_visit"
    DOCUMENT_COLLECTION = "document_collection"
    OTHER = "other"


# ============================================================================
# LEAD MODEL
# ============================================================================

class Lead(Base, TenantMixin, TimestampMixin):
    """
    CRM Lead Management
    Captures leads from multiple channels with scoring and assignment
    """
    __tablename__ = "crm_leads"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    lead_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic Information
    source = Column(SQLEnum(LeadSource), nullable=False, default=LeadSource.DIRECT)
    source_details = Column(String(255), nullable=True)  # Campaign name, referral source, etc.
    
    # Contact Information
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=True)
    full_name = Column(String(255), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    mobile = Column(String(20), nullable=False, index=True)
    alternate_mobile = Column(String(20), nullable=True)
    
    # Demographics
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    pincode = Column(String(10), nullable=True)
    
    # Lead Classification
    product_interest = Column(String(100), nullable=True)  # Loan type, deposit type, etc.
    loan_amount_required = Column(Numeric(15, 2), nullable=True)
    monthly_income = Column(Numeric(15, 2), nullable=True)
    occupation = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True)
    
    # Lead Scoring
    lead_score = Column(Integer, default=0, index=True)
    score_breakdown = Column(JSON, nullable=True)  # Detailed scoring factors
    lead_temperature = Column(SQLEnum(LeadTemperature), default=LeadTemperature.COLD)
    
    # Lead Status
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    priority = Column(SQLEnum(LeadPriority), default=LeadPriority.MEDIUM)
    is_qualified = Column(Boolean, default=False, index=True)
    qualification_reason = Column(Text, nullable=True)
    
    # Assignment & Routing
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_to_branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    assigned_date = Column(DateTime, nullable=True)
    auto_assigned = Column(Boolean, default=False)
    assignment_rules_applied = Column(JSON, nullable=True)
    
    # Follow-up Tracking
    last_contacted_date = Column(DateTime, nullable=True)
    next_follow_up_date = Column(DateTime, nullable=True, index=True)
    follow_up_count = Column(Integer, default=0)
    response_time_hours = Column(Integer, nullable=True)  # Time to first response
    
    # Conversion Tracking
    is_converted = Column(Boolean, default=False, index=True)
    converted_date = Column(DateTime, nullable=True)
    converted_to_customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    converted_to_loan_application_id = Column(Integer, nullable=True)
    conversion_time_hours = Column(Integer, nullable=True)
    
    # Loss Tracking
    is_lost = Column(Boolean, default=False)
    lost_date = Column(DateTime, nullable=True)
    lost_reason = Column(String(255), nullable=True)
    lost_remarks = Column(Text, nullable=True)
    
    # Duplicate Detection
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_lead_id = Column(Integer, ForeignKey("crm_leads.id"), nullable=True)
    duplicate_checked_date = Column(DateTime, nullable=True)
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    utm_source = Column(String(100), nullable=True)  # Marketing tracking
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    utm_content = Column(String(255), nullable=True)
    referrer_url = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Audit Fields
    is_active = Column(Boolean, default=True, index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], backref="assigned_leads")
    branch = relationship("Branch", foreign_keys=[assigned_to_branch_id])
    customer = relationship("Customer", foreign_keys=[converted_to_customer_id])
    duplicate_of = relationship("Lead", remote_side=[id], backref="duplicates")
    follow_ups = relationship("LeadFollowUp", back_populates="lead", cascade="all, delete-orphan")
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_lead_status_assigned", "status", "assigned_to_user_id"),
        Index("idx_lead_score_temp", "lead_score", "lead_temperature"),
        Index("idx_lead_created", "created_at"),
        Index("idx_lead_mobile_email", "mobile", "email"),
        Index("idx_lead_next_followup", "next_follow_up_date", "is_active"),
    )
    
    def __repr__(self):
        return f"<Lead {self.lead_code} - {self.full_name} - {self.status.value}>"


# ============================================================================
# LEAD FOLLOW-UP MODEL
# ============================================================================

class LeadFollowUp(Base, TenantMixin, TimestampMixin):
    """
    Lead Follow-up Activities
    Tracks all follow-up activities and communications
    """
    __tablename__ = "crm_lead_followups"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Lead Reference
    lead_id = Column(Integer, ForeignKey("crm_leads.id"), nullable=False, index=True)
    
    # Follow-up Details
    follow_up_type = Column(SQLEnum(FollowUpType), nullable=False)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    completed_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(FollowUpStatus), default=FollowUpStatus.PENDING, index=True)
    
    # Assignment
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Details
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)  # Result after completion
    next_action = Column(Text, nullable=True)
    
    # Customer Response
    customer_interested = Column(Boolean, nullable=True)
    customer_response = Column(Text, nullable=True)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_date = Column(DateTime, nullable=True)
    
    # Duration
    duration_minutes = Column(Integer, nullable=True)
    
    # Audit
    completed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_cancelled = Column(Boolean, default=False)
    cancellation_reason = Column(String(255), nullable=True)
    
    # Relationships
    lead = relationship("Lead", back_populates="follow_ups")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], backref="lead_followups")
    completed_by = relationship("User", foreign_keys=[completed_by_user_id])
    
    __table_args__ = (
        Index("idx_followup_scheduled", "scheduled_date", "status"),
        Index("idx_followup_assigned", "assigned_to_user_id", "status"),
    )
    
    def __repr__(self):
        return f"<LeadFollowUp {self.id} - {self.follow_up_type.value} - {self.status.value}>"


# ============================================================================
# LEAD ACTIVITY MODEL
# ============================================================================

class LeadActivity(Base, TenantMixin, TimestampMixin):
    """
    Lead Activity Log
    Comprehensive audit trail of all lead interactions
    """
    __tablename__ = "crm_lead_activities"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Lead Reference
    lead_id = Column(Integer, ForeignKey("crm_leads.id"), nullable=False, index=True)
    
    # Activity Details
    activity_type = Column(String(50), nullable=False, index=True)  # status_change, assignment, call, email, etc.
    activity_title = Column(String(255), nullable=False)
    activity_description = Column(Text, nullable=True)
    
    # Activity Date
    activity_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # User Context
    performed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    performed_by_name = Column(String(255), nullable=True)
    
    # Change Tracking
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    
    # Additional Context
    metadata = Column(JSON, nullable=True)
    is_system_generated = Column(Boolean, default=False)
    
    # Relationships
    lead = relationship("Lead", back_populates="activities")
    performed_by = relationship("User", foreign_keys=[performed_by_user_id])
    
    __table_args__ = (
        Index("idx_activity_date_type", "activity_date", "activity_type"),
        Index("idx_activity_lead", "lead_id", "activity_date"),
    )
    
    def __repr__(self):
        return f"<LeadActivity {self.id} - {self.activity_type} - {self.activity_title}>"


# ============================================================================
# LEAD SCORING RULE MODEL
# ============================================================================

class LeadScoringRule(Base, TenantMixin, TimestampMixin):
    """
    Lead Scoring Rules
    Configurable rules for automatic lead scoring
    """
    __tablename__ = "crm_lead_scoring_rules"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule Definition
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text, nullable=True)
    rule_category = Column(String(100), nullable=False)  # demographics, behavior, engagement, etc.
    
    # Criteria
    field_name = Column(String(100), nullable=False)  # Field to evaluate
    operator = Column(String(50), nullable=False)  # equals, greater_than, contains, etc.
    field_value = Column(String(255), nullable=True)
    
    # Scoring
    score_points = Column(Integer, nullable=False)  # Points to add/subtract
    
    # Rule Status
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=1)
    
    # Execution Tracking
    execution_count = Column(Integer, default=0)
    last_executed_date = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<LeadScoringRule {self.rule_name} - {self.score_points} points>"


# ============================================================================
# LEAD ASSIGNMENT RULE MODEL
# ============================================================================

class LeadAssignmentRule(Base, TenantMixin, TimestampMixin):
    """
    Lead Assignment Rules
    Automatic routing and assignment of leads
    """
    __tablename__ = "crm_lead_assignment_rules"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule Definition
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text, nullable=True)
    
    # Priority
    priority = Column(Integer, default=1, index=True)  # Lower number = higher priority
    
    # Conditions (JSON format)
    conditions = Column(JSON, nullable=False)  # Complex conditions in JSON
    
    # Assignment Strategy
    assignment_type = Column(String(50), nullable=False)  # round_robin, load_balanced, territory, manual
    assign_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assign_to_branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    assign_to_team = Column(String(100), nullable=True)
    
    # Load Balancing
    max_leads_per_user = Column(Integer, nullable=True)
    
    # Rule Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Execution Tracking
    execution_count = Column(Integer, default=0)
    last_executed_date = Column(DateTime, nullable=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Relationships
    assign_to_user = relationship("User", foreign_keys=[assign_to_user_id])
    assign_to_branch = relationship("Branch", foreign_keys=[assign_to_branch_id])
    
    def __repr__(self):
        return f"<LeadAssignmentRule {self.rule_name} - Priority {self.priority}>"
