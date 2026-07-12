"""
CRM Opportunity Management Models
Database models for opportunity tracking, sales pipeline, and win/loss analysis
"""

from sqlalchemy import Column, String, Numeric, Text, DateTime, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.shared.database.models import Base


class OpportunityStage(str, enum.Enum):
    """Opportunity stages in sales pipeline"""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class OpportunityType(str, enum.Enum):
    """Types of opportunities"""
    NEW_BUSINESS = "new_business"
    EXISTING_BUSINESS = "existing_business"
    RENEWAL = "renewal"
    UPSELL = "upsell"
    CROSS_SELL = "cross_sell"


class OpportunityPriority(str, enum.Enum):
    """Opportunity priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LossReason(str, enum.Enum):
    """Common reasons for losing opportunities"""
    PRICE = "price"
    COMPETITOR = "competitor"
    NO_BUDGET = "no_budget"
    TIMING = "timing"
    NO_DECISION = "no_decision"
    LOST_CONTACT = "lost_contact"
    PRODUCT_FIT = "product_fit"
    OTHER = "other"


class CRMOpportunity(Base):
    """
    CRM Opportunity Model
    Tracks sales opportunities through pipeline stages
    """
    __tablename__ = "crm_opportunities"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant & Organization
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Opportunity Identification
    opportunity_number = Column(String(50), unique=True, nullable=False, index=True)
    opportunity_name = Column(String(255), nullable=False)
    
    # Account & Contact Association
    account_id = Column(UUID(as_uuid=True), ForeignKey("crm_accounts.id"), nullable=False, index=True)
    primary_contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"), nullable=True)
    
    # Opportunity Details
    opportunity_type = Column(SQLEnum(OpportunityType), default=OpportunityType.NEW_BUSINESS)
    stage = Column(SQLEnum(OpportunityStage), default=OpportunityStage.PROSPECTING, nullable=False, index=True)
    priority = Column(SQLEnum(OpportunityPriority), default=OpportunityPriority.MEDIUM)
    
    # Financial Details
    estimated_value = Column(Numeric(15, 2), default=0)
    currency = Column(String(3), default="INR")
    probability = Column(Numeric(5, 2), default=0)  # Percentage (0-100)
    weighted_value = Column(Numeric(15, 2), default=0)  # estimated_value * probability/100
    
    # Timeline
    expected_close_date = Column(DateTime, nullable=True)
    actual_close_date = Column(DateTime, nullable=True)
    
    # Sales Information
    lead_source = Column(String(100), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Ownership & Assignment
    opportunity_owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    sales_team = Column(String(100), nullable=True)
    
    # Win/Loss Analysis
    is_won = Column(Boolean, default=False)
    is_lost = Column(Boolean, default=False)
    close_reason = Column(Text, nullable=True)
    loss_reason = Column(SQLEnum(LossReason), nullable=True)
    competitor_name = Column(String(255), nullable=True)
    
    # Descriptions & Notes
    description = Column(Text, nullable=True)
    next_step = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Stage History (JSONB for tracking stage transitions)
    stage_history = Column(JSONB, default=list)
    
    # Custom Fields
    custom_fields = Column(JSONB, default=dict)
    
    # Metadata
    tags = Column(JSONB, default=list)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    account = relationship("CRMAccount", back_populates="opportunities", foreign_keys=[account_id])
    primary_contact = relationship("CRMContact", foreign_keys=[primary_contact_id])
    products = relationship("CRMOpportunityProduct", back_populates="opportunity", cascade="all, delete-orphan")
    activities = relationship("CRMOpportunityActivity", back_populates="opportunity", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_opportunity_tenant_stage', 'tenant_id', 'stage'),
        Index('idx_opportunity_tenant_owner', 'tenant_id', 'opportunity_owner_id'),
        Index('idx_opportunity_tenant_account', 'tenant_id', 'account_id'),
        Index('idx_opportunity_close_date', 'expected_close_date'),
        Index('idx_opportunity_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<CRMOpportunity(id={self.id}, number={self.opportunity_number}, name={self.opportunity_name})>"


class CRMOpportunityProduct(Base):
    """
    CRM Opportunity Product Line Items
    Products/services associated with an opportunity
    """
    __tablename__ = "crm_opportunity_products"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant & Organization
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Opportunity Association
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("crm_opportunities.id"), nullable=False, index=True)
    
    # Product Details
    product_code = Column(String(50), nullable=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pricing
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(15, 2), default=0)
    discount_percentage = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_percentage = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    
    # Additional Information
    product_category = Column(String(100), nullable=True)
    line_notes = Column(Text, nullable=True)
    
    # Custom Fields
    custom_fields = Column(JSONB, default=dict)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    opportunity = relationship("CRMOpportunity", back_populates="products")
    
    def __repr__(self):
        return f"<CRMOpportunityProduct(id={self.id}, name={self.product_name})>"


class CRMOpportunityActivity(Base):
    """
    CRM Opportunity Activities
    Track activities and interactions related to opportunities
    """
    __tablename__ = "crm_opportunity_activities"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant & Organization
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Opportunity Association
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("crm_opportunities.id"), nullable=False, index=True)
    
    # Activity Details
    activity_type = Column(String(50), nullable=False)  # call, meeting, email, task, note
    activity_subject = Column(String(255), nullable=False)
    activity_description = Column(Text, nullable=True)
    
    # Timeline
    activity_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration_minutes = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(50), default="completed")  # planned, completed, cancelled
    
    # Participants
    participants = Column(JSONB, default=list)  # List of participant IDs
    
    # Outcome
    outcome = Column(Text, nullable=True)
    next_action = Column(Text, nullable=True)
    
    # Metadata
    custom_fields = Column(JSONB, default=dict)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    opportunity = relationship("CRMOpportunity", back_populates="activities")
    
    # Indexes
    __table_args__ = (
        Index('idx_activity_opportunity', 'opportunity_id', 'activity_date'),
        Index('idx_activity_type', 'activity_type'),
    )

    def __repr__(self):
        return f"<CRMOpportunityActivity(id={self.id}, type={self.activity_type})>"


class CRMPipelineStageConfig(Base):
    """
    CRM Pipeline Stage Configuration
    Customizable pipeline stages per tenant
    """
    __tablename__ = "crm_pipeline_stage_configs"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tenant & Organization
    tenant_id = Column(String(50), nullable=False, index=True)
    
    # Stage Configuration
    stage_name = Column(String(100), nullable=False)
    stage_key = Column(String(50), nullable=False)  # Used for API references
    display_order = Column(Integer, default=0)
    
    # Stage Properties
    default_probability = Column(Numeric(5, 2), default=0)
    is_active = Column(Boolean, default=True)
    is_closed_stage = Column(Boolean, default=False)  # Indicates if this is a terminal stage
    
    # Workflow
    required_fields = Column(JSONB, default=list)
    stage_duration_days = Column(Integer, nullable=True)  # Expected duration in this stage
    
    # Display
    color_code = Column(String(7), default="#6B7280")  # Hex color for UI
    icon = Column(String(50), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    custom_fields = Column(JSONB, default=dict)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_stage_config_tenant', 'tenant_id', 'is_active'),
        Index('idx_stage_config_order', 'tenant_id', 'display_order'),
    )

    def __repr__(self):
        return f"<CRMPipelineStageConfig(id={self.id}, name={self.stage_name})>"
