"""
CRM Lead Management Schemas
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

class LeadSourceEnum(str, Enum):
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


class LeadStatusEnum(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    NURTURING = "nurturing"
    CONVERTED = "converted"
    LOST = "lost"
    DUPLICATE = "duplicate"
    INVALID = "invalid"


class LeadPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class LeadTemperatureEnum(str, Enum):
    COLD = "cold"
    WARM = "warm"
    HOT = "hot"


class FollowUpStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class FollowUpTypeEnum(str, Enum):
    PHONE_CALL = "phone_call"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    MEETING = "meeting"
    SITE_VISIT = "site_visit"
    DOCUMENT_COLLECTION = "document_collection"
    OTHER = "other"


# ============================================================================
# LEAD SCHEMAS
# ============================================================================

class LeadBase(BaseModel):
    """Base lead fields"""
    source: LeadSourceEnum
    source_details: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: str = Field(..., min_length=10, max_length=20)
    alternate_mobile: Optional[str] = None
    city_id: Optional[int] = None
    state_id: Optional[int] = None
    pincode: Optional[str] = None
    product_interest: Optional[str] = None
    loan_amount_required: Optional[Decimal] = None
    monthly_income: Optional[Decimal] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    remarks: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('mobile', 'alternate_mobile')
    def validate_mobile(cls, v):
        if v and not v.isdigit():
            raise ValueError('Mobile must contain only digits')
        if v and len(v) < 10:
            raise ValueError('Mobile must be at least 10 digits')
        return v


class LeadCreate(LeadBase):
    """Create new lead"""
    pass


class LeadUpdate(BaseModel):
    """Update existing lead"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    city_id: Optional[int] = None
    state_id: Optional[int] = None
    pincode: Optional[str] = None
    product_interest: Optional[str] = None
    loan_amount_required: Optional[Decimal] = None
    monthly_income: Optional[Decimal] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    status: Optional[LeadStatusEnum] = None
    priority: Optional[LeadPriorityEnum] = None
    remarks: Optional[str] = None


class LeadResponse(LeadBase):
    """Lead response with all details"""
    id: int
    lead_code: str
    full_name: Optional[str] = None
    lead_score: int
    score_breakdown: Optional[Dict[str, Any]] = None
    lead_temperature: LeadTemperatureEnum
    status: LeadStatusEnum
    priority: LeadPriorityEnum
    is_qualified: bool
    qualification_reason: Optional[str] = None
    assigned_to_user_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    assigned_date: Optional[datetime] = None
    last_contacted_date: Optional[datetime] = None
    next_follow_up_date: Optional[datetime] = None
    follow_up_count: int
    response_time_hours: Optional[int] = None
    is_converted: bool
    converted_date: Optional[datetime] = None
    conversion_time_hours: Optional[int] = None
    is_lost: bool
    lost_reason: Optional[str] = None
    is_duplicate: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LeadListItem(BaseModel):
    """Simplified lead for list views"""
    id: int
    lead_code: str
    full_name: str
    mobile: str
    email: Optional[str] = None
    source: LeadSourceEnum
    product_interest: Optional[str] = None
    lead_score: int
    lead_temperature: LeadTemperatureEnum
    status: LeadStatusEnum
    priority: LeadPriorityEnum
    assigned_to_name: Optional[str] = None
    next_follow_up_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedLeadResponse(BaseModel):
    """Paginated lead list"""
    items: List[LeadListItem]
    total: int
    page: int
    page_size: int
    pages: int


class LeadDashboardStats(BaseModel):
    """Lead dashboard statistics"""
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    converted_leads: int
    lost_leads: int
    hot_leads: int
    overdue_follow_ups: int
    avg_lead_score: float
    avg_conversion_time_hours: Optional[float] = None
    conversion_rate: float
    today_follow_ups: int


# ============================================================================
# LEAD ACTIONS SCHEMAS
# ============================================================================

class LeadAssignRequest(BaseModel):
    """Assign lead to user"""
    user_id: int
    notes: Optional[str] = None


class LeadQualifyRequest(BaseModel):
    """Qualify/Disqualify lead"""
    is_qualified: bool
    reason: str = Field(..., min_length=1)


class LeadConvertRequest(BaseModel):
    """Convert lead to customer"""
    create_customer: bool = True
    create_loan_application: bool = False
    loan_product_id: Optional[int] = None
    notes: Optional[str] = None


class LeadLostRequest(BaseModel):
    """Mark lead as lost"""
    reason: str = Field(..., min_length=1)
    remarks: Optional[str] = None


# ============================================================================
# FOLLOW-UP SCHEMAS
# ============================================================================

class LeadFollowUpBase(BaseModel):
    """Base follow-up fields"""
    follow_up_type: FollowUpTypeEnum
    scheduled_date: datetime
    subject: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to_user_id: Optional[int] = None


class LeadFollowUpCreate(LeadFollowUpBase):
    """Create follow-up"""
    lead_id: int


class LeadFollowUpUpdate(BaseModel):
    """Update follow-up"""
    follow_up_type: Optional[FollowUpTypeEnum] = None
    scheduled_date: Optional[datetime] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    status: Optional[FollowUpStatusEnum] = None


class LeadFollowUpComplete(BaseModel):
    """Complete follow-up"""
    outcome: str = Field(..., min_length=1)
    next_action: Optional[str] = None
    customer_interested: Optional[bool] = None
    customer_response: Optional[str] = None
    duration_minutes: Optional[int] = None


class LeadFollowUpResponse(LeadFollowUpBase):
    """Follow-up response"""
    id: int
    lead_id: int
    status: FollowUpStatusEnum
    completed_date: Optional[datetime] = None
    outcome: Optional[str] = None
    next_action: Optional[str] = None
    customer_interested: Optional[bool] = None
    customer_response: Optional[str] = None
    duration_minutes: Optional[int] = None
    assigned_to_name: Optional[str] = None
    is_cancelled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedFollowUpResponse(BaseModel):
    """Paginated follow-up list"""
    items: List[LeadFollowUpResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# ACTIVITY SCHEMAS
# ============================================================================

class LeadActivityCreate(BaseModel):
    """Create activity"""
    activity_type: str
    activity_title: str
    activity_description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LeadActivityResponse(BaseModel):
    """Activity response"""
    id: int
    lead_id: int
    activity_type: str
    activity_title: str
    activity_description: Optional[str] = None
    activity_date: datetime
    performed_by_name: Optional[str] = None
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_system_generated: bool
    
    class Config:
        from_attributes = True


class PaginatedActivityResponse(BaseModel):
    """Paginated activity list"""
    items: List[LeadActivityResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# SCORING RULE SCHEMAS
# ============================================================================

class LeadScoringRuleBase(BaseModel):
    """Base scoring rule"""
    rule_name: str
    rule_description: Optional[str] = None
    rule_category: str
    field_name: str
    operator: str
    field_value: Optional[str] = None
    score_points: int
    priority: int = 1


class LeadScoringRuleCreate(LeadScoringRuleBase):
    """Create scoring rule"""
    pass


class LeadScoringRuleUpdate(BaseModel):
    """Update scoring rule"""
    rule_name: Optional[str] = None
    rule_description: Optional[str] = None
    score_points: Optional[int] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class LeadScoringRuleResponse(LeadScoringRuleBase):
    """Scoring rule response"""
    id: int
    is_active: bool
    execution_count: int
    last_executed_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ASSIGNMENT RULE SCHEMAS
# ============================================================================

class LeadAssignmentRuleBase(BaseModel):
    """Base assignment rule"""
    rule_name: str
    rule_description: Optional[str] = None
    priority: int = 1
    conditions: Dict[str, Any]
    assignment_type: str
    assign_to_user_id: Optional[int] = None
    assign_to_branch_id: Optional[int] = None
    assign_to_team: Optional[str] = None
    max_leads_per_user: Optional[int] = None


class LeadAssignmentRuleCreate(LeadAssignmentRuleBase):
    """Create assignment rule"""
    pass


class LeadAssignmentRuleUpdate(BaseModel):
    """Update assignment rule"""
    rule_name: Optional[str] = None
    rule_description: Optional[str] = None
    priority: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class LeadAssignmentRuleResponse(LeadAssignmentRuleBase):
    """Assignment rule response"""
    id: int
    is_active: bool
    execution_count: int
    success_count: int
    failure_count: int
    last_executed_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkLeadAssignRequest(BaseModel):
    """Bulk assign leads"""
    lead_ids: List[int]
    user_id: int
    notes: Optional[str] = None


class BulkLeadStatusUpdate(BaseModel):
    """Bulk update lead status"""
    lead_ids: List[int]
    status: LeadStatusEnum
    reason: Optional[str] = None


class BulkLeadImport(BaseModel):
    """Bulk import leads"""
    leads: List[LeadCreate]
    auto_assign: bool = True
    auto_score: bool = True


# ============================================================================
# FILTERS AND SEARCH
# ============================================================================

class LeadFilters(BaseModel):
    """Lead filter parameters"""
    page: int = 1
    page_size: int = 20
    search: Optional[str] = None
    source: Optional[LeadSourceEnum] = None
    status: Optional[LeadStatusEnum] = None
    priority: Optional[LeadPriorityEnum] = None
    temperature: Optional[LeadTemperatureEnum] = None
    assigned_to_user_id: Optional[int] = None
    is_qualified: Optional[bool] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    created_from: Optional[date] = None
    created_to: Optional[date] = None
    next_follow_up_from: Optional[date] = None
    next_follow_up_to: Optional[date] = None
