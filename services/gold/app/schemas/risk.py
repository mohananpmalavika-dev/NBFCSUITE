"""
Risk Management Schemas
Phase 11: Risk Management
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# ============================================================================
# RISK PARAMETER SCHEMAS
# ============================================================================

class RiskParameterBase(BaseModel):
    parameter_code: str = Field(..., max_length=50)
    parameter_name: str = Field(..., max_length=200)
    risk_category: str = Field(..., max_length=50)
    parameter_type: str = Field(..., max_length=50)
    parameter_value: Decimal = Field(...)
    unit: Optional[str] = Field(None, max_length=20)
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    description: Optional[str] = None
    calculation_method: Optional[str] = None
    is_active: bool = Field(default=True)
    effective_from: date
    effective_to: Optional[date] = None


class RiskParameterCreate(RiskParameterBase):
    created_by: UUID


class RiskParameterUpdate(BaseModel):
    parameter_name: Optional[str] = Field(None, max_length=200)
    parameter_value: Optional[Decimal] = None
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    effective_to: Optional[date] = None
    updated_by: UUID


class RiskParameterResponse(RiskParameterBase):
    parameter_id: UUID
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CREDIT RISK ASSESSMENT SCHEMAS
# ============================================================================

class CreditRiskAssessmentBase(BaseModel):
    loan_id: UUID
    customer_id: UUID
    assessment_date: date
    assessment_type: str = Field(..., max_length=50)
    credit_score: Optional[int] = None
    pd_score: Optional[Decimal] = Field(None, description="Probability of Default")
    lgd_score: Optional[Decimal] = Field(None, description="Loss Given Default")
    ead_amount: Optional[Decimal] = Field(None, description="Exposure at Default")
    internal_rating: Optional[str] = Field(None, max_length=20)
    external_rating: Optional[str] = Field(None, max_length=20)
    risk_grade: Optional[str] = Field(None, max_length=20)
    dscr: Optional[Decimal] = Field(None, description="Debt Service Coverage Ratio")
    ltv_ratio: Optional[Decimal] = Field(None, description="Loan to Value Ratio")
    debt_to_income: Optional[Decimal] = None
    collateral_quality_score: Optional[Decimal] = None
    repayment_history_score: Optional[Decimal] = None
    business_risk_score: Optional[Decimal] = None
    market_risk_score: Optional[Decimal] = None
    overall_risk_score: Decimal
    risk_category: str = Field(..., max_length=20)
    provision_amount: Optional[Decimal] = None
    provision_percentage: Optional[Decimal] = None
    assessment_notes: Optional[str] = None
    risk_factors: Optional[Dict[str, Any]] = None
    mitigating_factors: Optional[Dict[str, Any]] = None


class CreditRiskAssessmentCreate(CreditRiskAssessmentBase):
    created_by: UUID


class CreditRiskAssessmentUpdate(BaseModel):
    assessment_type: Optional[str] = Field(None, max_length=50)
    credit_score: Optional[int] = None
    overall_risk_score: Optional[Decimal] = None
    risk_category: Optional[str] = Field(None, max_length=20)
    provision_amount: Optional[Decimal] = None
    assessment_notes: Optional[str] = None
    risk_factors: Optional[Dict[str, Any]] = None
    updated_by: UUID


class CreditRiskAssessmentApprove(BaseModel):
    approved_by: UUID


class CreditRiskAssessmentResponse(CreditRiskAssessmentBase):
    assessment_id: UUID
    assessment_number: str
    assessment_status: str
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# OPERATIONAL RISK EVENT SCHEMAS
# ============================================================================

class OperationalRiskEventBase(BaseModel):
    event_date: date
    event_time: datetime
    event_category: str = Field(..., max_length=50)
    event_type: str = Field(..., max_length=100)
    event_severity: str = Field(..., max_length=20)
    event_title: str = Field(..., max_length=500)
    event_description: str
    root_cause: Optional[str] = None
    branch_id: Optional[UUID] = None
    department: Optional[str] = Field(None, max_length=100)
    process_name: Optional[str] = Field(None, max_length=200)
    financial_impact: Optional[Decimal] = None
    reputational_impact: Optional[str] = Field(None, max_length=20)
    customer_impact: Optional[int] = None
    operational_impact: Optional[str] = None
    reported_by: UUID
    assigned_to: Optional[UUID] = None
    responsible_party: Optional[UUID] = None
    control_failure: bool = Field(default=False)
    control_id: Optional[UUID] = None
    requires_regulatory_reporting: bool = Field(default=False)
    lessons_learned: Optional[str] = None
    corrective_actions: Optional[Dict[str, Any]] = None
    preventive_actions: Optional[Dict[str, Any]] = None


class OperationalRiskEventCreate(OperationalRiskEventBase):
    created_by: UUID


class OperationalRiskEventUpdate(BaseModel):
    event_severity: Optional[str] = Field(None, max_length=20)
    assigned_to: Optional[UUID] = None
    event_status: Optional[str] = Field(None, max_length=20)
    resolution_date: Optional[date] = None
    resolution_description: Optional[str] = None
    reported_to_regulator: Optional[bool] = None
    regulator_reference: Optional[str] = Field(None, max_length=100)
    reporting_date: Optional[date] = None
    lessons_learned: Optional[str] = None
    corrective_actions: Optional[Dict[str, Any]] = None
    updated_by: UUID


class OperationalRiskEventResponse(OperationalRiskEventBase):
    event_id: UUID
    event_number: str
    event_status: str
    resolution_date: Optional[date]
    resolution_description: Optional[str]
    reported_to_regulator: bool
    regulator_reference: Optional[str]
    reporting_date: Optional[date]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# MARKET RISK EXPOSURE SCHEMAS
# ============================================================================

class MarketRiskExposureBase(BaseModel):
    exposure_date: date
    gold_rate_per_gram: Decimal
    total_gold_weight_kg: Decimal
    total_gold_value: Decimal
    portfolio_loan_count: int
    portfolio_outstanding_amount: Decimal
    average_ltv: Optional[Decimal] = None
    var_1day_95: Optional[Decimal] = None
    var_1day_99: Optional[Decimal] = None
    var_10day_95: Optional[Decimal] = None
    var_10day_99: Optional[Decimal] = None
    stress_scenario_10pct_drop: Optional[Decimal] = None
    stress_scenario_20pct_drop: Optional[Decimal] = None
    stress_scenario_30pct_drop: Optional[Decimal] = None
    interest_rate_portfolio: Optional[Decimal] = None
    interest_rate_sensitivity: Optional[Decimal] = None
    duration_gap: Optional[Decimal] = None
    liquidity_coverage_ratio: Optional[Decimal] = None
    cash_to_assets_ratio: Optional[Decimal] = None
    portfolio_volatility: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    market_sentiment: Optional[str] = Field(None, max_length=20)
    gold_price_trend: Optional[str] = Field(None, max_length=20)
    market_volatility: Optional[str] = Field(None, max_length=20)
    hedging_strategy: Optional[str] = Field(None, max_length=100)
    hedged_exposure: Optional[Decimal] = None
    unhedged_exposure: Optional[Decimal] = None
    hedging_cost: Optional[Decimal] = None
    calculation_method: Optional[str] = Field(None, max_length=50)
    data_quality_score: Optional[Decimal] = None


class MarketRiskExposureCreate(MarketRiskExposureBase):
    created_by: UUID


class MarketRiskExposureResponse(MarketRiskExposureBase):
    exposure_id: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# CONCENTRATION RISK LIMIT SCHEMAS
# ============================================================================

class ConcentrationRiskLimitBase(BaseModel):
    limit_code: str = Field(..., max_length=50)
    limit_name: str = Field(..., max_length=200)
    concentration_type: str = Field(..., max_length=50)
    concentration_dimension: Optional[str] = Field(None, max_length=100)
    limit_value: Decimal
    limit_unit: str = Field(..., max_length=20)
    limit_basis: Optional[str] = Field(None, max_length=50)
    warning_threshold: Optional[Decimal] = None
    breach_threshold: Optional[Decimal] = None
    regulatory_limit: Optional[Decimal] = None
    monitoring_frequency: Optional[str] = Field(None, max_length=20)
    breach_action: Optional[str] = None
    escalation_required: bool = Field(default=False)
    is_active: bool = Field(default=True)
    effective_from: date
    effective_to: Optional[date] = None


class ConcentrationRiskLimitCreate(ConcentrationRiskLimitBase):
    created_by: UUID


class ConcentrationRiskLimitUpdate(BaseModel):
    limit_name: Optional[str] = Field(None, max_length=200)
    limit_value: Optional[Decimal] = None
    warning_threshold: Optional[Decimal] = None
    breach_threshold: Optional[Decimal] = None
    current_exposure: Optional[Decimal] = None
    utilization_percentage: Optional[Decimal] = None
    limit_status: Optional[str] = Field(None, max_length=20)
    monitoring_frequency: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    updated_by: UUID


class ConcentrationRiskLimitResponse(ConcentrationRiskLimitBase):
    limit_id: UUID
    current_exposure: Optional[Decimal]
    utilization_percentage: Optional[Decimal]
    limit_status: str
    last_breach_date: Optional[date]
    breach_count: int
    last_monitored_at: Optional[datetime]
    next_review_date: Optional[date]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RISK ALERT SCHEMAS
# ============================================================================

class RiskAlertBase(BaseModel):
    alert_category: str = Field(..., max_length=50)
    alert_type: str = Field(..., max_length=100)
    alert_severity: str = Field(..., max_length=20)
    alert_priority: str = Field(..., max_length=20)
    alert_title: str = Field(..., max_length=500)
    alert_message: str
    alert_source: Optional[str] = Field(None, max_length=100)
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[UUID] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    threshold_parameter: Optional[str] = Field(None, max_length=100)
    threshold_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    deviation_percentage: Optional[Decimal] = None
    assigned_to: Optional[UUID] = None
    department: Optional[str] = Field(None, max_length=100)
    requires_escalation: bool = Field(default=False)
    follow_up_required: bool = Field(default=False)
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None


class RiskAlertCreate(RiskAlertBase):
    created_by: UUID


class RiskAlertUpdate(BaseModel):
    assigned_to: Optional[UUID] = None
    alert_status: Optional[str] = Field(None, max_length=20)
    resolution_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    resolution_action: Optional[str] = Field(None, max_length=100)
    escalated_to: Optional[UUID] = None


class RiskAlertResolve(BaseModel):
    resolution_notes: str
    resolution_action: str = Field(..., max_length=100)


class RiskAlertResponse(RiskAlertBase):
    alert_id: UUID
    alert_number: str
    alert_date: datetime
    alert_status: str
    resolution_date: Optional[datetime]
    resolution_notes: Optional[str]
    resolution_action: Optional[str]
    escalated_to: Optional[UUID]
    escalated_at: Optional[datetime]
    notification_sent: bool
    notification_channels: Optional[Dict[str, Any]]
    notified_users: Optional[Dict[str, Any]]
    assigned_at: Optional[datetime]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RISK MITIGATION SCHEMAS
# ============================================================================

class RiskMitigationBase(BaseModel):
    risk_category: str = Field(..., max_length=50)
    risk_id: Optional[UUID] = None
    risk_description: Optional[str] = None
    mitigation_type: str = Field(..., max_length=50)
    mitigation_title: str = Field(..., max_length=500)
    mitigation_description: str
    implementation_plan: Optional[str] = None
    implementation_cost: Optional[Decimal] = None
    implementation_timeline: Optional[str] = Field(None, max_length=100)
    expected_completion_date: Optional[date] = None
    expected_risk_reduction: Optional[Decimal] = None
    owner_id: UUID
    owner_department: Optional[str] = Field(None, max_length=100)
    monitoring_frequency: Optional[str] = Field(None, max_length=20)
    dependencies: Optional[Dict[str, Any]] = None
    prerequisites: Optional[str] = None


class RiskMitigationCreate(RiskMitigationBase):
    created_by: UUID


class RiskMitigationUpdate(BaseModel):
    mitigation_status: Optional[str] = Field(None, max_length=20)
    actual_completion_date: Optional[date] = None
    actual_risk_reduction: Optional[Decimal] = None
    effectiveness_score: Optional[Decimal] = None
    approver_id: Optional[UUID] = None
    last_review_date: Optional[date] = None
    next_review_date: Optional[date] = None
    review_notes: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: UUID


class RiskMitigationApprove(BaseModel):
    approver_id: UUID


class RiskMitigationResponse(RiskMitigationBase):
    mitigation_id: UUID
    mitigation_number: str
    actual_completion_date: Optional[date]
    actual_risk_reduction: Optional[Decimal]
    effectiveness_score: Optional[Decimal]
    approver_id: Optional[UUID]
    approved_at: Optional[datetime]
    mitigation_status: str
    status_update_date: Optional[date]
    last_review_date: Optional[date]
    next_review_date: Optional[date]
    review_notes: Optional[str]
    supporting_documents: Optional[Dict[str, Any]]
    approval_documents: Optional[Dict[str, Any]]
    is_active: bool
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RISK REPORT SCHEMAS
# ============================================================================

class RiskReportBase(BaseModel):
    report_date: date
    report_type: str = Field(..., max_length=50)
    report_period: str = Field(..., max_length=50)
    period_start_date: date
    period_end_date: date
    report_title: str = Field(..., max_length=500)
    executive_summary: Optional[str] = None
    credit_risk_metrics: Optional[Dict[str, Any]] = None
    operational_risk_metrics: Optional[Dict[str, Any]] = None
    market_risk_metrics: Optional[Dict[str, Any]] = None
    concentration_risk_metrics: Optional[Dict[str, Any]] = None
    key_findings: Optional[Dict[str, Any]] = None
    risk_trends: Optional[Dict[str, Any]] = None
    breaches: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None
    action_items: Optional[Dict[str, Any]] = None
    prepared_by: UUID
    distribution_list: Optional[Dict[str, Any]] = None


class RiskReportCreate(RiskReportBase):
    created_by: UUID


class RiskReportUpdate(BaseModel):
    executive_summary: Optional[str] = None
    recommendations: Optional[str] = None
    reviewed_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    report_status: Optional[str] = Field(None, max_length=20)


class RiskReportApprove(BaseModel):
    approved_by: UUID


class RiskReportPublish(BaseModel):
    distribution_list: Dict[str, Any]


class RiskReportResponse(RiskReportBase):
    report_id: UUID
    report_number: str
    reviewed_by: Optional[UUID]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    report_status: str
    published_at: Optional[datetime]
    report_file_path: Optional[str]
    report_file_size: Optional[int]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# RISK DASHBOARD SCHEMAS
# ============================================================================

class RiskDashboardBase(BaseModel):
    dashboard_code: str = Field(..., max_length=50)
    dashboard_name: str = Field(..., max_length=200)
    dashboard_type: str = Field(..., max_length=50)
    layout_config: Dict[str, Any]
    widget_config: Dict[str, Any]
    filter_config: Optional[Dict[str, Any]] = None
    refresh_frequency: Optional[str] = Field(None, max_length=20)
    visibility: str = Field(default='private', max_length=20)
    owner_id: UUID
    shared_with: Optional[Dict[str, Any]] = None
    is_default: bool = Field(default=False)
    is_template: bool = Field(default=False)
    parent_dashboard_id: Optional[UUID] = None
    is_active: bool = Field(default=True)


class RiskDashboardCreate(RiskDashboardBase):
    created_by: UUID


class RiskDashboardUpdate(BaseModel):
    dashboard_name: Optional[str] = Field(None, max_length=200)
    layout_config: Optional[Dict[str, Any]] = None
    widget_config: Optional[Dict[str, Any]] = None
    filter_config: Optional[Dict[str, Any]] = None
    refresh_frequency: Optional[str] = Field(None, max_length=20)
    visibility: Optional[str] = Field(None, max_length=20)
    shared_with: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    updated_by: UUID


class RiskDashboardResponse(RiskDashboardBase):
    dashboard_id: UUID
    last_refreshed_at: Optional[datetime]
    data_as_of_date: Optional[date]
    view_count: int
    last_viewed_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# COMPLIANCE CHECK SCHEMAS
# ============================================================================

class ComplianceCheckBase(BaseModel):
    check_date: date
    compliance_category: str = Field(..., max_length=50)
    compliance_area: str = Field(..., max_length=100)
    regulation_reference: Optional[str] = Field(None, max_length=200)
    check_title: str = Field(..., max_length=500)
    check_description: Optional[str] = None
    check_type: Optional[str] = Field(None, max_length=50)
    check_scope: Optional[str] = Field(None, max_length=100)
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[UUID] = None
    requirement_description: Optional[str] = None
    compliance_criteria: Optional[str] = None
    expected_value: Optional[str] = Field(None, max_length=200)
    actual_value: Optional[str] = Field(None, max_length=200)
    check_result: str = Field(..., max_length=20)
    compliance_score: Optional[Decimal] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    potential_impact: Optional[str] = None
    deviation_details: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action_required: bool = Field(default=False)
    corrective_action_plan: Optional[str] = None
    action_owner_id: Optional[UUID] = None
    target_completion_date: Optional[date] = None
    follow_up_required: bool = Field(default=False)
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None
    evidence_documents: Optional[Dict[str, Any]] = None


class ComplianceCheckCreate(ComplianceCheckBase):
    created_by: UUID


class ComplianceCheckUpdate(BaseModel):
    actual_value: Optional[str] = Field(None, max_length=200)
    check_result: Optional[str] = Field(None, max_length=20)
    compliance_score: Optional[Decimal] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    deviation_details: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action_plan: Optional[str] = None
    actual_completion_date: Optional[date] = None
    check_status: Optional[str] = Field(None, max_length=20)
    follow_up_notes: Optional[str] = None
    evidence_documents: Optional[Dict[str, Any]] = None
    updated_by: UUID


class ComplianceCheckReview(BaseModel):
    reviewed_by: UUID
    review_notes: Optional[str] = None


class ComplianceCheckApprove(BaseModel):
    approved_by: UUID


class ComplianceCheckResponse(ComplianceCheckBase):
    check_id: UUID
    check_number: str
    actual_completion_date: Optional[date]
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    check_status: str
    audit_trail: Optional[Dict[str, Any]]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# FILTER AND LIST SCHEMAS
# ============================================================================

class CreditRiskAssessmentFilter(BaseModel):
    loan_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    risk_category: Optional[str] = None
    assessment_status: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)


class OperationalRiskEventFilter(BaseModel):
    event_category: Optional[str] = None
    event_severity: Optional[str] = None
    event_status: Optional[str] = None
    branch_id: Optional[UUID] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)


class RiskAlertFilter(BaseModel):
    alert_category: Optional[str] = None
    alert_severity: Optional[str] = None
    alert_status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=500)


class ComplianceCheckFilter(BaseModel):
    compliance_category: Optional[str] = None
    compliance_area: Optional[str] = None
    check_result: Optional[str] = None
    check_status: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=500)


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class CreditRiskStatistics(BaseModel):
    total_assessments: int
    assessments_by_category: Dict[str, int]
    avg_risk_score: Decimal
    avg_ltv: Decimal
    avg_pd: Decimal
    total_provisions: Decimal
    npa_count: int
    npa_percentage: Decimal


class OperationalRiskStatistics(BaseModel):
    total_events: int
    events_by_category: Dict[str, int]
    events_by_severity: Dict[str, int]
    total_financial_impact: Decimal
    resolved_count: int
    regulatory_reporting_count: int


class MarketRiskStatistics(BaseModel):
    current_gold_rate: Decimal
    total_gold_value: Decimal
    portfolio_outstanding: Decimal
    current_var_1day_99: Decimal
    portfolio_volatility: Decimal
    gold_rate_change_pct: Decimal


class ConcentrationRiskStatistics(BaseModel):
    total_limits: int
    within_limit_count: int
    warning_count: int
    breached_count: int
    avg_utilization_pct: Decimal


class ComplianceStatistics(BaseModel):
    total_checks: int
    compliant_count: int
    non_compliant_count: int
    partial_count: int
    compliance_rate: Decimal
    critical_issues: int


class RiskDashboardData(BaseModel):
    credit_risk: CreditRiskStatistics
    operational_risk: OperationalRiskStatistics
    market_risk: MarketRiskStatistics
    concentration_risk: ConcentrationRiskStatistics
    compliance: ComplianceStatistics
    alert_summary: Dict[str, int]
    last_updated: datetime



# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class CreditRiskApprovalRequest(BaseModel):
    approved_by: UUID
    approval_notes: Optional[str] = None


class RiskAlertResolveRequest(BaseModel):
    resolved_by: UUID
    resolution_notes: Optional[str] = None


class RiskMitigationApprovalRequest(BaseModel):
    approved_by: UUID
    approval_notes: Optional[str] = None


class RiskReportApprovalRequest(BaseModel):
    approved_by: UUID
    approval_notes: Optional[str] = None


class RiskReportPublishRequest(BaseModel):
    published_by: UUID


class ComplianceCheckReviewRequest(BaseModel):
    reviewed_by: UUID
    review_notes: Optional[str] = None


class ComplianceCheckApprovalRequest(BaseModel):
    approved_by: UUID
    approval_notes: Optional[str] = None


class ConcentrationRiskMonitorResponse(BaseModel):
    limit_id: UUID
    limit_name: str
    concentration_type: str
    limit_amount: Decimal
    current_utilization: Decimal
    utilization_percentage: Decimal
    breach_status: str

    class Config:
        from_attributes = True
