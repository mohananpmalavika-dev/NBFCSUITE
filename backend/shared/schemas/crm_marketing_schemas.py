"""
CRM Marketing Automation Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


# ============================================================================
# ENUMS
# ============================================================================

class CampaignTypeEnum:
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH_NOTIFICATION = "push_notification"
    SOCIAL_MEDIA = "social_media"
    MULTI_CHANNEL = "multi_channel"


class CampaignStatusEnum:
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SegmentationTypeEnum:
    STATIC = "static"
    DYNAMIC = "dynamic"


class LandingPageStatusEnum:
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
    ARCHIVED = "archived"


class CampaignExecutionStatusEnum:
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


# ============================================================================
# CAMPAIGN SCHEMAS
# ============================================================================

class MarketingCampaignBase(BaseModel):
    """Base Marketing Campaign schema"""
    campaign_name: str = Field(..., min_length=1, max_length=200)
    campaign_type: str = Field(default=CampaignTypeEnum.EMAIL)
    status: str = Field(default=CampaignStatusEnum.DRAFT)
    description: Optional[str] = None
    objective: Optional[str] = Field(None, max_length=200)
    
    # Targeting
    target_segment_id: Optional[UUID] = None
    
    # Content
    subject_line: Optional[str] = Field(None, max_length=500)
    email_content: Optional[str] = None
    sms_content: Optional[str] = None
    sender_name: Optional[str] = Field(None, max_length=100)
    sender_email: Optional[str] = Field(None, max_length=100)
    reply_to_email: Optional[str] = Field(None, max_length=100)
    
    # Landing Page
    landing_page_id: Optional[UUID] = None
    
    # Scheduling
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    scheduled_send_time: Optional[datetime] = None
    
    # Budget & Goals
    budget: Optional[Decimal] = None
    budget_currency: str = Field(default="INR")
    target_conversions: Optional[int] = None
    target_roi: Optional[Decimal] = None
    
    # Campaign Owner
    campaign_owner_id: Optional[UUID] = None
    
    # A/B Testing
    is_ab_test: bool = Field(default=False)
    ab_test_variant: Optional[str] = Field(None, max_length=20)
    ab_test_percentage: Optional[int] = None
    
    # Tags & Categories
    tags: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    
    # Settings
    settings: Optional[Dict[str, Any]] = None
    
    # Notes
    notes: Optional[str] = None


class MarketingCampaignCreate(MarketingCampaignBase):
    """Schema for creating a marketing campaign"""
    pass


class MarketingCampaignUpdate(BaseModel):
    """Schema for updating a marketing campaign"""
    campaign_name: Optional[str] = Field(None, min_length=1, max_length=200)
    campaign_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    target_segment_id: Optional[UUID] = None
    subject_line: Optional[str] = None
    email_content: Optional[str] = None
    sms_content: Optional[str] = None
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    reply_to_email: Optional[str] = None
    landing_page_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    scheduled_send_time: Optional[datetime] = None
    budget: Optional[Decimal] = None
    budget_currency: Optional[str] = None
    target_conversions: Optional[int] = None
    target_roi: Optional[Decimal] = None
    campaign_owner_id: Optional[UUID] = None
    is_ab_test: Optional[bool] = None
    ab_test_variant: Optional[str] = None
    ab_test_percentage: Optional[int] = None
    tags: Optional[str] = None
    category: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class MarketingCampaignResponse(MarketingCampaignBase):
    """Schema for campaign response"""
    id: UUID
    campaign_number: str
    tenant_id: str
    target_audience_size: int
    
    # Analytics
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    total_bounced: int
    total_unsubscribed: int
    
    # Rates
    open_rate: Optional[Decimal] = None
    click_rate: Optional[Decimal] = None
    conversion_rate: Optional[Decimal] = None
    bounce_rate: Optional[Decimal] = None
    unsubscribe_rate: Optional[Decimal] = None
    
    # Revenue
    revenue_generated: Optional[Decimal] = None
    roi: Optional[Decimal] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


class CampaignAnalytics(BaseModel):
    """Campaign analytics summary"""
    campaign_id: UUID
    campaign_name: str
    campaign_type: str
    status: str
    
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    total_bounced: int
    total_unsubscribed: int
    
    open_rate: float
    click_rate: float
    conversion_rate: float
    bounce_rate: float
    unsubscribe_rate: float
    
    revenue_generated: float
    roi: float
    
    start_date: Optional[datetime]
    end_date: Optional[datetime]


# ============================================================================
# SEGMENT SCHEMAS
# ============================================================================

class CustomerSegmentBase(BaseModel):
    """Base Customer Segment schema"""
    segment_name: str = Field(..., min_length=1, max_length=200)
    segmentation_type: str = Field(default=SegmentationTypeEnum.STATIC)
    description: Optional[str] = None
    criteria_type: Optional[str] = None
    
    # Rules (JSON)
    rules: Optional[Dict[str, Any]] = None
    
    # Segment Owner
    segment_owner_id: Optional[UUID] = None
    
    # Status
    is_active: bool = Field(default=True)
    
    # Refresh Settings
    auto_refresh: bool = Field(default=False)
    refresh_frequency: Optional[str] = Field(None, max_length=20)
    
    # Tags
    tags: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None


class CustomerSegmentCreate(CustomerSegmentBase):
    """Schema for creating a customer segment"""
    pass


class CustomerSegmentUpdate(BaseModel):
    """Schema for updating a customer segment"""
    segment_name: Optional[str] = Field(None, min_length=1, max_length=200)
    segmentation_type: Optional[str] = None
    description: Optional[str] = None
    criteria_type: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    segment_owner_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    auto_refresh: Optional[bool] = None
    refresh_frequency: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class CustomerSegmentResponse(CustomerSegmentBase):
    """Schema for segment response"""
    id: UUID
    segment_number: str
    tenant_id: str
    total_customers: int
    active_customers: int
    last_refreshed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


class SegmentMemberAdd(BaseModel):
    """Schema for adding members to segment"""
    segment_id: UUID
    customer_ids: List[UUID]


class SegmentMemberRemove(BaseModel):
    """Schema for removing members from segment"""
    segment_id: UUID
    customer_ids: List[UUID]


# ============================================================================
# LANDING PAGE SCHEMAS
# ============================================================================

class LandingPageBase(BaseModel):
    """Base Landing Page schema"""
    page_name: str = Field(..., min_length=1, max_length=200)
    page_title: str = Field(..., min_length=1, max_length=200)
    status: str = Field(default=LandingPageStatusEnum.DRAFT)
    slug: str = Field(..., min_length=1, max_length=200)
    custom_domain: Optional[str] = Field(None, max_length=200)
    
    # Content
    description: Optional[str] = None
    html_content: Optional[str] = None
    css_content: Optional[str] = None
    js_content: Optional[str] = None
    
    # Meta Tags
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    
    # Template
    template_id: Optional[UUID] = None
    template_name: Optional[str] = Field(None, max_length=100)
    
    # Form Settings
    has_form: bool = Field(default=True)
    form_fields: Optional[List[Dict[str, Any]]] = None
    submit_button_text: str = Field(default="Submit")
    thank_you_message: Optional[str] = None
    redirect_url: Optional[str] = Field(None, max_length=500)
    
    # Owner
    page_owner_id: Optional[UUID] = None
    
    # A/B Testing
    is_ab_test: bool = Field(default=False)
    ab_test_variant: Optional[str] = Field(None, max_length=20)
    
    # Tags
    tags: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None


class LandingPageCreate(LandingPageBase):
    """Schema for creating a landing page"""
    pass


class LandingPageUpdate(BaseModel):
    """Schema for updating a landing page"""
    page_name: Optional[str] = Field(None, min_length=1, max_length=200)
    page_title: Optional[str] = None
    status: Optional[str] = None
    slug: Optional[str] = None
    custom_domain: Optional[str] = None
    description: Optional[str] = None
    html_content: Optional[str] = None
    css_content: Optional[str] = None
    js_content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    template_id: Optional[UUID] = None
    template_name: Optional[str] = None
    has_form: Optional[bool] = None
    form_fields: Optional[List[Dict[str, Any]]] = None
    submit_button_text: Optional[str] = None
    thank_you_message: Optional[str] = None
    redirect_url: Optional[str] = None
    page_owner_id: Optional[UUID] = None
    is_ab_test: Optional[bool] = None
    ab_test_variant: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class LandingPageResponse(LandingPageBase):
    """Schema for landing page response"""
    id: UUID
    page_number: str
    tenant_id: str
    full_url: Optional[str] = None
    
    # Analytics
    total_visits: int
    unique_visits: int
    total_submissions: int
    conversion_rate: Optional[Decimal] = None
    
    # Publish Info
    published_at: Optional[datetime] = None
    published_by: Optional[UUID] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


class LandingPageSubmissionCreate(BaseModel):
    """Schema for creating a landing page submission"""
    landing_page_id: UUID
    campaign_id: Optional[UUID] = None
    form_data: Dict[str, Any]
    ip_address: Optional[str] = Field(None, max_length=50)
    user_agent: Optional[str] = Field(None, max_length=500)
    referrer_url: Optional[str] = Field(None, max_length=500)
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=100)
    utm_term: Optional[str] = Field(None, max_length=100)
    utm_content: Optional[str] = Field(None, max_length=100)


class LandingPageSubmissionResponse(BaseModel):
    """Schema for landing page submission response"""
    id: UUID
    landing_page_id: UUID
    campaign_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    form_data: Dict[str, Any]
    submitted_at: datetime
    is_processed: bool
    processed_at: Optional[datetime] = None
    lead_created: bool
    lead_id: Optional[UUID] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# CAMPAIGN EXECUTION SCHEMAS
# ============================================================================

class CampaignExecutionResponse(BaseModel):
    """Schema for campaign execution response"""
    id: UUID
    campaign_id: UUID
    customer_id: UUID
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_name: Optional[str] = None
    execution_status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    bounced_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    open_count: int
    click_count: int
    error_message: Optional[str] = None
    retry_count: int
    variant: Optional[str] = None
    revenue_attributed: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# CAMPAIGN TEMPLATE SCHEMAS
# ============================================================================

class CampaignTemplateBase(BaseModel):
    """Base Campaign Template schema"""
    template_name: str = Field(..., min_length=1, max_length=200)
    template_type: str
    description: Optional[str] = None
    subject_line: Optional[str] = Field(None, max_length=500)
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    is_public: bool = Field(default=False)
    template_owner_id: Optional[UUID] = None
    tags: Optional[str] = None


class CampaignTemplateCreate(CampaignTemplateBase):
    """Schema for creating a campaign template"""
    pass


class CampaignTemplateUpdate(BaseModel):
    """Schema for updating a campaign template"""
    template_name: Optional[str] = None
    template_type: Optional[str] = None
    description: Optional[str] = None
    subject_line: Optional[str] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None
    template_owner_id: Optional[UUID] = None
    tags: Optional[str] = None


class CampaignTemplateResponse(CampaignTemplateBase):
    """Schema for template response"""
    id: UUID
    template_number: str
    tenant_id: str
    usage_count: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    is_deleted: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# ACTION SCHEMAS
# ============================================================================

class CampaignLaunchRequest(BaseModel):
    """Schema for launching a campaign"""
    campaign_id: UUID
    send_immediately: bool = Field(default=False)
    test_mode: bool = Field(default=False)
    test_recipients: Optional[List[str]] = None


class CampaignPauseRequest(BaseModel):
    """Schema for pausing a campaign"""
    campaign_id: UUID
    reason: Optional[str] = None


class CampaignResumeRequest(BaseModel):
    """Schema for resuming a campaign"""
    campaign_id: UUID


class SegmentRefreshRequest(BaseModel):
    """Schema for refreshing a segment"""
    segment_id: UUID


# ============================================================================
# LIST SCHEMAS
# ============================================================================

class PaginatedCampaignList(BaseModel):
    """Paginated list of campaigns"""
    total: int
    page: int
    page_size: int
    campaigns: List[MarketingCampaignResponse]


class PaginatedSegmentList(BaseModel):
    """Paginated list of segments"""
    total: int
    page: int
    page_size: int
    segments: List[CustomerSegmentResponse]


class PaginatedLandingPageList(BaseModel):
    """Paginated list of landing pages"""
    total: int
    page: int
    page_size: int
    landing_pages: List[LandingPageResponse]


class PaginatedExecutionList(BaseModel):
    """Paginated list of campaign executions"""
    total: int
    page: int
    page_size: int
    executions: List[CampaignExecutionResponse]


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class MarketingDashboardStats(BaseModel):
    """Marketing automation dashboard statistics"""
    total_campaigns: int
    active_campaigns: int
    total_segments: int
    total_landing_pages: int
    total_messages_sent: int
    total_conversions: int
    average_open_rate: float
    average_click_rate: float
    average_conversion_rate: float
    total_revenue: float
    average_roi: float
    
    # Campaign breakdown
    campaigns_by_status: Dict[str, int]
    campaigns_by_type: Dict[str, int]
    
    # Recent campaigns
    recent_campaigns: List[MarketingCampaignResponse]
