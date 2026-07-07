"""
ALM (Asset Liability Management) Database Models
Maturity ladder, gap analysis, liquidity ratios, interest rate risk, quarterly returns
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Date, Text,
    ForeignKey, Enum, Index, CheckConstraint, JSON
)
from sqlalchemy.orm import relationship
import enum

from backend.shared.database.connection import Base


# Enums
class MaturityBucket(str, enum.Enum):
    """Maturity time buckets for ladder analysis"""
    UPTO_1_DAY = "upto_1_day"
    UPTO_7_DAYS = "upto_7_days"
    UPTO_14_DAYS = "upto_14_days"
    UPTO_1_MONTH = "upto_1_month"
    UPTO_2_MONTHS = "upto_2_months"
    UPTO_3_MONTHS = "upto_3_months"
    UPTO_6_MONTHS = "upto_6_months"
    UPTO_1_YEAR = "upto_1_year"
    UPTO_2_YEARS = "upto_2_years"
    UPTO_3_YEARS = "upto_3_years"
    UPTO_5_YEARS = "upto_5_years"
    ABOVE_5_YEARS = "above_5_years"


class GapType(str, enum.Enum):
    """Types of gaps in ALM analysis"""
    LIQUIDITY_GAP = "liquidity_gap"
    INTEREST_RATE_GAP = "interest_rate_gap"
    MATURITY_GAP = "maturity_gap"
    DURATION_GAP = "duration_gap"


class RiskLevel(str, enum.Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterestRateScenario(str, enum.Enum):
    """Interest rate scenarios for stress testing"""
    BASE = "base"
    PARALLEL_UP_100 = "parallel_up_100"
    PARALLEL_DOWN_100 = "parallel_down_100"
    PARALLEL_UP_200 = "parallel_up_200"
    PARALLEL_DOWN_200 = "parallel_down_200"
    STEEPENING = "steepening"
    FLATTENING = "flattening"


class ReportFrequency(str, enum.Enum):
    """Reporting frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


# Models
class MaturityLadder(Base):
    """
    Maturity Ladder Analysis
    Tracks assets and liabilities across maturity buckets
    """
    __tablename__ = "alm_maturity_ladder"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Report details
    report_date = Column(Date, nullable=False, index=True)
    bucket = Column(Enum(MaturityBucket), nullable=False, index=True)
    
    # Assets breakdown
    cash_and_bank_balance = Column(Numeric(18, 2), default=0.00)
    investments = Column(Numeric(18, 2), default=0.00)
    loans_and_advances = Column(Numeric(18, 2), default=0.00)
    fixed_assets = Column(Numeric(18, 2), default=0.00)
    other_assets = Column(Numeric(18, 2), default=0.00)
    total_assets = Column(Numeric(18, 2), nullable=False)
    
    # Liabilities breakdown
    deposits = Column(Numeric(18, 2), default=0.00)
    borrowings = Column(Numeric(18, 2), default=0.00)
    debt_securities = Column(Numeric(18, 2), default=0.00)
    other_liabilities = Column(Numeric(18, 2), default=0.00)
    total_liabilities = Column(Numeric(18, 2), nullable=False)
    
    # Gap analysis
    gap_amount = Column(Numeric(18, 2), nullable=False)  # Assets - Liabilities
    cumulative_gap = Column(Numeric(18, 2), nullable=False)
    gap_percentage = Column(Numeric(10, 4), nullable=True)
    
    # Interest sensitive classification
    interest_sensitive_assets = Column(Numeric(18, 2), default=0.00)
    interest_sensitive_liabilities = Column(Numeric(18, 2), default=0.00)
    interest_rate_gap = Column(Numeric(18, 2), nullable=True)
    
    # Duration
    avg_asset_duration = Column(Numeric(10, 4), nullable=True)
    avg_liability_duration = Column(Numeric(10, 4), nullable=True)
    duration_gap = Column(Numeric(10, 4), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_ml_tenant_date_bucket", "tenant_id", "report_date", "bucket", unique=True),
    )


class GapAnalysis(Base):
    """
    Comprehensive Gap Analysis
    Detailed analysis of liquidity, interest rate, and maturity gaps
    """
    __tablename__ = "alm_gap_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Report details
    report_date = Column(Date, nullable=False, index=True)
    analysis_type = Column(Enum(GapType), nullable=False)
    bucket = Column(Enum(MaturityBucket), nullable=False)
    
    # Inflows/Assets
    total_inflows = Column(Numeric(18, 2), nullable=False)
    contractual_inflows = Column(Numeric(18, 2), default=0.00)
    behavioral_inflows = Column(Numeric(18, 2), default=0.00)
    
    # Outflows/Liabilities
    total_outflows = Column(Numeric(18, 2), nullable=False)
    contractual_outflows = Column(Numeric(18, 2), default=0.00)
    behavioral_outflows = Column(Numeric(18, 2), default=0.00)
    
    # Gap metrics
    gap_amount = Column(Numeric(18, 2), nullable=False)
    cumulative_gap = Column(Numeric(18, 2), nullable=False)
    gap_ratio = Column(Numeric(10, 4), nullable=True)
    
    # Risk assessment
    risk_level = Column(Enum(RiskLevel), nullable=True)
    risk_score = Column(Numeric(10, 2), nullable=True)
    
    # Mitigation
    mitigation_required = Column(Boolean, default=False)
    mitigation_strategy = Column(Text, nullable=True)
    
    # Limits
    limit_breach = Column(Boolean, default=False)
    limit_value = Column(Numeric(18, 2), nullable=True)
    actual_value = Column(Numeric(18, 2), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_ga_tenant_date_type", "tenant_id", "report_date", "analysis_type"),
        Index("ix_ga_risk", "risk_level"),
        Index("ix_ga_breach", "limit_breach"),
    )


class LiquidityRatio(Base):
    """
    Liquidity Ratios Tracking
    Key liquidity metrics and regulatory ratios
    """
    __tablename__ = "alm_liquidity_ratios"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Report details
    report_date = Column(Date, nullable=False, index=True)
    
    # Basic liquidity ratios
    current_ratio = Column(Numeric(10, 4), nullable=True)
    quick_ratio = Column(Numeric(10, 4), nullable=True)
    cash_ratio = Column(Numeric(10, 4), nullable=True)
    
    # Regulatory ratios
    liquidity_coverage_ratio = Column(Numeric(10, 4), nullable=True)  # LCR
    net_stable_funding_ratio = Column(Numeric(10, 4), nullable=True)  # NSFR
    
    # NBFC specific ratios
    liquid_assets_to_total_assets = Column(Numeric(10, 4), nullable=True)
    liquid_assets_to_deposits = Column(Numeric(10, 4), nullable=True)
    liquid_assets_to_short_term_liabilities = Column(Numeric(10, 4), nullable=True)
    
    # Statutory liquidity ratio
    slr_ratio = Column(Numeric(10, 4), nullable=True)
    slr_requirement = Column(Numeric(10, 4), nullable=True)
    slr_compliance = Column(Boolean, default=True)
    
    # Advanced metrics
    loan_to_deposit_ratio = Column(Numeric(10, 4), nullable=True)
    deposit_concentration_ratio = Column(Numeric(10, 4), nullable=True)
    large_deposits_ratio = Column(Numeric(10, 4), nullable=True)
    
    # Funding stability
    stable_funding_ratio = Column(Numeric(10, 4), nullable=True)
    core_deposit_ratio = Column(Numeric(10, 4), nullable=True)
    volatile_liability_ratio = Column(Numeric(10, 4), nullable=True)
    
    # Risk indicators
    liquidity_stress_index = Column(Numeric(10, 4), nullable=True)
    funding_gap_ratio = Column(Numeric(10, 4), nullable=True)
    
    # Components for calculations
    high_quality_liquid_assets = Column(Numeric(18, 2), nullable=True)
    total_net_cash_outflows = Column(Numeric(18, 2), nullable=True)
    available_stable_funding = Column(Numeric(18, 2), nullable=True)
    required_stable_funding = Column(Numeric(18, 2), nullable=True)
    
    # Compliance status
    all_ratios_compliant = Column(Boolean, default=True)
    breached_ratios = Column(JSON, nullable=True)  # List of breached ratios
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_lr_tenant_date", "tenant_id", "report_date", unique=True),
        Index("ix_lr_compliance", "all_ratios_compliant"),
    )


class InterestRateRisk(Base):
    """
    Interest Rate Risk Analysis
    Tracks sensitivity to interest rate changes
    """
    __tablename__ = "alm_interest_rate_risk"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Report details
    report_date = Column(Date, nullable=False, index=True)
    scenario = Column(Enum(InterestRateScenario), nullable=False)
    
    # Current position
    net_interest_income_base = Column(Numeric(18, 2), nullable=False)
    market_value_equity_base = Column(Numeric(18, 2), nullable=False)
    
    # Interest rate shock impact
    interest_rate_change_bps = Column(Integer, nullable=False)  # Basis points
    net_interest_income_change = Column(Numeric(18, 2), nullable=True)
    net_interest_income_change_pct = Column(Numeric(10, 4), nullable=True)
    
    # Market value impact
    market_value_equity_change = Column(Numeric(18, 2), nullable=True)
    market_value_equity_change_pct = Column(Numeric(10, 4), nullable=True)
    
    # Duration analysis
    modified_duration_assets = Column(Numeric(10, 4), nullable=True)
    modified_duration_liabilities = Column(Numeric(10, 4), nullable=True)
    duration_gap = Column(Numeric(10, 4), nullable=True)
    
    # Repricing gap analysis
    repricing_gap_1_month = Column(Numeric(18, 2), nullable=True)
    repricing_gap_3_months = Column(Numeric(18, 2), nullable=True)
    repricing_gap_6_months = Column(Numeric(18, 2), nullable=True)
    repricing_gap_1_year = Column(Numeric(18, 2), nullable=True)
    cumulative_repricing_gap = Column(Numeric(18, 2), nullable=True)
    
    # Rate sensitive assets and liabilities
    rate_sensitive_assets = Column(Numeric(18, 2), nullable=True)
    rate_sensitive_liabilities = Column(Numeric(18, 2), nullable=True)
    rate_sensitive_gap = Column(Numeric(18, 2), nullable=True)
    
    # Risk metrics
    earnings_at_risk = Column(Numeric(18, 2), nullable=True)  # EaR
    value_at_risk = Column(Numeric(18, 2), nullable=True)  # VaR
    
    # Risk assessment
    risk_level = Column(Enum(RiskLevel), nullable=True)
    risk_score = Column(Numeric(10, 2), nullable=True)
    limit_breach = Column(Boolean, default=False)
    
    # Hedging
    hedging_required = Column(Boolean, default=False)
    hedging_strategy = Column(Text, nullable=True)
    hedge_effectiveness = Column(Numeric(10, 4), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_irr_tenant_date_scenario", "tenant_id", "report_date", "scenario"),
        Index("ix_irr_risk", "risk_level"),
        Index("ix_irr_breach", "limit_breach"),
    )


class QuarterlyReturn(Base):
    """
    ALM Quarterly Returns
    Regulatory returns and comprehensive ALM reporting
    """
    __tablename__ = "alm_quarterly_returns"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Return identification
    return_number = Column(String(50), nullable=False, unique=True, index=True)
    quarter = Column(Integer, nullable=False)  # 1, 2, 3, 4
    year = Column(Integer, nullable=False)
    report_date = Column(Date, nullable=False, index=True)
    
    # Structural Liquidity Statement (SLS)
    sls_data = Column(JSON, nullable=True)  # Complete SLS data
    
    # Interest Rate Sensitivity (IRS)
    irs_data = Column(JSON, nullable=True)  # Complete IRS data
    
    # Behavioral pattern analysis
    behavioral_data = Column(JSON, nullable=True)
    
    # Summary metrics
    total_assets = Column(Numeric(18, 2), nullable=False)
    total_liabilities = Column(Numeric(18, 2), nullable=False)
    net_worth = Column(Numeric(18, 2), nullable=False)
    
    # Key ratios
    liquidity_coverage_ratio = Column(Numeric(10, 4), nullable=True)
    cumulative_gap_1_year = Column(Numeric(18, 2), nullable=True)
    cumulative_gap_1_year_pct = Column(Numeric(10, 4), nullable=True)
    
    # Interest rate risk
    interest_rate_shock_impact_100bps = Column(Numeric(18, 2), nullable=True)
    interest_rate_shock_impact_200bps = Column(Numeric(18, 2), nullable=True)
    earnings_at_risk = Column(Numeric(18, 2), nullable=True)
    
    # Compliance status
    is_compliant = Column(Boolean, default=True)
    compliance_issues = Column(JSON, nullable=True)
    
    # Submission details
    prepared_by = Column(Integer, nullable=False)
    prepared_at = Column(DateTime, nullable=True)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Filing
    filed_to_regulator = Column(Boolean, default=False)
    filing_date = Column(Date, nullable=True)
    filing_reference = Column(String(100), nullable=True)
    
    # Attachments
    attachments = Column(JSON, nullable=True)  # Document URLs
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_qr_tenant_quarter", "tenant_id", "year", "quarter", unique=True),
        Index("ix_qr_filing", "filed_to_regulator", "filing_date"),
    )


class ALMLimits(Base):
    """
    ALM Limits and Thresholds
    Defines acceptable limits for various ALM metrics
    """
    __tablename__ = "alm_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Limit identification
    limit_name = Column(String(200), nullable=False)
    limit_type = Column(String(100), nullable=False)  # ratio, gap, duration, etc.
    
    # Time bucket (if applicable)
    maturity_bucket = Column(Enum(MaturityBucket), nullable=True)
    
    # Limit values
    minimum_value = Column(Numeric(18, 4), nullable=True)
    maximum_value = Column(Numeric(18, 4), nullable=True)
    target_value = Column(Numeric(18, 4), nullable=True)
    
    # Alert thresholds
    warning_threshold_lower = Column(Numeric(18, 4), nullable=True)
    warning_threshold_upper = Column(Numeric(18, 4), nullable=True)
    
    # Regulatory vs internal
    is_regulatory = Column(Boolean, default=False)
    regulatory_reference = Column(String(200), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    
    # Notes
    description = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("ix_alm_limits_tenant_active", "tenant_id", "is_active"),
        Index("ix_alm_limits_effective", "effective_from", "effective_to"),
    )


class ALMAlert(Base):
    """
    ALM Alerts and Notifications
    Tracks limit breaches and risk alerts
    """
    __tablename__ = "alm_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    
    # Alert details
    alert_date = Column(Date, nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # limit_breach, risk_alert, etc.
    severity = Column(Enum(RiskLevel), nullable=False)
    
    # Metric details
    metric_name = Column(String(200), nullable=False)
    metric_value = Column(Numeric(18, 4), nullable=False)
    limit_value = Column(Numeric(18, 4), nullable=True)
    deviation = Column(Numeric(18, 4), nullable=True)
    deviation_percentage = Column(Numeric(10, 4), nullable=True)
    
    # Related records
    maturity_ladder_id = Column(Integer, ForeignKey("alm_maturity_ladder.id"), nullable=True)
    gap_analysis_id = Column(Integer, ForeignKey("alm_gap_analysis.id"), nullable=True)
    liquidity_ratio_id = Column(Integer, ForeignKey("alm_liquidity_ratios.id"), nullable=True)
    interest_rate_risk_id = Column(Integer, ForeignKey("alm_interest_rate_risk.id"), nullable=True)
    
    # Alert message
    alert_message = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime, nullable=True)
    recipients = Column(JSON, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    maturity_ladder = relationship("MaturityLadder")
    gap_analysis = relationship("GapAnalysis")
    liquidity_ratio = relationship("LiquidityRatio")
    interest_rate_risk = relationship("InterestRateRisk")
    
    # Indexes
    __table_args__ = (
        Index("ix_alm_alerts_tenant_date", "tenant_id", "alert_date"),
        Index("ix_alm_alerts_severity", "severity"),
        Index("ix_alm_alerts_status", "is_resolved"),
    )
