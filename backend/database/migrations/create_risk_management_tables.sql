-- ============================================================================
-- Risk Management & Credit Policy Module - Database Migration Script
-- Creates all tables for credit policies, risk ratings, exposure limits,
-- pricing rules, and early warning system
-- ============================================================================

-- ============================================================================
-- 1. CREDIT POLICIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS credit_policies (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
    
    -- Policy Identification
    policy_code VARCHAR(50) UNIQUE NOT NULL,
    policy_name VARCHAR(200) NOT NULL,
    policy_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    
    -- Applicability
    product_types TEXT[],
    customer_segments TEXT[],
    loan_categories TEXT[],
    
    -- Credit Score Requirements
    min_cibil_score INTEGER NOT NULL,
    min_experian_score INTEGER,
    min_equifax_score INTEGER,
    min_crif_score INTEGER,
    bureau_vintage_months INTEGER DEFAULT 6,
    
    -- Income & DTI Criteria
    min_monthly_income NUMERIC(15, 2),
    max_debt_to_income_ratio NUMERIC(5, 2) NOT NULL,
    min_foir NUMERIC(5, 2),
    
    -- Loan Amount Limits
    min_loan_amount NUMERIC(15, 2) NOT NULL,
    max_loan_amount NUMERIC(15, 2) NOT NULL,
    ltv_ratio NUMERIC(5, 2),
    
    -- Age Criteria
    min_age INTEGER DEFAULT 21,
    max_age INTEGER DEFAULT 65,
    max_age_at_maturity INTEGER DEFAULT 70,
    
    -- Employment Criteria
    allowed_employment_types TEXT[],
    min_employment_months INTEGER DEFAULT 12,
    min_business_vintage_months INTEGER DEFAULT 24,
    
    -- Geographic Restrictions
    allowed_states TEXT[],
    restricted_pincodes TEXT[],
    tier_restrictions TEXT[],
    
    -- Negative Profiles
    max_active_loans INTEGER DEFAULT 3,
    max_enquiries_last_3months INTEGER DEFAULT 5,
    allow_defaults BOOLEAN DEFAULT FALSE,
    allow_settlements BOOLEAN DEFAULT FALSE,
    allow_write_offs BOOLEAN DEFAULT FALSE,
    min_months_since_default INTEGER,
    
    -- Co-applicant/Guarantor Rules
    requires_co_applicant BOOLEAN DEFAULT FALSE,
    requires_guarantor BOOLEAN DEFAULT FALSE,
    co_applicant_min_income NUMERIC(15, 2),
    
    -- Documentation Requirements
    mandatory_document_types INTEGER[],
    requires_bank_statement_months INTEGER DEFAULT 6,
    requires_itr_years INTEGER DEFAULT 2,
    
    -- Approval Authority Matrix
    approval_matrix JSONB,
    requires_credit_committee BOOLEAN DEFAULT FALSE,
    credit_committee_threshold NUMERIC(15, 2),
    
    -- Policy Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    
    -- Description
    description TEXT,
    terms_and_conditions TEXT,
    deviation_policy TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_credit_policy_tenant ON credit_policies(tenant_id);
CREATE INDEX idx_credit_policy_code ON credit_policies(policy_code);
CREATE INDEX idx_credit_policy_active ON credit_policies(tenant_id, is_active, is_deleted);

-- ============================================================================
-- 2. RISK PRICING RULES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS risk_pricing_rules (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
    credit_policy_id INTEGER NOT NULL REFERENCES credit_policies(id),
    
    -- Rule Identification
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    rule_priority INTEGER DEFAULT 0,
    
    -- Risk Factors (Conditions)
    min_credit_score INTEGER,
    max_credit_score INTEGER,
    min_loan_amount NUMERIC(15, 2),
    max_loan_amount NUMERIC(15, 2),
    min_tenure_months INTEGER,
    max_tenure_months INTEGER,
    customer_segment VARCHAR(50),
    employment_type VARCHAR(50),
    loan_category VARCHAR(50),
    risk_ratings TEXT[],
    
    -- Pricing Output
    base_interest_rate NUMERIC(5, 2) NOT NULL,
    rate_adjustment NUMERIC(5, 2) DEFAULT 0.00,
    final_interest_rate NUMERIC(5, 2) NOT NULL,
    
    -- Fee Adjustments
    processing_fee_adjustment NUMERIC(5, 2),
    reduce_documentation_charges BOOLEAN DEFAULT FALSE,
    waive_prepayment_charges BOOLEAN DEFAULT FALSE,
    
    -- Terms & Conditions
    max_ltv_override NUMERIC(5, 2),
    grace_period_days INTEGER,
    penal_interest_adjustment NUMERIC(5, 2),
    
    -- Incentives
    cashback_percentage NUMERIC(5, 2),
    loyalty_discount NUMERIC(5, 2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_pricing_rule_tenant ON risk_pricing_rules(tenant_id);
CREATE INDEX idx_pricing_rule_policy ON risk_pricing_rules(credit_policy_id);
CREATE INDEX idx_pricing_rule_active ON risk_pricing_rules(tenant_id, is_active, is_deleted);
CREATE INDEX idx_pricing_rule_priority ON risk_pricing_rules(rule_priority DESC);

-- ============================================================================
-- 3. EXPOSURE LIMITS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS exposure_limits (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
    
    -- Limit Identification
    limit_code VARCHAR(50) UNIQUE NOT NULL,
    limit_name VARCHAR(200) NOT NULL,
    limit_type VARCHAR(50) NOT NULL,
    
    -- Entity Reference
    customer_id UUID REFERENCES customers(id),
    industry_id UUID,
    state_code VARCHAR(10),
    product_type VARCHAR(50),
    collateral_type VARCHAR(50),
    dealer_id UUID,
    group_identifier VARCHAR(100),
    
    -- Limit Configuration
    limit_amount NUMERIC(15, 2) NOT NULL,
    utilized_amount NUMERIC(15, 2) DEFAULT 0.00,
    available_amount NUMERIC(15, 2) NOT NULL,
    utilization_percentage NUMERIC(5, 2) DEFAULT 0.00,
    
    -- Threshold Alerts
    warning_threshold_percentage NUMERIC(5, 2) DEFAULT 75.00,
    critical_threshold_percentage NUMERIC(5, 2) DEFAULT 90.00,
    breach_action VARCHAR(50),
    
    -- Limit Period
    limit_period VARCHAR(50) DEFAULT 'annual',
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    
    -- Regulatory Compliance
    regulatory_limit BOOLEAN DEFAULT FALSE,
    regulatory_reference VARCHAR(200),
    capital_charge_percentage NUMERIC(5, 2),
    
    -- Review & Monitoring
    last_review_date DATE,
    next_review_date DATE,
    review_frequency_days INTEGER DEFAULT 90,
    reviewer_id UUID,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_breached BOOLEAN DEFAULT FALSE,
    breach_date TIMESTAMP WITH TIME ZONE,
    breach_remarks TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_exposure_limit_tenant ON exposure_limits(tenant_id);
CREATE INDEX idx_exposure_limit_type ON exposure_limits(tenant_id, limit_type, is_active);
CREATE INDEX idx_exposure_breach ON exposure_limits(tenant_id, is_breached, is_active);
CREATE INDEX idx_exposure_customer ON exposure_limits(customer_id);

-- ============================================================================
-- 4. EXPOSURE TRANSACTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS exposure_transactions (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
    exposure_limit_id INTEGER NOT NULL REFERENCES exposure_limits(id),
    
    -- Transaction Details
    transaction_type VARCHAR(50) NOT NULL,
    transaction_reference VARCHAR(100),
    loan_application_id INTEGER REFERENCES loan_applications(id),
    loan_account_id INTEGER REFERENCES loan_accounts(id),
    
    -- Amount Movement
    amount NUMERIC(15, 2) NOT NULL,
    previous_utilized NUMERIC(15, 2) NOT NULL,
    new_utilized NUMERIC(15, 2) NOT NULL,
    
    -- Transaction Metadata
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    remarks TEXT,
    processed_by UUID,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_exposure_txn_limit ON exposure_transactions(exposure_limit_id);
CREATE INDEX idx_exposure_txn_date ON exposure_transactions(transaction_date DESC);

-- ============================================================================
-- 5. RISK RATINGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS risk_ratings (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
    
    -- Entity Reference
    customer_id UUID NOT NULL REFERENCES customers(id),
    loan_application_id INTEGER REFERENCES loan_applications(id),
    loan_account_id INTEGER REFERENCES loan_accounts(id),
    
    -- Rating Identification
    rating_type VARCHAR(50) NOT NULL,
    rating_date DATE NOT NULL,
    rating_valid_until DATE,
    
    -- Risk Rating
    risk_grade VARCHAR(10) NOT NULL,
    risk_score INTEGER NOT NULL,
    pd_percentage NUMERIC(5, 2),
    lgd_percentage NUMERIC(5, 2),
    ead_amount NUMERIC(15, 2),
    expected_loss NUMERIC(15, 2),
    
    -- Rating Factors (Scorecard)
    bureau_score INTEGER,
    bureau_score_weightage NUMERIC(5, 2),
    income_stability_score INTEGER,
    income_stability_weightage NUMERIC(5, 2),
    debt_burden_score INTEGER,
    debt_burden_weightage NUMERIC(5, 2),
    repayment_history_score INTEGER,
    repayment_history_weightage NUMERIC(5, 2),
    employment_stability_score INTEGER,
    employment_stability_weightage NUMERIC(5, 2),
    banking_behavior_score INTEGER,
    banking_behavior_weightage NUMERIC(5, 2),
    demographic_score INTEGER,
    demographic_weightage NUMERIC(5, 2),
    
    -- Additional Risk Indicators
    delinquency_flag BOOLEAN DEFAULT FALSE,
    fraud_flag BOOLEAN DEFAULT FALSE,
    litigation_flag BOOLEAN DEFAULT FALSE,
    negative_area_flag BOOLEAN DEFAULT FALSE,
    
    -- Credit Bureau Indicators
    dpd_max_last_12months INTEGER,
    dpd_max_last_24months INTEGER,
    active_loans_count INTEGER,
    enquiries_last_3months INTEGER,
    credit_utilization_percentage NUMERIC(5, 2),
    
    -- Behavioral Indicators
    avg_monthly_balance NUMERIC(15, 2),
    banking_relationship_months INTEGER,
    cheque_bounce_count_12months INTEGER,
    digital_payment_activity_score INTEGER,
    
    -- Override Information
    rating_override BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    override_approved_by UUID,
    override_date TIMESTAMP WITH TIME ZONE,
    original_risk_grade VARCHAR(10),
    original_risk_score INTEGER,
    
    -- Model Information
    rating_model_code VARCHAR(50),
    rating_model_version VARCHAR(20),
    
    -- Review Status
    review_required BOOLEAN DEFAULT FALSE,
    last_review_date DATE,
    next_review_date DATE,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_risk_rating_tenant ON risk_ratings(tenant_id);
CREATE INDEX idx_risk_rating_customer ON risk_ratings(tenant_id, customer_id, rating_date DESC);
CREATE INDEX idx_risk_rating_grade ON risk_ratings(tenant_id, risk_grade, rating_type);
CREATE INDEX idx_risk_rating_type ON risk_ratings(rating_type);

-- ============================================================================
-- 6. EARLY WARNING SIGNALS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS early_warning_signals (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
    
    -- Signal Configuration
    signal_code VARCHAR(50) UNIQUE NOT NULL,
    signal_name VARCHAR(200) NOT NULL,
    signal_category VARCHAR(50) NOT NULL,
    
    -- Severity
    severity_level VARCHAR(20) NOT NULL,
    risk_weight INTEGER DEFAULT 1,
    
    -- Detection Logic
    detection_rule JSONB NOT NULL,
    trigger_threshold NUMERIC(15, 2),
    monitoring_period_days INTEGER DEFAULT 30,
    
    -- Actions
    auto_escalate BOOLEAN DEFAULT FALSE,
    escalation_level VARCHAR(50),
    notification_template VARCHAR(100),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Description
    description TEXT,
    recommended_action TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_ews_signal_tenant ON early_warning_signals(tenant_id);
CREATE INDEX idx_ews_signal_category ON early_warning_signals(signal_category);
CREATE INDEX idx_ews_signal_active ON early_warning_signals(tenant_id, is_active);

-- ============================================================================
-- 7. EARLY WARNING ALERTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS early_warning_alerts (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL REFERENCES tenants(id),
    signal_id INTEGER NOT NULL REFERENCES early_warning_signals(id),
    
    -- Alert Reference
    alert_number VARCHAR(50) UNIQUE NOT NULL,
    alert_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Entity Reference
    customer_id UUID NOT NULL REFERENCES customers(id),
    loan_account_id INTEGER NOT NULL REFERENCES loan_accounts(id),
    
    -- Alert Details
    signal_category VARCHAR(50) NOT NULL,
    severity_level VARCHAR(20) NOT NULL,
    
    -- Detected Values
    detected_value NUMERIC(15, 2),
    threshold_value NUMERIC(15, 2),
    variance_percentage NUMERIC(5, 2),
    
    -- Alert Status
    status VARCHAR(50) DEFAULT 'open' NOT NULL,
    
    -- Response Tracking
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID,
    assigned_to UUID,
    assigned_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    resolution_remarks TEXT,
    
    -- Action Taken
    action_taken TEXT,
    action_date TIMESTAMP WITH TIME ZONE,
    action_by UUID,
    
    -- Impact Assessment
    customer_contacted BOOLEAN DEFAULT FALSE,
    contact_date TIMESTAMP WITH TIME ZONE,
    account_put_on_watch BOOLEAN DEFAULT FALSE,
    restructuring_initiated BOOLEAN DEFAULT FALSE,
    
    -- Escalation
    escalation_level INTEGER DEFAULT 0,
    escalated_to UUID,
    escalated_at TIMESTAMP WITH TIME ZONE,
    escalation_remarks TEXT,
    
    -- Recurrence
    is_recurring BOOLEAN DEFAULT FALSE,
    occurrence_count INTEGER DEFAULT 1,
    first_occurrence_date TIMESTAMP WITH TIME ZONE,
    last_occurrence_date TIMESTAMP WITH TIME ZONE,
    
    -- Additional Data
    alert_data JSONB,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_ews_alert_tenant ON early_warning_alerts(tenant_id);
CREATE INDEX idx_ews_alert_status ON early_warning_alerts(tenant_id, status, severity_level);
CREATE INDEX idx_ews_alert_account ON early_warning_alerts(tenant_id, loan_account_id, status);
CREATE INDEX idx_ews_alert_customer ON early_warning_alerts(customer_id);
CREATE INDEX idx_ews_alert_date ON early_warning_alerts(alert_date DESC);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_credit_policies_updated_at
    BEFORE UPDATE ON credit_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_pricing_rules_updated_at
    BEFORE UPDATE ON risk_pricing_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exposure_limits_updated_at
    BEFORE UPDATE ON exposure_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_ratings_updated_at
    BEFORE UPDATE ON risk_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_early_warning_signals_updated_at
    BEFORE UPDATE ON early_warning_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_early_warning_alerts_updated_at
    BEFORE UPDATE ON early_warning_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE credit_policies IS 'Credit policy engine configuration with eligibility criteria';
COMMENT ON TABLE risk_pricing_rules IS 'Risk-based pricing rules for dynamic interest rate calculation';
COMMENT ON TABLE exposure_limits IS 'Exposure limits for concentration risk management';
COMMENT ON TABLE exposure_transactions IS 'Exposure utilization and release transaction history';
COMMENT ON TABLE risk_ratings IS 'Customer and loan risk ratings with scorecard components';
COMMENT ON TABLE early_warning_signals IS 'Early warning signal definitions for portfolio monitoring';
COMMENT ON TABLE early_warning_alerts IS 'Generated early warning alerts for accounts';

-- ============================================================================
-- GRANT PERMISSIONS (Adjust based on your user setup)
-- ============================================================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nbfc_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nbfc_app_user;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
