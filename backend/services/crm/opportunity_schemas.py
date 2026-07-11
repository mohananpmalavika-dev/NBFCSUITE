"""
CRM Opportunity Management Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS (matching database)
# ============================================================================

class OpportunityStageEnum(str, Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityTypeEnum(str, Enum):
    NEW_BUSINESS = "new_business"
    EXISTING_CUSTOMER = "existing_customer"
    UPSELL = "upsell"
    CROSS_SELL = "cross_sell"
    RENEWAL = "renewal"


class OpportunityPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OpportunitySourceEnum(str, Enum):
    INBOUND_LEAD = "inbound_lead"
    OUTBOUND_PROSPECTING = "outbound_prospecting"
    REFERRAL = "referral"
    PARTNER = "partner"
    MARKETING_CAMPAIGN = "marketing_campaign"
    TRADE_SHOW = "trade_show"
    WEBSITE = "website"
    EXISTING_CUSTOMER = "existing_customer"
    OTHER = "other"


class LossReasonEnum(str, Enum):
    PRICE_TOO_HIGH = "price_too_high"
    LOST_TO_COMPETITOR = "lost_to_competitor"
    NO_BUDGET = "no_budget"
    NO_DECISION = "no_decision"
    TIMING_NOT_RIGHT = "timing_not_right"
    PRODUCT_NOT_FIT = "product_not_fit"
    WENT_WITH_INCUMBENT = "went_with_incumbent"
    PROJECT_CANCELLED = "project_cancelled"
    UNRESPONSIVE = "unresponsive"
    OTHER = "other"


class CompetitorPositionEnum(str, Enum):
    UNKNOWN = "unknown"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    INCUMBENT = "incumbent"


class ActivityOutcomeEnum(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    NO_ANSWER = "no_answer"


# ============================================================================
# OPPORTUNITY SCHEMAS
# ============================================================================

class OpportunityBase(BaseModel):
    """Base opportunity fields"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    opportunity_type: OpportunityTypeEnum
    source: OpportunitySourceEnum
    
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    contact_name: str = Field(..., min_length=1, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_mobile: str = Field(..., min_length=10, max_length=20)
    company_name: Optional[str] = None
    
    estimated_value: Decimal = Field(..., gt=0)
    expected_revenue: Optional[Decimal] = None
    currency: str = "INR"
    
    current_stage: OpportunityStageEnum = OpportunityStageEnum.PROSPECTING
    win_probability: int = Field(default=10, ge=0, le=100)
    priority: OpportunityPriorityEnum = OpportunityPriorityEnum.MEDIUM
    
    expected_close_date: date
    
    next_step: Optional[str] = None
    pain_points: Optional[List[str]] = None
    decision_makers: Optional[List[Dict[str, str]]] = None
    buying_process: Optional[str] = None
    
    budget_confirmed: bool = False
    authority_confirmed: bool = False
    need_confirmed: bool = False
    timeline_confirmed: bool = False
    
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    @validator('contact_mobile')
    def validate_mobile(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Mobile must contain only digits')
        return v


class OpportunityCreate(OpportunityBase):
    """Create new opportunity"""
    owner_user_id: Optional[int] = None  # If not provided, defaults to current user
    sales_team_ids: Optional[List[int]] = None


class OpportunityUpdate(BaseModel):
    """Update existing opportunity"""
    name: Optional[str] = None
    description: Optional[str] = None
    opportunity_type: Optional[OpportunityTypeEnum] = None
    
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_mobile: Optional[str] = None
    company_name: Optional[str] = None
    
    estimated_value: Optional[Decimal] = None
    expected_revenue: Optional[Decimal] = None
    
    priority: Optional[OpportunityPriorityEnum] = None
    expected_close_date: Optional[date] = None
    
    next_step: Optional[str] = None
    pain_points: Optional[List[str]] = None
    decision_makers: Optional[List[Dict[str, str]]] = None
    buying_process: Optional[str] = None
    
    budget_confirmed: Optional[bool] = None
    authority_confirmed: Optional[bool] = None
    need_confirmed: Optional[bool] = None
    timeline_confirmed: Optional[bool] = None
    
    tags: Optional[List[str]] = None


class OpportunityResponse(OpportunityBase):
    """Opportunity response with all details"""
    id: int
    opportunity_code: str
    
    owner_user_id: int
    owner_name: Optional[str] = None
    sales_team_ids: Optional[List[int]] = None
    
    actual_value: Optional[Decimal] = None
    stage_entered_date: datetime
    previous_stage: Optional[OpportunityStageEnum] = None
    
    is_active: bool
    is_won: bool
    is_lost: bool
    
    won_date: Optional[datetime] = None
    won_value: Optional[Decimal] = None
    won_reason: Optional[str] = None
    
    lost_date: Optional[datetime] = None
    loss_reason: Optional[LossReasonEnum] = None
    loss_reason_details: Optional[str] = None
    competitor_name: Optional[str] = None
    
    days_in_pipeline: int
    days_in_current_stage: int
    stage_changes_count: int
    activities_count: int
    last_activity_date: Optional[datetime] = None
    
    first_contact_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OpportunityListItem(BaseModel):
    """Simplified opportunity for list views"""
    id: int
    opportunity_code: str
    name: str
    company_name: Optional[str] = None
    contact_name: str
    contact_mobile: str
    
    estimated_value: Decimal
    currency: str
    
    current_stage: OpportunityStageEnum
    win_probability: int
    priority: OpportunityPriorityEnum
    
    owner_name: Optional[str] = None
    expected_close_date: date
    days_in_pipeline: int
    days_in_current_stage: int
    
    is_won: bool
    is_lost: bool
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedOpportunityResponse(BaseModel):
    """Paginated opportunity list"""
    items: List[OpportunityListItem]
    total: int
    page: int
    page_size: int
    pages: int


class OpportunityFilters(BaseModel):
    """Filters for opportunity list"""
    page: int = 1
    page_size: int = 20
    search: Optional[str] = None
    
    stage: Optional[OpportunityStageEnum] = None
    opportunity_type: Optional[OpportunityTypeEnum] = None
    source: Optional[OpportunitySourceEnum] = None
    priority: Optional[OpportunityPriorityEnum] = None
    
    owner_user_id: Optional[int] = None
    is_won: Optional[bool] = None
    is_lost: Optional[bool] = None
    is_active: Optional[bool] = None
    
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    min_probability: Optional[int] = None
    max_probability: Optional[int] = None
    
    close_date_from: Optional[date] = None
    close_date_to: Optional[date] = None
    created_from: Optional[date] = None
    created_to: Optional[date] = None


# ============================================================================
# STAGE TRANSITION SCHEMAS
# ============================================================================

class StageTransitionRequest(BaseModel):
    """Request to move opportunity to new stage"""
    to_stage: OpportunityStageEnum
    win_probability: Optional[int] = Field(None, ge=0, le=100)
    change_reason: Optional[str] = None
    notes: Optional[str] = None


class StageHistoryResponse(BaseModel):
    """Stage history item"""
    id: int
    opportunity_id: int
    from_stage: Optional[OpportunityStageEnum] = None
    to_stage: OpportunityStageEnum
    stage_entered_date: datetime
    stage_exited_date: Optional[datetime] = None
    days_in_stage: Optional[int] = None
    probability_before: Optional[int] = None
    probability_after: Optional[int] = None
    value_before: Optional[Decimal] = None
    value_after: Optional[Decimal] = None
    changed_by_name: Optional[str] = None
    change_reason: Optional[str] = None
    notes: Optional[str] = None
    is_forward: bool
    is_current: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# WIN/LOSS SCHEMAS
# ============================================================================

class OpportunityWinRequest(BaseModel):
    """Mark opportunity as won"""
    won_value: Decimal = Field(..., gt=0)
    won_reason: Optional[str] = None
    actual_close_date: Optional[date] = None
    notes: Optional[str] = None


class OpportunityLossRequest(BaseModel):
    """Mark opportunity as lost"""
    loss_reason: LossReasonEnum
    loss_reason_details: str
    competitor_name: Optional[str] = None
    actual_close_date: Optional[date] = None
    notes: Optional[str] = None


# ============================================================================
# ACTIVITY SCHEMAS
# ============================================================================

class OpportunityActivityCreate(BaseModel):
    """Create opportunity activity"""
    opportunity_id: int
    activity_type: str = Field(..., min_length=1, max_length=50)
    activity_title: str = Field(..., min_length=1, max_length=255)
    activity_description: Optional[str] = None
    activity_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    outcome: Optional[ActivityOutcomeEnum] = None
    outcome_details: Optional[str] = None
    next_action: Optional[str] = None
    attendees: Optional[List[Dict[str, str]]] = None
    is_key_milestone: bool = False


class OpportunityActivityUpdate(BaseModel):
    """Update opportunity activity"""
    activity_title: Optional[str] = None
    activity_description: Optional[str] = None
    outcome: Optional[ActivityOutcomeEnum] = None
    outcome_details: Optional[str] = None
    next_action: Optional[str] = None


class OpportunityActivityResponse(BaseModel):
    """Activity response"""
    id: int
    opportunity_id: int
    activity_type: str
    activity_title: str
    activity_description: Optional[str] = None
    activity_date: datetime
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None
    outcome_details: Optional[str] = None
    next_action: Optional[str] = None
    performed_by_name: Optional[str] = None
    attendees: Optional[List[Dict[str, str]]] = None
    is_key_milestone: bool
    is_system_generated: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedActivityResponse(BaseModel):
    """Paginated activity list"""
    items: List[OpportunityActivityResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================

class OpportunityProductCreate(BaseModel):
    """Add product to opportunity"""
    opportunity_id: int
    product_name: str = Field(..., min_length=1, max_length=255)
    product_code: Optional[str] = None
    product_category: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal = Field(default=1, gt=0)
    unit_price: Decimal = Field(..., gt=0)
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    discount_amount: Decimal = Field(default=0, ge=0)
    loan_product_id: Optional[int] = None
    loan_amount: Optional[Decimal] = None
    loan_tenure_months: Optional[int] = None
    interest_rate: Optional[Decimal] = None
    notes: Optional[str] = None


class OpportunityProductUpdate(BaseModel):
    """Update opportunity product"""
    product_name: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class OpportunityProductResponse(BaseModel):
    """Product response"""
    id: int
    opportunity_id: int
    product_name: str
    product_code: Optional[str] = None
    product_category: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    line_total: Decimal
    loan_product_id: Optional[int] = None
    loan_amount: Optional[Decimal] = None
    loan_tenure_months: Optional[int] = None
    interest_rate: Optional[Decimal] = None
    notes: Optional[str] = None
    sort_order: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# COMPETITOR SCHEMAS
# ============================================================================

class OpportunityCompetitorCreate(BaseModel):
    """Add competitor to opportunity"""
    opportunity_id: int
    competitor_name: str = Field(..., min_length=1, max_length=255)
    competitor_product: Optional[str] = None
    position: CompetitorPositionEnum = CompetitorPositionEnum.UNKNOWN
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    competitor_price: Optional[Decimal] = None
    win_strategy: Optional[str] = None
    notes: Optional[str] = None


class OpportunityCompetitorUpdate(BaseModel):
    """Update competitor"""
    position: Optional[CompetitorPositionEnum] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    competitor_price: Optional[Decimal] = None
    win_strategy: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class OpportunityCompetitorResponse(BaseModel):
    """Competitor response"""
    id: int
    opportunity_id: int
    competitor_name: str
    competitor_product: Optional[str] = None
    position: CompetitorPositionEnum
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    competitor_price: Optional[Decimal] = None
    win_strategy: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    eliminated_date: Optional[datetime] = None
    elimination_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# NOTE SCHEMAS
# ============================================================================

class OpportunityNoteCreate(BaseModel):
    """Create opportunity note"""
    opportunity_id: int
    title: Optional[str] = None
    content: str = Field(..., min_length=1)
    note_type: Optional[str] = None
    is_pinned: bool = False


class OpportunityNoteUpdate(BaseModel):
    """Update opportunity note"""
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None
    is_pinned: Optional[bool] = None


class OpportunityNoteResponse(BaseModel):
    """Note response"""
    id: int
    opportunity_id: int
    title: Optional[str] = None
    content: str
    note_type: Optional[str] = None
    is_pinned: bool
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# ANALYTICS & DASHBOARD SCHEMAS
# ============================================================================

class OpportunityDashboardStats(BaseModel):
    """Dashboard statistics"""
    # Pipeline overview
    total_opportunities: int
    active_opportunities: int
    total_pipeline_value: Decimal
    weighted_pipeline_value: Decimal  # Sum of (value * probability)
    
    # Stage distribution
    prospecting_count: int
    qualification_count: int
    needs_analysis_count: int
    proposal_count: int
    negotiation_count: int
    
    # Win/Loss
    won_count: int
    won_value: Decimal
    lost_count: int
    lost_value: Decimal
    win_rate: float  # Percentage
    
    # Timeline
    avg_days_in_pipeline: float
    closing_this_month_count: int
    closing_this_month_value: Decimal
    overdue_count: int
    
    # Activity
    activities_this_week: int
    opportunities_without_activity_7days: int
    
    # Probabilities
    high_probability_count: int  # > 70%
    high_probability_value: Decimal


class PipelineAnalytics(BaseModel):
    """Pipeline analytics by stage"""
    stage: OpportunityStageEnum
    count: int
    total_value: Decimal
    avg_value: Decimal
    avg_days_in_stage: float
    conversion_rate: float  # To next stage
    

class WinLossAnalysis(BaseModel):
    """Win/loss analysis"""
    period: str  # e.g., "2024-Q1", "2024-01"
    
    won_count: int
    won_value: Decimal
    avg_won_value: Decimal
    avg_days_to_win: float
    
    lost_count: int
    lost_value: Decimal
    
    win_rate: float
    
    # Loss reasons breakdown
    loss_reasons: Dict[str, int]
    
    # Top competitors
    top_competitors: List[Dict[str, Any]]


class ForecastData(BaseModel):
    """Sales forecast data"""
    period: str
    
    best_case: Decimal  # Sum of opportunities > 90% probability
    commit: Decimal  # Sum of opportunities > 70% probability
    most_likely: Decimal  # Weighted pipeline value
    pipeline: Decimal  # Total pipeline value
    
    opportunities_closing: int


# ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkOpportunityUpdate(BaseModel):
    """Bulk update opportunities"""
    opportunity_ids: List[int]
    owner_user_id: Optional[int] = None
    priority: Optional[OpportunityPriorityEnum] = None
    stage: Optional[OpportunityStageEnum] = None
    tags: Optional[List[str]] = None


class BulkDeleteRequest(BaseModel):
    """Bulk delete opportunities"""
    opportunity_ids: List[int]
    reason: Optional[str] = None
