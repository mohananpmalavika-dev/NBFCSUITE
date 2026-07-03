-- ============================================================================
-- Phase 11: Risk Management Migration
-- ============================================================================
-- Description: Comprehensive risk management system with credit risk,
--              operational risk, market risk, concentration risk, and compliance
-- Version: 1.0.0
-- Date: 2026-07-03
-- ============================================================================

-- ============================================================================
-- 1. RISK PARAMETERS TABLE
-- ============================================================================
CREATE TABLE gold_risk_parameters (
    parameter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parameter_code VARCHAR(50) NOT NULL UNIQUE,
    parameter_name VARCHAR(200) NOT NULL,
    risk_category VARCHAR(50) NOT NULL, -- 'credit', 'operational', 'market', 'concentration'
    parameter_type VARCHAR(50) NOT NULL, -- 'threshold', 'limit', 'ratio', 'score'
    parameter_value DECIMAL(20,4) NOT NULL,
    unit VARCHAR(20), -- 'percentage', 'amount', 'count', 'score'
    min_value DECIMAL(20,4),
    max_value DECIMAL(20,4),
    warning_threshold DECIMAL(20,4),
    critical_threshold DECIMAL(20,4),
    description TEXT,
    calculation_method TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_parameters_code ON gold_risk_parameters(parameter_code);
CREATE INDEX idx_risk_parameters_category ON gold_risk_parameters(risk_category);
CREATE INDEX idx_risk_parameters_active ON gold_risk_parameters(is_active);
CREATE INDEX idx_risk_parameters_effective ON gold_risk_parameters(effective_from, effective_to);

-- ============================================================================
-- 2. CREDIT RISK ASSESSMENTS TABLE
-- ============================================================================
CREATE TABLE gold_credit_risk_assessments (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_number VARCHAR(50) NOT NULL UNIQUE,
    loan_id UUID NOT NULL,
    customer_id UUID NOT NULL,
    assessment_date DATE NOT NULL,
    assessment_type VARCHAR(50) NOT NULL, -- 'initial', 'periodic', 'trigger_based'
    
    -- Credit Scores
    credit_score INTEGER,
    pd_score DECIMAL(10,4), -- Probability of Default
    lgd_score DECIMAL(10,4), -- Loss Given Default
    ead_amount DECIMAL(20,2), -- Exposure at Default
    
    -- Risk Ratings
    internal_rating VARCHAR(20), -- 'AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'D'
    external_rating VARCHAR(20),
    risk_grade VARCHAR(20), -- 'low', 'moderate', 'high', 'very_high'
    
    -- Financial Ratios
    dscr DECIMAL(10,4), -- Debt Service Coverage Ratio
    ltv_ratio DECIMAL(10,4), -- Loan to Value Ratio
    debt_to_income DECIMAL(10,4),
    
    -- Risk Factors
    collateral_quality_score DECIMAL(10,2),
    repayment_history_score DECIMAL(10,2),
    business_risk_score DECIMAL(10,2),
    market_risk_score DECIMAL(10,2),
    
    -- Assessment Results
    overall_risk_score DECIMAL(10,2) NOT NULL,
    risk_category VARCHAR(20) NOT NULL, -- 'standard', 'watch', 'substandard', 'doubtful', 'loss'
    
    -- Provisions
    provision_amount DECIMAL(20,2),
    provision_percentage DECIMAL(10,4),
    
    -- Status
    assessment_status VARCHAR(20) NOT NULL DEFAULT 'draft',
    approved_by UUID,
    approved_at TIMESTAMP,
    
    -- Metadata
    assessment_notes TEXT,
    risk_factors JSONB,
    mitigating_factors JSONB,
    
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_credit_risk_number ON gold_credit_risk_assessments(assessment_number);
CREATE INDEX idx_credit_risk_loan ON gold_credit_risk_assessments(loan_id);
CREATE INDEX idx_credit_risk_customer ON gold_credit_risk_assessments(customer_id);
CREATE INDEX idx_credit_risk_date ON gold_credit_risk_assessments(assessment_date);
CREATE INDEX idx_credit_risk_category ON gold_credit_risk_assessments(risk_category);
CREATE INDEX idx_credit_risk_status ON gold_credit_risk_assessments(assessment_status);

-- ============================================================================
-- 3. OPERATIONAL RISK EVENTS TABLE
-- ============================================================================
CREATE TABLE gold_operational_risk_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_number VARCHAR(50) NOT NULL UNIQUE,
    event_date DATE NOT NULL,
    event_time TIMESTAMP NOT NULL,
    
    -- Event Classification
    event_category VARCHAR(50) NOT NULL, -- 'fraud', 'error', 'system_failure', 'compliance_breach', 'security_incident'
    event_type VARCHAR(100) NOT NULL,
    event_severity VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    
    -- Event Details
    event_title VARCHAR(500) NOT NULL,
    event_description TEXT NOT NULL,
    root_cause TEXT,
    
    -- Location
    branch_id UUID,
    department VARCHAR(100),
    process_name VARCHAR(200),
    
    -- Impact Assessment
    financial_impact DECIMAL(20,2),
    reputational_impact VARCHAR(20), -- 'none', 'low', 'medium', 'high'
    customer_impact INTEGER, -- number of customers affected
    operational_impact TEXT,
    
    -- People Involved
    reported_by UUID NOT NULL,
    assigned_to UUID,
    responsible_party UUID,
    
    -- Status & Resolution
    event_status VARCHAR(20) NOT NULL DEFAULT 'reported', -- 'reported', 'investigating', 'resolved', 'closed'
    resolution_date DATE,
    resolution_description TEXT,
    
    -- Risk Controls
    control_failure BOOLEAN DEFAULT FALSE,
    control_id UUID,
    
    -- Regulatory Reporting
    requires_regulatory_reporting BOOLEAN DEFAULT FALSE,
    reported_to_regulator BOOLEAN DEFAULT FALSE,
    regulator_reference VARCHAR(100),
    reporting_date DATE,
    
    -- Lessons Learned
    lessons_learned TEXT,
    corrective_actions JSONB,
    preventive_actions JSONB,
    
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_op_risk_number ON gold_operational_risk_events(event_number);
CREATE INDEX idx_op_risk_date ON gold_operational_risk_events(event_date);
CREATE INDEX idx_op_risk_category ON gold_operational_risk_events(event_category);
CREATE INDEX idx_op_risk_severity ON gold_operational_risk_events(event_severity);
CREATE INDEX idx_op_risk_status ON gold_operational_risk_events(event_status);
CREATE INDEX idx_op_risk_branch ON gold_operational_risk_events(branch_id);

-- ============================================================================
-- 4. MARKET RISK EXPOSURES TABLE
-- ============================================================================
CREATE TABLE gold_market_risk_exposures (
    exposure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exposure_date DATE NOT NULL,
    
    -- Gold Price Risk
    gold_rate_per_gram DECIMAL(10,2) NOT NULL,
    total_gold_weight_kg DECIMAL(10,3) NOT NULL,
    total_gold_value DECIMAL(20,2) NOT NULL,
    
    -- Portfolio Composition
    portfolio_loan_count INTEGER NOT NULL,
    portfolio_outstanding_amount DECIMAL(20,2) NOT NULL,
    average_ltv DECIMAL(10,4),
    
    -- Value at Risk (VaR)
    var_1day_95 DECIMAL(20,2), -- 1-day VaR at 95% confidence
    var_1day_99 DECIMAL(20,2), -- 1-day VaR at 99% confidence
    var_10day_95 DECIMAL(20,2),
    var_10day_99 DECIMAL(20,2),
    
    -- Stress Testing
    stress_scenario_10pct_drop DECIMAL(20,2),
    stress_scenario_20pct_drop DECIMAL(20,2),
    stress_scenario_30pct_drop DECIMAL(20,2),
    
    -- Interest Rate Risk
    interest_rate_portfolio DECIMAL(10,4),
    interest_rate_sensitivity DECIMAL(20,2),
    duration_gap DECIMAL(10,4),
    
    -- Liquidity Risk
    liquidity_coverage_ratio DECIMAL(10,4),
    cash_to_assets_ratio DECIMAL(10,4),
    
    -- Risk Metrics
    portfolio_volatility DECIMAL(10,4),
    sharpe_ratio DECIMAL(10,4),
    
    -- Market Conditions
    market_sentiment VARCHAR(20), -- 'bullish', 'neutral', 'bearish'
    gold_price_trend VARCHAR(20), -- 'rising', 'stable', 'falling'
    market_volatility VARCHAR(20), -- 'low', 'moderate', 'high'
    
    -- Hedging
    hedging_strategy VARCHAR(100),
    hedged_exposure DECIMAL(20,2),
    unhedged_exposure DECIMAL(20,2),
    hedging_cost DECIMAL(20,2),
    
    -- Status
    calculation_method VARCHAR(50),
    data_quality_score DECIMAL(10,2),
    
    created_by UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_market_risk_date ON gold_market_risk_exposures(exposure_date);
CREATE INDEX idx_market_risk_gold_rate ON gold_market_risk_exposures(gold_rate_per_gram);

-- ============================================================================
-- 5. CONCENTRATION RISK LIMITS TABLE
-- ============================================================================
CREATE TABLE gold_concentration_risk_limits (
    limit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    limit_code VARCHAR(50) NOT NULL UNIQUE,
    limit_name VARCHAR(200) NOT NULL,
    
    -- Concentration Type
    concentration_type VARCHAR(50) NOT NULL, -- 'customer', 'branch', 'geography', 'product', 'collateral'
    concentration_dimension VARCHAR(100), -- specific dimension like 'single_customer', 'top_10_customers'
    
    -- Limit Definition
    limit_value DECIMAL(20,2) NOT NULL,
    limit_unit VARCHAR(20) NOT NULL, -- 'amount', 'percentage', 'count'
    limit_basis VARCHAR(50), -- 'total_portfolio', 'capital', 'net_worth'
    
    -- Thresholds
    warning_threshold DECIMAL(20,2),
    breach_threshold DECIMAL(20,2),
    regulatory_limit DECIMAL(20,2),
    
    -- Current Exposure
    current_exposure DECIMAL(20,2),
    utilization_percentage DECIMAL(10,4),
    
    -- Status
    limit_status VARCHAR(20) DEFAULT 'within_limit', -- 'within_limit', 'warning', 'breached'
    last_breach_date DATE,
    breach_count INTEGER DEFAULT 0,
    
    -- Monitoring
    monitoring_frequency VARCHAR(20), -- 'daily', 'weekly', 'monthly'
    last_monitored_at TIMESTAMP,
    next_review_date DATE,
    
    -- Actions
    breach_action TEXT,
    escalation_required BOOLEAN DEFAULT FALSE,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conc_risk_code ON gold_concentration_risk_limits(limit_code);
CREATE INDEX idx_conc_risk_type ON gold_concentration_risk_limits(concentration_type);
CREATE INDEX idx_conc_risk_status ON gold_concentration_risk_limits(limit_status);
CREATE INDEX idx_conc_risk_active ON gold_concentration_risk_limits(is_active);

-- ============================================================================
-- 6. RISK ALERTS TABLE
-- ============================================================================
CREATE TABLE gold_risk_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_number VARCHAR(50) NOT NULL UNIQUE,
    alert_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Alert Classification
    alert_category VARCHAR(50) NOT NULL, -- 'credit', 'operational', 'market', 'concentration', 'compliance'
    alert_type VARCHAR(100) NOT NULL,
    alert_severity VARCHAR(20) NOT NULL, -- 'info', 'warning', 'critical'
    alert_priority VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'urgent'
    
    -- Alert Details
    alert_title VARCHAR(500) NOT NULL,
    alert_message TEXT NOT NULL,
    alert_source VARCHAR(100), -- 'system', 'manual', 'scheduled_check'
    
    -- Entity Reference
    entity_type VARCHAR(50), -- 'loan', 'customer', 'branch', 'portfolio'
    entity_id UUID,
    reference_number VARCHAR(100),
    
    -- Threshold Breach
    threshold_parameter VARCHAR(100),
    threshold_value DECIMAL(20,4),
    actual_value DECIMAL(20,4),
    deviation_percentage DECIMAL(10,4),
    
    -- Assignment
    assigned_to UUID,
    assigned_at TIMESTAMP,
    department VARCHAR(100),
    
    -- Status & Resolution
    alert_status VARCHAR(20) NOT NULL DEFAULT 'open', -- 'open', 'investigating', 'resolved', 'dismissed'
    resolution_date TIMESTAMP,
    resolution_notes TEXT,
    resolution_action VARCHAR(100),
    
    -- Escalation
    requires_escalation BOOLEAN DEFAULT FALSE,
    escalated_to UUID,
    escalated_at TIMESTAMP,
    
    -- Notifications
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_channels JSONB, -- ['email', 'sms', 'dashboard']
    notified_users JSONB,
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_notes TEXT,
    
    created_by UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_alerts_number ON gold_risk_alerts(alert_number);
CREATE INDEX idx_risk_alerts_date ON gold_risk_alerts(alert_date);
CREATE INDEX idx_risk_alerts_category ON gold_risk_alerts(alert_category);
CREATE INDEX idx_risk_alerts_severity ON gold_risk_alerts(alert_severity);
CREATE INDEX idx_risk_alerts_status ON gold_risk_alerts(alert_status);
CREATE INDEX idx_risk_alerts_assigned ON gold_risk_alerts(assigned_to);
CREATE INDEX idx_risk_alerts_entity ON gold_risk_alerts(entity_type, entity_id);

-- ============================================================================
-- 7. RISK MITIGATIONS TABLE
-- ============================================================================
CREATE TABLE gold_risk_mitigations (
    mitigation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mitigation_number VARCHAR(50) NOT NULL UNIQUE,
    
    -- Risk Reference
    risk_category VARCHAR(50) NOT NULL,
    risk_id UUID, -- reference to assessment/event/exposure
    risk_description TEXT,
    
    -- Mitigation Details
    mitigation_type VARCHAR(50) NOT NULL, -- 'control', 'transfer', 'avoid', 'accept', 'reduce'
    mitigation_title VARCHAR(500) NOT NULL,
    mitigation_description TEXT NOT NULL,
    
    -- Implementation
    implementation_plan TEXT,
    implementation_cost DECIMAL(20,2),
    implementation_timeline VARCHAR(100),
    expected_completion_date DATE,
    actual_completion_date DATE,
    
    -- Effectiveness
    expected_risk_reduction DECIMAL(10,4), -- percentage
    actual_risk_reduction DECIMAL(10,4),
    effectiveness_score DECIMAL(10,2),
    
    -- Ownership
    owner_id UUID NOT NULL,
    owner_department VARCHAR(100),
    approver_id UUID,
    approved_at TIMESTAMP,
    
    -- Status
    mitigation_status VARCHAR(20) NOT NULL DEFAULT 'planned', -- 'planned', 'in_progress', 'implemented', 'verified', 'failed'
    status_update_date DATE,
    
    -- Monitoring
    monitoring_frequency VARCHAR(20),
    last_review_date DATE,
    next_review_date DATE,
    review_notes TEXT,
    
    -- Dependencies
    dependencies JSONB,
    prerequisites TEXT,
    
    -- Documentation
    supporting_documents JSONB,
    approval_documents JSONB,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_mitigations_number ON gold_risk_mitigations(mitigation_number);
CREATE INDEX idx_risk_mitigations_category ON gold_risk_mitigations(risk_category);
CREATE INDEX idx_risk_mitigations_risk ON gold_risk_mitigations(risk_id);
CREATE INDEX idx_risk_mitigations_status ON gold_risk_mitigations(mitigation_status);
CREATE INDEX idx_risk_mitigations_owner ON gold_risk_mitigations(owner_id);

-- ============================================================================
-- 8. RISK REPORTS TABLE
-- ============================================================================
CREATE TABLE gold_risk_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_number VARCHAR(50) NOT NULL UNIQUE,
    report_date DATE NOT NULL,
    
    -- Report Classification
    report_type VARCHAR(50) NOT NULL, -- 'credit_risk', 'operational_risk', 'market_risk', 'comprehensive'
    report_period VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'monthly', 'quarterly', 'annual'
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    
    -- Report Content
    report_title VARCHAR(500) NOT NULL,
    executive_summary TEXT,
    
    -- Risk Metrics (JSONB for flexibility)
    credit_risk_metrics JSONB,
    operational_risk_metrics JSONB,
    market_risk_metrics JSONB,
    concentration_risk_metrics JSONB,
    
    -- Key Findings
    key_findings JSONB,
    risk_trends JSONB,
    breaches JSONB,
    
    -- Recommendations
    recommendations TEXT,
    action_items JSONB,
    
    -- Approval
    prepared_by UUID NOT NULL,
    reviewed_by UUID,
    approved_by UUID,
    approved_at TIMESTAMP,
    
    -- Status
    report_status VARCHAR(20) NOT NULL DEFAULT 'draft', -- 'draft', 'review', 'approved', 'published'
    
    -- Distribution
    distribution_list JSONB,
    published_at TIMESTAMP,
    
    -- File Storage
    report_file_path VARCHAR(1000),
    report_file_size BIGINT,
    
    created_by UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_reports_number ON gold_risk_reports(report_number);
CREATE INDEX idx_risk_reports_date ON gold_risk_reports(report_date);
CREATE INDEX idx_risk_reports_type ON gold_risk_reports(report_type);
CREATE INDEX idx_risk_reports_period ON gold_risk_reports(period_start_date, period_end_date);
CREATE INDEX idx_risk_reports_status ON gold_risk_reports(report_status);

-- ============================================================================
-- 9. RISK DASHBOARDS TABLE
-- ============================================================================
CREATE TABLE gold_risk_dashboards (
    dashboard_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_code VARCHAR(50) NOT NULL UNIQUE,
    dashboard_name VARCHAR(200) NOT NULL,
    dashboard_type VARCHAR(50) NOT NULL, -- 'executive', 'credit', 'operational', 'market', 'comprehensive'
    
    -- Dashboard Configuration
    layout_config JSONB NOT NULL,
    widget_config JSONB NOT NULL,
    filter_config JSONB,
    
    -- Data Refresh
    refresh_frequency VARCHAR(20), -- 'realtime', 'hourly', 'daily'
    last_refreshed_at TIMESTAMP,
    data_as_of_date DATE,
    
    -- Access Control
    visibility VARCHAR(20) NOT NULL DEFAULT 'private', -- 'private', 'shared', 'public'
    owner_id UUID NOT NULL,
    shared_with JSONB, -- list of user IDs
    
    -- Customization
    is_default BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    parent_dashboard_id UUID,
    
    -- Usage
    view_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP,
    
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_dashboards_code ON gold_risk_dashboards(dashboard_code);
CREATE INDEX idx_risk_dashboards_type ON gold_risk_dashboards(dashboard_type);
CREATE INDEX idx_risk_dashboards_owner ON gold_risk_dashboards(owner_id);
CREATE INDEX idx_risk_dashboards_active ON gold_risk_dashboards(is_active);

-- ============================================================================
-- 10. COMPLIANCE CHECKS TABLE
-- ============================================================================
CREATE TABLE gold_compliance_checks (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_number VARCHAR(50) NOT NULL UNIQUE,
    check_date DATE NOT NULL,
    
    -- Compliance Area
    compliance_category VARCHAR(50) NOT NULL, -- 'regulatory', 'internal_policy', 'industry_standard'
    compliance_area VARCHAR(100) NOT NULL, -- 'rbi_guidelines', 'aml_kyc', 'lending_norms', 'fair_practices'
    regulation_reference VARCHAR(200),
    
    -- Check Details
    check_title VARCHAR(500) NOT NULL,
    check_description TEXT,
    check_type VARCHAR(50), -- 'manual', 'automated', 'periodic', 'trigger_based'
    
    -- Scope
    check_scope VARCHAR(100), -- 'portfolio', 'branch', 'customer', 'transaction'
    entity_type VARCHAR(50),
    entity_id UUID,
    
    -- Compliance Requirements
    requirement_description TEXT,
    compliance_criteria TEXT,
    expected_value VARCHAR(200),
    
    -- Check Results
    actual_value VARCHAR(200),
    check_result VARCHAR(20) NOT NULL, -- 'compliant', 'non_compliant', 'partial', 'not_applicable'
    compliance_score DECIMAL(10,2),
    
    -- Risk Assessment
    risk_level VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    potential_impact TEXT,
    
    -- Non-Compliance Details
    deviation_details TEXT,
    root_cause TEXT,
    
    -- Actions
    corrective_action_required BOOLEAN DEFAULT FALSE,
    corrective_action_plan TEXT,
    action_owner_id UUID,
    target_completion_date DATE,
    actual_completion_date DATE,
    
    -- Approval & Review
    reviewed_by UUID,
    reviewed_at TIMESTAMP,
    approved_by UUID,
    approved_at TIMESTAMP,
    
    -- Status
    check_status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'under_review', 'approved'
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_notes TEXT,
    
    -- Documentation
    evidence_documents JSONB,
    audit_trail JSONB,
    
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_compliance_checks_number ON gold_compliance_checks(check_number);
CREATE INDEX idx_compliance_checks_date ON gold_compliance_checks(check_date);
CREATE INDEX idx_compliance_checks_category ON gold_compliance_checks(compliance_category);
CREATE INDEX idx_compliance_checks_area ON gold_compliance_checks(compliance_area);
CREATE INDEX idx_compliance_checks_result ON gold_compliance_checks(check_result);
CREATE INDEX idx_compliance_checks_status ON gold_compliance_checks(check_status);
CREATE INDEX idx_compliance_checks_entity ON gold_compliance_checks(entity_type, entity_id);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Credit Risk Portfolio Summary
CREATE OR REPLACE VIEW v_credit_risk_portfolio AS
SELECT 
    cr.risk_category,
    COUNT(DISTINCT cr.loan_id) as loan_count,
    COUNT(DISTINCT cr.customer_id) as customer_count,
    AVG(cr.overall_risk_score) as avg_risk_score,
    AVG(cr.ltv_ratio) as avg_ltv,
    AVG(cr.pd_score) as avg_pd,
    SUM(cr.provision_amount) as total_provisions,
    COUNT(CASE WHEN cr.risk_category IN ('substandard', 'doubtful', 'loss') THEN 1 END) as npa_count
FROM gold_credit_risk_assessments cr
WHERE cr.assessment_status = 'approved'
AND cr.assessment_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY cr.risk_category;

-- View: Operational Risk Events Summary
CREATE OR REPLACE VIEW v_operational_risk_summary AS
SELECT 
    DATE_TRUNC('month', ore.event_date) as month,
    ore.event_category,
    ore.event_severity,
    COUNT(*) as event_count,
    SUM(ore.financial_impact) as total_financial_impact,
    COUNT(CASE WHEN ore.event_status = 'resolved' THEN 1 END) as resolved_count,
    COUNT(CASE WHEN ore.requires_regulatory_reporting THEN 1 END) as regulatory_reporting_count
FROM gold_operational_risk_events ore
WHERE ore.event_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', ore.event_date), ore.event_category, ore.event_severity;

-- View: Market Risk Exposure Trend
CREATE OR REPLACE VIEW v_market_risk_trend AS
SELECT 
    mre.exposure_date,
    mre.gold_rate_per_gram,
    mre.total_gold_value,
    mre.var_1day_99,
    mre.portfolio_outstanding_amount,
    mre.average_ltv,
    mre.market_sentiment,
    LAG(mre.gold_rate_per_gram) OVER (ORDER BY mre.exposure_date) as prev_gold_rate,
    ((mre.gold_rate_per_gram - LAG(mre.gold_rate_per_gram) OVER (ORDER BY mre.exposure_date)) / 
     LAG(mre.gold_rate_per_gram) OVER (ORDER BY mre.exposure_date) * 100) as gold_rate_change_pct
FROM gold_market_risk_exposures mre
ORDER BY mre.exposure_date DESC;

-- View: Risk Alerts Dashboard
CREATE OR REPLACE VIEW v_risk_alerts_dashboard AS
SELECT 
    ra.alert_category,
    ra.alert_severity,
    ra.alert_status,
    COUNT(*) as alert_count,
    COUNT(CASE WHEN ra.alert_date >= CURRENT_DATE THEN 1 END) as today_count,
    COUNT(CASE WHEN ra.requires_escalation THEN 1 END) as escalation_count,
    COUNT(CASE WHEN ra.assigned_to IS NULL THEN 1 END) as unassigned_count,
    MAX(ra.alert_date) as last_alert_date
FROM gold_risk_alerts ra
WHERE ra.alert_status IN ('open', 'investigating')
GROUP BY ra.alert_category, ra.alert_severity, ra.alert_status;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_risk_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_risk_parameters_updated_at
    BEFORE UPDATE ON gold_risk_parameters
    FOR EACH ROW EXECUTE FUNCTION update_risk_updated_at();

CREATE TRIGGER trg_credit_risk_updated_at
    BEFORE UPDATE ON gold_credit_risk_assessments
    FOR EACH ROW EXECUTE FUNCTION update_risk_updated_at();

CREATE TRIGGER trg_op_risk_updated_at
    BEFORE UPDATE ON gold_operational_risk_events
    FOR EACH ROW EXECUTE FUNCTION update_risk_updated_at();

CREATE TRIGGER trg_conc_risk_updated_at
    BEFORE UPDATE ON gold_concentration_risk_limits
    FOR EACH ROW EXECUTE FUNCTION update_risk_updated_at();

CREATE TRIGGER trg_risk_mitigations_updated_at
    BEFORE UPDATE ON gold_risk_mitigations
    FOR EACH ROW EXECUTE FUNCTION update_risk_updated_at();

CREATE TRIGGER trg_risk_dashboards_updated_at
    BEFORE UPDATE ON gold_risk_dashboards
    FOR EACH ROW EXECUTE FUNCTION update_risk_updated_at();

CREATE TRIGGER trg_compliance_checks_updated_at
    BEFORE UPDATE ON gold_compliance_checks
    FOR EACH ROW EXECUTE FUNCTION update_risk_updated_at();

-- Trigger: Generate alert number
CREATE OR REPLACE FUNCTION generate_risk_alert_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.alert_number := 'ALT' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || LPAD(NEXTVAL('seq_risk_alert')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE seq_risk_alert START 1;

CREATE TRIGGER trg_risk_alert_number
    BEFORE INSERT ON gold_risk_alerts
    FOR EACH ROW 
    WHEN (NEW.alert_number IS NULL)
    EXECUTE FUNCTION generate_risk_alert_number();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Risk Parameters
INSERT INTO gold_risk_parameters (parameter_code, parameter_name, risk_category, parameter_type, parameter_value, unit, warning_threshold, critical_threshold, description, is_active, effective_from, created_by) VALUES
('PARAM_MAX_LTV', 'Maximum Loan-to-Value Ratio', 'credit', 'ratio', 75.00, 'percentage', 70.00, 75.00, 'Maximum LTV allowed for gold loans', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_MIN_DSCR', 'Minimum Debt Service Coverage Ratio', 'credit', 'ratio', 1.25, 'ratio', 1.30, 1.25, 'Minimum DSCR required for loan approval', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_MAX_SINGLE_CUST', 'Maximum Single Customer Exposure', 'concentration', 'limit', 10.00, 'percentage', 8.00, 10.00, 'Maximum exposure to single customer as % of portfolio', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_MAX_BRANCH_CONC', 'Maximum Branch Concentration', 'concentration', 'limit', 25.00, 'percentage', 20.00, 25.00, 'Maximum concentration in single branch', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_VAR_LIMIT', 'Value at Risk Limit', 'market', 'limit', 5.00, 'percentage', 4.00, 5.00, 'Maximum VaR as % of portfolio value', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_OP_LOSS_LIMIT', 'Operational Loss Limit', 'operational', 'limit', 1000000.00, 'amount', 750000.00, 1000000.00, 'Maximum acceptable operational loss per event', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_NPA_RATIO', 'NPA Ratio Threshold', 'credit', 'ratio', 5.00, 'percentage', 3.00, 5.00, 'Maximum acceptable NPA ratio', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_PROVISION_STD', 'Standard Asset Provision', 'credit', 'ratio', 0.40, 'percentage', NULL, NULL, 'Provision percentage for standard assets', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_PROVISION_SUBS', 'Substandard Asset Provision', 'credit', 'ratio', 15.00, 'percentage', NULL, NULL, 'Provision percentage for substandard assets', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('PARAM_PROVISION_DOUBT', 'Doubtful Asset Provision', 'credit', 'ratio', 40.00, 'percentage', NULL, NULL, 'Provision percentage for doubtful assets', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000');

-- Concentration Risk Limits
INSERT INTO gold_concentration_risk_limits (limit_code, limit_name, concentration_type, concentration_dimension, limit_value, limit_unit, limit_basis, warning_threshold, breach_threshold, monitoring_frequency, is_active, effective_from, created_by) VALUES
('LIMIT_SINGLE_CUST', 'Single Customer Limit', 'customer', 'single_customer', 10.00, 'percentage', 'total_portfolio', 8.00, 10.00, 'daily', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('LIMIT_TOP10_CUST', 'Top 10 Customers Limit', 'customer', 'top_10_customers', 40.00, 'percentage', 'total_portfolio', 35.00, 40.00, 'weekly', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('LIMIT_BRANCH_MAX', 'Maximum Branch Exposure', 'branch', 'single_branch', 25.00, 'percentage', 'total_portfolio', 20.00, 25.00, 'daily', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('LIMIT_GEO_STATE', 'State Geographic Concentration', 'geography', 'single_state', 50.00, 'percentage', 'total_portfolio', 45.00, 50.00, 'monthly', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'),
('LIMIT_PRODUCT_TYPE', 'Product Type Concentration', 'product', 'single_product', 80.00, 'percentage', 'total_portfolio', 75.00, 80.00, 'monthly', TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE gold_risk_parameters IS 'Risk management parameters and thresholds';
COMMENT ON TABLE gold_credit_risk_assessments IS 'Credit risk assessments for loans';
COMMENT ON TABLE gold_operational_risk_events IS 'Operational risk events and incidents';
COMMENT ON TABLE gold_market_risk_exposures IS 'Market risk exposures and VaR calculations';
COMMENT ON TABLE gold_concentration_risk_limits IS 'Concentration risk limits and monitoring';
COMMENT ON TABLE gold_risk_alerts IS 'Risk alerts and notifications';
COMMENT ON TABLE gold_risk_mitigations IS 'Risk mitigation actions and controls';
COMMENT ON TABLE gold_risk_reports IS 'Risk management reports';
COMMENT ON TABLE gold_risk_dashboards IS 'Risk dashboard configurations';
COMMENT ON TABLE gold_compliance_checks IS 'Compliance checks and audits';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
