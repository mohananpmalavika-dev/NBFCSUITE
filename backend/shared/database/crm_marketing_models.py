"""
CRM Marketing Automation Models
Campaign management, Email/SMS campaigns, Landing pages, and Segmentation
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, Date, DateTime, Boolean, ForeignKey, Index, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from backend.shared.database.models import BaseModel


class CampaignType(str, enum.Enum):
    """Campaign type enumeration"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH_NOTIFICATION = "push_notification"
    SOCIAL_MEDIA = "social_media"
    MULTI_CHANNEL = "multi_channel"


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SegmentationType(str, enum.Enum):
    """Segmentation type enumeration"""
    STATIC = "static"
    DYNAMIC = "dynamic"


class SegmentCriteria(str, enum.Enum):
    """Segment criteria enumeration"""
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    GEOGRAPHIC = "geographic"
    FIRMOGRAPHIC = "firmographic"
    PSYCHOGRAPHIC = "psychographic"
    TRANSACTIONAL = "transactional"


class LandingPageStatus(str, enum.Enum):
    """Landing page status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
    ARCHIVED = "archived"


class CampaignExecutionStatus(str, enum.Enum):
    """Campaign execution status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    CONVERTED = "converted"
    BOUNCED = "bounced"
    FAILED = "failed"
    UNSUBSCRIBED = "unsubscribed"


class MarketingCampaign(BaseModel):
    """
    Marketing Campaign Model
    Manages marketing campaigns across multiple channels
    """
    __tablename__ = "marketing_campaigns"
    
    # Basic Information
    campaign_number = Column(String(50), nullable=False, index=True)
    campaign_name = Column(String(200), nullable=False, index=True)
    campaign_type = Column(SQLEnum(CampaignType), nullable=False, default=CampaignType.EMAIL)
    status = Column(SQLEnum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT, index=True)
    
    # Campaign Details
    description = Column(Text, nullable=True)
    objective = Column(String(200), nullable=True)
    
    # Targeting
    target_segment_id = Column(UUID(as_uuid=True), ForeignKey('customer_segments.id'), nullable=True, index=True)
    target_audience_size = Column(Integer, default=0)
    
    # Content
    subject_line = Column(String(500), nullable=True)  # For email/SMS
    email_content = Column(Text, nullable=True)  # Email HTML content
    sms_content = Column(Text, nullable=True)  # SMS text content
    sender_name = Column(String(100), nullable=True)
    sender_email = Column(String(100), nullable=True)
    reply_to_email = Column(String(100), nullable=True)
    
    # Landing Page
    landing_page_id = Column(UUID(as_uuid=True), ForeignKey('landing_pages.id'), nullable=True)
    
    # Scheduling
    start_date = Column(DateTime, nullable=True, index=True)
    end_date = Column(DateTime, nullable=True)
    scheduled_send_time = Column(DateTime, nullable=True)
    
    # Budget & Goals
    budget = Column(Numeric(15, 2), nullable=True)
    budget_currency = Column(String(10), default="INR")
    target_conversions = Column(Integer, nullable=True)
    target_roi = Column(Numeric(10, 2), nullable=True)
    
    # Campaign Owner
    campaign_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Tracking & Analytics
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    total_bounced = Column(Integer, default=0)
    total_unsubscribed = Column(Integer, default=0)
    
    # Rates (calculated fields)
    open_rate = Column(Numeric(5, 2), default=0)  # Percentage
    click_rate = Column(Numeric(5, 2), default=0)  # Percentage
    conversion_rate = Column(Numeric(5, 2), default=0)  # Percentage
    bounce_rate = Column(Numeric(5, 2), default=0)  # Percentage
    unsubscribe_rate = Column(Numeric(5, 2), default=0)  # Percentage
    
    # Revenue Tracking
    revenue_generated = Column(Numeric(15, 2), default=0)
    roi = Column(Numeric(10, 2), default=0)  # Return on Investment
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_test_variant = Column(String(20), nullable=True)  # A, B, C, etc.
    ab_test_percentage = Column(Integer, nullable=True)  # Split percentage
    
    # Tags & Categories
    tags = Column(String(500), nullable=True)  # Comma-separated
    category = Column(String(100), nullable=True)
    
    # Additional Settings
    settings = Column(JSONB, nullable=True)  # JSON settings for advanced configuration
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    segment = relationship("CustomerSegment", foreign_keys=[target_segment_id], backref="campaigns")
    landing_page = relationship("LandingPage", foreign_keys=[landing_page_id], backref="campaigns")
    
    # Unique constraint: campaign_number per tenant
    __table_args__ = (
        Index('idx_tenant_campaign_number', 'tenant_id', 'campaign_number', unique=True),
        Index('idx_campaign_status', 'tenant_id', 'status'),
        Index('idx_campaign_type', 'tenant_id', 'campaign_type'),
        Index('idx_campaign_dates', 'tenant_id', 'start_date', 'end_date'),
    )
    
    def __repr__(self):
        return f"<MarketingCampaign(id={self.id}, campaign_number={self.campaign_number}, campaign_name={self.campaign_name})>"


class CustomerSegment(BaseModel):
    """
    Customer Segment Model
    Defines customer segments for targeted campaigns
    """
    __tablename__ = "customer_segments"
    
    # Basic Information
    segment_number = Column(String(50), nullable=False, index=True)
    segment_name = Column(String(200), nullable=False, index=True)
    segmentation_type = Column(SQLEnum(SegmentationType), nullable=False, default=SegmentationType.STATIC)
    
    # Segment Details
    description = Column(Text, nullable=True)
    criteria_type = Column(SQLEnum(SegmentCriteria), nullable=True)
    
    # Segmentation Rules (JSON)
    rules = Column(JSONB, nullable=True)  # Complex filtering rules
    """
    Example rules format:
    {
        "conditions": [
            {"field": "age", "operator": ">=", "value": 25},
            {"field": "city", "operator": "in", "value": ["Mumbai", "Delhi"]},
            {"field": "total_purchases", "operator": ">", "value": 10}
        ],
        "logic": "AND"  # or "OR"
    }
    """
    
    # Segment Size
    total_customers = Column(Integer, default=0)
    active_customers = Column(Integer, default=0)
    
    # Segment Owner
    segment_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Refresh Settings (for dynamic segments)
    auto_refresh = Column(Boolean, default=False)
    last_refreshed_at = Column(DateTime, nullable=True)
    refresh_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly
    
    # Tags
    tags = Column(String(500), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Unique constraint: segment_number per tenant
    __table_args__ = (
        Index('idx_tenant_segment_number', 'tenant_id', 'segment_number', unique=True),
        Index('idx_segment_type', 'tenant_id', 'segmentation_type'),
        Index('idx_segment_active', 'tenant_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<CustomerSegment(id={self.id}, segment_number={self.segment_number}, segment_name={self.segment_name})>"


class SegmentMember(BaseModel):
    """
    Segment Member Model
    Maps customers to segments
    """
    __tablename__ = "segment_members"
    
    segment_id = Column(UUID(as_uuid=True), ForeignKey('customer_segments.id'), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # References customers table
    
    # Membership Details
    added_date = Column(DateTime, nullable=False, index=True)
    added_by = Column(UUID(as_uuid=True), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Segment
    segment = relationship("CustomerSegment", backref="members")
    
    # Unique constraint: one customer per segment per tenant
    __table_args__ = (
        Index('idx_tenant_segment_customer', 'tenant_id', 'segment_id', 'customer_id', unique=True),
        Index('idx_segment_members', 'tenant_id', 'segment_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<SegmentMember(segment_id={self.segment_id}, customer_id={self.customer_id})>"


class LandingPage(BaseModel):
    """
    Landing Page Model
    Campaign landing pages for conversions
    """
    __tablename__ = "landing_pages"
    
    # Basic Information
    page_number = Column(String(50), nullable=False, index=True)
    page_name = Column(String(200), nullable=False, index=True)
    page_title = Column(String(200), nullable=False)
    status = Column(SQLEnum(LandingPageStatus), nullable=False, default=LandingPageStatus.DRAFT, index=True)
    
    # URL & Slug
    slug = Column(String(200), nullable=False, index=True)  # URL-friendly identifier
    custom_domain = Column(String(200), nullable=True)
    full_url = Column(String(500), nullable=True)
    
    # Content
    description = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)  # Full HTML content
    css_content = Column(Text, nullable=True)  # Custom CSS
    js_content = Column(Text, nullable=True)  # Custom JavaScript
    
    # Meta Tags (SEO)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(500), nullable=True)
    meta_keywords = Column(String(500), nullable=True)
    
    # Template
    template_id = Column(UUID(as_uuid=True), nullable=True)
    template_name = Column(String(100), nullable=True)
    
    # Form Settings
    has_form = Column(Boolean, default=True)
    form_fields = Column(JSONB, nullable=True)  # JSON array of form fields
    submit_button_text = Column(String(100), default="Submit")
    thank_you_message = Column(Text, nullable=True)
    redirect_url = Column(String(500), nullable=True)
    
    # Owner
    page_owner_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Analytics
    total_visits = Column(Integer, default=0)
    unique_visits = Column(Integer, default=0)
    total_submissions = Column(Integer, default=0)
    conversion_rate = Column(Numeric(5, 2), default=0)  # Percentage
    
    # Publish Settings
    published_at = Column(DateTime, nullable=True)
    published_by = Column(UUID(as_uuid=True), nullable=True)
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_test_variant = Column(String(20), nullable=True)
    
    # Tags
    tags = Column(String(500), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Unique constraint: slug per tenant
    __table_args__ = (
        Index('idx_tenant_page_number', 'tenant_id', 'page_number', unique=True),
        Index('idx_tenant_page_slug', 'tenant_id', 'slug', unique=True),
        Index('idx_page_status', 'tenant_id', 'status'),
    )
    
    def __repr__(self):
        return f"<LandingPage(id={self.id}, page_number={self.page_number}, page_name={self.page_name})>"


class CampaignExecution(BaseModel):
    """
    Campaign Execution Model
    Tracks individual campaign message deliveries
    """
    __tablename__ = "campaign_executions"
    
    # Campaign Reference
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('marketing_campaigns.id'), nullable=False, index=True)
    
    # Recipient
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    recipient_email = Column(String(100), nullable=True, index=True)
    recipient_phone = Column(String(20), nullable=True, index=True)
    recipient_name = Column(String(200), nullable=True)
    
    # Execution Details
    execution_status = Column(SQLEnum(CampaignExecutionStatus), nullable=False, default=CampaignExecutionStatus.PENDING, index=True)
    sent_at = Column(DateTime, nullable=True, index=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)
    bounced_at = Column(DateTime, nullable=True)
    unsubscribed_at = Column(DateTime, nullable=True)
    
    # Engagement Metrics
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    
    # Error Tracking
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # A/B Test Variant
    variant = Column(String(20), nullable=True)
    
    # External IDs (for tracking with email/SMS providers)
    external_message_id = Column(String(200), nullable=True, index=True)
    provider_name = Column(String(100), nullable=True)
    
    # Revenue Attribution
    revenue_attributed = Column(Numeric(15, 2), default=0)
    
    # Campaign
    campaign = relationship("MarketingCampaign", backref="executions")
    
    # Indexes
    __table_args__ = (
        Index('idx_execution_campaign', 'tenant_id', 'campaign_id'),
        Index('idx_execution_customer', 'tenant_id', 'customer_id'),
        Index('idx_execution_status', 'tenant_id', 'execution_status'),
        Index('idx_execution_sent', 'tenant_id', 'sent_at'),
    )
    
    def __repr__(self):
        return f"<CampaignExecution(id={self.id}, campaign_id={self.campaign_id}, status={self.execution_status})>"


class LandingPageSubmission(BaseModel):
    """
    Landing Page Submission Model
    Tracks form submissions on landing pages
    """
    __tablename__ = "landing_page_submissions"
    
    # Landing Page Reference
    landing_page_id = Column(UUID(as_uuid=True), ForeignKey('landing_pages.id'), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey('marketing_campaigns.id'), nullable=True, index=True)
    
    # Submitter Information
    customer_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Form Data (JSON)
    form_data = Column(JSONB, nullable=False)  # All form fields as JSON
    """
    Example:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "message": "I'm interested in your product"
    }
    """
    
    # Submission Details
    submitted_at = Column(DateTime, nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referrer_url = Column(String(500), nullable=True)
    
    # UTM Parameters
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    utm_term = Column(String(100), nullable=True)
    utm_content = Column(String(100), nullable=True)
    
    # Processing
    is_processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Lead Creation
    lead_created = Column(Boolean, default=False)
    lead_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    landing_page = relationship("LandingPage", backref="submissions")
    campaign = relationship("MarketingCampaign", backref="submissions")
    
    # Indexes
    __table_args__ = (
        Index('idx_submission_page', 'tenant_id', 'landing_page_id'),
        Index('idx_submission_campaign', 'tenant_id', 'campaign_id'),
        Index('idx_submission_date', 'tenant_id', 'submitted_at'),
        Index('idx_submission_processed', 'tenant_id', 'is_processed'),
    )
    
    def __repr__(self):
        return f"<LandingPageSubmission(id={self.id}, landing_page_id={self.landing_page_id})>"


class CampaignTemplate(BaseModel):
    """
    Campaign Template Model
    Reusable templates for campaigns
    """
    __tablename__ = "campaign_templates"
    
    # Basic Information
    template_number = Column(String(50), nullable=False, index=True)
    template_name = Column(String(200), nullable=False, index=True)
    template_type = Column(SQLEnum(CampaignType), nullable=False)
    
    # Content
    description = Column(Text, nullable=True)
    subject_line = Column(String(500), nullable=True)
    html_content = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    
    # Category
    category = Column(String(100), nullable=True, index=True)
    
    # Usage
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Owner
    template_owner_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Tags
    tags = Column(String(500), nullable=True)
    
    # Unique constraint: template_number per tenant
    __table_args__ = (
        Index('idx_tenant_template_number', 'tenant_id', 'template_number', unique=True),
        Index('idx_template_type', 'tenant_id', 'template_type'),
        Index('idx_template_category', 'tenant_id', 'category'),
    )
    
    def __repr__(self):
        return f"<CampaignTemplate(id={self.id}, template_number={self.template_number}, template_name={self.template_name})>"
