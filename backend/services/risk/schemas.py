"""
Risk Management Schemas
Pydantic models for credit policy, risk rating, exposure limits, and early warning systems
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional, List, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class CustomerSegment(str, Enum):
    RETAIL = "retail"
    MSME = "msme"
    CORPORATE = "corporate"


class LoanCategory(str, Enum):
    SECURED = "secured"
    UNSECURED = "unsecured"


class EmploymentType(str, Enum):
    SALARIED = "salaried"
    SELF_EMPLOYED = "self_employed"
    BUSINESS = "business"
    PROFESSIONAL = "professional"


class RiskGrade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C_PLUS = "C+"
    C = "C"
    D = "D"


class ExposureLimitType(str, Enum):
    CUSTOMER = "customer"
    GROUP = "group"
    INDUSTRY = "industry"
    GEOGRAPHY = "geography"
    PRODUCT = "product"
    COLLATERAL_TYPE = "collateral_type"
    DEALER = "dealer"


class BreachAction(str, Enum):
    ALERT = "alert"
    BLOCK = "block"
    REQUIRE_APPROVAL = "require_approval"


class SignalCategory(str, Enum):
    PAYMENT_BEHAVIOR = "payment_behavior"
    FINANCIAL_STRESS = "financial_stress"
    CREDIT_BUREAU = "credit_bureau"
    BANKING_BEHAVIOR = "banking_behavior"
    BUSINESS_PERFORMANCE = "business_performance"
    EXTERNAL_FACTORS = "external_factors"
    RELATIONSHIP_CHANGES = "relationship_changes"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"


class RatingType(str, Enum):
    CUSTOMER = "customer"
    APPLICATION = "application"
    ACCOUNT = "account"


# ============================================================================
# CREDIT POLICY SCHEMAS
# ============================================================================

class CreditPolicyBase(BaseModel):
    policy_code: str = Field(..., max_length=50)
    policy_name: str = Field(..., max_length=200)
    policy_version: str = Field(default="1.0", max_length=20)
    
    # Applicability
    product_types: List[str] = Field(default_factory=list)
    customer_segments: List[str] = Field(default_factory=list)
    loan_categories: List[str] = Field(default_factory=list)
    
    # Credit Score Requirements
    min_cibil_score: int = Field(..., ge=300, le=900)
    min_experian_score: Optional[int] = Field(None, ge=300, le=900)
    min_equifax_score: Optional[int] = Field(None, ge=300, le=900)
    min_crif_score: Optional[int] = Field(None, ge=300, le=900)
    bureau_vintage_months: int = Field(default=6, ge=0)
    
    # Income & DTI
    min_monthly_income: Optional[Decimal] = Field(None, ge=0)
    max_debt_to_income_ratio: Decimal = Field(..., ge=0, le=100)
    min_foir: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Loan Amount
    min_loan_amount: Decimal = Field(..., gt=0)
    max_loan_amount: Decimal = Field(..., gt=0)
    ltv_ratio: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Age
    min_age: int = Field(default=21, ge=18, le=100)
    max_age: int = Field(default=65, ge=18, le=100)
    max_age_at_maturity: int = Field(default=70, ge=18, le=100)
    
    # Employment
    allowed_employment_types: List[str] = Field(default_factory=list)
    min_employment_months: int = Field(default=12, ge=0)
    min_business_vintage_months: int = Field(default=24, ge=0)
    
    # Geographic
    allowed_states: Optional[List[str]] = None
    restricted_pincodes: Optional[List[str]] = None
    tier_restrictions: Optional[List[str]] = None
    
    # Negative Profiles
    max_active_loans: int = Field(default=3, ge=0)
    max_enquiries_last_3months: int = Field(default=5, ge=0)
    allow_defaults: bool = False
    allow_settlements: bool = False
    allow_write_offs: bool = False
    min_months_since_default: Optional[int] = Field(None, ge=0)
    
    # Co-applicant
    requires_co_applicant: bool = False
    requires_guarantor: bool = False
    co_applicant_min_income: Optional[Decimal] = Field(None, ge=0)
    
    # Documentation
    mandatory_document_types: Optional[List[int]] = None
    requires_bank_statement_months: int = Field(default=6, ge=0, le=24)
    requires_itr_years: int = Field(default=2, ge=0, le=10)
    
    # Approval Matrix
    approval_matrix: Optional[Dict[str, Any]] = None
    requires_credit_committee: bool = False
    credit_committee_threshold: Optional[Decimal] = Field(None, ge=0)
    
    # Status
    is_active: bool = True
    effective_from: date
    effective_to: Optional[date] = None
    
    # Description
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    deviation_policy: Optional[str] = None
    
    @field_validator('max_loan_amount')
    @classmethod
    def validate_loan_amounts(cls, v, info):
        if 'min_loan_amount' in info.data and v < info.data['min_loan_amount']:
            raise ValueError('max_loan_amount must be >= min_loan_amount')
        return v
    
    @field_validator('max_age')
    @classmethod
    def validate_ages(cls, v, info):
        if 'min_age' in info.data and v < info.data['min_age']:
            raise ValueError('max_age must be >= min_age')
        return v


class CreditPolicyCreate(CreditPolicyBase):
    pass


class CreditPolicyUpdate(BaseModel):
    policy_name: Optional[str] = Field(None, max_length=200)
    min_cibil_score: Optional[int] = Field(None, ge=300, le=900)
    max_debt_to_income_ratio: Optional[Decimal] = Field(None, ge=0, le=100)
    min_loan_amount: Optional[Decimal] = Field(None, gt=0)
    max_loan_amount: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None


class CreditPolicyResponse(CreditPolicyBase):
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreditPolicyListResponse(BaseModel):
    items: List[CreditPolicyResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# RISK PRICING SCHEMAS
# ============================================================================

class RiskPricingRuleBase(BaseModel):
    credit_policy_id: int
    rule_code: str = Field(..., max_length=50)
    rule_name: str = Field(..., max_length=200)
    rule_priority: int = Field(default=0, ge=0)
    
    # Conditions
    min_credit_score: Optional[int] = Field(None, ge=300, le=900)
    max_credit_score: Optional[int] = Field(None, ge=300, le=900)
    min_loan_amount: Optional[Decimal] = Field(None, ge=0)
    max_loan_amount: Optional[Decimal] = Field(None, ge=0)
    min_tenure_months: Optional[int] = Field(None, ge=1, le=360)
    max_tenure_months: Optional[int] = Field(None, ge=1, le=360)
    customer_segment: Optional[str] = None
    employment_type: Optional[str] = None
    loan_category: Optional[str] = None
    risk_ratings: Optional[List[str]] = None
    
    # Pricing
    base_interest_rate: Decimal = Field(..., ge=0, le=100)
    rate_adjustment: Decimal = Field(default=0.00, ge=-10, le=10)
    final_interest_rate: Decimal = Field(..., ge=0, le=100)
    
    # Fee Adjustments
    processing_fee_adjustment: Optional[Decimal] = Field(None, ge=-100, le=100)
    reduce_documentation_charges: bool = False
    waive_prepayment_charges: bool = False
    
    # Terms
    max_ltv_override: Optional[Decimal] = Field(None, ge=0, le=100)
    grace_period_days: Optional[int] = Field(None, ge=0, le=30)
    penal_interest_adjustment: Optional[Decimal] = Field(None, ge=-10, le=10)
    
    # Incentives
    cashback_percentage: Optional[Decimal] = Field(None, ge=0, le=10)
    loyalty_discount: Optional[Decimal] = Field(None, ge=0, le=10)
    
    # Status
    is_active: bool = True
    effective_from: date
    effective_to: Optional[date] = None


class RiskPricingRuleCreate(RiskPricingRuleBase):
    pass


class RiskPricingRuleUpdate(BaseModel):
    rule_name: Optional[str] = Field(None, max_length=200)
    rule_priority: Optional[int] = Field(None, ge=0)
    base_interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    rate_adjustment: Optional[Decimal] = Field(None, ge=-10, le=10)
    final_interest_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class RiskPricingRuleResponse(RiskPricingRuleBase):
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RiskPricingRuleListResponse(BaseModel):
    items: List[RiskPricingRuleResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PricingCalculationRequest(BaseModel):
    """Request to calculate pricing for a loan application"""
    customer_id: str
    loan_amount: Decimal = Field(..., gt=0)
    tenure_months: int = Field(..., ge=1, le=360)
    credit_score: int = Field(..., ge=300, le=900)
    employment_type: str
    loan_category: str
    customer_segment: Optional[str] = "retail"
    product_type: str


class PricingCalculationResponse(BaseModel):
    """Pricing calculation result"""
    base_rate: Decimal
    risk_adjustment: Decimal
    final_rate: Decimal
    processing_fee_adjustment: Optional[Decimal] = None
    applicable_rule_code: Optional[str] = None
    applicable_rule_name: Optional[str] = None
    cashback_percentage: Optional[Decimal] = None
    loyalty_discount: Optional[Decimal] = None
    waive_prepayment_charges: bool = False


# ============================================================================
# EXPOSURE LIMIT SCHEMAS
# ============================================================================

class ExposureLimitBase(BaseModel):
    limit_code: str = Field(..., max_length=50)
    limit_name: str = Field(..., max_length=200)
    limit_type: ExposureLimitType
    
    # Entity Reference (based on type)
    customer_id: Optional[str] = None
    industry_id: Optional[str] = None
    state_code: Optional[str] = Field(None, max_length=10)
    product_type: Optional[str] = Field(None, max_length=50)
    collateral_type: Optional[str] = Field(None, max_length=50)
    dealer_id: Optional[str] = None
    group_identifier: Optional[str] = Field(None, max_length=100)
    
    # Limit
    limit_amount: Decimal = Field(..., gt=0)
    
    # Thresholds
    warning_threshold_percentage: Decimal = Field(default=75.00, ge=0, le=100)
    critical_threshold_percentage: Decimal = Field(default=90.00, ge=0, le=100)
    breach_action: BreachAction = BreachAction.ALERT
    
    # Period
    limit_period: str = Field(default="annual")
    period_start_date: date
    period_end_date: date
    
    # Regulatory
    regulatory_limit: bool = False
    regulatory_reference: Optional[str] = Field(None, max_length=200)
    capital_charge_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Review
    review_frequency_days: int = Field(default=90, ge=1)
    
    # Status
    is_active: bool = True
    
    @field_validator('period_end_date')
    @classmethod
    def validate_period(cls, v, info):
        if 'period_start_date' in info.data and v <= info.data['period_start_date']:
            raise ValueError('period_end_date must be after period_start_date')
        return v


class ExposureLimitCreate(ExposureLimitBase):
    pass


class ExposureLimitUpdate(BaseModel):
    limit_name: Optional[str] = Field(None, max_length=200)
    limit_amount: Optional[Decimal] = Field(None, gt=0)
    warning_threshold_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    critical_threshold_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class ExposureLimitResponse(ExposureLimitBase):
    id: int
    tenant_id: str
    utilized_amount: Decimal
    available_amount: Decimal
    utilization_percentage: Decimal
    is_breached: bool
    breach_date: Optional[datetime] = None
    breach_remarks: Optional[str] = None
    last_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExposureLimitListResponse(BaseModel):
    items: List[ExposureLimitResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ExposureUtilizationRequest(BaseModel):
    """Request to utilize/release exposure"""
    amount: Decimal = Field(..., gt=0)
    transaction_reference: str = Field(..., max_length=100)
    loan_application_id: Optional[int] = None
    loan_account_id: Optional[int] = None
    remarks: Optional[str] = None


class ExposureTransactionResponse(BaseModel):
    id: int
    exposure_limit_id: int
    transaction_type: str
    transaction_reference: str
    amount: Decimal
    previous_utilized: Decimal
    new_utilized: Decimal
    transaction_date: datetime
    remarks: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# RISK RATING SCHEMAS
# ============================================================================

class RiskRatingBase(BaseModel):
    customer_id: str
    loan_application_id: Optional[int] = None
    loan_account_id: Optional[int] = None
    rating_type: RatingType
    rating_date: date
    rating_valid_until: Optional[date] = None
    
    # Rating
    risk_grade: RiskGrade
    risk_score: int = Field(..., ge=0, le=1000)
    pd_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    lgd_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    ead_amount: Optional[Decimal] = Field(None, ge=0)
    expected_loss: Optional[Decimal] = Field(None, ge=0)
    
    # Scorecard Components
    bureau_score: Optional[int] = Field(None, ge=0, le=1000)
    bureau_score_weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    income_stability_score: Optional[int] = Field(None, ge=0, le=1000)
    income_stability_weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    debt_burden_score: Optional[int] = Field(None, ge=0, le=1000)
    debt_burden_weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    repayment_history_score: Optional[int] = Field(None, ge=0, le=1000)
    repayment_history_weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    employment_stability_score: Optional[int] = Field(None, ge=0, le=1000)
    employment_stability_weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    banking_behavior_score: Optional[int] = Field(None, ge=0, le=1000)
    banking_behavior_weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    demographic_score: Optional[int] = Field(None, ge=0, le=1000)
    demographic_weightage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Risk Flags
    delinquency_flag: bool = False
    fraud_flag: bool = False
    litigation_flag: bool = False
    negative_area_flag: bool = False
    
    # Bureau Indicators
    dpd_max_last_12months: Optional[int] = Field(None, ge=0)
    dpd_max_last_24months: Optional[int] = Field(None, ge=0)
    active_loans_count: Optional[int] = Field(None, ge=0)
    enquiries_last_3months: Optional[int] = Field(None, ge=0)
    credit_utilization_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    # Model Info
    rating_model_code: Optional[str] = Field(None, max_length=50)
    rating_model_version: Optional[str] = Field(None, max_length=20)


class RiskRatingCreate(RiskRatingBase):
    pass


class RiskRatingOverrideRequest(BaseModel):
    new_risk_grade: RiskGrade
    new_risk_score: int = Field(..., ge=0, le=1000)
    override_reason: str = Field(..., min_length=10)


class RiskRatingResponse(RiskRatingBase):
    id: int
    tenant_id: str
    rating_override: bool
    override_reason: Optional[str] = None
    original_risk_grade: Optional[str] = None
    original_risk_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RiskRatingListResponse(BaseModel):
    items: List[RiskRatingResponse]
    total: int
    page: int
    page_size: int
    pages: int


class RiskRatingStats(BaseModel):
    """Risk rating portfolio statistics"""
    total_rated_customers: int
    rating_distribution: Dict[str, int]  # {"A+": 100, "A": 200, ...}
    average_score: float
    high_risk_count: int
    high_risk_percentage: float
    avg_pd_percentage: Optional[float] = None
    total_expected_loss: Optional[Decimal] = None


# ============================================================================
# EARLY WARNING SIGNAL SCHEMAS
# ============================================================================

class EarlyWarningSignalBase(BaseModel):
    signal_code: str = Field(..., max_length=50)
    signal_name: str = Field(..., max_length=200)
    signal_category: SignalCategory
    severity_level: SeverityLevel
    risk_weight: int = Field(default=1, ge=1, le=10)
    
    # Detection Logic
    detection_rule: Dict[str, Any]
    trigger_threshold: Optional[Decimal] = None
    monitoring_period_days: int = Field(default=30, ge=1)
    
    # Actions
    auto_escalate: bool = False
    escalation_level: Optional[str] = Field(None, max_length=50)
    notification_template: Optional[str] = Field(None, max_length=100)
    
    # Status
    is_active: bool = True
    
    # Description
    description: Optional[str] = None
    recommended_action: Optional[str] = None


class EarlyWarningSignalCreate(EarlyWarningSignalBase):
    pass


class EarlyWarningSignalUpdate(BaseModel):
    signal_name: Optional[str] = Field(None, max_length=200)
    severity_level: Optional[SeverityLevel] = None
    detection_rule: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class EarlyWarningSignalResponse(EarlyWarningSignalBase):
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EarlyWarningSignalListResponse(BaseModel):
    items: List[EarlyWarningSignalResponse]
    total: int
    page: int
    page_size: int
    pages: int


class EarlyWarningAlertResponse(BaseModel):
    id: int
    tenant_id: str
    signal_id: int
    alert_number: str
    alert_date: datetime
    
    # References
    customer_id: str
    loan_account_id: int
    customer_name: Optional[str] = None
    loan_account_number: Optional[str] = None
    
    # Alert Details
    signal_code: Optional[str] = None
    signal_name: Optional[str] = None
    signal_category: str
    severity_level: str
    
    # Values
    detected_value: Optional[Decimal] = None
    threshold_value: Optional[Decimal] = None
    variance_percentage: Optional[Decimal] = None
    
    # Status
    status: AlertStatus
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_remarks: Optional[str] = None
    
    # Action
    action_taken: Optional[str] = None
    action_date: Optional[datetime] = None
    
    # Escalation
    escalation_level: int
    escalated_at: Optional[datetime] = None
    
    # Recurrence
    is_recurring: bool
    occurrence_count: int
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EarlyWarningAlertListResponse(BaseModel):
    items: List[EarlyWarningAlertResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AlertActionRequest(BaseModel):
    """Request to take action on an alert"""
    action: str = Field(..., pattern="^(acknowledge|assign|resolve|escalate|mark_false_positive)$")
    remarks: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_remarks: Optional[str] = None


class EarlyWarningAlertStats(BaseModel):
    """Early warning alert statistics"""
    total_alerts: int
    open_alerts: int
    critical_alerts: int
    high_alerts: int
    resolved_today: int
    avg_resolution_time_hours: Optional[float] = None
    alerts_by_category: Dict[str, int]
    alerts_by_severity: Dict[str, int]


# ============================================================================
# POLICY EVALUATION SCHEMAS
# ============================================================================

class PolicyEvaluationRequest(BaseModel):
    """Request to evaluate a loan application against credit policies"""
    customer_id: str
    loan_amount: Decimal = Field(..., gt=0)
    tenure_months: int = Field(..., ge=1, le=360)
    product_type: str
    loan_category: str
    customer_segment: Optional[str] = "retail"
    credit_score: int = Field(..., ge=300, le=900)
    monthly_income: Decimal = Field(..., gt=0)
    existing_obligations: Decimal = Field(default=0, ge=0)
    age: int = Field(..., ge=18, le=100)
    employment_type: str


class PolicyEvaluationResponse(BaseModel):
    """Policy evaluation result"""
    eligible: bool
    applicable_policy_code: Optional[str] = None
    applicable_policy_name: Optional[str] = None
    risk_grade: Optional[str] = None
    suggested_interest_rate: Optional[Decimal] = None
    max_eligible_amount: Optional[Decimal] = None
    
    # Evaluation Details
    passed_checks: List[str]
    failed_checks: List[str]
    warnings: List[str]
    
    # DTI Calculation
    debt_to_income_ratio: Decimal
    foir: Optional[Decimal] = None
    
    # Recommendations
    recommendations: List[str]
