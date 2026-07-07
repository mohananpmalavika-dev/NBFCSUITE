"""
Risk Management & Credit Policy Models
Models for credit policies, risk ratings, exposure limits, pricing rules, and early warning signals
"""

from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, Date, 
    DateTime, ForeignKey, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class CreditPolicy(Base):
    """Credit Policy Engine Configuration"""
    __tablename__ = "credit_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Policy Identification
    policy_code = Column(String(50), unique=True, nullable=False, index=True)
    policy_name = Column(String(200), nullable=False)
    policy_version = Column(String(20), nullable=False, default="1.0")
    
    # Applicability
    product_types = Column(ARRAY(String))  # ['personal', 'business', 'gold']
    customer_segments = Column(ARRAY(String))  # ['retail', 'msme', 'corporate']
    loan_categories = Column(ARRAY(String))  # ['secured', 'unsecured']
    
    # Credit Score Requirements
    min_cibil_score = Column(Integer, nullable=False)
    min_experian_score = Column(Integer)
    min_equifax_score = Column(Integer)
    min_crif_score = Column(Integer)
    bureau_vintage_months = Column(Integer, default=6)  # Minimum credit history
    
    # Income & DTI Criteria
    min_monthly_income = Column(Numeric(15, 2))
    max_debt_to_income_ratio = Column(Numeric(5, 2), nullable=False)  # e.g., 50.00 for 50%
    min_foir = Column(Numeric(5, 2))  # Fixed Obligation to Income Ratio
    
    # Loan Amount Limits
    min_loan_amount = Column(Numeric(15, 2), nullable=False)
    max_loan_amount = Column(Numeric(15, 2), nullable=False)
    ltv_ratio = Column(Numeric(5, 2))  # Loan to Value for secured loans
    
    # Age Criteria
    min_age = Column(Integer, default=21)
    max_age = Column(Integer, default=65)
    max_age_at_maturity = Column(Integer, default=70)
    
    # Employment Criteria
    allowed_employment_types = Column(ARRAY(String))  # ['salaried', 'self_employed', 'business']
    min_employment_months = Column(Integer, default=12)
    min_business_vintage_months = Column(Integer, default=24)
    
    # Geographic Restrictions
    allowed_states = Column(ARRAY(String))
    restricted_pincodes = Column(ARRAY(String))
    tier_restrictions = Column(ARRAY(String))  # ['tier1', 'tier2', 'tier3']
    
    # Negative Profiles (Auto-Reject)
    max_active_loans = Column(Integer, default=3)
    max_enquiries_last_3months = Column(Integer, default=5)
    allow_defaults = Column(Boolean, default=False)
    allow_settlements = Column(Boolean, default=False)
    allow_write_offs = Column(Boolean, default=False)
    min_months_since_default = Column(Integer)
    
    # Co-applicant/Guarantor Rules
    requires_co_applicant = Column(Boolean, default=False)
    requires_guarantor = Column(Boolean, default=False)
    co_applicant_min_income = Column(Numeric(15, 2))
    
    # Documentation Requirements
    mandatory_document_types = Column(ARRAY(Integer))  # Document type IDs
    requires_bank_statement_months = Column(Integer, default=6)
    requires_itr_years = Column(Integer, default=2)
    
    # Approval Authority Matrix
    approval_matrix = Column(JSON)  # {"amount_slabs": [{"max": 100000, "approver_level": 1}]}
    requires_credit_committee = Column(Boolean, default=False)
    credit_committee_threshold = Column(Numeric(15, 2))
    
    # Policy Status
    is_active = Column(Boolean, default=True, index=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    # Description
    description = Column(Text)
    terms_and_conditions = Column(Text)
    deviation_policy = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    pricing_rules = relationship("RiskPricingRule", back_populates="credit_policy")


class RiskPricingRule(Base):
    """Risk-Based Pricing Configuration"""
    __tablename__ = "risk_pricing_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    credit_policy_id = Column(Integer, ForeignKey("credit_policies.id"), nullable=False, index=True)
    
    # Rule Identification
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(200), nullable=False)
    rule_priority = Column(Integer, default=0)  # Higher priority rules evaluated first
    
    # Risk Factors (Condition-based)
    min_credit_score = Column(Integer)
    max_credit_score = Column(Integer)
    min_loan_amount = Column(Numeric(15, 2))
    max_loan_amount = Column(Numeric(15, 2))
    min_tenure_months = Column(Integer)
    max_tenure_months = Column(Integer)
    customer_segment = Column(String(50))  # retail, msme, corporate
    employment_type = Column(String(50))  # salaried, self_employed
    loan_category = Column(String(50))  # secured, unsecured
    
    # Risk Rating Condition
    risk_ratings = Column(ARRAY(String))  # ['A+', 'A', 'B+', 'B', 'C']
    
    # Pricing Output
    base_interest_rate = Column(Numeric(5, 2), nullable=False)
    rate_adjustment = Column(Numeric(5, 2), default=0.00)  # +/- adjustment
    final_interest_rate = Column(Numeric(5, 2), nullable=False)
    
    # Fee Adjustments
    processing_fee_adjustment = Column(Numeric(5, 2))  # +/- percentage adjustment
    reduce_documentation_charges = Column(Boolean, default=False)
    waive_prepayment_charges = Column(Boolean, default=False)
    
    # Terms & Conditions
    max_ltv_override = Column(Numeric(5, 2))
    grace_period_days = Column(Integer)
    penal_interest_adjustment = Column(Numeric(5, 2))
    
    # Incentives
    cashback_percentage = Column(Numeric(5, 2))
    loyalty_discount = Column(Numeric(5, 2))
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    credit_policy = relationship("CreditPolicy", back_populates="pricing_rules")


class ExposureLimit(Base):
    """Exposure Limits & Concentration Risk Management"""
    __tablename__ = "exposure_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Limit Identification
    limit_code = Column(String(50), unique=True, nullable=False, index=True)
    limit_name = Column(String(200), nullable=False)
    limit_type = Column(String(50), nullable=False, index=True)
    # customer, group, industry, geography, product, collateral_type, dealer
    
    # Entity Reference (based on limit_type)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    industry_id = Column(UUID(as_uuid=True))
    state_code = Column(String(10))
    product_type = Column(String(50))
    collateral_type = Column(String(50))
    dealer_id = Column(UUID(as_uuid=True))
    group_identifier = Column(String(100))  # For group/family exposure
    
    # Limit Configuration
    limit_amount = Column(Numeric(15, 2), nullable=False)
    utilized_amount = Column(Numeric(15, 2), default=0.00)
    available_amount = Column(Numeric(15, 2), nullable=False)
    utilization_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Threshold Alerts
    warning_threshold_percentage = Column(Numeric(5, 2), default=75.00)
    critical_threshold_percentage = Column(Numeric(5, 2), default=90.00)
    breach_action = Column(String(50))  # alert, block, require_approval
    
    # Limit Period
    limit_period = Column(String(50), default="annual")  # annual, quarterly, rolling
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    # Regulatory Compliance
    regulatory_limit = Column(Boolean, default=False)
    regulatory_reference = Column(String(200))  # RBI guideline reference
    capital_charge_percentage = Column(Numeric(5, 2))
    
    # Review & Monitoring
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    review_frequency_days = Column(Integer, default=90)
    reviewer_id = Column(UUID(as_uuid=True))
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_breached = Column(Boolean, default=False, index=True)
    breach_date = Column(DateTime(timezone=True))
    breach_remarks = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    transactions = relationship("ExposureTransaction", back_populates="exposure_limit")


class ExposureTransaction(Base):
    """Exposure Limit Utilization Transactions"""
    __tablename__ = "exposure_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    exposure_limit_id = Column(Integer, ForeignKey("exposure_limits.id"), nullable=False, index=True)
    
    # Transaction Details
    transaction_type = Column(String(50), nullable=False)  # utilization, release, adjustment
    transaction_reference = Column(String(100))  # Loan account number or application number
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"))
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"))
    
    # Amount Movement
    amount = Column(Numeric(15, 2), nullable=False)
    previous_utilized = Column(Numeric(15, 2), nullable=False)
    new_utilized = Column(Numeric(15, 2), nullable=False)
    
    # Transaction Metadata
    transaction_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    remarks = Column(Text)
    processed_by = Column(UUID(as_uuid=True))
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    exposure_limit = relationship("ExposureLimit", back_populates="transactions")


class RiskRating(Base):
    """Customer/Loan Risk Rating & Scoring"""
    __tablename__ = "risk_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Entity Reference
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), index=True)
    
    # Rating Identification
    rating_type = Column(String(50), nullable=False)  # customer, application, account
    rating_date = Column(Date, nullable=False, index=True)
    rating_valid_until = Column(Date)
    
    # Risk Rating
    risk_grade = Column(String(10), nullable=False, index=True)  # A+, A, B+, B, C+, C, D
    risk_score = Column(Integer, nullable=False)  # 0-1000
    pd_percentage = Column(Numeric(5, 2))  # Probability of Default
    lgd_percentage = Column(Numeric(5, 2))  # Loss Given Default
    ead_amount = Column(Numeric(15, 2))  # Exposure at Default
    expected_loss = Column(Numeric(15, 2))  # EL = PD * LGD * EAD
    
    # Rating Factors (Scorecard Components)
    bureau_score = Column(Integer)
    bureau_score_weightage = Column(Numeric(5, 2))
    
    income_stability_score = Column(Integer)
    income_stability_weightage = Column(Numeric(5, 2))
    
    debt_burden_score = Column(Integer)
    debt_burden_weightage = Column(Numeric(5, 2))
    
    repayment_history_score = Column(Integer)
    repayment_history_weightage = Column(Numeric(5, 2))
    
    employment_stability_score = Column(Integer)
    employment_stability_weightage = Column(Numeric(5, 2))
    
    banking_behavior_score = Column(Integer)
    banking_behavior_weightage = Column(Numeric(5, 2))
    
    demographic_score = Column(Integer)
    demographic_weightage = Column(Numeric(5, 2))
    
    # Additional Risk Indicators
    delinquency_flag = Column(Boolean, default=False)
    fraud_flag = Column(Boolean, default=False)
    litigation_flag = Column(Boolean, default=False)
    negative_area_flag = Column(Boolean, default=False)
    
    # Credit Bureau Indicators
    dpd_max_last_12months = Column(Integer)
    dpd_max_last_24months = Column(Integer)
    active_loans_count = Column(Integer)
    enquiries_last_3months = Column(Integer)
    credit_utilization_percentage = Column(Numeric(5, 2))
    
    # Behavioral Indicators
    avg_monthly_balance = Column(Numeric(15, 2))
    banking_relationship_months = Column(Integer)
    cheque_bounce_count_12months = Column(Integer)
    digital_payment_activity_score = Column(Integer)
    
    # Override Information
    rating_override = Column(Boolean, default=False)
    override_reason = Column(Text)
    override_approved_by = Column(UUID(as_uuid=True))
    override_date = Column(DateTime(timezone=True))
    original_risk_grade = Column(String(10))
    original_risk_score = Column(Integer)
    
    # Model Information
    rating_model_code = Column(String(50))
    rating_model_version = Column(String(20))
    
    # Review Status
    review_required = Column(Boolean, default=False)
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)


class EarlyWarningSignal(Base):
    """Early Warning Signals (EWS) for Portfolio Monitoring"""
    __tablename__ = "early_warning_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Signal Configuration
    signal_code = Column(String(50), unique=True, nullable=False, index=True)
    signal_name = Column(String(200), nullable=False)
    signal_category = Column(String(50), nullable=False, index=True)
    # payment_behavior, financial_stress, credit_bureau, banking_behavior, 
    # business_performance, external_factors, relationship_changes
    
    # Severity
    severity_level = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    risk_weight = Column(Integer, default=1)  # Contribution to overall risk score
    
    # Detection Logic
    detection_rule = Column(JSON, nullable=False)
    # {"condition": "dpd", "operator": ">=", "value": 30, "days": 1}
    
    # Thresholds
    trigger_threshold = Column(Numeric(15, 2))
    monitoring_period_days = Column(Integer, default=30)
    
    # Actions
    auto_escalate = Column(Boolean, default=False)
    escalation_level = Column(String(50))  # branch_manager, credit_manager, collections
    notification_template = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Description
    description = Column(Text)
    recommended_action = Column(Text)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    alerts = relationship("EarlyWarningAlert", back_populates="signal")


class EarlyWarningAlert(Base):
    """Generated Early Warning Alerts for Accounts"""
    __tablename__ = "early_warning_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id"), nullable=False, index=True)
    signal_id = Column(Integer, ForeignKey("early_warning_signals.id"), nullable=False, index=True)
    
    # Alert Reference
    alert_number = Column(String(50), unique=True, nullable=False, index=True)
    alert_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Entity Reference
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)
    loan_account_id = Column(Integer, ForeignKey("loan_accounts.id"), nullable=False, index=True)
    
    # Alert Details
    signal_category = Column(String(50), nullable=False, index=True)
    severity_level = Column(String(20), nullable=False, index=True)
    
    # Detected Values
    detected_value = Column(Numeric(15, 2))
    threshold_value = Column(Numeric(15, 2))
    variance_percentage = Column(Numeric(5, 2))
    
    # Alert Status
    status = Column(String(50), nullable=False, default="open", index=True)
    # open, acknowledged, investigating, resolved, false_positive, escalated
    
    # Response Tracking
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(UUID(as_uuid=True))
    
    assigned_to = Column(UUID(as_uuid=True))
    assigned_at = Column(DateTime(timezone=True))
    
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True))
    resolution_remarks = Column(Text)
    
    # Action Taken
    action_taken = Column(Text)
    action_date = Column(DateTime(timezone=True))
    action_by = Column(UUID(as_uuid=True))
    
    # Impact Assessment
    customer_contacted = Column(Boolean, default=False)
    contact_date = Column(DateTime(timezone=True))
    account_put_on_watch = Column(Boolean, default=False)
    restructuring_initiated = Column(Boolean, default=False)
    
    # Escalation
    escalation_level = Column(Integer, default=0)
    escalated_to = Column(UUID(as_uuid=True))
    escalated_at = Column(DateTime(timezone=True))
    escalation_remarks = Column(Text)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    occurrence_count = Column(Integer, default=1)
    first_occurrence_date = Column(DateTime(timezone=True))
    last_occurrence_date = Column(DateTime(timezone=True))
    
    # Additional Data
    alert_data = Column(JSON)  # Flexible field for signal-specific data
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    signal = relationship("EarlyWarningSignal", back_populates="alerts")


# Indexes for performance optimization
Index('idx_credit_policy_active', CreditPolicy.tenant_id, CreditPolicy.is_active, CreditPolicy.is_deleted)
Index('idx_pricing_rule_active', RiskPricingRule.tenant_id, RiskPricingRule.is_active, RiskPricingRule.is_deleted)
Index('idx_exposure_limit_type', ExposureLimit.tenant_id, ExposureLimit.limit_type, ExposureLimit.is_active)
Index('idx_exposure_breach', ExposureLimit.tenant_id, ExposureLimit.is_breached, ExposureLimit.is_active)
Index('idx_risk_rating_customer', RiskRating.tenant_id, RiskRating.customer_id, RiskRating.rating_date)
Index('idx_risk_rating_grade', RiskRating.tenant_id, RiskRating.risk_grade, RiskRating.rating_type)
Index('idx_ews_alert_status', EarlyWarningAlert.tenant_id, EarlyWarningAlert.status, EarlyWarningAlert.severity_level)
Index('idx_ews_alert_account', EarlyWarningAlert.tenant_id, EarlyWarningAlert.loan_account_id, EarlyWarningAlert.status)
