"""
Decision Engine Database Models

Models for instant decision-making, pre-approved offers, decision strategies,
caching, and analytics.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, Numeric, JSON, Index
from sqlalchemy.sql import func
from datetime import datetime
from backend.shared.database.connection import Base


class InstantDecision(Base):
    """
    Instant decision records for loan approvals and other financial decisions.
    Stores request, response, and decision factors.
    """
    __tablename__ = "instant_decisions"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_number = Column(String(50), unique=True, nullable=False, index=True)

    # Decision Details
    decision_type = Column(String(50), nullable=False, index=True)
    # Types: loan_approval, pre_approved, limit_increase, eligibility, quick_quote
    entity_type = Column(String(50), nullable=False)  # loan_application, customer, product
    entity_id = Column(Integer, nullable=True, index=True)

    # Customer Information
    customer_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=True, index=True)

    # Request Data
    request_data = Column(JSON, nullable=False)
    # Stores complete request parameters

    # Decision Result
    decision_result = Column(String(50), nullable=False, index=True)
    # Results: approved, rejected, manual_review, pending
    approved_amount = Column(Numeric(15, 2), nullable=True)
    approved_tenure = Column(Integer, nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    processing_fee = Column(Numeric(10, 2), nullable=True)
    monthly_emi = Column(Numeric(10, 2), nullable=True)

    # Decision Factors
    decision_factors = Column(JSON, nullable=True)
    # List of factors that influenced the decision
    rules_applied = Column(JSON, nullable=True)
    # Rules evaluated during decision
    confidence_score = Column(Numeric(5, 2), nullable=True)
    # Confidence score 0-100

    # Explanation
    decision_reason = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    rejection_reasons = Column(JSON, nullable=True)
    # List of reasons if rejected

    # Strategy
    strategy_used = Column(String(50), nullable=False)
    # instant, cached, rule_based, ml_based
    strategy_id = Column(Integer, nullable=True)

    # Performance
    evaluation_time_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)
    rules_evaluation_time_ms = Column(Integer, nullable=True)

    # Status
    status = Column(String(50), default="active", index=True)
    # active, expired, superseded, accepted, rejected_by_customer
    valid_until = Column(DateTime, nullable=True)
    # Offer validity period

    # Acceptance
    accepted_at = Column(DateTime, nullable=True)
    accepted_by = Column(Integer, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    rejected_at = Column(DateTime, nullable=True)

    # Application Created
    application_id = Column(Integer, nullable=True)
    # If customer accepts and creates application

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_instant_decisions_customer_status', 'customer_id', 'status'),
        Index('idx_instant_decisions_tenant_type', 'tenant_id', 'decision_type'),
        Index('idx_instant_decisions_created_at', 'created_at'),
    )


class PreApprovedOffer(Base):
    """
    Pre-calculated offers for eligible customers.
    System-generated or manually created offers.
    """
    __tablename__ = "pre_approved_offers"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_code = Column(String(50), unique=True, nullable=False, index=True)

    # Customer & Product
    customer_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)

    # Offer Type
    offer_type = Column(String(50), nullable=False, index=True)
    # Types: pre_approved_loan, limit_increase, special_rate, instant_approval

    # Amount Details
    approved_amount = Column(Numeric(15, 2), nullable=False)
    min_amount = Column(Numeric(15, 2), nullable=True)
    max_amount = Column(Numeric(15, 2), nullable=False)

    # Terms
    interest_rate = Column(Numeric(5, 2), nullable=False)
    special_rate = Column(Boolean, default=False)
    min_tenure = Column(Integer, nullable=True)
    max_tenure = Column(Integer, nullable=False)
    processing_fee = Column(Numeric(10, 2), nullable=True)
    processing_fee_waiver = Column(Boolean, default=False)

    # Benefits
    benefits = Column(JSON, nullable=True)
    # {
    #   "zero_processing_fee": true,
    #   "instant_disbursement": true,
    #   "flexible_tenure": true
    # }

    # Validity
    valid_from = Column(DateTime, nullable=False, index=True)
    valid_until = Column(DateTime, nullable=False, index=True)

    # Status
    status = Column(String(50), default="active", index=True)
    # active, expired, used, cancelled, superseded

    # Usage Tracking
    viewed_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime, nullable=True)
    used_at = Column(DateTime, nullable=True)
    used_by = Column(Integer, nullable=True)
    application_id = Column(Integer, nullable=True)

    # Calculation Details
    calculation_factors = Column(JSON, nullable=True)
    # Factors used to calculate this offer
    credit_score = Column(Integer, nullable=True)
    risk_category = Column(String(50), nullable=True)

    # Source
    source = Column(String(50), default="system")
    # system, manual, campaign
    campaign_id = Column(Integer, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_pre_approved_offers_customer_status', 'customer_id', 'status'),
        Index('idx_pre_approved_offers_validity', 'valid_from', 'valid_until'),
    )


class DecisionStrategy(Base):
    """
    Configurable decision strategies for different decision types.
    Defines rules, thresholds, and behavior for instant decisions.
    """
    __tablename__ = "decision_strategies"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_code = Column(String(50), unique=True, nullable=False, index=True)

    # Strategy Details
    strategy_name = Column(String(200), nullable=False)
    decision_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Configuration
    strategy_config = Column(JSON, nullable=False)
    # {
    #   "rule_categories": ["credit_policy", "risk_assessment"],
    #   "evaluation_strategy": "all_match",
    #   "auto_approve_threshold": 85,
    #   "manual_review_threshold": 70,
    #   "auto_reject_threshold": 50,
    #   "max_amount_auto_approve": 500000,
    #   "cache_ttl_minutes": 30,
    #   "enable_cache": true,
    #   "require_credit_bureau": false,
    #   "offer_validity_hours": 72
    # }

    # Thresholds
    auto_approve_threshold = Column(Numeric(5, 2), nullable=False, default=85.0)
    manual_review_threshold = Column(Numeric(5, 2), nullable=False, default=70.0)
    auto_reject_threshold = Column(Numeric(5, 2), nullable=True)

    # Limits
    max_amount_auto_approve = Column(Numeric(15, 2), nullable=True)
    min_amount = Column(Numeric(15, 2), nullable=True)

    # Priority
    priority = Column(Integer, default=100)
    # Lower number = higher priority

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)

    # Performance Tracking
    total_executions = Column(Integer, default=0)
    total_approvals = Column(Integer, default=0)
    total_rejections = Column(Integer, default=0)
    avg_execution_time_ms = Column(Integer, default=0)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_decision_strategies_type_active', 'decision_type', 'is_active'),
        Index('idx_decision_strategies_tenant_active', 'tenant_id', 'is_active'),
    )


class DecisionCache(Base):
    """
    Cache for instant decision results to improve performance.
    TTL-based expiration with hit tracking.
    """
    __tablename__ = "decision_cache"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    # MD5 hash of (customer_id, decision_type, request_params)

    # Cache Details
    decision_type = Column(String(50), nullable=False, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=True)

    # Cached Data
    cached_decision = Column(JSON, nullable=False)
    # Complete decision response

    # Cache Metadata
    hit_count = Column(Integer, default=0)
    last_hit_at = Column(DateTime, nullable=True)
    
    # TTL
    ttl_minutes = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_decision_cache_customer_type', 'customer_id', 'decision_type'),
        Index('idx_decision_cache_expires_at', 'expires_at'),
    )


class DecisionAnalytics(Base):
    """
    Aggregated analytics and metrics for decision performance.
    Time-series data for monitoring and reporting.
    """
    __tablename__ = "decision_analytics"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Time Period
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)  # 0-23 for hourly metrics
    period_type = Column(String(20), nullable=False, default="daily")
    # daily, hourly

    # Decision Details
    decision_type = Column(String(50), nullable=False, index=True)
    strategy_code = Column(String(50), nullable=True, index=True)

    # Volume Metrics
    total_requests = Column(Integer, default=0)
    approved_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    manual_review_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    # Approval Metrics
    approval_rate = Column(Numeric(5, 2), default=0)
    # Approved / (Approved + Rejected) * 100
    rejection_rate = Column(Numeric(5, 2), default=0)
    manual_review_rate = Column(Numeric(5, 2), default=0)

    # Performance Metrics
    avg_evaluation_time_ms = Column(Integer, default=0)
    min_evaluation_time_ms = Column(Integer, nullable=True)
    max_evaluation_time_ms = Column(Integer, nullable=True)
    p95_evaluation_time_ms = Column(Integer, nullable=True)

    # Cache Metrics
    cache_hit_count = Column(Integer, default=0)
    cache_miss_count = Column(Integer, default=0)
    cache_hit_rate = Column(Numeric(5, 2), default=0)

    # Amount Metrics
    total_approved_amount = Column(Numeric(18, 2), default=0)
    avg_approved_amount = Column(Numeric(15, 2), default=0)
    min_approved_amount = Column(Numeric(15, 2), nullable=True)
    max_approved_amount = Column(Numeric(15, 2), nullable=True)

    # Confidence Metrics
    avg_confidence_score = Column(Numeric(5, 2), default=0)
    low_confidence_count = Column(Integer, default=0)
    # Count of decisions with confidence < 70

    # Conversion Metrics
    acceptance_count = Column(Integer, default=0)
    acceptance_rate = Column(Numeric(5, 2), default=0)
    # Accepted / Approved * 100
    avg_time_to_acceptance_hours = Column(Numeric(10, 2), nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_decision_analytics_date_type', 'date', 'decision_type'),
        Index('idx_decision_analytics_tenant_date', 'tenant_id', 'date'),
    )


class DecisionLimit(Base):
    """
    Customer credit limits calculated by the decision engine.
    Tracks approved limits, utilization, and refresh cycles.
    """
    __tablename__ = "decision_limits"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Customer & Product
    customer_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)

    # Limit Details
    approved_limit = Column(Numeric(15, 2), nullable=False)
    utilized_amount = Column(Numeric(15, 2), default=0)
    available_limit = Column(Numeric(15, 2), nullable=False)

    # Calculation
    calculation_date = Column(DateTime, nullable=False)
    calculation_factors = Column(JSON, nullable=True)
    credit_score = Column(Integer, nullable=True)
    risk_category = Column(String(50), nullable=True)

    # Validity
    valid_from = Column(DateTime, nullable=False, index=True)
    valid_until = Column(DateTime, nullable=False, index=True)
    next_review_date = Column(DateTime, nullable=True)

    # Status
    status = Column(String(50), default="active", index=True)
    # active, expired, suspended, cancelled

    # Utilization Tracking
    last_utilized_at = Column(DateTime, nullable=True)
    utilization_count = Column(Integer, default=0)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=False, index=True)

    # Audit Trail
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Indexes
    __table_args__ = (
        Index('idx_decision_limits_customer_product', 'customer_id', 'product_id', 'status'),
        Index('idx_decision_limits_validity', 'valid_from', 'valid_until'),
    )

