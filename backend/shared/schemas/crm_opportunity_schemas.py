"""
CRM Opportunity Management Schemas
Pydantic schemas for opportunity API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============================================================================
# ENUMS
# ============================================================================

class OpportunityStageEnum(str):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityTypeEnum(str):
    NEW_BUSINESS = "new_business"
    EXISTING_BUSINESS = "existing_business"
    RENEWAL = "renewal"
    UPSELL = "upsell"
    CROSS_SELL = "cross_sell"


class OpportunityPriorityEnum(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LossReasonEnum(str):
    PRICE = "price"
    COMPETITOR = "competitor"
    NO_BUDGET = "no_budget"
    TIMING = "timing"
    NO_DECISION = "no_decision"
    LOST_CONTACT = "lost_contact"
    PRODUCT_FIT = "product_fit"
    OTHER = "other"


# ============================================================================
# OPPORTUNITY PRODUCT SCHEMAS
# ============================================================================

class CRMOpportunityProductBase(BaseModel):
    product_code: Optional[str] = None
    product_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    quantity: Decimal = Field(default=Decimal("1.0"), ge=0)
    unit_price: Decimal = Field(default=Decimal("0.0"), ge=0)
    discount_percentage: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    discount_amount: Decimal = Field(default=Decimal("0.0"), ge=0)
    tax_percentage: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal("0.0"), ge=0)
    product_category: Optional[str] = None
    line_notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CRMOpportunityProductCreate(CRMOpportunityProductBase):
    pass


class CRMOpportunityProductUpdate(BaseModel):
    product_code: Optional[str] = None
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, ge=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    tax_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    product_category: Optional[str] = None
    line_notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class CRMOpportunityProductResponse(CRMOpportunityProductBase):
    id: UUID
    opportunity_id: UUID
    total_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# OPPORTUNITY ACTIVITY SCHEMAS
# ============================================================================

class CRMOpportunityActivityBase(BaseModel):
    activity_type: str = Field(..., max_length=50)  # call, meeting, email, task, note
    activity_subject: str = Field(..., min_length=1, max_length=255)
    activity_description: Optional[str] = None
    activity_date: datetime = Field(default_factory=datetime.utcnow)
    duration_minutes: Optional[int] = Field(None, ge=0)
    status: str = Field(default="completed", max_length=50)
    participants: Optional[List[str]] = Field(default_factory=list)
    outcome: Optional[str] = None
    next_action: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CRMOpportunityActivityCreate(CRMOpportunityActivityBase):
    opportunity_id: UUID


class CRMOpportunityActivityUpdate(BaseModel):
    activity_type: Optional[str] = Field(None, max_length=50)
    activity_subject: Optional[str] = Field(None, min_length=1, max_length=255)
    activity_description: Optional[str] = None
    activity_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    participants: Optional[List[str]] = None
    outcome: Optional[str] = None
    next_action: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class CRMOpportunityActivityResponse(CRMOpportunityActivityBase):
    id: UUID
    opportunity_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# OPPORTUNITY SCHEMAS
# ============================================================================

class CRMOpportunityBase(BaseModel):
    opportunity_name: str = Field(..., min_length=1, max_length=255)
    account_id: UUID
    primary_contact_id: Optional[UUID] = None
    opportunity_type: str = Field(default="new_business")
    stage: str = Field(default="prospecting")
    priority: str = Field(default="medium")
    estimated_value: Decimal = Field(default=Decimal("0.0"), ge=0)
    currency: str = Field(default="INR", max_length=3)
    probability: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    lead_source: Optional[str] = Field(None, max_length=100)
    campaign_id: Optional[UUID] = None
    opportunity_owner_id: UUID
    sales_team: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    next_step: Optional[str] = None
    internal_notes: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CRMOpportunityCreate(CRMOpportunityBase):
    products: Optional[List[CRMOpportunityProductCreate]] = Field(default_factory=list)


class CRMOpportunityUpdate(BaseModel):
    opportunity_name: Optional[str] = Field(None, min_length=1, max_length=255)
    primary_contact_id: Optional[UUID] = None
    opportunity_type: Optional[str] = None
    stage: Optional[str] = None
    priority: Optional[str] = None
    estimated_value: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    probability: Optional[Decimal] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    lead_source: Optional[str] = Field(None, max_length=100)
    campaign_id: Optional[UUID] = None
    opportunity_owner_id: Optional[UUID] = None
    sales_team: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    next_step: Optional[str] = None
    internal_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class CRMOpportunityResponse(CRMOpportunityBase):
    id: UUID
    opportunity_number: str
    weighted_value: Decimal
    is_won: bool
    is_lost: bool
    close_reason: Optional[str] = None
    loss_reason: Optional[str] = None
    competitor_name: Optional[str] = None
    actual_close_date: Optional[datetime] = None
    stage_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CRMOpportunityDetailResponse(CRMOpportunityResponse):
    """Extended opportunity response with related data"""
    products: List[CRMOpportunityProductResponse] = Field(default_factory=list)
    activities: List[CRMOpportunityActivityResponse] = Field(default_factory=list)
    account_name: Optional[str] = None
    contact_name: Optional[str] = None
    owner_name: Optional[str] = None


# ============================================================================
# OPPORTUNITY STAGE TRANSITION SCHEMA
# ============================================================================

class CRMOpportunityStageTransition(BaseModel):
    new_stage: str
    reason: Optional[str] = None
    probability: Optional[Decimal] = Field(None, ge=0, le=100)


class CRMOpportunityCloseWon(BaseModel):
    actual_close_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    close_reason: Optional[str] = None
    actual_value: Optional[Decimal] = Field(None, ge=0)


class CRMOpportunityCloseLost(BaseModel):
    actual_close_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    loss_reason: str
    close_reason: Optional[str] = None
    competitor_name: Optional[str] = None


# ============================================================================
# PIPELINE AND ANALYTICS SCHEMAS
# ============================================================================

class PipelineStageStats(BaseModel):
    stage: str
    stage_name: str
    count: int
    total_value: Decimal
    weighted_value: Decimal
    avg_probability: Decimal
    opportunities: List[Dict[str, Any]] = Field(default_factory=list)


class PipelineOverview(BaseModel):
    total_opportunities: int
    total_value: Decimal
    weighted_pipeline_value: Decimal
    avg_deal_size: Decimal
    stages: List[PipelineStageStats]


class WinLossAnalysis(BaseModel):
    total_closed: int
    won_count: int
    lost_count: int
    win_rate: Decimal
    total_won_value: Decimal
    total_lost_value: Decimal
    avg_won_deal_size: Decimal
    avg_lost_deal_size: Decimal
    loss_reasons: Dict[str, int]
    top_competitors: List[Dict[str, Any]]


class OpportunityForecast(BaseModel):
    period: str
    best_case: Decimal
    most_likely: Decimal
    worst_case: Decimal
    opportunities_closing: int


class SalesPerformanceMetrics(BaseModel):
    owner_id: UUID
    owner_name: str
    total_opportunities: int
    won_opportunities: int
    lost_opportunities: int
    win_rate: Decimal
    total_value: Decimal
    won_value: Decimal
    avg_deal_size: Decimal
    avg_sales_cycle_days: Optional[Decimal] = None


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginatedOpportunityList(BaseModel):
    items: List[CRMOpportunityResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


class PaginatedActivityList(BaseModel):
    items: List[CRMOpportunityActivityResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
