"""
Risk Management Models
Phase 11: Risk Management
"""
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Date, Text, 
    DECIMAL, BigInteger, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class RiskParameter(Base):
    """Risk management parameters and thresholds"""
    __tablename__ = "gold_risk_parameters"

    parameter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parameter_code = Column(String(50), nullable=False, unique=True, index=True)
    parameter_name = Column(String(200), nullable=False)
    risk_category = Column(String(50), nullable=False, index=True)
    parameter_type = Column(String(50), nullable=False)
    parameter_value = Column(DECIMAL(20, 4), nullable=False)
    unit = Column(String(20))
    min_value = Column(DECIMAL(20, 4))
    max_value = Column(DECIMAL(20, 4))
    warning_threshold = Column(DECIMAL(20, 4))
    critical_threshold = Column(DECIMAL(20, 4))
    description = Column(Text)
    calculation_method = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, index=True)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class CreditRiskAssessment(Base):
    """Credit risk assessments for loans"""
    __tablename__ = "gold_credit_risk_assessments"

    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_number = Column(String(50), nullable=False, unique=True, index=True)
    loan_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assessment_date = Column(Date, nullable=False, index=True)
    assessment_type = Column(String(50), nullable=False)
    
    # Credit Scores
    credit_score = Column(Integer)
    pd_score = Column(DECIMAL(10, 4))
    lgd_score = Column(DECIMAL(10, 4))
    ead_amount = Column(DECIMAL(20, 2))
    
    # Risk Ratings
    internal_rating = Column(String(20))
    external_rating = Column(String(20))
    risk_grade = Column(String(20))
    
    # Financial Ratios
    dscr = Column(DECIMAL(10, 4))
    ltv_ratio = Column(DECIMAL(10, 4))
    debt_to_income = Column(DECIMAL(10, 4))
    
    # Risk Factors
    collateral_quality_score = Column(DECIMAL(10, 2))
    repayment_history_score = Column(DECIMAL(10, 2))
    business_risk_score = Column(DECIMAL(10, 2))
    market_risk_score = Column(DECIMAL(10, 2))
    
    # Assessment Results
    overall_risk_score = Column(DECIMAL(10, 2), nullable=False)
    risk_category = Column(String(20), nullable=False, index=True)
    
    # Provisions
    provision_amount = Column(DECIMAL(20, 2))
    provision_percentage = Column(DECIMAL(10, 4))
    
    # Status
    assessment_status = Column(String(20), nullable=False, default='draft', index=True)
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Metadata
    assessment_notes = Column(Text)
    risk_factors = Column(JSONB)
    mitigating_factors = Column(JSONB)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class OperationalRiskEvent(Base):
    """Operational risk events and incidents"""
    __tablename__ = "gold_operational_risk_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_number = Column(String(50), nullable=False, unique=True, index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_time = Column(DateTime(timezone=True), nullable=False)
    
    # Event Classification
    event_category = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    event_severity = Column(String(20), nullable=False, index=True)
    
    # Event Details
    event_title = Column(String(500), nullable=False)
    event_description = Column(Text, nullable=False)
    root_cause = Column(Text)
    
    # Location
    branch_id = Column(UUID(as_uuid=True), index=True)
    department = Column(String(100))
    process_name = Column(String(200))
    
    # Impact Assessment
    financial_impact = Column(DECIMAL(20, 2))
    reputational_impact = Column(String(20))
    customer_impact = Column(Integer)
    operational_impact = Column(Text)
    
    # People Involved
    reported_by = Column(UUID(as_uuid=True), nullable=False)
    assigned_to = Column(UUID(as_uuid=True))
    responsible_party = Column(UUID(as_uuid=True))
    
    # Status & Resolution
    event_status = Column(String(20), nullable=False, default='reported', index=True)
    resolution_date = Column(Date)
    resolution_description = Column(Text)
    
    # Risk Controls
    control_failure = Column(Boolean, default=False)
    control_id = Column(UUID(as_uuid=True))
    
    # Regulatory Reporting
    requires_regulatory_reporting = Column(Boolean, default=False)
    reported_to_regulator = Column(Boolean, default=False)
    regulator_reference = Column(String(100))
    reporting_date = Column(Date)
    
    # Lessons Learned
    lessons_learned = Column(Text)
    corrective_actions = Column(JSONB)
    preventive_actions = Column(JSONB)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class MarketRiskExposure(Base):
    """Market risk exposures and VaR calculations"""
    __tablename__ = "gold_market_risk_exposures"

    exposure_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exposure_date = Column(Date, nullable=False, index=True)
    
    # Gold Price Risk
    gold_rate_per_gram = Column(DECIMAL(10, 2), nullable=False, index=True)
    total_gold_weight_kg = Column(DECIMAL(10, 3), nullable=False)
    total_gold_value = Column(DECIMAL(20, 2), nullable=False)
    
    # Portfolio Composition
    portfolio_loan_count = Column(Integer, nullable=False)
    portfolio_outstanding_amount = Column(DECIMAL(20, 2), nullable=False)
    average_ltv = Column(DECIMAL(10, 4))
    
    # Value at Risk (VaR)
    var_1day_95 = Column(DECIMAL(20, 2))
    var_1day_99 = Column(DECIMAL(20, 2))
    var_10day_95 = Column(DECIMAL(20, 2))
    var_10day_99 = Column(DECIMAL(20, 2))
    
    # Stress Testing
    stress_scenario_10pct_drop = Column(DECIMAL(20, 2))
    stress_scenario_20pct_drop = Column(DECIMAL(20, 2))
    stress_scenario_30pct_drop = Column(DECIMAL(20, 2))
    
    # Interest Rate Risk
    interest_rate_portfolio = Column(DECIMAL(10, 4))
    interest_rate_sensitivity = Column(DECIMAL(20, 2))
    duration_gap = Column(DECIMAL(10, 4))
    
    # Liquidity Risk
    liquidity_coverage_ratio = Column(DECIMAL(10, 4))
    cash_to_assets_ratio = Column(DECIMAL(10, 4))
    
    # Risk Metrics
    portfolio_volatility = Column(DECIMAL(10, 4))
    sharpe_ratio = Column(DECIMAL(10, 4))
    
    # Market Conditions
    market_sentiment = Column(String(20))
    gold_price_trend = Column(String(20))
    market_volatility = Column(String(20))
    
    # Hedging
    hedging_strategy = Column(String(100))
    hedged_exposure = Column(DECIMAL(20, 2))
    unhedged_exposure = Column(DECIMAL(20, 2))
    hedging_cost = Column(DECIMAL(20, 2))
    
    # Status
    calculation_method = Column(String(50))
    data_quality_score = Column(DECIMAL(10, 2))
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ConcentrationRiskLimit(Base):
    """Concentration risk limits and monitoring"""
    __tablename__ = "gold_concentration_risk_limits"

    limit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    limit_code = Column(String(50), nullable=False, unique=True, index=True)
    limit_name = Column(String(200), nullable=False)
    
    # Concentration Type
    concentration_type = Column(String(50), nullable=False, index=True)
    concentration_dimension = Column(String(100))
    
    # Limit Definition
    limit_value = Column(DECIMAL(20, 2), nullable=False)
    limit_unit = Column(String(20), nullable=False)
    limit_basis = Column(String(50))
    
    # Thresholds
    warning_threshold = Column(DECIMAL(20, 2))
    breach_threshold = Column(DECIMAL(20, 2))
    regulatory_limit = Column(DECIMAL(20, 2))
    
    # Current Exposure
    current_exposure = Column(DECIMAL(20, 2))
    utilization_percentage = Column(DECIMAL(10, 4))
    
    # Status
    limit_status = Column(String(20), default='within_limit', index=True)
    last_breach_date = Column(Date)
    breach_count = Column(Integer, default=0)
    
    # Monitoring
    monitoring_frequency = Column(String(20))
    last_monitored_at = Column(DateTime(timezone=True))
    next_review_date = Column(Date)
    
    # Actions
    breach_action = Column(Text)
    escalation_required = Column(Boolean, default=False)
    
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class RiskAlert(Base):
    """Risk alerts and notifications"""
    __tablename__ = "gold_risk_alerts"

    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_number = Column(String(50), nullable=False, unique=True, index=True)
    alert_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Alert Classification
    alert_category = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)
    alert_severity = Column(String(20), nullable=False, index=True)
    alert_priority = Column(String(20), nullable=False)
    
    # Alert Details
    alert_title = Column(String(500), nullable=False)
    alert_message = Column(Text, nullable=False)
    alert_source = Column(String(100))
    
    # Entity Reference
    entity_type = Column(String(50), index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    reference_number = Column(String(100))
    
    # Threshold Breach
    threshold_parameter = Column(String(100))
    threshold_value = Column(DECIMAL(20, 4))
    actual_value = Column(DECIMAL(20, 4))
    deviation_percentage = Column(DECIMAL(10, 4))
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), index=True)
    assigned_at = Column(DateTime(timezone=True))
    department = Column(String(100))
    
    # Status & Resolution
    alert_status = Column(String(20), nullable=False, default='open', index=True)
    resolution_date = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    resolution_action = Column(String(100))
    
    # Escalation
    requires_escalation = Column(Boolean, default=False)
    escalated_to = Column(UUID(as_uuid=True))
    escalated_at = Column(DateTime(timezone=True))
    
    # Notifications
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSONB)
    notified_users = Column(JSONB)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    follow_up_notes = Column(Text)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index('idx_risk_alerts_entity', 'entity_type', 'entity_id'),
    )


class RiskMitigation(Base):
    """Risk mitigation actions and controls"""
    __tablename__ = "gold_risk_mitigations"

    mitigation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitigation_number = Column(String(50), nullable=False, unique=True, index=True)
    
    # Risk Reference
    risk_category = Column(String(50), nullable=False, index=True)
    risk_id = Column(UUID(as_uuid=True), index=True)
    risk_description = Column(Text)
    
    # Mitigation Details
    mitigation_type = Column(String(50), nullable=False)
    mitigation_title = Column(String(500), nullable=False)
    mitigation_description = Column(Text, nullable=False)
    
    # Implementation
    implementation_plan = Column(Text)
    implementation_cost = Column(DECIMAL(20, 2))
    implementation_timeline = Column(String(100))
    expected_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    
    # Effectiveness
    expected_risk_reduction = Column(DECIMAL(10, 4))
    actual_risk_reduction = Column(DECIMAL(10, 4))
    effectiveness_score = Column(DECIMAL(10, 2))
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    owner_department = Column(String(100))
    approver_id = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Status
    mitigation_status = Column(String(20), nullable=False, default='planned', index=True)
    status_update_date = Column(Date)
    
    # Monitoring
    monitoring_frequency = Column(String(20))
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    review_notes = Column(Text)
    
    # Dependencies
    dependencies = Column(JSONB)
    prerequisites = Column(Text)
    
    # Documentation
    supporting_documents = Column(JSONB)
    approval_documents = Column(JSONB)
    
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class RiskReport(Base):
    """Risk management reports"""
    __tablename__ = "gold_risk_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_number = Column(String(50), nullable=False, unique=True, index=True)
    report_date = Column(Date, nullable=False, index=True)
    
    # Report Classification
    report_type = Column(String(50), nullable=False, index=True)
    report_period = Column(String(50), nullable=False)
    period_start_date = Column(Date, nullable=False, index=True)
    period_end_date = Column(Date, nullable=False, index=True)
    
    # Report Content
    report_title = Column(String(500), nullable=False)
    executive_summary = Column(Text)
    
    # Risk Metrics
    credit_risk_metrics = Column(JSONB)
    operational_risk_metrics = Column(JSONB)
    market_risk_metrics = Column(JSONB)
    concentration_risk_metrics = Column(JSONB)
    
    # Key Findings
    key_findings = Column(JSONB)
    risk_trends = Column(JSONB)
    breaches = Column(JSONB)
    
    # Recommendations
    recommendations = Column(Text)
    action_items = Column(JSONB)
    
    # Approval
    prepared_by = Column(UUID(as_uuid=True), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Status
    report_status = Column(String(20), nullable=False, default='draft', index=True)
    
    # Distribution
    distribution_list = Column(JSONB)
    published_at = Column(DateTime(timezone=True))
    
    # File Storage
    report_file_path = Column(String(1000))
    report_file_size = Column(BigInteger)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index('idx_risk_reports_period', 'period_start_date', 'period_end_date'),
    )


class RiskDashboard(Base):
    """Risk dashboard configurations"""
    __tablename__ = "gold_risk_dashboards"

    dashboard_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_code = Column(String(50), nullable=False, unique=True, index=True)
    dashboard_name = Column(String(200), nullable=False)
    dashboard_type = Column(String(50), nullable=False, index=True)
    
    # Dashboard Configuration
    layout_config = Column(JSONB, nullable=False)
    widget_config = Column(JSONB, nullable=False)
    filter_config = Column(JSONB)
    
    # Data Refresh
    refresh_frequency = Column(String(20))
    last_refreshed_at = Column(DateTime(timezone=True))
    data_as_of_date = Column(Date)
    
    # Access Control
    visibility = Column(String(20), nullable=False, default='private')
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    shared_with = Column(JSONB)
    
    # Customization
    is_default = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    parent_dashboard_id = Column(UUID(as_uuid=True))
    
    # Usage
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime(timezone=True))
    
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ComplianceCheck(Base):
    """Compliance checks and audits"""
    __tablename__ = "gold_compliance_checks"

    check_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_number = Column(String(50), nullable=False, unique=True, index=True)
    check_date = Column(Date, nullable=False, index=True)
    
    # Compliance Area
    compliance_category = Column(String(50), nullable=False, index=True)
    compliance_area = Column(String(100), nullable=False, index=True)
    regulation_reference = Column(String(200))
    
    # Check Details
    check_title = Column(String(500), nullable=False)
    check_description = Column(Text)
    check_type = Column(String(50))
    
    # Scope
    check_scope = Column(String(100))
    entity_type = Column(String(50), index=True)
    entity_id = Column(UUID(as_uuid=True), index=True)
    
    # Compliance Requirements
    requirement_description = Column(Text)
    compliance_criteria = Column(Text)
    expected_value = Column(String(200))
    
    # Check Results
    actual_value = Column(String(200))
    check_result = Column(String(20), nullable=False, index=True)
    compliance_score = Column(DECIMAL(10, 2))
    
    # Risk Assessment
    risk_level = Column(String(20))
    potential_impact = Column(Text)
    
    # Non-Compliance Details
    deviation_details = Column(Text)
    root_cause = Column(Text)
    
    # Actions
    corrective_action_required = Column(Boolean, default=False)
    corrective_action_plan = Column(Text)
    action_owner_id = Column(UUID(as_uuid=True))
    target_completion_date = Column(Date)
    actual_completion_date = Column(Date)
    
    # Approval & Review
    reviewed_by = Column(UUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Status
    check_status = Column(String(20), nullable=False, default='pending', index=True)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    follow_up_notes = Column(Text)
    
    # Documentation
    evidence_documents = Column(JSONB)
    audit_trail = Column(JSONB)
    
    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_compliance_checks_entity', 'entity_type', 'entity_id'),
    )
