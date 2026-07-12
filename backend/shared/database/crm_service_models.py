"""
CRM Customer Service Models
Ticket Management, Knowledge Base, SLA Tracking
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index, Enum as SQLEnum, DateTime, Boolean, Interval
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta

from backend.shared.database.models import BaseModel


# ============================================================================
# ENUMS
# ============================================================================

class TicketPriority(str, enum.Enum):
    """Ticket priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    """Ticket status enumeration"""
    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    PENDING_INTERNAL = "pending_internal"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketCategory(str, enum.Enum):
    """Ticket category enumeration"""
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    PRODUCT = "product"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"
    OTHER = "other"


class TicketChannel(str, enum.Enum):
    """Ticket source channel enumeration"""
    EMAIL = "email"
    PHONE = "phone"
    WEB = "web"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    WALK_IN = "walk_in"


class ArticleStatus(str, enum.Enum):
    """Knowledge article status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"


class ArticleCategory(str, enum.Enum):
    """Knowledge article category enumeration"""
    FAQ = "faq"
    HOW_TO = "how_to"
    TROUBLESHOOTING = "troubleshooting"
    POLICY = "policy"
    ANNOUNCEMENT = "announcement"
    GUIDE = "guide"


class SLAStatus(str, enum.Enum):
    """SLA status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class SLAMetricType(str, enum.Enum):
    """SLA metric type enumeration"""
    FIRST_RESPONSE = "first_response"
    RESOLUTION = "resolution"
    ESCALATION = "escalation"


# ============================================================================
# TICKET MODELS
# ============================================================================

class Ticket(BaseModel):
    """Ticket model for customer service requests"""
    __tablename__ = "crm_tickets"

    # Core Fields
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Customer Information
    account_id = Column(UUID(as_uuid=True), ForeignKey("crm_accounts.id"), nullable=True, index=True)
    contact_name = Column(String(200))
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    
    # Classification
    category = Column(SQLEnum(TicketCategory), nullable=False, index=True)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM, index=True)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.NEW, index=True)
    channel = Column(SQLEnum(TicketChannel), nullable=False, default=TicketChannel.WEB)
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    assigned_team = Column(String(100))
    
    # SLA Tracking
    sla_id = Column(UUID(as_uuid=True), ForeignKey("crm_slas.id"), nullable=True)
    first_response_due = Column(DateTime)
    resolution_due = Column(DateTime)
    first_response_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    sla_breached = Column(Boolean, default=False)
    
    # Related Information
    parent_ticket_id = Column(UUID(as_uuid=True), ForeignKey("crm_tickets.id"), nullable=True)
    related_article_id = Column(UUID(as_uuid=True), ForeignKey("crm_knowledge_articles.id"), nullable=True)
    
    # Additional Fields
    tags = Column(ARRAY(String), default=[])
    custom_fields = Column(Text)  # JSON string for extensibility
    
    # Satisfaction
    satisfaction_rating = Column(Integer)  # 1-5
    satisfaction_comment = Column(Text)
    
    # Relationships
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_crm_tickets_tenant', 'tenant_id'),
        Index('idx_crm_tickets_number', 'ticket_number'),
        Index('idx_crm_tickets_account', 'account_id'),
        Index('idx_crm_tickets_status', 'status'),
        Index('idx_crm_tickets_priority', 'priority'),
        Index('idx_crm_tickets_assigned', 'assigned_to'),
        Index('idx_crm_tickets_category', 'category'),
        Index('idx_crm_tickets_created', 'created_at'),
        Index('idx_crm_tickets_sla_breach', 'sla_breached'),
    )


class TicketComment(BaseModel):
    """Ticket comment/note model"""
    __tablename__ = "crm_ticket_comments"

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("crm_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_type = Column(String(50), default="comment")  # comment, internal_note, status_change, system
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes not visible to customer
    is_system = Column(Boolean, default=False)  # System-generated comments
    
    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    
    # Indexes
    __table_args__ = (
        Index('idx_crm_ticket_comments_ticket', 'ticket_id'),
        Index('idx_crm_ticket_comments_created', 'created_at'),
    )


class TicketAttachment(BaseModel):
    """Ticket attachment model"""
    __tablename__ = "crm_ticket_attachments"

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("crm_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(100))
    mime_type = Column(String(200))
    
    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    
    # Indexes
    __table_args__ = (
        Index('idx_crm_ticket_attachments_ticket', 'ticket_id'),
    )


# ============================================================================
# KNOWLEDGE BASE MODELS
# ============================================================================

class KnowledgeArticle(BaseModel):
    """Knowledge base article model"""
    __tablename__ = "crm_knowledge_articles"

    # Core Fields
    article_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)  # Short summary
    
    # Classification
    category = Column(SQLEnum(ArticleCategory), nullable=False, index=True)
    status = Column(SQLEnum(ArticleStatus), nullable=False, default=ArticleStatus.DRAFT, index=True)
    
    # Organization
    tags = Column(ARRAY(String), default=[])
    related_products = Column(ARRAY(String), default=[])
    
    # SEO & Search
    meta_description = Column(String(500))
    keywords = Column(ARRAY(String), default=[])
    
    # Authoring
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    published_at = Column(DateTime)
    
    # Analytics
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    
    # Versioning
    version = Column(Integer, default=1)
    is_featured = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    # Related Information
    parent_article_id = Column(UUID(as_uuid=True), ForeignKey("crm_knowledge_articles.id"), nullable=True)
    
    # Relationships
    attachments = relationship("ArticleAttachment", back_populates="article", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_crm_articles_tenant', 'tenant_id'),
        Index('idx_crm_articles_number', 'article_number'),
        Index('idx_crm_articles_slug', 'slug'),
        Index('idx_crm_articles_status', 'status'),
        Index('idx_crm_articles_category', 'category'),
        Index('idx_crm_articles_author', 'author_id'),
        Index('idx_crm_articles_published', 'published_at'),
        Index('idx_crm_articles_featured', 'is_featured'),
    )


class ArticleAttachment(BaseModel):
    """Knowledge article attachment model"""
    __tablename__ = "crm_article_attachments"

    article_id = Column(UUID(as_uuid=True), ForeignKey("crm_knowledge_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    mime_type = Column(String(200))
    display_order = Column(Integer, default=0)
    
    # Relationships
    article = relationship("KnowledgeArticle", back_populates="attachments")
    
    # Indexes
    __table_args__ = (
        Index('idx_crm_article_attachments_article', 'article_id'),
    )


# ============================================================================
# SLA MODELS
# ============================================================================

class SLA(BaseModel):
    """Service Level Agreement model"""
    __tablename__ = "crm_slas"

    # Core Fields
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(SLAStatus), nullable=False, default=SLAStatus.ACTIVE, index=True)
    
    # Applicability
    priority = Column(SQLEnum(TicketPriority), nullable=True, index=True)  # null = applies to all
    category = Column(SQLEnum(TicketCategory), nullable=True)  # null = applies to all
    
    # SLA Metrics (in minutes)
    first_response_time = Column(Integer, nullable=False)  # minutes
    resolution_time = Column(Integer, nullable=False)  # minutes
    escalation_time = Column(Integer)  # minutes
    
    # Business Hours
    use_business_hours = Column(Boolean, default=True)
    business_hours_start = Column(String(5), default="09:00")  # HH:MM format
    business_hours_end = Column(String(5), default="18:00")  # HH:MM format
    business_days = Column(ARRAY(Integer), default=[1, 2, 3, 4, 5])  # 1=Monday, 7=Sunday
    
    # Escalation
    escalate_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    escalation_enabled = Column(Boolean, default=False)
    
    # Priority & Ordering
    display_order = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_crm_slas_tenant', 'tenant_id'),
        Index('idx_crm_slas_status', 'status'),
        Index('idx_crm_slas_priority', 'priority'),
        Index('idx_crm_slas_default', 'is_default'),
    )


class SLAViolation(BaseModel):
    """SLA violation tracking model"""
    __tablename__ = "crm_sla_violations"

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("crm_tickets.id"), nullable=False, index=True)
    sla_id = Column(UUID(as_uuid=True), ForeignKey("crm_slas.id"), nullable=False, index=True)
    metric_type = Column(SQLEnum(SLAMetricType), nullable=False)
    
    # Timing
    due_at = Column(DateTime, nullable=False)
    violated_at = Column(DateTime, nullable=False)
    breach_duration = Column(Interval)  # How long the SLA was breached
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Escalation
    escalated = Column(Boolean, default=False)
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    escalated_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_crm_sla_violations_ticket', 'ticket_id'),
        Index('idx_crm_sla_violations_sla', 'sla_id'),
        Index('idx_crm_sla_violations_metric', 'metric_type'),
        Index('idx_crm_sla_violations_resolved', 'is_resolved'),
        Index('idx_crm_sla_violations_due', 'due_at'),
    )
