"""
CRM Customer Service Models
Includes: Ticket Management, Knowledge Base, SLA Tracking
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey, Enum, Numeric, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.shared.database.models import Base


# ==================== ENUMS ====================

class TicketPriority(str, enum.Enum):
    """Ticket Priority Levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    """Ticket Lifecycle Status"""
    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    PENDING_INTERNAL = "pending_internal"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    CANCELLED = "cancelled"


class TicketCategory(str, enum.Enum):
    """Ticket Categories"""
    ACCOUNT = "account"
    LOAN = "loan"
    DEPOSIT = "deposit"
    PAYMENT = "payment"
    TECHNICAL = "technical"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    REQUEST = "request"
    FEEDBACK = "feedback"
    OTHER = "other"


class TicketChannel(str, enum.Enum):
    """Ticket Source Channels"""
    PHONE = "phone"
    EMAIL = "email"
    WEB_PORTAL = "web_portal"
    MOBILE_APP = "mobile_app"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    WALK_IN = "walk_in"
    WHATSAPP = "whatsapp"


class SLAStatus(str, enum.Enum):
    """SLA Compliance Status"""
    WITHIN_SLA = "within_sla"
    APPROACHING_BREACH = "approaching_breach"
    BREACHED = "breached"
    PAUSED = "paused"


class KnowledgeBaseStatus(str, enum.Enum):
    """Knowledge Base Article Status"""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleCategory(str, enum.Enum):
    """Knowledge Base Categories"""
    GETTING_STARTED = "getting_started"
    ACCOUNT_MANAGEMENT = "account_management"
    LOAN_PRODUCTS = "loan_products"
    DEPOSIT_PRODUCTS = "deposit_products"
    PAYMENTS = "payments"
    TROUBLESHOOTING = "troubleshooting"
    FAQ = "faq"
    POLICIES = "policies"
    TECHNICAL = "technical"
    OTHER = "other"


# ==================== MODELS ====================

class Ticket(Base):
    """Support Ticket Model"""
    __tablename__ = "crm_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(200))
    customer_phone = Column(String(20))
    
    # Ticket Details
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(TicketCategory), nullable=False, index=True)
    priority = Column(Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM, index=True)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.NEW, index=True)
    channel = Column(Enum(TicketChannel), nullable=False)
    
    # Assignment
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    assigned_to_team = Column(String(100), index=True)
    assigned_at = Column(DateTime)
    
    # Resolution
    resolution = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by_user_id = Column(Integer, ForeignKey("users.id"))
    closed_at = Column(DateTime)
    closed_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # SLA Tracking
    sla_policy_id = Column(Integer, ForeignKey("crm_sla_policies.id"), index=True)
    sla_status = Column(Enum(SLAStatus), default=SLAStatus.WITHIN_SLA, index=True)
    sla_first_response_due = Column(DateTime)
    sla_first_response_at = Column(DateTime)
    sla_resolution_due = Column(DateTime)
    sla_paused_duration = Column(Integer, default=0)  # Minutes
    sla_breach_reason = Column(Text)
    
    # Ratings & Feedback
    customer_satisfaction_rating = Column(Integer)  # 1-5
    customer_feedback = Column(Text)
    
    # Tags & References
    tags = Column(JSON)  # Array of tags
    related_entity_type = Column(String(50))  # loan, deposit, account, etc.
    related_entity_id = Column(Integer)
    
    # Tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), index=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_user_id])
    closed_by = relationship("User", foreign_keys=[closed_by_user_id])
    sla_policy = relationship("SLAPolicy", back_populates="tickets")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    activities = relationship("TicketActivity", back_populates="ticket", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_ticket_customer_status', 'customer_id', 'status'),
        Index('idx_ticket_assigned_status', 'assigned_to_user_id', 'status'),
        Index('idx_ticket_priority_status', 'priority', 'status'),
        Index('idx_ticket_category_status', 'category', 'status'),
        Index('idx_ticket_sla_status', 'sla_status', 'status'),
        Index('idx_ticket_created', 'created_at'),
        Index('idx_ticket_tenant', 'tenant_id', 'status'),
    )


class TicketComment(Base):
    """Ticket Comments/Conversation"""
    __tablename__ = "crm_ticket_comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("crm_tickets.id"), nullable=False, index=True)
    
    # Comment Details
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal note or customer-visible
    is_solution = Column(Boolean, default=False)  # Mark as solution
    
    # Attachments
    has_attachments = Column(Boolean, default=False)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    created_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_comment_ticket', 'ticket_id', 'created_at'),
    )


class TicketAttachment(Base):
    """Ticket File Attachments"""
    __tablename__ = "crm_ticket_attachments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("crm_tickets.id"), nullable=False, index=True)
    comment_id = Column(Integer, ForeignKey("crm_ticket_comments.id"), index=True)
    
    # File Details
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # Bytes
    file_type = Column(String(100))
    mime_type = Column(String(100))
    
    # Audit
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    comment = relationship("TicketComment")
    uploaded_by = relationship("User")


class TicketActivity(Base):
    """Ticket Activity Log/Audit Trail"""
    __tablename__ = "crm_ticket_activities"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("crm_tickets.id"), nullable=False, index=True)
    
    # Activity Details
    activity_type = Column(String(50), nullable=False)  # created, assigned, status_changed, etc.
    description = Column(Text, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    metadata = Column(JSON)  # Additional context
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    ticket = relationship("Ticket", back_populates="activities")
    created_by = relationship("User")


class SLAPolicy(Base):
    """SLA Policy Definitions"""
    __tablename__ = "crm_sla_policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Conditions
    applies_to_priority = Column(JSON)  # Array of priorities
    applies_to_category = Column(JSON)  # Array of categories
    applies_to_channel = Column(JSON)  # Array of channels
    
    # SLA Targets (in minutes)
    first_response_time = Column(Integer, nullable=False)  # Minutes
    resolution_time = Column(Integer, nullable=False)  # Minutes
    escalation_time = Column(Integer)  # Minutes before escalation
    
    # Business Hours
    business_hours_only = Column(Boolean, default=True)
    business_start_hour = Column(Integer, default=9)  # 9 AM
    business_end_hour = Column(Integer, default=18)  # 6 PM
    include_weekends = Column(Boolean, default=False)
    
    # Escalation
    escalation_enabled = Column(Boolean, default=True)
    escalate_to_user_id = Column(Integer, ForeignKey("users.id"))
    escalate_to_team = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    priority_order = Column(Integer, default=0)  # For multiple policies
    
    # Tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    tickets = relationship("Ticket", back_populates="sla_policy")
    escalate_to = relationship("User")


class KnowledgeBaseArticle(Base):
    """Knowledge Base Articles"""
    __tablename__ = "crm_knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    article_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Article Content
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    summary = Column(Text)
    content = Column(Text, nullable=False)
    keywords = Column(JSON)  # Array of keywords
    
    # Categorization
    category = Column(Enum(ArticleCategory), nullable=False, index=True)
    tags = Column(JSON)  # Array of tags
    
    # Publishing
    status = Column(Enum(KnowledgeBaseStatus), nullable=False, default=KnowledgeBaseStatus.DRAFT, index=True)
    published_at = Column(DateTime)
    published_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Visibility
    is_public = Column(Boolean, default=True)  # Visible to customers
    is_internal = Column(Boolean, default=False)  # Only for staff
    
    # Related Articles
    related_articles = Column(JSON)  # Array of article IDs
    
    # Metrics
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    average_rating = Column(Numeric(3, 2))
    
    # Attachments
    attachments = Column(JSON)  # Array of file paths
    
    # SEO
    meta_description = Column(String(500))
    meta_keywords = Column(String(500))
    
    # Tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    updated_by = relationship("User", foreign_keys=[updated_by_user_id])
    published_by = relationship("User", foreign_keys=[published_by_user_id])
    feedbacks = relationship("KnowledgeBaseFeedback", back_populates="article", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_kb_status_category', 'status', 'category'),
        Index('idx_kb_published', 'published_at'),
        Index('idx_kb_tenant_status', 'tenant_id', 'status'),
    )


class KnowledgeBaseFeedback(Base):
    """Knowledge Base Article Feedback"""
    __tablename__ = "crm_kb_feedback"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("crm_knowledge_base.id"), nullable=False, index=True)
    
    # Feedback
    is_helpful = Column(Boolean, nullable=False)
    rating = Column(Integer)  # 1-5
    comment = Column(Text)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    article = relationship("KnowledgeBaseArticle", back_populates="feedbacks")
    user = relationship("User")
    customer = relationship("Customer")


class TicketTemplate(Base):
    """Ticket Response Templates"""
    __tablename__ = "crm_ticket_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(200), nullable=False)
    template_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Template Content
    subject_template = Column(String(500))
    content_template = Column(Text, nullable=False)
    
    # Usage
    category = Column(Enum(TicketCategory), index=True)
    usage_type = Column(String(50))  # response, resolution, auto_reply, etc.
    
    # Variables
    available_variables = Column(JSON)  # List of merge variables
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    created_by = relationship("User")
