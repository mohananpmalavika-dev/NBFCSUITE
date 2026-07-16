"""
Credit Policy Integration Models
Risk-based pricing and credit decisioning models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

from backend.shared.database.connection import Base


# =====================================================================
# ENUMS
# =====================================================================

class DecisionOutcome(str, Enum):
    """Credit decision outcomes"""
    AUTO_APPROVED = "AUTO_APPROVED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    DECLINED = "DECLINED"
    COUNTER_OFFER = "COUNTER_OFFER"


class ReviewTriggerType(str, Enum):
    """Manual review trigger types"""
    CREDIT_SCORE = "CREDIT_SCORE"
    INCOME_VERIFICATION = "INCOME_VERIFICATION"
    EMPLOYMENT_TYPE = "EMPLOYMENT_TYPE"
    LOAN_AMOUNT = "LOAN_AMOUNT"
    DEBT_TO_INCOME = "DEBT_TO_INCOME"
    EXISTING_OBLIGATIONS = "EXISTING_OBLIGATIONS"
    ADVERSE_BUREAU = "ADVERSE_BUREAU"
    FRAUD_INDICATOR = "FRAUD_INDICATOR"
    POLICY_EXCEPTION = "POLICY_EXCEPTION"


class DeclineReason(str, Enum):
    """Decline reason codes"""
    LOW_CREDIT_SCORE = "LOW_CREDIT_SCORE"
    INSUFFICIENT_INCOME = "INSUFFICIENT_INCOME"
    HIGH_DTI_RATIO = "HIGH_DTI_RATIO"
    ADVERSE_CREDIT_HISTORY = "ADVERSE_CREDIT_HISTORY"
    EMPLOYMENT_UNSTABLE = "EMPLOYMENT_UNSTABLE"
    INCOMPLETE_DOCUMENTATION = "INCOMPLETE_DOCUMENTATION"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    FRAUD_DETECTED = "FRAUD_DETECTED"
    EXPOSURE_LIMIT_EXCEEDED = "EXPOSURE_LIMIT_EXCEEDED"
    CONCENTRATION_LIMIT = "CONCENTRATION_LIMIT"
    SECTORAL_CAP_EXCEEDED = "SECTORAL_CAP_EXCEEDED"


class PricingTier(str, Enum):
    """Risk pricing tiers"""
    PRIME = "PRIME"
    NEAR_PRIME = "NEAR_PRIME"
    SUB_PRIME = "SUB_PRIME"
    HIGH_RISK = "HIGH_RISK"


class ExposureType(str, Enum):
    """Exposure limit types"""
    CUSTOMER = "CUSTOMER"
    GROUP = "GROUP"
    INDUSTRY = "INDUSTRY"
    GEOGRAPHY = "GEOGRAPHY"
    PRODUCT = "PRODUCT"


class PolicyStatus(str, Enum):
    """Policy status"""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


# =====================================================================
# DATABASE MODELS
# =====================================================================

class CreditPolicy(Base):
    """Master credit policy definition"""
    __tablename__ = "credit_policies"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    product_id = Column(PGUUID(as_uuid=True), index=True)
    
    # Basic info
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    version = Column(String(20), default="1.0")
    
    # Status
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.DRAFT)
    is_active = Column(Boolean, default=False)
    
    # Effective dates
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    
    # Relationships
    risk_pricing = relationship("RiskBasedPricing", back_populates="policy", uselist=False, cascade="all, delete-orphan")
    score_rates = relationship("ScoreBasedRate", back_populates="policy", cascade="all, delete-orphan")
    ltv_ratios = relationship("LTVRatio", back_populates="policy", cascade="all, delete-orphan")
    exposure_limits = relationship("ExposureLimit", back_populates="policy", cascade="all, delete-orphan")
    concentration_limits = relationship("ConcentrationLimit", back_populates="policy", cascade="all, delete-orphan")
    sectoral_caps = relationship("SectoralCap", back_populates="policy", cascade="all, delete-orphan")
    auto_approval_criteria = relationship("AutoApprovalCriteria", back_populates="policy", uselist=False, cascade="all, delete-orphan")
    manual_review_triggers = relationship("ManualReviewTrigger", back_populates="policy", cascade="all, delete-orphan")
    decision_matrix = relationship("DecisionMatrix", back_populates="policy", cascade="all, delete-orphan")
    counter_offer_rules = relationship("CounterOfferRule", back_populates="policy", cascade="all, delete-orphan")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))
    updated_by = Column(PGUUID(as_uuid=True))
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True))
    updated_by = Column(PGUUID(as_uuid=True))


class RiskBasedPricing(Base):
    """Base risk-based pricing configuration"""
    __tablename__ = "risk_based_pricing"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Base pricing
    base_interest_rate = Column(Float, nullable=False)
    min_interest_rate = Column(Float, nullable=False)
    max_interest_rate = Column(Float, nullable=False)
    
    # Risk adjustments
    credit_score_weight = Column(Float, default=0.4)  # Weight in pricing calculation
    ltv_weight = Column(Float, default=0.3)
    dti_weight = Column(Float, default=0.2)
    other_factors_weight = Column(Float, default=0.1)
    
    # Fee adjustments
    processing_fee_range = Column(JSON)  # {"min": 1.0, "max": 3.0}
    risk_premium_range = Column(JSON)  # {"min": 0.0, "max": 2.0}
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="risk_pricing")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScoreBasedRate(Base):
    """Credit score-based interest rate tiers"""
    __tablename__ = "score_based_rates"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Score range
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    
    # Pricing tier
    pricing_tier = Column(SQLEnum(PricingTier), nullable=False)
    
    # Rates
    base_rate = Column(Float, nullable=False)
    rate_adjustment = Column(Float, default=0.0)  # Additional adjustment
    processing_fee_percent = Column(Float)
    risk_premium_percent = Column(Float)
    
    # Limits
    max_loan_amount = Column(Float)
    max_ltv_ratio = Column(Float)
    
    # Priority for overlapping ranges
    priority = Column(Integer, default=0)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="score_rates")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class LTVRatio(Base):
    """Loan-to-Value ratio limits"""
    __tablename__ = "ltv_ratios"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Collateral type
    collateral_type = Column(String(100), nullable=False)
    collateral_subtype = Column(String(100))
    
    # LTV limits
    max_ltv_ratio = Column(Float, nullable=False)  # As percentage
    preferred_ltv_ratio = Column(Float)  # For better pricing
    
    # Rate adjustment based on LTV
    ltv_rate_adjustments = Column(JSON)  # {"0-60": 0.0, "60-80": 0.5, "80-90": 1.0}
    
    # Additional requirements
    requires_insurance = Column(Boolean, default=False)
    requires_guarantor = Column(Boolean, default=False)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="ltv_ratios")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)


class ExposureLimit(Base):
    """Customer/Group/Industry exposure limits"""
    __tablename__ = "exposure_limits"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Exposure type
    exposure_type = Column(SQLEnum(ExposureType), nullable=False)
    exposure_name = Column(String(255), nullable=False)  # Industry name, group name, etc.
    
    # Limits
    max_exposure_amount = Column(Float, nullable=False)
    max_exposure_percentage = Column(Float)  # % of total portfolio
    
    # Single obligor limits
    max_single_obligor_amount = Column(Float)
    max_single_obligor_percentage = Column(Float)
    
    # Warning thresholds
    warning_threshold_percentage = Column(Float, default=80.0)  # Alert at 80% of limit
    
    # Current exposure (calculated)
    current_exposure = Column(Float, default=0.0)
    last_calculated_at = Column(DateTime)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="exposure_limits")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConcentrationLimit(Base):
    """Portfolio concentration limits"""
    __tablename__ = "concentration_limits"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Concentration parameter
    parameter_name = Column(String(100), nullable=False)  # e.g., "Top 10 Borrowers"
    parameter_type = Column(String(50), nullable=False)  # TOP_N, INDUSTRY, GEOGRAPHY, etc.
    
    # Limits
    max_concentration_percentage = Column(Float, nullable=False)
    target_concentration_percentage = Column(Float)
    
    # Calculation method
    calculation_criteria = Column(JSON)  # {"top_n": 10, "metric": "outstanding_amount"}
    
    # Monitoring
    current_concentration = Column(Float, default=0.0)
    breach_count = Column(Integer, default=0)
    last_breach_date = Column(DateTime)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="concentration_limits")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SectoralCap(Base):
    """Sector-wise lending caps (RBI compliance)"""
    __tablename__ = "sectoral_caps"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Sector information
    sector_code = Column(String(50), nullable=False)
    sector_name = Column(String(255), nullable=False)
    subsector = Column(String(255))
    
    # Caps
    max_sector_percentage = Column(Float, nullable=False)  # % of total AUM
    max_sector_amount = Column(Float)
    min_sector_percentage = Column(Float)  # Minimum diversification requirement
    
    # RBI priority sector classification
    is_priority_sector = Column(Boolean, default=False)
    priority_sector_category = Column(String(100))  # Agriculture, MSME, Housing, etc.
    
    # Current allocation
    current_allocation_percentage = Column(Float, default=0.0)
    current_allocation_amount = Column(Float, default=0.0)
    
    # Compliance
    is_compliant = Column(Boolean, default=True)
    compliance_notes = Column(Text)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="sectoral_caps")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AutoApprovalCriteria(Base):
    """Auto-approval criteria configuration"""
    __tablename__ = "auto_approval_criteria"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False, unique=True)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Credit score criteria
    min_credit_score = Column(Integer)
    credit_score_source = Column(String(50))  # CIBIL, EXPERIAN, EQUIFAX
    
    # Income criteria
    min_monthly_income = Column(Float)
    max_dti_ratio = Column(Float)  # Debt-to-Income ratio
    
    # Employment criteria
    allowed_employment_types = Column(JSON)  # ["SALARIED", "SELF_EMPLOYED_PROFESSIONAL"]
    min_employment_months = Column(Integer)
    
    # Loan criteria
    max_loan_amount = Column(Float)
    max_ltv_ratio = Column(Float)
    allowed_loan_purposes = Column(JSON)
    
    # Bureau checks
    max_active_loans = Column(Integer)
    max_dpd_days = Column(Integer)  # Days Past Due in last 12 months
    allow_restructured_accounts = Column(Boolean, default=False)
    
    # Residence criteria
    allowed_residence_types = Column(JSON)  # ["OWNED", "RENTED"]
    min_residence_months = Column(Integer)
    allowed_geographies = Column(JSON)  # List of allowed states/cities
    
    # Document requirements (relaxed for auto-approval)
    required_document_types = Column(JSON)
    
    # Additional validations
    require_bank_statement_analysis = Column(Boolean, default=True)
    min_bank_statement_months = Column(Integer, default=6)
    
    # Fraud checks
    require_dedupe_check = Column(Boolean, default=True)
    require_fraud_check = Column(Boolean, default=True)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="auto_approval_criteria")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ManualReviewTrigger(Base):
    """Manual review triggers"""
    __tablename__ = "manual_review_triggers"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Trigger information
    trigger_type = Column(SQLEnum(ReviewTriggerType), nullable=False)
    trigger_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Trigger condition
    condition_field = Column(String(100), nullable=False)
    condition_operator = Column(String(20), nullable=False)  # <, >, =, <=, >=, IN, NOT IN
    condition_value = Column(JSON, nullable=False)  # Can be number, string, list
    
    # Action
    review_level = Column(String(50))  # L1, L2, COMMITTEE
    priority = Column(String(20), default="NORMAL")  # LOW, NORMAL, HIGH, URGENT
    
    # Additional checks required
    additional_checks = Column(JSON)  # ["CREDIT_BUREAU", "FIELD_VERIFICATION"]
    additional_documents = Column(JSON)  # Additional documents to collect
    
    # Notes/Instructions for reviewer
    reviewer_instructions = Column(Text)
    
    # Enable/disable
    is_active = Column(Boolean, default=True)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="manual_review_triggers")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DecisionMatrix(Base):
    """Decision matrix rules"""
    __tablename__ = "decision_matrix"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Matrix entry
    rule_name = Column(String(255), nullable=False)
    rule_priority = Column(Integer, default=0)  # Higher priority rules evaluated first
    
    # Conditions (all must match)
    credit_score_range = Column(JSON)  # {"min": 700, "max": 850}
    loan_amount_range = Column(JSON)
    ltv_range = Column(JSON)
    dti_range = Column(JSON)
    employment_types = Column(JSON)
    income_range = Column(JSON)
    bureau_conditions = Column(JSON)  # {"max_dpd": 0, "max_enquiries": 3}
    custom_conditions = Column(JSON)  # Additional flexible conditions
    
    # Decision outcome
    decision_outcome = Column(SQLEnum(DecisionOutcome), nullable=False)
    
    # For DECLINED
    decline_reason = Column(SQLEnum(DeclineReason))
    decline_message = Column(Text)
    
    # For MANUAL_REVIEW
    review_level = Column(String(50))
    review_instructions = Column(Text)
    
    # For COUNTER_OFFER
    allow_counter_offer = Column(Boolean, default=False)
    
    # Enable/disable
    is_active = Column(Boolean, default=True)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="decision_matrix")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CounterOfferRule(Base):
    """Counter-offer generation rules"""
    __tablename__ = "counter_offer_rules"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(PGUUID(as_uuid=True), ForeignKey("credit_policies.id"), nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    
    # Rule information
    rule_name = Column(String(255), nullable=False)
    rule_priority = Column(Integer, default=0)
    
    # Trigger conditions
    trigger_conditions = Column(JSON, nullable=False)  # When to generate counter-offer
    
    # Offer adjustments
    loan_amount_adjustment = Column(JSON)  # {"type": "PERCENTAGE", "value": 80}
    interest_rate_adjustment = Column(JSON)  # {"type": "ADD", "value": 2.0}
    tenure_adjustment = Column(JSON)  # {"type": "REDUCE", "months": 12}
    
    # Additional requirements
    require_guarantor = Column(Boolean, default=False)
    require_collateral = Column(Boolean, default=False)
    additional_documents = Column(JSON)
    
    # Processing fee adjustment
    processing_fee_adjustment = Column(JSON)
    
    # Message to customer
    counter_offer_message = Column(Text)
    terms_and_conditions = Column(Text)
    
    # Valid until
    offer_validity_days = Column(Integer, default=7)
    
    # Enable/disable
    is_active = Column(Boolean, default=True)
    
    # Relationship
    policy = relationship("CreditPolicy", back_populates="counter_offer_rules")
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# =====================================================================
# PYDANTIC SCHEMAS
# =====================================================================

class CreditPolicyBase(BaseModel):
    """Base credit policy schema"""
    name: str
    code: str
    description: Optional[str] = None
    product_id: Optional[UUID] = None
    version: str = "1.0"
    status: PolicyStatus = PolicyStatus.DRAFT
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class CreditPolicyCreate(CreditPolicyBase):
    """Create credit policy schema"""
    pass


class CreditPolicyUpdate(BaseModel):
    """Update credit policy schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PolicyStatus] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class RiskBasedPricingSchema(BaseModel):
    """Risk-based pricing schema"""
    base_interest_rate: float
    min_interest_rate: float
    max_interest_rate: float
    credit_score_weight: float = 0.4
    ltv_weight: float = 0.3
    dti_weight: float = 0.2
    other_factors_weight: float = 0.1
    processing_fee_range: Dict[str, float]
    risk_premium_range: Dict[str, float]


class ScoreBasedRateSchema(BaseModel):
    """Score-based rate schema"""
    min_score: int
    max_score: int
    pricing_tier: PricingTier
    base_rate: float
    rate_adjustment: float = 0.0
    processing_fee_percent: Optional[float] = None
    risk_premium_percent: Optional[float] = None
    max_loan_amount: Optional[float] = None
    max_ltv_ratio: Optional[float] = None
    priority: int = 0



class LTVRatioSchema(BaseModel):
    """LTV ratio schema"""
    collateral_type: str
    collateral_subtype: Optional[str] = None
    max_ltv_ratio: float
    preferred_ltv_ratio: Optional[float] = None
    ltv_rate_adjustments: Optional[Dict[str, float]] = None
    requires_insurance: bool = False
    requires_guarantor: bool = False


class ExposureLimitSchema(BaseModel):
    """Exposure limit schema"""
    exposure_type: ExposureType
    exposure_name: str
    max_exposure_amount: float
    max_exposure_percentage: Optional[float] = None
    max_single_obligor_amount: Optional[float] = None
    max_single_obligor_percentage: Optional[float] = None
    warning_threshold_percentage: float = 80.0


class ConcentrationLimitSchema(BaseModel):
    """Concentration limit schema"""
    parameter_name: str
    parameter_type: str
    max_concentration_percentage: float
    target_concentration_percentage: Optional[float] = None
    calculation_criteria: Dict[str, Any]


class SectoralCapSchema(BaseModel):
    """Sectoral cap schema"""
    sector_code: str
    sector_name: str
    subsector: Optional[str] = None
    max_sector_percentage: float
    max_sector_amount: Optional[float] = None
    min_sector_percentage: Optional[float] = None
    is_priority_sector: bool = False
    priority_sector_category: Optional[str] = None


class AutoApprovalCriteriaSchema(BaseModel):
    """Auto-approval criteria schema"""
    min_credit_score: Optional[int] = None
    credit_score_source: Optional[str] = None
    min_monthly_income: Optional[float] = None
    max_dti_ratio: Optional[float] = None
    allowed_employment_types: Optional[List[str]] = None
    min_employment_months: Optional[int] = None
    max_loan_amount: Optional[float] = None
    max_ltv_ratio: Optional[float] = None
    allowed_loan_purposes: Optional[List[str]] = None
    max_active_loans: Optional[int] = None
    max_dpd_days: Optional[int] = None
    allow_restructured_accounts: bool = False
    allowed_residence_types: Optional[List[str]] = None
    min_residence_months: Optional[int] = None
    allowed_geographies: Optional[List[str]] = None
    required_document_types: Optional[List[str]] = None
    require_bank_statement_analysis: bool = True
    min_bank_statement_months: int = 6
    require_dedupe_check: bool = True
    require_fraud_check: bool = True



class ManualReviewTriggerSchema(BaseModel):
    """Manual review trigger schema"""
    trigger_type: ReviewTriggerType
    trigger_name: str
    description: Optional[str] = None
    condition_field: str
    condition_operator: str
    condition_value: Any
    review_level: Optional[str] = None
    priority: str = "NORMAL"
    additional_checks: Optional[List[str]] = None
    additional_documents: Optional[List[str]] = None
    reviewer_instructions: Optional[str] = None
    is_active: bool = True


class DecisionMatrixSchema(BaseModel):
    """Decision matrix schema"""
    rule_name: str
    rule_priority: int = 0
    credit_score_range: Optional[Dict[str, int]] = None
    loan_amount_range: Optional[Dict[str, float]] = None
    ltv_range: Optional[Dict[str, float]] = None
    dti_range: Optional[Dict[str, float]] = None
    employment_types: Optional[List[str]] = None
    income_range: Optional[Dict[str, float]] = None
    bureau_conditions: Optional[Dict[str, Any]] = None
    custom_conditions: Optional[Dict[str, Any]] = None
    decision_outcome: DecisionOutcome
    decline_reason: Optional[DeclineReason] = None
    decline_message: Optional[str] = None
    review_level: Optional[str] = None
    review_instructions: Optional[str] = None
    allow_counter_offer: bool = False
    is_active: bool = True


class CounterOfferRuleSchema(BaseModel):
    """Counter-offer rule schema"""
    rule_name: str
    rule_priority: int = 0
    trigger_conditions: Dict[str, Any]
    loan_amount_adjustment: Optional[Dict[str, Any]] = None
    interest_rate_adjustment: Optional[Dict[str, Any]] = None
    tenure_adjustment: Optional[Dict[str, Any]] = None
    require_guarantor: bool = False
    require_collateral: bool = False
    additional_documents: Optional[List[str]] = None
    processing_fee_adjustment: Optional[Dict[str, Any]] = None
    counter_offer_message: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    offer_validity_days: int = 7
    is_active: bool = True


class CreditPolicyResponse(CreditPolicyBase):
    """Credit policy response schema"""
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True



class PricingCalculationRequest(BaseModel):
    """Request for pricing calculation"""
    policy_id: UUID
    credit_score: int
    loan_amount: float
    collateral_value: Optional[float] = None
    monthly_income: float
    monthly_obligations: float
    employment_type: str
    other_factors: Optional[Dict[str, Any]] = None


class PricingCalculationResponse(BaseModel):
    """Response for pricing calculation"""
    base_rate: float
    risk_adjusted_rate: float
    final_interest_rate: float
    processing_fee_percent: float
    risk_premium_percent: float
    pricing_tier: PricingTier
    ltv_ratio: Optional[float] = None
    dti_ratio: float
    rate_breakdown: Dict[str, float]
    pricing_factors: Dict[str, Any]


class CreditDecisionRequest(BaseModel):
    """Request for credit decision"""
    policy_id: UUID
    application_id: UUID
    credit_score: int
    loan_amount: float
    monthly_income: float
    monthly_obligations: float
    employment_type: str
    employment_months: int
    collateral_value: Optional[float] = None
    residence_type: str
    residence_months: int
    geography: str
    bureau_data: Dict[str, Any]
    bank_statement_data: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None


class CreditDecisionResponse(BaseModel):
    """Response for credit decision"""
    decision_outcome: DecisionOutcome
    approved_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    decline_reason: Optional[DeclineReason] = None
    decline_message: Optional[str] = None
    review_level: Optional[str] = None
    review_instructions: Optional[str] = None
    counter_offer: Optional[Dict[str, Any]] = None
    decision_reasons: List[str]
    matched_rules: List[str]
    risk_assessment: Dict[str, Any]


class ExposureCheckRequest(BaseModel):
    """Request for exposure check"""
    policy_id: UUID
    customer_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    industry: Optional[str] = None
    geography: Optional[str] = None
    product_id: Optional[UUID] = None
    loan_amount: float


class ExposureCheckResponse(BaseModel):
    """Response for exposure check"""
    is_within_limits: bool
    exceeded_limits: List[Dict[str, Any]]
    current_exposure: Dict[str, float]
    available_limit: Dict[str, float]
    warnings: List[str]
