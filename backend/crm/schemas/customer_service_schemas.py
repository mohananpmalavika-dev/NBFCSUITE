"""
CRM Customer Service Schemas
Pydantic models for API requests/responses
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class TicketPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class TicketStatusEnum(str, Enum):
    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    PENDING_INTERNAL = "pending_internal"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    CANCELLED = "cancelled"


class TicketCategoryEnum(str, Enum):
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


class TicketChannelEnum(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    WEB_PORTAL = "web_portal"
    MOBILE_APP = "mobile_app"
    CHAT = "chat"
    SOCIAL_MEDIA = "social_media"
    WALK_IN = "walk_in"
    WHATSAPP = "whatsapp"


class SLAStatusEnum(str, Enum):
    WITHIN_SLA = "within_sla"
    APPROACHING_BREACH = "approaching_breach"
    BREACHED = "breached"
    PAUSED = "paused"


class KBStatusEnum(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleCategoryEnum(str, Enum):
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


# ==================== TICKET SCHEMAS ====================

class TicketCreate(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    subject: str = Field(..., min_length=5, max_length=500, description="Ticket subject")
    description: str = Field(..., min_length=10, description="Detailed description")
    category: TicketCategoryEnum = Field(..., description="Ticket category")
    priority: TicketPriorityEnum = Field(default=TicketPriorityEnum.MEDIUM, description="Priority level")
    channel: TicketChannelEnum = Field(..., description="Source channel")
    assigned_to_user_id: Optional[int] = None
    assigned_to_team: Optional[str] = None
    tags: Optional[List[str]] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    branch_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": 1,
                "subject": "Unable to access loan account",
                "description": "Customer is unable to login to view loan account details",
                "category": "technical",
                "priority": "high",
                "channel": "phone",
                "tags": ["login", "loan_account"]
            }
        }


class TicketUpdate(BaseModel):
    subject: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[TicketCategoryEnum] = None
    priority: Optional[TicketPriorityEnum] = None
    status: Optional[TicketStatusEnum] = None
    assigned_to_user_id: Optional[int] = None
    assigned_to_team: Optional[str] = None
    resolution: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketAssign(BaseModel):
    assigned_to_user_id: Optional[int] = None
    assigned_to_team: Optional[str] = None
    notes: Optional[str] = None


class TicketResolve(BaseModel):
    resolution: str = Field(..., min_length=10, description="Resolution details")
    resolution_category: Optional[str] = None
    send_notification: bool = True


class TicketClose(BaseModel):
    closing_notes: Optional[str] = None
    send_notification: bool = True


class TicketReopen(BaseModel):
    reason: str = Field(..., min_length=10, description="Reason for reopening")


class TicketRating(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback: Optional[str] = None


class TicketCommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, description="Comment text")
    is_internal: bool = Field(default=False, description="Internal note")
    is_solution: bool = Field(default=False, description="Mark as solution")


class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    comment: str
    is_internal: bool
    is_solution: bool
    created_at: datetime
    created_by_user_id: int
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class TicketActivityResponse(BaseModel):
    id: int
    activity_type: str
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    customer_id: int
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    subject: str
    description: str
    category: str
    priority: str
    status: str
    channel: str
    assigned_to_user_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    assigned_to_team: Optional[str] = None
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sla_status: Optional[str] = None
    sla_first_response_due: Optional[datetime] = None
    sla_resolution_due: Optional[datetime] = None
    customer_satisfaction_rating: Optional[int] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Additional fields
    is_overdue: Optional[bool] = None
    time_to_resolution: Optional[int] = None  # Minutes
    comment_count: Optional[int] = None
    attachment_count: Optional[int] = None

    class Config:
        from_attributes = True


class TicketDetailResponse(TicketResponse):
    comments: List[TicketCommentResponse] = []
    activities: List[TicketActivityResponse] = []


class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== SLA SCHEMAS ====================

class SLAPolicyCreate(BaseModel):
    policy_name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    applies_to_priority: Optional[List[str]] = None
    applies_to_category: Optional[List[str]] = None
    applies_to_channel: Optional[List[str]] = None
    first_response_time: int = Field(..., gt=0, description="Minutes")
    resolution_time: int = Field(..., gt=0, description="Minutes")
    escalation_time: Optional[int] = Field(None, gt=0)
    business_hours_only: bool = True
    business_start_hour: int = Field(default=9, ge=0, le=23)
    business_end_hour: int = Field(default=18, ge=0, le=23)
    include_weekends: bool = False
    escalation_enabled: bool = True
    escalate_to_user_id: Optional[int] = None
    escalate_to_team: Optional[str] = None
    is_active: bool = True
    priority_order: int = 0

    @validator('business_end_hour')
    def validate_business_hours(cls, v, values):
        if 'business_start_hour' in values and v <= values['business_start_hour']:
            raise ValueError('business_end_hour must be greater than business_start_hour')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "policy_name": "Critical Priority SLA",
                "description": "SLA for critical priority tickets",
                "applies_to_priority": ["critical", "urgent"],
                "first_response_time": 15,
                "resolution_time": 240,
                "escalation_time": 120,
                "business_hours_only": False
            }
        }


class SLAPolicyUpdate(BaseModel):
    policy_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    applies_to_priority: Optional[List[str]] = None
    applies_to_category: Optional[List[str]] = None
    applies_to_channel: Optional[List[str]] = None
    first_response_time: Optional[int] = Field(None, gt=0)
    resolution_time: Optional[int] = Field(None, gt=0)
    escalation_time: Optional[int] = Field(None, gt=0)
    business_hours_only: Optional[bool] = None
    business_start_hour: Optional[int] = Field(None, ge=0, le=23)
    business_end_hour: Optional[int] = Field(None, ge=0, le=23)
    include_weekends: Optional[bool] = None
    escalation_enabled: Optional[bool] = None
    escalate_to_user_id: Optional[int] = None
    escalate_to_team: Optional[str] = None
    is_active: Optional[bool] = None
    priority_order: Optional[int] = None


class SLAPolicyResponse(BaseModel):
    id: int
    policy_name: str
    description: Optional[str] = None
    applies_to_priority: Optional[List[str]] = None
    applies_to_category: Optional[List[str]] = None
    applies_to_channel: Optional[List[str]] = None
    first_response_time: int
    resolution_time: int
    escalation_time: Optional[int] = None
    business_hours_only: bool
    business_start_hour: int
    business_end_hour: int
    include_weekends: bool
    escalation_enabled: bool
    escalate_to_user_id: Optional[int] = None
    escalate_to_team: Optional[str] = None
    is_active: bool
    priority_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class SLAMetricsResponse(BaseModel):
    total_tickets: int
    within_sla: int
    approaching_breach: int
    breached: int
    average_first_response_time: float  # Minutes
    average_resolution_time: float  # Minutes
    sla_compliance_rate: float  # Percentage


# ==================== KNOWLEDGE BASE SCHEMAS ====================

class KnowledgeBaseCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    summary: Optional[str] = None
    content: str = Field(..., min_length=50, description="Article content")
    category: ArticleCategoryEnum
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_public: bool = True
    is_internal: bool = False
    related_articles: Optional[List[int]] = None
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "How to Apply for a Personal Loan",
                "summary": "Step-by-step guide to apply for a personal loan",
                "content": "Detailed content here...",
                "category": "loan_products",
                "keywords": ["loan", "personal loan", "application"],
                "tags": ["loans", "how-to"],
                "is_public": True
            }
        }


class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    summary: Optional[str] = None
    content: Optional[str] = Field(None, min_length=50)
    category: Optional[ArticleCategoryEnum] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[KBStatusEnum] = None
    is_public: Optional[bool] = None
    is_internal: Optional[bool] = None
    related_articles: Optional[List[int]] = None
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)


class KnowledgeBasePublish(BaseModel):
    publish_now: bool = True
    scheduled_publish_at: Optional[datetime] = None


class KnowledgeBaseFeedbackCreate(BaseModel):
    is_helpful: bool
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    article_number: str
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    category: str
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: str
    is_public: bool
    is_internal: bool
    published_at: Optional[datetime] = None
    view_count: int
    helpful_count: int
    not_helpful_count: int
    average_rating: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class KnowledgeBaseListResponse(BaseModel):
    articles: List[KnowledgeBaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class KnowledgeBaseSearchResponse(BaseModel):
    articles: List[KnowledgeBaseResponse]
    total: int
    search_query: str


# ==================== TEMPLATE SCHEMAS ====================

class TicketTemplateCreate(BaseModel):
    template_name: str = Field(..., min_length=3, max_length=200)
    template_code: str = Field(..., min_length=3, max_length=50)
    subject_template: Optional[str] = Field(None, max_length=500)
    content_template: str = Field(..., min_length=10)
    category: Optional[TicketCategoryEnum] = None
    usage_type: Optional[str] = None
    available_variables: Optional[List[str]] = None
    is_active: bool = True


class TicketTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, min_length=3, max_length=200)
    subject_template: Optional[str] = Field(None, max_length=500)
    content_template: Optional[str] = Field(None, min_length=10)
    category: Optional[TicketCategoryEnum] = None
    usage_type: Optional[str] = None
    available_variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TicketTemplateResponse(BaseModel):
    id: int
    template_name: str
    template_code: str
    subject_template: Optional[str] = None
    content_template: str
    category: Optional[str] = None
    usage_type: Optional[str] = None
    available_variables: Optional[List[str]] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== DASHBOARD SCHEMAS ====================

class TicketStatistics(BaseModel):
    total_tickets: int
    new_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    average_resolution_time: float  # Hours
    customer_satisfaction_avg: Optional[float] = None


class AgentPerformance(BaseModel):
    user_id: int
    user_name: str
    assigned_tickets: int
    resolved_tickets: int
    average_resolution_time: float  # Hours
    customer_satisfaction_avg: Optional[float] = None
    sla_compliance_rate: float  # Percentage


class TicketTrendData(BaseModel):
    date: str
    new_tickets: int
    resolved_tickets: int
    closed_tickets: int


class DashboardResponse(BaseModel):
    statistics: TicketStatistics
    sla_metrics: SLAMetricsResponse
    top_agents: List[AgentPerformance]
    ticket_trends: List[TicketTrendData]
    tickets_by_category: Dict[str, int]
    tickets_by_priority: Dict[str, int]
    tickets_by_channel: Dict[str, int]


# ==================== FILTER SCHEMAS ====================

class TicketFilterParams(BaseModel):
    status: Optional[List[str]] = None
    priority: Optional[List[str]] = None
    category: Optional[List[str]] = None
    assigned_to_user_id: Optional[int] = None
    customer_id: Optional[int] = None
    channel: Optional[List[str]] = None
    sla_status: Optional[List[str]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    search_query: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")
