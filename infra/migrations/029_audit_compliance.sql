-- ============================================================================
-- Phase 12: Audit & Compliance
-- Migration: 029_audit_compliance.sql
-- Description: Comprehensive audit trail, compliance management, and regulatory reporting
-- ============================================================================

-- ============================================================================
-- TABLE: audit_trails
-- Description: Universal audit trail for all system activities
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_trails (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Event Information
    event_type VARCHAR(50) NOT NULL, -- create, update, delete, approve, reject, login, logout
    event_category VARCHAR(50) NOT NULL, -- transaction, configuration, security, access
    entity_type VARCHAR(100) NOT NULL, -- loan, customer, payment, etc.
    entity_id UUID,
    entity_reference VARCHAR(100),
    
    -- User Information
    user_id UUID NOT NULL,
    user_name VARCHAR(200),
    user_role VARCHAR(100),
    user_ip_address INET,
    user_location VARCHAR(200),
    session_id UUID,
    
    -- Change Information
    action_performed VARCHAR(200) NOT NULL,
    action_status VARCHAR(20) NOT NULL, -- success, failed, partial
    old_values JSONB,
    new_values JSONB,
    changed_fields TEXT[],
    
    -- Request Information
    request_method VARCHAR(10), -- GET, POST, PUT, DELETE
    request_endpoint VARCHAR(500),
    request_payload JSONB,
    response_status INTEGER,
    response_message TEXT,
    
    -- Business Context
    transaction_id UUID,
    parent_audit_id UUID,
    workflow_id UUID,
    approval_level INTEGER,
    
    -- Risk & Security
    risk_level VARCHAR(20), -- low, medium, high, critical
    security_flag BOOLEAN DEFAULT FALSE,
    compliance_flag BOOLEAN DEFAULT FALSE,
    fraud_flag BOOLEAN DEFAULT FALSE,
    
    -- Additional Information
    remarks TEXT,
    metadata JSONB,
    tags TEXT[],
    
    -- Timing
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processing_duration_ms INTEGER,
    
    -- Archival
    is_archived BOOLEAN DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE,
    retention_until DATE
);

-- Indexes for audit_trails
CREATE INDEX idx_audit_trails_event_type ON audit_trails(event_type);
CREATE INDEX idx_audit_trails_event_category ON audit_trails(event_category);
CREATE INDEX idx_audit_trails_entity_type ON audit_trails(entity_type);
CREATE INDEX idx_audit_trails_entity_id ON audit_trails(entity_id);
CREATE INDEX idx_audit_trails_user_id ON audit_trails(user_id);
CREATE INDEX idx_audit_trails_event_timestamp ON audit_trails(event_timestamp DESC);
CREATE INDEX idx_audit_trails_action_status ON audit_trails(action_status);
CREATE INDEX idx_audit_trails_risk_level ON audit_trails(risk_level);
CREATE INDEX idx_audit_trails_security_flag ON audit_trails(security_flag) WHERE security_flag = TRUE;
CREATE INDEX idx_audit_trails_compliance_flag ON audit_trails(compliance_flag) WHERE compliance_flag = TRUE;
CREATE INDEX idx_audit_trails_fraud_flag ON audit_trails(fraud_flag) WHERE fraud_flag = TRUE;
CREATE INDEX idx_audit_trails_transaction_id ON audit_trails(transaction_id);
CREATE INDEX idx_audit_trails_session_id ON audit_trails(session_id);
CREATE INDEX idx_audit_trails_retention ON audit_trails(retention_until) WHERE is_archived = FALSE;
CREATE INDEX idx_audit_trails_metadata ON audit_trails USING GIN(metadata);


-- ============================================================================
-- TABLE: compliance_rules
-- Description: Define compliance rules and regulations
-- ============================================================================
CREATE TABLE IF NOT EXISTS compliance_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Rule Identification
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    rule_category VARCHAR(50) NOT NULL, -- regulatory, internal_policy, industry_standard
    
    -- Regulatory Information
    regulation_name VARCHAR(200),
    regulation_code VARCHAR(100),
    regulatory_body VARCHAR(200),
    jurisdiction VARCHAR(100),
    
    -- Rule Details
    rule_description TEXT NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- mandatory, optional, best_practice
    severity_level VARCHAR(20) NOT NULL, -- critical, high, medium, low
    
    -- Scope
    applicable_entities TEXT[], -- loan, customer, transaction, etc.
    applicable_processes TEXT[], -- origination, servicing, collections
    applicable_departments TEXT[],
    
    -- Implementation
    validation_method VARCHAR(50), -- automated, manual, hybrid
    validation_frequency VARCHAR(50), -- real_time, daily, weekly, monthly
    validation_query TEXT,
    validation_script TEXT,
    
    -- Thresholds & Limits
    threshold_values JSONB,
    breach_conditions JSONB,
    
    -- Actions
    on_breach_action VARCHAR(50), -- alert, block, escalate, log
    escalation_rules JSONB,
    remediation_steps TEXT,
    
    -- Documentation
    reference_documents JSONB,
    related_rules UUID[],
    change_history JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    last_reviewed_date DATE,
    next_review_date DATE,
    
    -- Audit
    created_by UUID NOT NULL,
    updated_by UUID,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_compliance_rules_code ON compliance_rules(rule_code);
CREATE INDEX idx_compliance_rules_category ON compliance_rules(rule_category);
CREATE INDEX idx_compliance_rules_type ON compliance_rules(rule_type);
CREATE INDEX idx_compliance_rules_severity ON compliance_rules(severity_level);
CREATE INDEX idx_compliance_rules_active ON compliance_rules(is_active);
CREATE INDEX idx_compliance_rules_effective ON compliance_rules(effective_from, effective_to);
CREATE INDEX idx_compliance_rules_review ON compliance_rules(next_review_date) WHERE is_active = TRUE;


-- ============================================================================
-- TABLE: compliance_violations
-- Description: Track compliance rule violations and breaches
-- ============================================================================
CREATE TABLE IF NOT EXISTS compliance_violations (
    violation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Violation Identification
    violation_number VARCHAR(50) UNIQUE NOT NULL,
    rule_id UUID NOT NULL REFERENCES compliance_rules(rule_id),
    
    -- Violation Details
    violation_type VARCHAR(50) NOT NULL, -- breach, near_miss, potential_risk
    severity_level VARCHAR(20) NOT NULL,
    violation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    detection_method VARCHAR(50), -- automated, manual, audit, complaint
    
    -- Entity Information
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    entity_reference VARCHAR(200),
    
    -- Context
    violation_description TEXT NOT NULL,
    root_cause TEXT,
    contributing_factors JSONB,
    business_impact TEXT,
    financial_impact DECIMAL(15,2),
    
    -- Evidence
    evidence_documents JSONB,
    screenshots JSONB,
    audit_trail_references UUID[],
    
    -- Response
    immediate_action_taken TEXT,
    corrective_actions JSONB,
    preventive_actions JSONB,
    
    -- Resolution
    violation_status VARCHAR(20) NOT NULL DEFAULT 'open', -- open, investigating, remediated, closed
    resolution_date TIMESTAMP WITH TIME ZONE,
    resolution_summary TEXT,
    lessons_learned TEXT,
    
    -- Responsibility
    detected_by UUID,
    assigned_to UUID,
    responsible_party UUID,
    resolved_by UUID,
    
    -- Regulatory Reporting
    requires_regulatory_reporting BOOLEAN DEFAULT FALSE,
    reported_to_regulator BOOLEAN DEFAULT FALSE,
    regulator_reference VARCHAR(100),
    reporting_date DATE,
    regulator_response TEXT,
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_notes TEXT,
    
    -- Audit
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_compliance_violations_number ON compliance_violations(violation_number);
CREATE INDEX idx_compliance_violations_rule ON compliance_violations(rule_id);
CREATE INDEX idx_compliance_violations_type ON compliance_violations(violation_type);
CREATE INDEX idx_compliance_violations_severity ON compliance_violations(severity_level);
CREATE INDEX idx_compliance_violations_status ON compliance_violations(violation_status);
CREATE INDEX idx_compliance_violations_date ON compliance_violations(violation_date DESC);
CREATE INDEX idx_compliance_violations_entity ON compliance_violations(entity_type, entity_id);
CREATE INDEX idx_compliance_violations_assigned ON compliance_violations(assigned_to);
CREATE INDEX idx_compliance_violations_regulatory ON compliance_violations(requires_regulatory_reporting) 
    WHERE requires_regulatory_reporting = TRUE;
CREATE INDEX idx_compliance_violations_follow_up ON compliance_violations(follow_up_date) 
    WHERE follow_up_required = TRUE AND violation_status != 'closed';


-- ============================================================================
-- TABLE: audit_schedules
-- Description: Schedule and manage periodic audits
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Schedule Information
    schedule_name VARCHAR(200) NOT NULL,
    schedule_code VARCHAR(50) UNIQUE NOT NULL,
    audit_type VARCHAR(50) NOT NULL, -- internal, external, regulatory, compliance
    audit_category VARCHAR(50) NOT NULL, -- financial, operational, IT, security
    
    -- Scope
    audit_scope TEXT NOT NULL,
    audit_objectives TEXT,
    areas_to_audit TEXT[],
    processes_to_review TEXT[],
    
    -- Frequency
    frequency_type VARCHAR(50) NOT NULL, -- one_time, daily, weekly, monthly, quarterly, annual
    frequency_value INTEGER,
    frequency_unit VARCHAR(20),
    
    -- Scheduling
    start_date DATE NOT NULL,
    end_date DATE,
    next_audit_date DATE,
    last_audit_date DATE,
    
    -- Resources
    lead_auditor UUID,
    audit_team UUID[],
    estimated_duration_days INTEGER,
    budget_amount DECIMAL(15,2),
    
    -- Notifications
    notification_before_days INTEGER DEFAULT 7,
    notify_users UUID[],
    
    -- Status
    schedule_status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, paused, completed, cancelled
    is_mandatory BOOLEAN DEFAULT FALSE,
    
    -- Audit
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_schedules_code ON audit_schedules(schedule_code);
CREATE INDEX idx_audit_schedules_type ON audit_schedules(audit_type);
CREATE INDEX idx_audit_schedules_category ON audit_schedules(audit_category);
CREATE INDEX idx_audit_schedules_status ON audit_schedules(schedule_status);
CREATE INDEX idx_audit_schedules_next_date ON audit_schedules(next_audit_date) 
    WHERE schedule_status = 'active';
CREATE INDEX idx_audit_schedules_lead ON audit_schedules(lead_auditor);

-- ============================================================================
-- TABLE: audit_executions
-- Description: Track actual audit execution and findings
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Execution Information
    execution_number VARCHAR(50) UNIQUE NOT NULL,
    schedule_id UUID REFERENCES audit_schedules(schedule_id),
    audit_type VARCHAR(50) NOT NULL,
    audit_name VARCHAR(200) NOT NULL,
    
    -- Planning
    planned_start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,
    
    -- Scope
    audit_scope TEXT NOT NULL,
    audit_criteria TEXT,
    sampling_method VARCHAR(100),
    sample_size INTEGER,
    
    -- Team
    lead_auditor UUID NOT NULL,
    audit_team_members UUID[],
    external_auditors JSONB,
    
    -- Execution
    execution_status VARCHAR(20) NOT NULL DEFAULT 'planned', 
    -- planned, in_progress, fieldwork_complete, reporting, completed, cancelled
    completion_percentage INTEGER DEFAULT 0,
    
    -- Findings Summary
    total_findings INTEGER DEFAULT 0,
    critical_findings INTEGER DEFAULT 0,
    high_findings INTEGER DEFAULT 0,
    medium_findings INTEGER DEFAULT 0,
    low_findings INTEGER DEFAULT 0,
    
    -- Results
    overall_rating VARCHAR(20), -- excellent, satisfactory, needs_improvement, unsatisfactory
    key_observations TEXT,
    strengths_identified TEXT,
    areas_for_improvement TEXT,
    
    -- Reports
    draft_report_date DATE,
    final_report_date DATE,
    report_file_path VARCHAR(500),
    executive_summary TEXT,
    
    -- Follow-up
    requires_follow_up BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    follow_up_completed BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    methodology_used VARCHAR(100),
    standards_followed TEXT[],
    tools_used TEXT[],
    evidence_collected JSONB,
    
    -- Audit
    created_by UUID NOT NULL,
    updated_by UUID,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_executions_number ON audit_executions(execution_number);
CREATE INDEX idx_audit_executions_schedule ON audit_executions(schedule_id);
CREATE INDEX idx_audit_executions_type ON audit_executions(audit_type);
CREATE INDEX idx_audit_executions_status ON audit_executions(execution_status);
CREATE INDEX idx_audit_executions_lead ON audit_executions(lead_auditor);
CREATE INDEX idx_audit_executions_start_date ON audit_executions(planned_start_date DESC);
CREATE INDEX idx_audit_executions_rating ON audit_executions(overall_rating);
CREATE INDEX idx_audit_executions_follow_up ON audit_executions(follow_up_date) 
    WHERE requires_follow_up = TRUE AND follow_up_completed = FALSE;


-- ============================================================================
-- TABLE: audit_findings
-- Description: Track individual audit findings and observations
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_findings (
    finding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Finding Information
    finding_number VARCHAR(50) UNIQUE NOT NULL,
    execution_id UUID NOT NULL REFERENCES audit_executions(execution_id),
    
    -- Classification
    finding_type VARCHAR(50) NOT NULL, -- control_weakness, non_compliance, inefficiency, best_practice
    finding_category VARCHAR(50) NOT NULL, -- financial, operational, IT, security, compliance
    severity_level VARCHAR(20) NOT NULL, -- critical, high, medium, low
    risk_level VARCHAR(20) NOT NULL, -- critical, high, medium, low
    
    -- Details
    finding_title VARCHAR(500) NOT NULL,
    finding_description TEXT NOT NULL,
    condition_observed TEXT NOT NULL,
    criteria_reference TEXT,
    cause_analysis TEXT,
    effect_impact TEXT,
    
    -- Impact Assessment
    financial_impact DECIMAL(15,2),
    operational_impact TEXT,
    reputational_impact TEXT,
    compliance_impact TEXT,
    
    -- Recommendation
    recommendation TEXT NOT NULL,
    management_response TEXT,
    agreed_action_plan TEXT,
    
    -- Responsible Parties
    process_owner UUID,
    responsible_person UUID,
    remediation_owner UUID,
    
    -- Timeline
    target_completion_date DATE,
    actual_completion_date DATE,
    extended_deadline DATE,
    extension_reason TEXT,
    
    -- Status
    finding_status VARCHAR(20) NOT NULL DEFAULT 'open', 
    -- open, acknowledged, in_progress, resolved, verified, closed, risk_accepted
    
    -- Resolution
    resolution_description TEXT,
    resolution_evidence JSONB,
    verified_by UUID,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_notes TEXT,
    
    -- Recurrence
    is_repeat_finding BOOLEAN DEFAULT FALSE,
    previous_finding_id UUID,
    recurrence_count INTEGER DEFAULT 0,
    
    -- Evidence
    evidence_documents JSONB,
    screenshots JSONB,
    supporting_data JSONB,
    
    -- Follow-up
    follow_up_required BOOLEAN DEFAULT TRUE,
    follow_up_date DATE,
    follow_up_notes TEXT,
    
    -- Audit
    identified_by UUID NOT NULL,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_findings_number ON audit_findings(finding_number);
CREATE INDEX idx_audit_findings_execution ON audit_findings(execution_id);
CREATE INDEX idx_audit_findings_type ON audit_findings(finding_type);
CREATE INDEX idx_audit_findings_severity ON audit_findings(severity_level);
CREATE INDEX idx_audit_findings_risk ON audit_findings(risk_level);
CREATE INDEX idx_audit_findings_status ON audit_findings(finding_status);
CREATE INDEX idx_audit_findings_responsible ON audit_findings(responsible_person);
CREATE INDEX idx_audit_findings_target_date ON audit_findings(target_completion_date);
CREATE INDEX idx_audit_findings_follow_up ON audit_findings(follow_up_date) 
    WHERE follow_up_required = TRUE AND finding_status NOT IN ('closed', 'verified');
CREATE INDEX idx_audit_findings_repeat ON audit_findings(is_repeat_finding) 
    WHERE is_repeat_finding = TRUE;

-- ============================================================================
-- TABLE: regulatory_reports
-- Description: Track regulatory reporting submissions
-- ============================================================================
CREATE TABLE IF NOT EXISTS regulatory_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Report Information
    report_number VARCHAR(50) UNIQUE NOT NULL,
    report_name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL, -- periodic, ad_hoc, incident, compliance
    report_category VARCHAR(50) NOT NULL, -- prudential, statistical, supervisory
    
    -- Regulatory Details
    regulatory_body VARCHAR(200) NOT NULL,
    regulation_reference VARCHAR(100),
    report_template_code VARCHAR(50),
    
    -- Reporting Period
    reporting_frequency VARCHAR(50), -- daily, weekly, monthly, quarterly, annual
    reporting_period_from DATE NOT NULL,
    reporting_period_to DATE NOT NULL,
    
    -- Submission
    due_date DATE NOT NULL,
    submission_date DATE,
    submission_method VARCHAR(50), -- online_portal, email, physical, API
    submission_reference VARCHAR(100),
    
    -- Content
    report_data JSONB NOT NULL,
    calculated_metrics JSONB,
    supporting_schedules JSONB,
    explanatory_notes TEXT,
    
    -- Files
    report_file_path VARCHAR(500),
    report_format VARCHAR(20), -- PDF, Excel, XML, JSON
    file_size_kb INTEGER,
    file_hash VARCHAR(128),
    
    -- Status
    report_status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- draft, under_review, approved, submitted, acknowledged, rejected
    
    -- Workflow
    prepared_by UUID NOT NULL,
    reviewed_by UUID,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    submitted_by UUID,
    
    -- Response
    acknowledgement_received BOOLEAN DEFAULT FALSE,
    acknowledgement_date DATE,
    acknowledgement_reference VARCHAR(100),
    regulator_feedback TEXT,
    
    -- Revisions
    is_revised BOOLEAN DEFAULT FALSE,
    revision_number INTEGER DEFAULT 1,
    revision_reason TEXT,
    original_report_id UUID,
    
    -- Alerts
    is_overdue BOOLEAN DEFAULT FALSE,
    reminder_sent BOOLEAN DEFAULT FALSE,
    escalation_level INTEGER DEFAULT 0,
    
    -- Audit
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_regulatory_reports_number ON regulatory_reports(report_number);
CREATE INDEX idx_regulatory_reports_type ON regulatory_reports(report_type);
CREATE INDEX idx_regulatory_reports_body ON regulatory_reports(regulatory_body);
CREATE INDEX idx_regulatory_reports_status ON regulatory_reports(report_status);
CREATE INDEX idx_regulatory_reports_due_date ON regulatory_reports(due_date);
CREATE INDEX idx_regulatory_reports_period ON regulatory_reports(reporting_period_from, reporting_period_to);
CREATE INDEX idx_regulatory_reports_overdue ON regulatory_reports(is_overdue) 
    WHERE is_overdue = TRUE;
CREATE INDEX idx_regulatory_reports_prepared ON regulatory_reports(prepared_by);


-- ============================================================================
-- TABLE: compliance_certifications
-- Description: Track compliance certifications and attestations
-- ============================================================================
CREATE TABLE IF NOT EXISTS compliance_certifications (
    certification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Certification Information
    certification_number VARCHAR(50) UNIQUE NOT NULL,
    certification_name VARCHAR(200) NOT NULL,
    certification_type VARCHAR(50) NOT NULL, -- self_certification, third_party, regulatory
    certification_category VARCHAR(50) NOT NULL, -- ISO, SOC, PCI_DSS, GDPR, etc.
    
    -- Standards
    standard_name VARCHAR(200) NOT NULL,
    standard_version VARCHAR(50),
    standard_body VARCHAR(200),
    
    -- Scope
    certification_scope TEXT NOT NULL,
    covered_processes TEXT[],
    covered_systems TEXT[],
    covered_locations TEXT[],
    
    -- Validity
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    renewal_date DATE,
    
    -- Assessment
    assessment_body VARCHAR(200),
    assessor_name VARCHAR(200),
    assessment_date_from DATE,
    assessment_date_to DATE,
    
    -- Results
    certification_status VARCHAR(20) NOT NULL DEFAULT 'active',
    -- active, expired, suspended, withdrawn, under_review
    assessment_result VARCHAR(50), -- passed, passed_with_conditions, failed
    conditions_or_observations TEXT,
    
    -- Documentation
    certificate_file_path VARCHAR(500),
    certificate_number VARCHAR(100),
    assessment_report_path VARCHAR(500),
    supporting_documents JSONB,
    
    -- Maintenance
    surveillance_audits JSONB,
    last_surveillance_date DATE,
    next_surveillance_date DATE,
    
    -- Compliance
    compliance_requirements JSONB,
    gaps_identified JSONB,
    remediation_plan TEXT,
    
    -- Notifications
    renewal_reminder_days INTEGER DEFAULT 90,
    notify_users UUID[],
    
    -- Costs
    certification_cost DECIMAL(15,2),
    annual_maintenance_cost DECIMAL(15,2),
    
    -- Audit
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_compliance_certifications_number ON compliance_certifications(certification_number);
CREATE INDEX idx_compliance_certifications_type ON compliance_certifications(certification_type);
CREATE INDEX idx_compliance_certifications_status ON compliance_certifications(certification_status);
CREATE INDEX idx_compliance_certifications_expiry ON compliance_certifications(expiry_date);
CREATE INDEX idx_compliance_certifications_standard ON compliance_certifications(standard_name);

-- ============================================================================
-- TABLE: policy_acknowledgements
-- Description: Track policy and procedure acknowledgements by users
-- ============================================================================
CREATE TABLE IF NOT EXISTS policy_acknowledgements (
    acknowledgement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Policy Information
    policy_id UUID NOT NULL,
    policy_name VARCHAR(200) NOT NULL,
    policy_version VARCHAR(20) NOT NULL,
    policy_type VARCHAR(50) NOT NULL, -- policy, procedure, guideline, standard
    
    -- User Information
    user_id UUID NOT NULL,
    user_name VARCHAR(200) NOT NULL,
    user_role VARCHAR(100),
    user_department VARCHAR(100),
    
    -- Acknowledgement
    acknowledgement_date TIMESTAMP WITH TIME ZONE NOT NULL,
    acknowledgement_method VARCHAR(50), -- digital_signature, checkbox, biometric
    acknowledgement_ip_address INET,
    acknowledgement_device VARCHAR(200),
    
    -- Understanding
    understanding_confirmed BOOLEAN NOT NULL,
    quiz_taken BOOLEAN DEFAULT FALSE,
    quiz_score DECIMAL(5,2),
    quiz_passed BOOLEAN,
    
    -- Compliance
    compliance_status VARCHAR(20) NOT NULL DEFAULT 'acknowledged',
    -- acknowledged, compliant, non_compliant, expired
    
    -- Training
    training_completed BOOLEAN DEFAULT FALSE,
    training_date DATE,
    training_certificate_id UUID,
    
    -- Validity
    valid_from DATE NOT NULL,
    valid_until DATE,
    requires_renewal BOOLEAN DEFAULT TRUE,
    renewal_frequency_days INTEGER,
    
    -- Reminders
    reminder_sent BOOLEAN DEFAULT FALSE,
    reminder_date DATE,
    escalation_sent BOOLEAN DEFAULT FALSE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policy_acknowledgements_policy ON policy_acknowledgements(policy_id);
CREATE INDEX idx_policy_acknowledgements_user ON policy_acknowledgements(user_id);
CREATE INDEX idx_policy_acknowledgements_date ON policy_acknowledgements(acknowledgement_date DESC);
CREATE INDEX idx_policy_acknowledgements_status ON policy_acknowledgements(compliance_status);
CREATE INDEX idx_policy_acknowledgements_valid ON policy_acknowledgements(valid_until) 
    WHERE compliance_status = 'acknowledged';
CREATE INDEX idx_policy_acknowledgements_user_policy ON policy_acknowledgements(user_id, policy_id);


-- ============================================================================
-- TABLE: data_retention_logs
-- Description: Track data retention and deletion activities
-- ============================================================================
CREATE TABLE IF NOT EXISTS data_retention_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Retention Information
    log_number VARCHAR(50) UNIQUE NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    entity_reference VARCHAR(200),
    
    -- Action Details
    action_type VARCHAR(50) NOT NULL, -- archive, delete, anonymize, retain
    action_reason VARCHAR(100) NOT NULL, -- policy_expiry, legal_requirement, user_request
    retention_policy_id UUID,
    
    -- Data Details
    data_category VARCHAR(100) NOT NULL,
    data_classification VARCHAR(50), -- public, internal, confidential, restricted
    record_count INTEGER,
    data_size_mb DECIMAL(15,2),
    
    -- Timing
    original_creation_date DATE,
    retention_period_days INTEGER,
    retention_expiry_date DATE,
    action_date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Legal & Compliance
    legal_hold_applied BOOLEAN DEFAULT FALSE,
    legal_hold_id UUID,
    compliance_requirement TEXT,
    regulatory_reference VARCHAR(200),
    
    -- Verification
    verification_required BOOLEAN DEFAULT TRUE,
    verified_by UUID,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_method VARCHAR(100),
    
    -- Recovery
    is_recoverable BOOLEAN DEFAULT FALSE,
    recovery_window_days INTEGER,
    recovery_location VARCHAR(500),
    
    -- Audit Trail
    data_hash VARCHAR(128),
    deletion_certificate_id UUID,
    evidence_file_path VARCHAR(500),
    
    -- Metadata
    affected_systems TEXT[],
    backup_status VARCHAR(50),
    related_entities JSONB,
    
    -- Status
    action_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- pending, in_progress, completed, failed, rolled_back
    error_message TEXT,
    
    -- Audit
    initiated_by UUID NOT NULL,
    approved_by UUID,
    executed_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_data_retention_logs_number ON data_retention_logs(log_number);
CREATE INDEX idx_data_retention_logs_entity_type ON data_retention_logs(entity_type);
CREATE INDEX idx_data_retention_logs_entity_id ON data_retention_logs(entity_id);
CREATE INDEX idx_data_retention_logs_action_type ON data_retention_logs(action_type);
CREATE INDEX idx_data_retention_logs_action_date ON data_retention_logs(action_date DESC);
CREATE INDEX idx_data_retention_logs_status ON data_retention_logs(action_status);
CREATE INDEX idx_data_retention_logs_legal_hold ON data_retention_logs(legal_hold_applied) 
    WHERE legal_hold_applied = TRUE;
CREATE INDEX idx_data_retention_logs_retention_expiry ON data_retention_logs(retention_expiry_date);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: v_audit_trail_summary
CREATE OR REPLACE VIEW v_audit_trail_summary AS
SELECT 
    DATE(event_timestamp) as audit_date,
    event_category,
    entity_type,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) FILTER (WHERE action_status = 'success') as successful_events,
    COUNT(*) FILTER (WHERE action_status = 'failed') as failed_events,
    COUNT(*) FILTER (WHERE security_flag = TRUE) as security_events,
    COUNT(*) FILTER (WHERE compliance_flag = TRUE) as compliance_events,
    COUNT(*) FILTER (WHERE fraud_flag = TRUE) as fraud_events
FROM audit_trails
WHERE event_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(event_timestamp), event_category, entity_type
ORDER BY audit_date DESC, total_events DESC;

-- View: v_active_audit_findings
CREATE OR REPLACE VIEW v_active_audit_findings AS
SELECT 
    f.finding_id,
    f.finding_number,
    f.finding_title,
    f.severity_level,
    f.risk_level,
    f.finding_status,
    f.target_completion_date,
    f.responsible_person,
    e.execution_number,
    e.audit_name,
    e.audit_type,
    CASE 
        WHEN f.target_completion_date < CURRENT_DATE THEN 'overdue'
        WHEN f.target_completion_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'due_soon'
        ELSE 'on_track'
    END as deadline_status,
    CURRENT_DATE - f.target_completion_date as days_overdue
FROM audit_findings f
JOIN audit_executions e ON f.execution_id = e.execution_id
WHERE f.finding_status NOT IN ('closed', 'verified')
ORDER BY f.severity_level, f.target_completion_date;

-- View: v_compliance_violations_summary
CREATE OR REPLACE VIEW v_compliance_violations_summary AS
SELECT 
    r.rule_category,
    r.rule_name,
    COUNT(v.violation_id) as total_violations,
    COUNT(*) FILTER (WHERE v.severity_level = 'critical') as critical_violations,
    COUNT(*) FILTER (WHERE v.severity_level = 'high') as high_violations,
    COUNT(*) FILTER (WHERE v.violation_status = 'open') as open_violations,
    SUM(v.financial_impact) as total_financial_impact,
    COUNT(*) FILTER (WHERE v.requires_regulatory_reporting = TRUE) as regulatory_reportable,
    MAX(v.violation_date) as last_violation_date
FROM compliance_violations v
JOIN compliance_rules r ON v.rule_id = r.rule_id
WHERE v.violation_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY r.rule_category, r.rule_name
ORDER BY total_violations DESC;

-- View: v_regulatory_reporting_calendar
CREATE OR REPLACE VIEW v_regulatory_reporting_calendar AS
SELECT 
    report_id,
    report_number,
    report_name,
    regulatory_body,
    reporting_frequency,
    due_date,
    report_status,
    CASE 
        WHEN due_date < CURRENT_DATE AND report_status NOT IN ('submitted', 'acknowledged') THEN 'overdue'
        WHEN due_date <= CURRENT_DATE + INTERVAL '7 days' THEN 'due_soon'
        ELSE 'upcoming'
    END as urgency_status,
    CURRENT_DATE - due_date as days_overdue,
    prepared_by,
    approved_by
FROM regulatory_reports
WHERE due_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY due_date, regulatory_body;


-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_audit_trails_updated_at
    BEFORE UPDATE ON audit_trails
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_compliance_rules_updated_at
    BEFORE UPDATE ON compliance_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_compliance_violations_updated_at
    BEFORE UPDATE ON compliance_violations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_audit_schedules_updated_at
    BEFORE UPDATE ON audit_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_audit_executions_updated_at
    BEFORE UPDATE ON audit_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_audit_findings_updated_at
    BEFORE UPDATE ON audit_findings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_regulatory_reports_updated_at
    BEFORE UPDATE ON regulatory_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_compliance_certifications_updated_at
    BEFORE UPDATE ON compliance_certifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_policy_acknowledgements_updated_at
    BEFORE UPDATE ON policy_acknowledgements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Auto-generate audit trail number
CREATE OR REPLACE FUNCTION generate_audit_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.finding_number IS NULL THEN
        NEW.finding_number := 'AUD-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                             LPAD(NEXTVAL('audit_finding_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE IF NOT EXISTS audit_finding_seq START 1;

CREATE TRIGGER trigger_generate_finding_number
    BEFORE INSERT ON audit_findings
    FOR EACH ROW
    WHEN (NEW.finding_number IS NULL)
    EXECUTE FUNCTION generate_audit_number();

-- Trigger: Auto-generate violation number
CREATE OR REPLACE FUNCTION generate_violation_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.violation_number IS NULL THEN
        NEW.violation_number := 'VIO-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || 
                               LPAD(NEXTVAL('violation_seq')::TEXT, 6, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE IF NOT EXISTS violation_seq START 1;

CREATE TRIGGER trigger_generate_violation_number
    BEFORE INSERT ON compliance_violations
    FOR EACH ROW
    WHEN (NEW.violation_number IS NULL)
    EXECUTE FUNCTION generate_violation_number();

-- Trigger: Update audit execution completion percentage
CREATE OR REPLACE FUNCTION update_execution_completion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.finding_status IN ('closed', 'verified') THEN
        UPDATE audit_executions
        SET completion_percentage = (
            SELECT COALESCE(
                (COUNT(*) FILTER (WHERE finding_status IN ('closed', 'verified'))::DECIMAL / 
                 NULLIF(COUNT(*), 0) * 100), 0
            )
            FROM audit_findings
            WHERE execution_id = NEW.execution_id
        )
        WHERE execution_id = NEW.execution_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_execution_completion
    AFTER UPDATE ON audit_findings
    FOR EACH ROW
    WHEN (OLD.finding_status IS DISTINCT FROM NEW.finding_status)
    EXECUTE FUNCTION update_execution_completion();

-- Trigger: Update audit execution findings summary
CREATE OR REPLACE FUNCTION update_execution_findings_summary()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE audit_executions
    SET 
        total_findings = (SELECT COUNT(*) FROM audit_findings WHERE execution_id = NEW.execution_id),
        critical_findings = (SELECT COUNT(*) FROM audit_findings WHERE execution_id = NEW.execution_id AND severity_level = 'critical'),
        high_findings = (SELECT COUNT(*) FROM audit_findings WHERE execution_id = NEW.execution_id AND severity_level = 'high'),
        medium_findings = (SELECT COUNT(*) FROM audit_findings WHERE execution_id = NEW.execution_id AND severity_level = 'medium'),
        low_findings = (SELECT COUNT(*) FROM audit_findings WHERE execution_id = NEW.execution_id AND severity_level = 'low')
    WHERE execution_id = NEW.execution_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_findings_summary
    AFTER INSERT OR UPDATE ON audit_findings
    FOR EACH ROW
    EXECUTE FUNCTION update_execution_findings_summary();

-- Trigger: Check regulatory report overdue status
CREATE OR REPLACE FUNCTION check_report_overdue()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.due_date < CURRENT_DATE AND NEW.report_status NOT IN ('submitted', 'acknowledged') THEN
        NEW.is_overdue := TRUE;
    ELSE
        NEW.is_overdue := FALSE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_report_overdue
    BEFORE INSERT OR UPDATE ON regulatory_reports
    FOR EACH ROW
    EXECUTE FUNCTION check_report_overdue();


-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Insert sample compliance rules
INSERT INTO compliance_rules (
    rule_code, rule_name, rule_category, regulation_name, regulatory_body,
    rule_description, rule_type, severity_level, applicable_entities,
    validation_method, validation_frequency, on_breach_action,
    is_active, effective_from, created_by
) VALUES
(
    'KYC-001', 'Customer KYC Verification', 'regulatory', 'AML/KYC Guidelines', 
    'Reserve Bank of India',
    'All customers must complete KYC verification before loan disbursement',
    'mandatory', 'critical', ARRAY['customer', 'loan'],
    'automated', 'real_time', 'block',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
),
(
    'LTV-001', 'Loan to Value Ratio Limit', 'internal_policy', 'Lending Policy', 
    'Internal Risk Committee',
    'LTV ratio must not exceed 75% for gold loans',
    'mandatory', 'high', ARRAY['loan', 'appraisal'],
    'automated', 'real_time', 'alert',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
),
(
    'DOC-001', 'Document Retention Period', 'regulatory', 'Record Keeping Standards', 
    'Financial Regulator',
    'Loan documents must be retained for minimum 7 years',
    'mandatory', 'high', ARRAY['document', 'loan'],
    'automated', 'monthly', 'log',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
),
(
    'AUD-001', 'Regular Audit Requirement', 'regulatory', 'Audit Standards', 
    'Statutory Auditor',
    'Annual external audit of all financial operations',
    'mandatory', 'critical', ARRAY['audit', 'financial'],
    'manual', 'annual', 'escalate',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
),
(
    'DAT-001', 'Data Privacy Compliance', 'regulatory', 'Data Protection Act', 
    'Data Protection Authority',
    'Customer data must be encrypted and access-controlled',
    'mandatory', 'critical', ARRAY['customer', 'data'],
    'automated', 'real_time', 'block',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
),
(
    'COL-001', 'Collection Practice Standards', 'regulatory', 'Fair Practices Code', 
    'Banking Ombudsman',
    'Collection practices must adhere to fair practices code',
    'mandatory', 'high', ARRAY['collection', 'customer'],
    'manual', 'weekly', 'alert',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
),
(
    'INT-001', 'Interest Rate Disclosure', 'regulatory', 'Consumer Protection Act', 
    'Consumer Forum',
    'All interest rates and charges must be disclosed to customers',
    'mandatory', 'high', ARRAY['loan', 'customer'],
    'automated', 'real_time', 'block',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
),
(
    'SEC-001', 'Security Access Controls', 'internal_policy', 'Information Security Policy', 
    'IT Security Team',
    'Role-based access control must be implemented for all systems',
    'mandatory', 'critical', ARRAY['access', 'security'],
    'automated', 'real_time', 'block',
    TRUE, '2024-01-01', '00000000-0000-0000-0000-000000000000'
);

-- Insert sample audit schedules
INSERT INTO audit_schedules (
    schedule_name, schedule_code, audit_type, audit_category,
    audit_scope, frequency_type, start_date, next_audit_date,
    estimated_duration_days, schedule_status, is_mandatory, created_by
) VALUES
(
    'Annual Financial Audit', 'AUD-SCH-001', 'external', 'financial',
    'Complete financial statements and accounting records review',
    'annual', '2024-01-01', '2025-01-01', 30, 'active', TRUE,
    '00000000-0000-0000-0000-000000000000'
),
(
    'Quarterly Operational Audit', 'AUD-SCH-002', 'internal', 'operational',
    'Review operational processes and controls',
    'quarterly', '2024-01-01', '2025-01-01', 10, 'active', TRUE,
    '00000000-0000-0000-0000-000000000000'
),
(
    'IT Security Audit', 'AUD-SCH-003', 'internal', 'IT',
    'Assessment of IT security controls and data protection',
    'quarterly', '2024-01-01', '2025-01-01', 15, 'active', TRUE,
    '00000000-0000-0000-0000-000000000000'
),
(
    'Compliance Audit', 'AUD-SCH-004', 'internal', 'compliance',
    'Review compliance with regulatory requirements',
    'quarterly', '2024-01-01', '2025-01-01', 7, 'active', TRUE,
    '00000000-0000-0000-0000-000000000000'
),
(
    'Vault Physical Verification', 'AUD-SCH-005', 'internal', 'operational',
    'Physical verification of gold ornaments in vault',
    'monthly', '2024-01-01', '2025-01-01', 2, 'active', TRUE,
    '00000000-0000-0000-0000-000000000000'
);

-- Insert sample compliance certifications
INSERT INTO compliance_certifications (
    certification_number, certification_name, certification_type, certification_category,
    standard_name, standard_version, certification_scope,
    issue_date, expiry_date, certification_status, created_by
) VALUES
(
    'CERT-ISO-001', 'ISO 27001 Certification', 'third_party', 'ISO',
    'ISO/IEC 27001:2013', '2013', 
    'Information Security Management System covering all IT operations',
    '2024-01-01', '2027-01-01', 'active',
    '00000000-0000-0000-0000-000000000000'
),
(
    'CERT-SOC-001', 'SOC 2 Type II', 'third_party', 'SOC',
    'SOC 2 Type II', '2023', 
    'Security, availability, and confidentiality of customer data',
    '2024-06-01', '2025-06-01', 'active',
    '00000000-0000-0000-0000-000000000000'
),
(
    'CERT-PCI-001', 'PCI DSS Compliance', 'third_party', 'PCI_DSS',
    'PCI DSS v4.0', '4.0', 
    'Payment card data security across all systems',
    '2024-03-01', '2025-03-01', 'active',
    '00000000-0000-0000-0000-000000000000'
);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE audit_trails IS 'Universal audit trail for all system activities';
COMMENT ON TABLE compliance_rules IS 'Compliance rules and regulatory requirements';
COMMENT ON TABLE compliance_violations IS 'Compliance rule violations and breaches';
COMMENT ON TABLE audit_schedules IS 'Scheduled audit plans and calendars';
COMMENT ON TABLE audit_executions IS 'Actual audit execution records';
COMMENT ON TABLE audit_findings IS 'Individual audit findings and observations';
COMMENT ON TABLE regulatory_reports IS 'Regulatory reporting submissions';
COMMENT ON TABLE compliance_certifications IS 'Compliance certifications and attestations';
COMMENT ON TABLE policy_acknowledgements IS 'Policy and procedure acknowledgements';
COMMENT ON TABLE data_retention_logs IS 'Data retention and deletion activity logs';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
