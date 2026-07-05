"""
Decision Engine Pydantic Schemas

Request and response schemas for instant decisions, pre-approved offers,
strategies, and analytics.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


# ==================== ENUMS ====================

class DecisionType(str, Enum):
    """Types of decisions"""
    LOAN_APPROVAL = "loan_approval"
    PRE_APPROVED = "pre_approved"
    LIMIT_INCREASE = "limit_increase"
    ELIGIBILITY = "eligibility"
    QUICK_QUOTE = "quick_quote"
    PRODUCT_RECOMMENDATION = "product_recommendation"


class DecisionResult(str, Enum):
    """Decision outcomes"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"
    PENDING = "pending"
    ERROR = "error"


class DecisionStatus(str, Enum):
    """Decision status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    ACCEPTED = "accepted"
    REJECTED_BY_CUSTOMER = "rejected_by_customer"


class OfferType(str, Enum):
    """Pre-approved offer types"""
    PRE_APPROVED_LOAN = "pre_approved_loan"
    LIMIT_INCREASE = "limit_increase"
    SPECIAL_RATE = "special_rate"
    INSTANT_APPROVAL = "instant_approval"


class OfferStatus(str, Enum):
    """Offer status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    USED = "used"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class StrategyType(str, Enum):
    """Decision strategy types"""
    INSTANT = "instant"
    CACHED = "cached"
    RULE_BASED = "rule_based"
    ML_BASED = "ml_based"


# ==================== DECISION FACTOR SCHEMA ====================

class DecisionFactor(BaseModel):
    """A factor that influenced the decision"""
    factor: str = Field(..., description="Factor name")
    value: Any = Field(..., description="Factor value")
    impact: str = Field(..., description="positive, negative, neutral")
    weight: Optional[float] = Field(None, description="Factor weight 0-1")
    description: Optional[str] = Field(None, description="Factor description")


# ==================== INSTANT DECISION SCHEMAS ====================

class InstantDecisionRequest(BaseModel):
    """Request schema for instant decision"""
    decision_type: DecisionType = Field(..., description="Type of decision")
    customer_id: int = Field(..., description="Customer ID")
    product_id: Optional[int] = Field(None, description="Product ID")
    request_data: Dict[str, Any] = Field(..., description="Request parameters")
    use_cache: bool = Field(True, description="Use cached decision if available")
    strategy_code: Optional[str] = Field(None, description="Override default strategy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_type": "loan_approval",
                "customer_id": 12345,
                "product_id": 1,
                "request_data": {
                    "loan_amount": 500000,
                    "tenure": 36,
                    "purpose": "personal",
                    "customer_data": {
                        "monthly_income": 75000,
                        "existing_emi": 15000,
                        "employment_type": "salaried"
                    }
                },
                "use_cache": True
            }
        }


class InstantDecisionResponse(BaseModel):
    """Response schema for instant decision"""
    decision_id: int
    decision_number: str
    decision_result: DecisionResult
    approved_amount: Optional[Decimal] = None
    approved_tenure: Optional[int] = None
    interest_rate: Optional[Decimal] = None
    processing_fee: Optional[Decimal] = None
    monthly_emi: Optional[Decimal] = None
    confidence_score: Optional[Decimal] = None
    decision_reason: Optional[str] = None
    recommendation: Optional[str] = None
    rejection_reasons: Optional[List[str]] = None
    decision_factors: Optional[List[DecisionFactor]] = None
    rules_applied: Optional[List[Dict[str, Any]]] = None
    valid_until: Optional[datetime] = None
    evaluation_time_ms: Optional[int] = None
    cache_hit: bool = False
    strategy_used: str
    
    class Config:
        from_attributes = True


class DecisionDetails(InstantDecisionResponse):
    """Extended decision details with full information"""
    entity_type: str
    entity_id: Optional[int]
    customer_id: int
    product_id: Optional[int]
    request_data: Dict[str, Any]
    status: DecisionStatus
    accepted_at: Optional[datetime]
    rejected_at: Optional[datetime]
    application_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class DecisionAcceptRequest(BaseModel):
    """Request to accept a decision/offer"""
    remarks: Optional[str] = Field(None, description="Acceptance remarks")


class DecisionRejectRequest(BaseModel):
    """Request to reject a decision/offer"""
    reason: str = Field(..., min_length=10, description="Rejection reason")


class DecisionRecalculateRequest(BaseModel):
    """Request to recalculate a decision"""
    use_cache: bool = Field(False, description="Use cache for recalculation")
    updated_data: Optional[Dict[str, Any]] = Field(None, description="Updated request data")


# ==================== PRE-APPROVED OFFER SCHEMAS ====================

class OfferCalculateRequest(BaseModel):
    """Request to calculate pre-approved offer"""
    customer_id: int = Field(..., description="Customer ID")
    product_id: int = Field(..., description="Product ID")
    offer_type: OfferType = Field(OfferType.PRE_APPROVED_LOAN, description="Offer type")
    validity_days: int = Field(30, ge=1, le=90, description="Offer validity in days")


class PreApprovedOfferCreate(BaseModel):
    """Schema for creating pre-approved offer"""
    customer_id: int = Field(..., description="Customer ID")
    product_id: int = Field(..., description="Product ID")
    offer_type: OfferType = Field(..., description="Offer type")
    approved_amount: Decimal = Field(..., gt=0, description="Approved amount")
    min_amount: Optional[Decimal] = Field(None, gt=0, description="Minimum amount")
    max_amount: Decimal = Field(..., gt=0, description="Maximum amount")
    interest_rate: Decimal = Field(..., gt=0, le=50, description="Interest rate %")
    special_rate: bool = Field(False, description="Special rate offer")
    min_tenure: Optional[int] = Field(None, ge=1, description="Minimum tenure")
    max_tenure: int = Field(..., ge=1, description="Maximum tenure")
    processing_fee: Optional[Decimal] = Field(None, ge=0, description="Processing fee")
    processing_fee_waiver: bool = Field(False, description="Fee waiver")
    benefits: Optional[Dict[str, Any]] = Field(None, description="Additional benefits")
    valid_from: datetime = Field(..., description="Validity start")
    valid_until: datetime = Field(..., description="Validity end")
    calculation_factors: Optional[Dict[str, Any]] = Field(None, description="Calculation factors")


class PreApprovedOfferResponse(BaseModel):
    """Response schema for pre-approved offer"""
    id: int
    offer_code: str
    customer_id: int
    product_id: int
    offer_type: str
    approved_amount: Decimal
    min_amount: Optional[Decimal]
    max_amount: Decimal
    interest_rate: Decimal
    special_rate: bool
    min_tenure: Optional[int]
    max_tenure: int
    processing_fee: Optional[Decimal]
    processing_fee_waiver: bool
    benefits: Optional[Dict[str, Any]]
    valid_from: datetime
    valid_until: datetime
    status: str
    viewed_count: int
    used_at: Optional[datetime]
    application_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class OfferUseRequest(BaseModel):
    """Request to use an offer"""
    loan_amount: Decimal = Field(..., gt=0, description="Requested loan amount")
    tenure: int = Field(..., ge=1, description="Requested tenure")
    purpose: str = Field(..., description="Loan purpose")
    remarks: Optional[str] = Field(None, description="Additional remarks")


# ==================== DECISION STRATEGY SCHEMAS ====================

class StrategyConfig(BaseModel):
    """Configuration for decision strategy"""
    rule_categories: List[str] = Field(..., description="Rule categories to evaluate")
    evaluation_strategy: str = Field("all_match", description="Rule evaluation strategy")
    auto_approve_threshold: Decimal = Field(85.0, ge=0, le=100, description="Auto-approve threshold")
    manual_review_threshold: Decimal = Field(70.0, ge=0, le=100, description="Manual review threshold")
    auto_reject_threshold: Optional[Decimal] = Field(None, ge=0, le=100, description="Auto-reject threshold")
    max_amount_auto_approve: Optional[Decimal] = Field(None, gt=0, description="Max auto-approve amount")
    cache_ttl_minutes: int = Field(30, ge=0, le=1440, description="Cache TTL in minutes")
    enable_cache: bool = Field(True, description="Enable caching")
    require_credit_bureau: bool = Field(False, description="Require credit bureau check")
    offer_validity_hours: int = Field(72, ge=1, le=720, description="Offer validity hours")


class DecisionStrategyCreate(BaseModel):
    """Schema for creating decision strategy"""
    strategy_code: str = Field(..., max_length=50, description="Unique strategy code")
    strategy_name: str = Field(..., max_length=200, description="Strategy name")
    decision_type: DecisionType = Field(..., description="Decision type")
    description: Optional[str] = Field(None, description="Strategy description")
    strategy_config: StrategyConfig = Field(..., description="Strategy configuration")
    auto_approve_threshold: Decimal = Field(85.0, ge=0, le=100)
    manual_review_threshold: Decimal = Field(70.0, ge=0, le=100)
    auto_reject_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    max_amount_auto_approve: Optional[Decimal] = Field(None, gt=0)
    min_amount: Optional[Decimal] = Field(None, gt=0)
    priority: int = Field(100, ge=1, le=1000, description="Priority (lower = higher)")
    is_active: bool = Field(True, description="Active status")
    is_default: bool = Field(False, description="Default strategy")


class DecisionStrategyUpdate(BaseModel):
    """Schema for updating decision strategy"""
    strategy_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    strategy_config: Optional[StrategyConfig] = None
    auto_approve_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    manual_review_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    auto_reject_threshold: Optional[Decimal] = Field(None, ge=0, le=100)
    max_amount_auto_approve: Optional[Decimal] = Field(None, gt=0)
    min_amount: Optional[Decimal] = Field(None, gt=0)
    priority: Optional[int] = Field(None, ge=1, le=1000)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class DecisionStrategyResponse(BaseModel):
    """Response schema for decision strategy"""
    id: int
    strategy_code: str
    strategy_name: str
    decision_type: str
    description: Optional[str]
    strategy_config: Dict[str, Any]
    auto_approve_threshold: Decimal
    manual_review_threshold: Decimal
    auto_reject_threshold: Optional[Decimal]
    max_amount_auto_approve: Optional[Decimal]
    min_amount: Optional[Decimal]
    priority: int
    is_active: bool
    is_default: bool
    total_executions: int
    total_approvals: int
    total_rejections: int
    avg_execution_time_ms: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== LIMIT SCHEMAS ====================

class LimitCalculationRequest(BaseModel):
    """Request to calculate credit limit"""
    customer_id: int = Field(..., description="Customer ID")
    product_id: int = Field(..., description="Product ID")
    validity_days: int = Field(90, ge=1, le=365, description="Limit validity days")


class DecisionLimitResponse(BaseModel):
    """Response schema for credit limit"""
    id: int
    customer_id: int
    product_id: int
    approved_limit: Decimal
    utilized_amount: Decimal
    available_limit: Decimal
    calculation_date: datetime
    calculation_factors: Optional[Dict[str, Any]]
    credit_score: Optional[int]
    risk_category: Optional[str]
    valid_from: datetime
    valid_until: datetime
    next_review_date: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True


# ==================== ANALYTICS SCHEMAS ====================

class DecisionMetrics(BaseModel):
    """Decision metrics summary"""
    total_requests: int
    approved_count: int
    rejected_count: int
    manual_review_count: int
    error_count: int
    approval_rate: Decimal
    rejection_rate: Decimal
    manual_review_rate: Decimal
    avg_evaluation_time_ms: int
    cache_hit_rate: Decimal
    total_approved_amount: Decimal
    avg_approved_amount: Decimal
    avg_confidence_score: Decimal


class DecisionAnalyticsResponse(BaseModel):
    """Response for decision analytics"""
    date: date
    decision_type: str
    strategy_code: Optional[str]
    metrics: DecisionMetrics


class ApprovalRateTrend(BaseModel):
    """Approval rate trend data"""
    date: date
    decision_type: str
    approval_rate: Decimal
    total_requests: int
    approved_count: int


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    decision_type: str
    avg_evaluation_time_ms: int
    min_evaluation_time_ms: Optional[int]
    max_evaluation_time_ms: Optional[int]
    p95_evaluation_time_ms: Optional[int]
    cache_hit_rate: Decimal


class CacheStatistics(BaseModel):
    """Cache statistics"""
    total_cached_entries: int
    cache_hit_count: int
    cache_miss_count: int
    cache_hit_rate: Decimal
    avg_ttl_minutes: int
    oldest_entry_age_minutes: Optional[int]


class DecisionTypeStatistics(BaseModel):
    """Statistics by decision type"""
    decision_type: str
    total_requests: int
    approval_rate: Decimal
    avg_evaluation_time_ms: int
    avg_approved_amount: Decimal
    cache_hit_rate: Decimal


# ==================== FILTER SCHEMAS ====================

class DecisionListFilters(BaseModel):
    """Filters for listing decisions"""
    decision_type: Optional[DecisionType] = None
    decision_result: Optional[DecisionResult] = None
    status: Optional[DecisionStatus] = None
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    cache_hit: Optional[bool] = None


class OfferListFilters(BaseModel):
    """Filters for listing offers"""
    offer_type: Optional[OfferType] = None
    status: Optional[OfferStatus] = None
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    valid_only: bool = True  # Only show currently valid offers


# ==================== QUICK QUOTE SCHEMA ====================

class QuickQuoteRequest(BaseModel):
    """Request for quick loan quote"""
    customer_id: int = Field(..., description="Customer ID")
    product_id: int = Field(..., description="Product ID")
    loan_amount: Decimal = Field(..., gt=0, description="Requested amount")
    tenure: int = Field(..., ge=1, description="Requested tenure")


class QuickQuoteResponse(BaseModel):
    """Response for quick quote"""
    eligible: bool
    approved_amount: Optional[Decimal]
    interest_rate: Optional[Decimal]
    processing_fee: Optional[Decimal]
    monthly_emi: Optional[Decimal]
    total_interest: Optional[Decimal]
    total_repayment: Optional[Decimal]
    eligibility_message: str
    decision_factors: Optional[List[DecisionFactor]]


# ==================== EXPLANATION SCHEMA ====================

class DecisionExplanation(BaseModel):
    """Detailed explanation of a decision"""
    decision_id: int
    decision_number: str
    decision_result: DecisionResult
    explanation: str
    decision_factors: List[DecisionFactor]
    rules_applied: List[Dict[str, Any]]
    confidence_score: Decimal
    recommendation: str
    next_steps: List[str]

