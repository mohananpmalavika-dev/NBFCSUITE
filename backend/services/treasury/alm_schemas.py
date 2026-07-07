"""
ALM (Asset Liability Management) Schemas
Pydantic models for API request/response validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from backend.shared.database.alm_models import (
    MaturityBucket,
    GapType,
    RiskLevel,
    InterestRateScenario,
    ReportFrequency
)


# ============================================================================
# Maturity Ladder Schemas
# ============================================================================

class MaturityLadderBase(BaseModel):
    """Base schema for Maturity Ladder"""
    report_date: date
    bucket: MaturityBucket
    cash_and_bank_balance: Decimal = Decimal("0.00")
    investments: Decimal = Decimal("0.00")
    loans_and_advances: Decimal = Decimal("0.00")
    fixed_assets: Decimal = Decimal("0.00")
    other_assets: Decimal = Decimal("0.00")
    deposits: Decimal = Decimal("0.00")
    borrowings: Decimal = Decimal("0.00")
    debt_securities: Decimal = Decimal("0.00")
    other_liabilities: Decimal = Decimal("0.00")
    interest_sensitive_assets: Decimal = Decimal("0.00")
    interest_sensitive_liabilities: Decimal = Decimal("0.00")
    avg_asset_duration: Optional[Decimal] = None
    avg_liability_duration: Optional[Decimal] = None
    notes: Optional[str] = None


class MaturityLadderCreate(MaturityLadderBase):
    """Schema for creating maturity ladder entry"""
    pass


class MaturityLadderUpdate(BaseModel):
    """Schema for updating maturity ladder entry"""
    cash_and_bank_balance: Optional[Decimal] = None
    investments: Optional[Decimal] = None
    loans_and_advances: Optional[Decimal] = None
    fixed_assets: Optional[Decimal] = None
    other_assets: Optional[Decimal] = None
    deposits: Optional[Decimal] = None
    borrowings: Optional[Decimal] = None
    debt_securities: Optional[Decimal] = None
    other_liabilities: Optional[Decimal] = None
    interest_sensitive_assets: Optional[Decimal] = None
    interest_sensitive_liabilities: Optional[Decimal] = None
    avg_asset_duration: Optional[Decimal] = None
    avg_liability_duration: Optional[Decimal] = None
    notes: Optional[str] = None


class MaturityLadderResponse(MaturityLadderBase):
    """Schema for maturity ladder response"""
    id: int
    tenant_id: int
    total_assets: Decimal
    total_liabilities: Decimal
    gap_amount: Decimal
    cumulative_gap: Decimal
    gap_percentage: Optional[Decimal]
    interest_rate_gap: Optional[Decimal]
    duration_gap: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class MaturityLadderListResponse(BaseModel):
    """Schema for listing maturity ladder entries"""
    entries: List[MaturityLadderResponse]
    total: int
    report_date: date
    total_assets: Decimal
    total_liabilities: Decimal
    net_gap: Decimal


class MaturityLadderSummary(BaseModel):
    """Summary of maturity ladder analysis"""
    report_date: date
    total_assets: Decimal
    total_liabilities: Decimal
    overall_gap: Decimal
    short_term_gap: Decimal  # Up to 1 year
    medium_term_gap: Decimal  # 1-3 years
    long_term_gap: Decimal  # 3+ years
    risk_level: RiskLevel
    largest_gap_bucket: MaturityBucket
    largest_gap_amount: Decimal


# ============================================================================
# Gap Analysis Schemas
# ============================================================================

class GapAnalysisBase(BaseModel):
    """Base schema for Gap Analysis"""
    report_date: date
    analysis_type: GapType
    bucket: MaturityBucket
    contractual_inflows: Decimal = Decimal("0.00")
    behavioral_inflows: Decimal = Decimal("0.00")
    contractual_outflows: Decimal = Decimal("0.00")
    behavioral_outflows: Decimal = Decimal("0.00")
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[Decimal] = None
    mitigation_required: bool = False
    mitigation_strategy: Optional[str] = None
    limit_value: Optional[Decimal] = None
    notes: Optional[str] = None


class GapAnalysisCreate(GapAnalysisBase):
    """Schema for creating gap analysis entry"""
    pass


class GapAnalysisUpdate(BaseModel):
    """Schema for updating gap analysis entry"""
    contractual_inflows: Optional[Decimal] = None
    behavioral_inflows: Optional[Decimal] = None
    contractual_outflows: Optional[Decimal] = None
    behavioral_outflows: Optional[Decimal] = None
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[Decimal] = None
    mitigation_required: Optional[bool] = None
    mitigation_strategy: Optional[str] = None
    limit_value: Optional[Decimal] = None
    notes: Optional[str] = None


class GapAnalysisResponse(GapAnalysisBase):
    """Schema for gap analysis response"""
    id: int
    tenant_id: int
    total_inflows: Decimal
    total_outflows: Decimal
    gap_amount: Decimal
    cumulative_gap: Decimal
    gap_ratio: Optional[Decimal]
    limit_breach: bool
    actual_value: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class GapAnalysisListResponse(BaseModel):
    """Schema for listing gap analysis entries"""
    entries: List[GapAnalysisResponse]
    total: int
    report_date: date
    analysis_type: GapType


class GapAnalysisSummary(BaseModel):
    """Summary of gap analysis"""
    report_date: date
    analysis_type: GapType
    total_gap: Decimal
    critical_buckets: List[str]
    limit_breaches: int
    mitigation_required: bool
    overall_risk_level: RiskLevel


# ============================================================================
# Liquidity Ratio Schemas
# ============================================================================

class LiquidityRatioBase(BaseModel):
    """Base schema for Liquidity Ratios"""
    report_date: date
    current_ratio: Optional[Decimal] = None
    quick_ratio: Optional[Decimal] = None
    cash_ratio: Optional[Decimal] = None
    liquidity_coverage_ratio: Optional[Decimal] = None
    net_stable_funding_ratio: Optional[Decimal] = None
    liquid_assets_to_total_assets: Optional[Decimal] = None
    liquid_assets_to_deposits: Optional[Decimal] = None
    liquid_assets_to_short_term_liabilities: Optional[Decimal] = None
    slr_ratio: Optional[Decimal] = None
    slr_requirement: Optional[Decimal] = None
    loan_to_deposit_ratio: Optional[Decimal] = None
    deposit_concentration_ratio: Optional[Decimal] = None
    large_deposits_ratio: Optional[Decimal] = None
    stable_funding_ratio: Optional[Decimal] = None
    core_deposit_ratio: Optional[Decimal] = None
    volatile_liability_ratio: Optional[Decimal] = None
    liquidity_stress_index: Optional[Decimal] = None
    funding_gap_ratio: Optional[Decimal] = None
    high_quality_liquid_assets: Optional[Decimal] = None
    total_net_cash_outflows: Optional[Decimal] = None
    available_stable_funding: Optional[Decimal] = None
    required_stable_funding: Optional[Decimal] = None
    notes: Optional[str] = None


class LiquidityRatioCreate(LiquidityRatioBase):
    """Schema for creating liquidity ratio entry"""
    pass


class LiquidityRatioUpdate(BaseModel):
    """Schema for updating liquidity ratio entry"""
    current_ratio: Optional[Decimal] = None
    quick_ratio: Optional[Decimal] = None
    cash_ratio: Optional[Decimal] = None
    liquidity_coverage_ratio: Optional[Decimal] = None
    net_stable_funding_ratio: Optional[Decimal] = None
    liquid_assets_to_total_assets: Optional[Decimal] = None
    liquid_assets_to_deposits: Optional[Decimal] = None
    liquid_assets_to_short_term_liabilities: Optional[Decimal] = None
    slr_ratio: Optional[Decimal] = None
    slr_requirement: Optional[Decimal] = None
    loan_to_deposit_ratio: Optional[Decimal] = None
    deposit_concentration_ratio: Optional[Decimal] = None
    large_deposits_ratio: Optional[Decimal] = None
    stable_funding_ratio: Optional[Decimal] = None
    core_deposit_ratio: Optional[Decimal] = None
    volatile_liability_ratio: Optional[Decimal] = None
    liquidity_stress_index: Optional[Decimal] = None
    funding_gap_ratio: Optional[Decimal] = None
    high_quality_liquid_assets: Optional[Decimal] = None
    total_net_cash_outflows: Optional[Decimal] = None
    available_stable_funding: Optional[Decimal] = None
    required_stable_funding: Optional[Decimal] = None
    notes: Optional[str] = None


class LiquidityRatioResponse(LiquidityRatioBase):
    """Schema for liquidity ratio response"""
    id: int
    tenant_id: int
    slr_compliance: bool
    all_ratios_compliant: bool
    breached_ratios: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class LiquidityRatioListResponse(BaseModel):
    """Schema for listing liquidity ratios"""
    ratios: List[LiquidityRatioResponse]
    total: int
    date_range: Dict[str, date]


class LiquidityRatioTrend(BaseModel):
    """Liquidity ratio trends"""
    metric_name: str
    values: List[Dict[str, Any]]  # [{date, value}]
    average: Decimal
    trend: str  # improving, declining, stable


# ============================================================================
# Interest Rate Risk Schemas
# ============================================================================

class InterestRateRiskBase(BaseModel):
    """Base schema for Interest Rate Risk"""
    report_date: date
    scenario: InterestRateScenario
    net_interest_income_base: Decimal
    market_value_equity_base: Decimal
    interest_rate_change_bps: int
    net_interest_income_change: Optional[Decimal] = None
    net_interest_income_change_pct: Optional[Decimal] = None
    market_value_equity_change: Optional[Decimal] = None
    market_value_equity_change_pct: Optional[Decimal] = None
    modified_duration_assets: Optional[Decimal] = None
    modified_duration_liabilities: Optional[Decimal] = None
    duration_gap: Optional[Decimal] = None
    repricing_gap_1_month: Optional[Decimal] = None
    repricing_gap_3_months: Optional[Decimal] = None
    repricing_gap_6_months: Optional[Decimal] = None
    repricing_gap_1_year: Optional[Decimal] = None
    cumulative_repricing_gap: Optional[Decimal] = None
    rate_sensitive_assets: Optional[Decimal] = None
    rate_sensitive_liabilities: Optional[Decimal] = None
    rate_sensitive_gap: Optional[Decimal] = None
    earnings_at_risk: Optional[Decimal] = None
    value_at_risk: Optional[Decimal] = None
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[Decimal] = None
    hedging_required: bool = False
    hedging_strategy: Optional[str] = None
    hedge_effectiveness: Optional[Decimal] = None
    notes: Optional[str] = None


class InterestRateRiskCreate(InterestRateRiskBase):
    """Schema for creating interest rate risk entry"""
    pass


class InterestRateRiskUpdate(BaseModel):
    """Schema for updating interest rate risk entry"""
    net_interest_income_base: Optional[Decimal] = None
    market_value_equity_base: Optional[Decimal] = None
    net_interest_income_change: Optional[Decimal] = None
    net_interest_income_change_pct: Optional[Decimal] = None
    market_value_equity_change: Optional[Decimal] = None
    market_value_equity_change_pct: Optional[Decimal] = None
    modified_duration_assets: Optional[Decimal] = None
    modified_duration_liabilities: Optional[Decimal] = None
    duration_gap: Optional[Decimal] = None
    repricing_gap_1_month: Optional[Decimal] = None
    repricing_gap_3_months: Optional[Decimal] = None
    repricing_gap_6_months: Optional[Decimal] = None
    repricing_gap_1_year: Optional[Decimal] = None
    rate_sensitive_assets: Optional[Decimal] = None
    rate_sensitive_liabilities: Optional[Decimal] = None
    earnings_at_risk: Optional[Decimal] = None
    value_at_risk: Optional[Decimal] = None
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[Decimal] = None
    hedging_required: Optional[bool] = None
    hedging_strategy: Optional[str] = None
    hedge_effectiveness: Optional[Decimal] = None
    notes: Optional[str] = None


class InterestRateRiskResponse(InterestRateRiskBase):
    """Schema for interest rate risk response"""
    id: int
    tenant_id: int
    limit_breach: bool
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class InterestRateRiskListResponse(BaseModel):
    """Schema for listing interest rate risk entries"""
    entries: List[InterestRateRiskResponse]
    total: int
    report_date: date


class InterestRateRiskSummary(BaseModel):
    """Summary of interest rate risk"""
    report_date: date
    base_scenario: InterestRateRiskResponse
    worst_case_scenario: InterestRateRiskResponse
    overall_risk_level: RiskLevel
    hedging_recommended: bool


# ============================================================================
# Quarterly Return Schemas
# ============================================================================

class QuarterlyReturnBase(BaseModel):
    """Base schema for Quarterly Return"""
    quarter: int = Field(..., ge=1, le=4)
    year: int
    report_date: date
    sls_data: Optional[Dict[str, Any]] = None
    irs_data: Optional[Dict[str, Any]] = None
    behavioral_data: Optional[Dict[str, Any]] = None
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    liquidity_coverage_ratio: Optional[Decimal] = None
    cumulative_gap_1_year: Optional[Decimal] = None
    cumulative_gap_1_year_pct: Optional[Decimal] = None
    interest_rate_shock_impact_100bps: Optional[Decimal] = None
    interest_rate_shock_impact_200bps: Optional[Decimal] = None
    earnings_at_risk: Optional[Decimal] = None
    compliance_issues: Optional[Dict[str, Any]] = None
    attachments: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class QuarterlyReturnCreate(QuarterlyReturnBase):
    """Schema for creating quarterly return"""
    pass


class QuarterlyReturnUpdate(BaseModel):
    """Schema for updating quarterly return"""
    sls_data: Optional[Dict[str, Any]] = None
    irs_data: Optional[Dict[str, Any]] = None
    behavioral_data: Optional[Dict[str, Any]] = None
    total_assets: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    net_worth: Optional[Decimal] = None
    liquidity_coverage_ratio: Optional[Decimal] = None
    cumulative_gap_1_year: Optional[Decimal] = None
    cumulative_gap_1_year_pct: Optional[Decimal] = None
    interest_rate_shock_impact_100bps: Optional[Decimal] = None
    interest_rate_shock_impact_200bps: Optional[Decimal] = None
    earnings_at_risk: Optional[Decimal] = None
    is_compliant: Optional[bool] = None
    compliance_issues: Optional[Dict[str, Any]] = None
    attachments: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class QuarterlyReturnResponse(QuarterlyReturnBase):
    """Schema for quarterly return response"""
    id: int
    tenant_id: int
    return_number: str
    is_compliant: bool
    prepared_by: int
    prepared_at: Optional[datetime]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    filed_to_regulator: bool
    filing_date: Optional[date]
    filing_reference: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class QuarterlyReturnListResponse(BaseModel):
    """Schema for listing quarterly returns"""
    returns: List[QuarterlyReturnResponse]
    total: int


class QuarterlyReturnApproval(BaseModel):
    """Schema for approving quarterly return"""
    approval_notes: Optional[str] = None


class QuarterlyReturnFiling(BaseModel):
    """Schema for filing quarterly return"""
    filing_date: date
    filing_reference: Optional[str] = None


# ============================================================================
# ALM Limits Schemas
# ============================================================================

class ALMLimitBase(BaseModel):
    """Base schema for ALM Limits"""
    limit_name: str
    limit_type: str
    maturity_bucket: Optional[MaturityBucket] = None
    minimum_value: Optional[Decimal] = None
    maximum_value: Optional[Decimal] = None
    target_value: Optional[Decimal] = None
    warning_threshold_lower: Optional[Decimal] = None
    warning_threshold_upper: Optional[Decimal] = None
    is_regulatory: bool = False
    regulatory_reference: Optional[str] = None
    effective_from: date
    effective_to: Optional[date] = None
    description: Optional[str] = None


class ALMLimitCreate(ALMLimitBase):
    """Schema for creating ALM limit"""
    pass


class ALMLimitUpdate(BaseModel):
    """Schema for updating ALM limit"""
    limit_name: Optional[str] = None
    minimum_value: Optional[Decimal] = None
    maximum_value: Optional[Decimal] = None
    target_value: Optional[Decimal] = None
    warning_threshold_lower: Optional[Decimal] = None
    warning_threshold_upper: Optional[Decimal] = None
    is_regulatory: Optional[bool] = None
    regulatory_reference: Optional[str] = None
    is_active: Optional[bool] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None


class ALMLimitResponse(ALMLimitBase):
    """Schema for ALM limit response"""
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class ALMLimitListResponse(BaseModel):
    """Schema for listing ALM limits"""
    limits: List[ALMLimitResponse]
    total: int


# ============================================================================
# ALM Alert Schemas
# ============================================================================

class ALMAlertBase(BaseModel):
    """Base schema for ALM Alerts"""
    alert_date: date
    alert_type: str
    severity: RiskLevel
    metric_name: str
    metric_value: Decimal
    limit_value: Optional[Decimal] = None
    deviation: Optional[Decimal] = None
    deviation_percentage: Optional[Decimal] = None
    alert_message: str
    recommendation: Optional[str] = None


class ALMAlertCreate(ALMAlertBase):
    """Schema for creating ALM alert"""
    maturity_ladder_id: Optional[int] = None
    gap_analysis_id: Optional[int] = None
    liquidity_ratio_id: Optional[int] = None
    interest_rate_risk_id: Optional[int] = None


class ALMAlertResponse(ALMAlertBase):
    """Schema for ALM alert response"""
    id: int
    tenant_id: int
    maturity_ladder_id: Optional[int]
    gap_analysis_id: Optional[int]
    liquidity_ratio_id: Optional[int]
    interest_rate_risk_id: Optional[int]
    is_acknowledged: bool
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[datetime]
    is_resolved: bool
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    notification_sent: bool
    notification_sent_at: Optional[datetime]
    recipients: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ALMAlertListResponse(BaseModel):
    """Schema for listing ALM alerts"""
    alerts: List[ALMAlertResponse]
    total: int
    unresolved_count: int
    critical_count: int


class ALMAlertAcknowledge(BaseModel):
    """Schema for acknowledging alert"""
    notes: Optional[str] = None


class ALMAlertResolve(BaseModel):
    """Schema for resolving alert"""
    resolution_notes: str


# ============================================================================
# Dashboard Schemas
# ============================================================================

class ALMDashboard(BaseModel):
    """Comprehensive ALM dashboard data"""
    as_of_date: date
    
    # Maturity ladder summary
    maturity_summary: MaturityLadderSummary
    
    # Gap analysis summary
    liquidity_gap_summary: GapAnalysisSummary
    interest_rate_gap_summary: GapAnalysisSummary
    
    # Key liquidity ratios
    current_ratio: Optional[Decimal]
    lcr: Optional[Decimal]
    nsfr: Optional[Decimal]
    
    # Interest rate risk
    interest_rate_risk_summary: Dict[str, Any]
    
    # Alerts
    active_alerts: int
    critical_alerts: int
    
    # Compliance
    all_limits_compliant: bool
    breached_limits: List[str]


class ALMReport(BaseModel):
    """Comprehensive ALM report"""
    report_date: date
    report_type: str
    
    maturity_ladder: List[MaturityLadderResponse]
    gap_analysis: List[GapAnalysisResponse]
    liquidity_ratios: LiquidityRatioResponse
    interest_rate_risks: List[InterestRateRiskResponse]
    
    summary: Dict[str, Any]
    recommendations: List[str]
