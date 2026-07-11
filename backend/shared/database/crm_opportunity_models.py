"""
CRM Opportunity Management Models
Database models for opportunity tracking, sales pipeline, stage management, and win/loss analysis
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date,
    Numeric, ForeignKey, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from .models import Base, TimestampMixin, TenantMixin


# ============================================================================
# ENUMS
# ============================================================================

class OpportunityStageEnum(str, Enum):
    """Opportunity pipeline stages"""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityType(str, Enum):
    """Type of opportunity"""
    NEW_BUSINESS = "new_business"
    EXISTING_CUSTOMER = "existing_customer"
    UPSELL = "upsell"
    CROSS_SELL = "cross_sell"
    RENEWAL = "renewal"


class OpportunityPriority(str, Enum):
    """Opportunity priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OpportunitySource(str, Enum):
    """Source of opportunity"""
    INBOUND_LEAD = "inbound_lead"
    OUTBOUND_PROSPECTING = "outbound_prospecting"
    REFERRAL = "referral"
    PARTNER = "partner"
    MARKETING_CAMPAIGN = "marketing_campaign"
    TRADE_SHOW = "trade_show"
    WEBSITE = "website"
    EXISTING_CUSTOMER = "existing_customer"
    OTHER = "other"


class LossReason(str, Enum):
    """Reasons for lost opportunities"""
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


class CompetitorPosition(str, Enum):
    """Competitor's position in the deal"""
    UNKNOWN = "unknown"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    INCUMBENT = "incumbent"


# ============================================================================
# OPPORTUNITY MODEL
# ============================================================================

class Opportunity(Base, TenantMixin, TimestampMixin):
    """
    Sales Opportunity Management
    Tracks sales pipeline from prospecting to close (won/lost)
    """
    __tablename__ = "crm_opportunities"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    opportunity_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    opportunity_type = Column(SQLEnum(OpportunityType), nullable=False, default=OpportunityType.NEW_BUSINESS)
    source = Column(SQLEnum(OpportunitySource), nullable=False)
    
    # Customer/Lead Reference
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("crm_leads.id"), nullable=True, index=True)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=True)
    contact_mobile = Column(String(20), nullable=False)
    company_name = Column(String(255), nullable=True)
    
    # Financial Details
    estimated_value = Column(Numeric(15, 2), nullable=False, index=True)
    expected_revenue = Column(Numeric(15, 2), nullable=True)
    actual_value = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="INR")
    
    # Pipeline Stage
    current_stage = Column(SQLEnum(OpportunityStageEnum), nullable=False, default=OpportunityStageEnum.PROSPECTING, index=True)
    stage_entered_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    previous_stage = Column(SQLEnum(OpportunityStageEnum), nullable=True)
    
    # Probability & Priority
    win_probability = Column(Integer, default=10, nullable=False)  # 0-100%
    priority = Column(SQLEnum(OpportunityPriority), default=OpportunityPriority.MEDIUM)
    
    # Timeline
    expected_close_date = Column(Date, nullable=False, index=True)
    actual_close_date = Column(Date, nullable=True)
    first_contact_date = Column(Date, nullable=True)
    
    # Assignment
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sales_team_ids = Column(JSON, nullable=True)  # List of user IDs involved
    
    # Status Tracking
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_won = Column(Boolean, default=False, index=True)
    is_lost = Column(Boolean, default=False, index=True)
    
    # Win Details
    won_date = Column(DateTime, nullable=True)
    won_value = Column(Numeric(15, 2), nullable=True)
    won_reason = Column(Text, nullable=True)
    
    # Loss Details
    lost_date = Column(DateTime, nullable=True)
    loss_reason = Column(SQLEnum(LossReason), nullable=True)
    loss_reason_details = Column(Text, nullable=True)
    competitor_name = Column(String(255), nullable=True)
    
    # Metrics
    days_in_pipeline = Column(Integer, default=0)
    days_in_current_stage = Column(Integer, default=0)
    stage_changes_count = Column(Integer, default=0)
    activities_count = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    
    # Additional Information
    next_step = Column(Text, nullable=True)
    pain_points = Column(JSON, nullable=True)  # List of customer pain points
    decision_makers = Column(JSON, nullable=True)  # List of key decision makers
    buying_process = Column(Text, nullable=True)
    budget_confirmed = Column(Boolean, default=False)
    authority_confirmed = Column(Boolean, default=False)
    need_confirmed = Column(Boolean, default=False)
    timeline_confirmed = Column(Boolean, default=False)
    
    # Tags & Metadata
    tags = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id], backref="opportunities")
    lead = relationship("Lead", foreign_keys=[lead_id], backref="opportunities")
    owner = relationship("User", foreign_keys=[owner_user_id], backref="owned_opportunities")
    
    stage_history = relationship("OpportunityStageHistory", back_populates="opportunity", cascade="all, delete-orphan")
    activities = relationship("OpportunityActivity", back_populates="opportunity", cascade="all, delete-orphan")
    products = relationship("OpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan")
    competitors = relationship("OpportunityCompetitor", back_populates="opportunity", cascade="all, delete-orphan")
    notes = relationship("OpportunityNote", back_populates="opportunity", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_opp_tenant_stage", "tenant_id", "current_stage"),
        Index("idx_opp_tenant_owner", "tenant_id", "owner_user_id"),
        Index("idx_opp_tenant_active", "tenant_id", "is_active"),
        Index("idx_opp_close_date", "expected_close_date", "current_stage"),
        Index("idx_opp_value", "estimated_value", "current_stage"),
    )
    
    def __repr__(self):
        return f"<Opportunity {self.opportunity_code} - {self.name} - {self.current_stage.value}>"


# ============================================================================
# OPPORTUNITY STAGE HISTORY MODEL
# ============================================================================

class OpportunityStageHistory(Base, TenantMixin, TimestampMixin):
    """
    Opportunity Stage Change History
    Tracks all stage transitions for pipeline analysis
    """
    __tablename__ = "crm_opportunity_stage_history"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Opportunity Reference
    opportunity_id = Column(Integer, ForeignKey("crm_opportunities.id"), nullable=False, index=True)
    
    # Stage Transition
    from_stage = Column(SQLEnum(OpportunityStageEnum), nullable=True)
    to_stage = Column(SQLEnum(OpportunityStageEnum), nullable=False, index=True)
    
    # Timing
    stage_entered_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    stage_exited_date = Column(DateTime, nullable=True)
    days_in_stage = Column(Integer, nullable=True)
    
    # Probability Change
    probability_before = Column(Integer, nullable=True)
    probability_after = Column(Integer, nullable=True)
    
    # Value Change
    value_before = Column(Numeric(15, 2), nullable=True)
    value_after = Column(Numeric(15, 2), nullable=True)
    
    # Context
    changed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    change_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Flags
    is_forward = Column(Boolean, default=True)  # True if moving forward, False if backward
    is_current = Column(Boolean, default=True, index=True)  # True for current stage
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="stage_history")
    changed_by = relationship("User", foreign_keys=[changed_by_user_id])
    
    __table_args__ = (
        Index("idx_stage_hist_opp", "opportunity_id", "stage_entered_date"),
        Index("idx_stage_hist_current", "opportunity_id", "is_current"),
    )
    
    def __repr__(self):
        return f"<StageHistory {self.id} - {self.from_stage} -> {self.to_stage}>"


# ============================================================================
# OPPORTUNITY ACTIVITY MODEL
# ============================================================================

class OpportunityActivity(Base, TenantMixin, TimestampMixin):
    """
    Opportunity Activity Log
    Tracks all interactions and touchpoints with opportunity
    """
    __tablename__ = "crm_opportunity_activities"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Opportunity Reference
    opportunity_id = Column(Integer, ForeignKey("crm_opportunities.id"), nullable=False, index=True)
    
    # Activity Details
    activity_type = Column(String(50), nullable=False, index=True)  # call, email, meeting, demo, proposal, etc.
    activity_title = Column(String(255), nullable=False)
    activity_description = Column(Text, nullable=True)
    
    # Timing
    activity_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Outcome
    outcome = Column(String(50), nullable=True)  # positive, neutral, negative, no_answer
    outcome_details = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True)
    
    # User Context
    performed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    attendees = Column(JSON, nullable=True)  # List of people involved
    
    # Change Tracking (for system activities)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    
    # Flags
    is_key_milestone = Column(Boolean, default=False)
    is_system_generated = Column(Boolean, default=False)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="activities")
    performed_by = relationship("User", foreign_keys=[performed_by_user_id])
    
    __table_args__ = (
        Index("idx_activity_opp_date", "opportunity_id", "activity_date"),
        Index("idx_activity_type_date", "activity_type", "activity_date"),
    )
    
    def __repr__(self):
        return f"<OpportunityActivity {self.id} - {self.activity_type} - {self.activity_title}>"


# ============================================================================
# OPPORTUNITY PRODUCT MODEL
# ============================================================================

class OpportunityProduct(Base, TenantMixin, TimestampMixin):
    """
    Products/Services in Opportunity
    Line items for opportunity value calculation
    """
    __tablename__ = "crm_opportunity_products"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Opportunity Reference
    opportunity_id = Column(Integer, ForeignKey("crm_opportunities.id"), nullable=False, index=True)
    
    # Product Details
    product_name = Column(String(255), nullable=False)
    product_code = Column(String(50), nullable=True)
    product_category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Pricing
    quantity = Column(Numeric(10, 2), default=1, nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    line_total = Column(Numeric(15, 2), nullable=False)
    
    # Loan Product Reference (for NBFC)
    loan_product_id = Column(Integer, ForeignKey("loan_products.id"), nullable=True)
    loan_amount = Column(Numeric(15, 2), nullable=True)
    loan_tenure_months = Column(Integer, nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    
    # Additional Info
    notes = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="products")
    loan_product = relationship("LoanProduct", foreign_keys=[loan_product_id])
    
    __table_args__ = (
        Index("idx_opp_product", "opportunity_id", "sort_order"),
    )
    
    def __repr__(self):
        return f"<OpportunityProduct {self.id} - {self.product_name}>"


# ============================================================================
# OPPORTUNITY COMPETITOR MODEL
# ============================================================================

class OpportunityCompetitor(Base, TenantMixin, TimestampMixin):
    """
    Competitor Analysis for Opportunity
    Track competitors in the sales process
    """
    __tablename__ = "crm_opportunity_competitors"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Opportunity Reference
    opportunity_id = Column(Integer, ForeignKey("crm_opportunities.id"), nullable=False, index=True)
    
    # Competitor Information
    competitor_name = Column(String(255), nullable=False, index=True)
    competitor_product = Column(String(255), nullable=True)
    
    # Competitive Position
    position = Column(SQLEnum(CompetitorPosition), default=CompetitorPosition.UNKNOWN)
    
    # Strengths & Weaknesses
    strengths = Column(JSON, nullable=True)  # List of competitor strengths
    weaknesses = Column(JSON, nullable=True)  # List of competitor weaknesses
    
    # Pricing
    competitor_price = Column(Numeric(15, 2), nullable=True)
    
    # Analysis
    win_strategy = Column(Text, nullable=True)  # How to win against this competitor
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    eliminated_date = Column(DateTime, nullable=True)
    elimination_reason = Column(Text, nullable=True)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="competitors")
    
    __table_args__ = (
        Index("idx_competitor_opp", "opportunity_id", "is_active"),
    )
    
    def __repr__(self):
        return f"<OpportunityCompetitor {self.id} - {self.competitor_name}>"


# ============================================================================
# OPPORTUNITY NOTE MODEL
# ============================================================================

class OpportunityNote(Base, TenantMixin, TimestampMixin):
    """
    Opportunity Notes
    Free-form notes and observations
    """
    __tablename__ = "crm_opportunity_notes"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Opportunity Reference
    opportunity_id = Column(Integer, ForeignKey("crm_opportunities.id"), nullable=False, index=True)
    
    # Note Content
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    
    # Classification
    note_type = Column(String(50), nullable=True)  # internal, customer_feedback, research, etc.
    is_pinned = Column(Boolean, default=False)
    
    # User Context
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="notes")
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    
    __table_args__ = (
        Index("idx_note_opp", "opportunity_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<OpportunityNote {self.id}>"
