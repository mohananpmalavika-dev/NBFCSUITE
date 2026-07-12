"""
CRM Customer Service Schemas
Pydantic models for validation and serialization
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from backend.shared.database.crm_service_models import (
    TicketPriority, TicketStatus, TicketCategory, TicketChannel,
    ArticleStatus, ArticleCategory, SLAStatus, SLAMetricType
)


# ============================================================================
# TICKET SCHEMAS
# ============================================================================

class TicketCommentBase(BaseModel):
    comment_type: str = "comment"
    content: str
    is_internal: bool = False
    is_system: bool = False


class TicketCommentCreate(TicketCommentBase):
    ticket_id: UUID


class TicketCommentUpdate(BaseModel):
    content: Optional[str] = None
    is_internal: Optional[bool] = None


class TicketCommentResponse(TicketCommentBase):
    id: UUID
    ticket_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    
    class Config:
        from_attributes = True


class TicketAttachmentBase(BaseModel):
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None


class TicketAttachmentCreate(TicketAttachmentBase):
    ticket_id: UUID


class TicketAttachmentResponse(TicketAttachmentBase):
    id: UUID
    ticket_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    subject: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.NEW
    channel: TicketChannel = TicketChannel.WEB
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    tags: List[str] = []
    custom_fields: Optional[str] = None


class TicketCreate(TicketBase):
    account_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    assigned_team: Optional[str] = None
    sla_id: Optional[UUID] = None
    parent_ticket_id: Optional[UUID] = None
    related_article_id: Optional[UUID] = None


class TicketUpdate(BaseModel):
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    channel: Optional[TicketChannel] = None
    account_id: Optional[UUID] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    assigned_to: Optional[UUID] = None
    assigned_team: Optional[str] = None
    sla_id: Optional[UUID] = None
    parent_ticket_id: Optional[UUID] = None
    related_article_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[str] = None
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class TicketResponse(TicketBase):
    id: UUID
    ticket_number: str
    account_id: Optional[UUID]
    assigned_to: Optional[UUID]
    assigned_team: Optional[str]
    sla_id: Optional[UUID]
    first_response_due: Optional[datetime]
    resolution_due: Optional[datetime]
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    sla_breached: bool
    parent_ticket_id: Optional[UUID]
    related_article_id: Optional[UUID]
    satisfaction_rating: Optional[int]
    satisfaction_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    
    # Optional related data
    comments: List[TicketCommentResponse] = []
    attachments: List[TicketAttachmentResponse] = []
    account_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class TicketListParams(BaseModel):
    skip: int = 0
    limit: int = 20
    search: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_to: Optional[UUID] = None
    account_id: Optional[UUID] = None
    sla_breached: Optional[bool] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None


class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TicketSatisfactionUpdate(BaseModel):
    satisfaction_rating: int = Field(..., ge=1, le=5)
    satisfaction_comment: Optional[str] = None


class TicketAssignmentUpdate(BaseModel):
    assigned_to: Optional[UUID] = None
    assigned_team: Optional[str] = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    comment: Optional[str] = None


# ============================================================================
# KNOWLEDGE BASE SCHEMAS
# ============================================================================

class ArticleAttachmentBase(BaseModel):
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    display_order: int = 0


class ArticleAttachmentCreate(ArticleAttachmentBase):
    article_id: UUID


class ArticleAttachmentResponse(ArticleAttachmentBase):
    id: UUID
    article_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = None
    category: ArticleCategory
    status: ArticleStatus = ArticleStatus.DRAFT
    tags: List[str] = []
    related_products: List[str] = []
    meta_description: Optional[str] = Field(None, max_length=500)
    keywords: List[str] = []
    is_featured: bool = False
    display_order: int = 0


class KnowledgeArticleCreate(KnowledgeArticleBase):
    slug: Optional[str] = None
    parent_article_id: Optional[UUID] = None
    
    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        if v is None and 'title' in values:
            # Generate slug from title
            import re
            slug = values['title'].lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            return slug[:500]
        return v


class KnowledgeArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    slug: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = None
    category: Optional[ArticleCategory] = None
    status: Optional[ArticleStatus] = None
    tags: Optional[List[str]] = None
    related_products: Optional[List[str]] = None
    meta_description: Optional[str] = Field(None, max_length=500)
    keywords: Optional[List[str]] = None
    parent_article_id: Optional[UUID] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None
    reviewer_id: Optional[UUID] = None


class KnowledgeArticleResponse(KnowledgeArticleBase):
    id: UUID
    article_number: str
    slug: str
    author_id: UUID
    reviewer_id: Optional[UUID]
    published_at: Optional[datetime]
    view_count: int
    helpful_count: int
    not_helpful_count: int
    version: int
    parent_article_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    # Optional related data
    attachments: List[ArticleAttachmentResponse] = []
    author_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class KnowledgeArticleListParams(BaseModel):
    skip: int = 0
    limit: int = 20
    search: Optional[str] = None
    category: Optional[ArticleCategory] = None
    status: Optional[ArticleStatus] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    author_id: Optional[UUID] = None


class KnowledgeArticleListResponse(BaseModel):
    articles: List[KnowledgeArticleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ArticleFeedbackUpdate(BaseModel):
    helpful: bool  # True = helpful, False = not helpful


class ArticlePublishUpdate(BaseModel):
    status: ArticleStatus
    reviewer_id: Optional[UUID] = None


# ============================================================================
# SLA SCHEMAS
# ============================================================================

class SLABase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: SLAStatus = SLAStatus.ACTIVE
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    first_response_time: int = Field(..., gt=0)  # minutes
    resolution_time: int = Field(..., gt=0)  # minutes
    escalation_time: Optional[int] = Field(None, gt=0)  # minutes
    use_business_hours: bool = True
    business_hours_start: str = "09:00"
    business_hours_end: str = "18:00"
    business_days: List[int] = [1, 2, 3, 4, 5]  # 1=Monday, 7=Sunday
    escalation_enabled: bool = False
    escalate_to: Optional[UUID] = None
    is_default: bool = False
    display_order: int = 0


class SLACreate(SLABase):
    pass


class SLAUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[SLAStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    first_response_time: Optional[int] = Field(None, gt=0)
    resolution_time: Optional[int] = Field(None, gt=0)
    escalation_time: Optional[int] = Field(None, gt=0)
    use_business_hours: Optional[bool] = None
    business_hours_start: Optional[str] = None
    business_hours_end: Optional[str] = None
    business_days: Optional[List[int]] = None
    escalation_enabled: Optional[bool] = None
    escalate_to: Optional[UUID] = None
    is_default: Optional[bool] = None
    display_order: Optional[int] = None


class SLAResponse(SLABase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    
    # Optional related data
    escalate_to_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SLAListParams(BaseModel):
    skip: int = 0
    limit: int = 50
    status: Optional[SLAStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None


class SLAListResponse(BaseModel):
    slas: List[SLAResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SLAViolationBase(BaseModel):
    metric_type: SLAMetricType
    due_at: datetime
    violated_at: datetime


class SLAViolationCreate(SLAViolationBase):
    ticket_id: UUID
    sla_id: UUID
    breach_duration: Optional[timedelta] = None


class SLAViolationUpdate(BaseModel):
    is_resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    escalated: Optional[bool] = None
    escalated_to: Optional[UUID] = None
    escalated_at: Optional[datetime] = None


class SLAViolationResponse(SLAViolationBase):
    id: UUID
    ticket_id: UUID
    sla_id: UUID
    breach_duration: Optional[timedelta]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    escalated: bool
    escalated_to: Optional[UUID]
    escalated_at: Optional[datetime]
    created_at: datetime
    
    # Optional related data
    ticket_number: Optional[str] = None
    sla_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class SLAViolationListParams(BaseModel):
    skip: int = 0
    limit: int = 20
    ticket_id: Optional[UUID] = None
    sla_id: Optional[UUID] = None
    metric_type: Optional[SLAMetricType] = None
    is_resolved: Optional[bool] = None


class SLAViolationListResponse(BaseModel):
    violations: List[SLAViolationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# DASHBOARD & ANALYTICS SCHEMAS
# ============================================================================

class TicketStats(BaseModel):
    total_tickets: int
    new_tickets: int
    open_tickets: int
    in_progress_tickets: int
    pending_tickets: int
    resolved_tickets: int
    closed_tickets: int
    sla_breached_tickets: int
    avg_first_response_time: Optional[float]  # minutes
    avg_resolution_time: Optional[float]  # minutes
    avg_satisfaction_rating: Optional[float]


class TicketStatsByPriority(BaseModel):
    priority: TicketPriority
    count: int
    sla_breached: int


class TicketStatsByCategory(BaseModel):
    category: TicketCategory
    count: int
    avg_resolution_time: Optional[float]


class SLAPerformance(BaseModel):
    sla_id: UUID
    sla_name: str
    total_tickets: int
    met: int
    breached: int
    compliance_rate: float  # percentage


class AgentPerformance(BaseModel):
    agent_id: UUID
    agent_name: str
    assigned_tickets: int
    resolved_tickets: int
    avg_resolution_time: Optional[float]
    avg_satisfaction_rating: Optional[float]


class ServiceDashboard(BaseModel):
    overview: TicketStats
    by_priority: List[TicketStatsByPriority]
    by_category: List[TicketStatsByCategory]
    sla_performance: List[SLAPerformance]
    top_agents: List[AgentPerformance]


# ============================================================================
# API RESPONSE WRAPPERS
# ============================================================================

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[Dict[str, Any]] = None


class TicketAPIResponse(APIResponse):
    data: Optional[TicketResponse] = None


class TicketListAPIResponse(APIResponse):
    data: Optional[TicketListResponse] = None


class KnowledgeArticleAPIResponse(APIResponse):
    data: Optional[KnowledgeArticleResponse] = None


class KnowledgeArticleListAPIResponse(APIResponse):
    data: Optional[KnowledgeArticleListResponse] = None


class SLAAPIResponse(APIResponse):
    data: Optional[SLAResponse] = None


class SLAListAPIResponse(APIResponse):
    data: Optional[SLAListResponse] = None


class ServiceDashboardAPIResponse(APIResponse):
    data: Optional[ServiceDashboard] = None
