-- =====================================================
-- Phase 15: Platform Administration
-- Migration: 032_platform_admin.sql
-- Description: System administration and configuration
-- =====================================================

-- =====================================================
-- TABLE: system_settings
-- Description: Platform configuration settings
-- =====================================================
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(50) NOT NULL, -- 'STRING', 'INTEGER', 'BOOLEAN', 'JSON', 'ENCRYPTED'
    category VARCHAR(50) NOT NULL, -- 'GENERAL', 'SECURITY', 'INTEGRATION', 'NOTIFICATIONS', 'FEATURES'
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    is_editable BOOLEAN DEFAULT TRUE,
    requires_restart BOOLEAN DEFAULT FALSE,
    validation_rules JSONB,
    default_value TEXT,
    
    -- Audit
    last_modified_by UUID REFERENCES users(id),
    last_modified_at TIMESTAMPTZ,
    change_history JSONB DEFAULT '[]',
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: roles
-- Description: User roles and permissions
-- =====================================================
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_code VARCHAR(50) UNIQUE NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    description TEXT,
    role_type VARCHAR(50) NOT NULL, -- 'SYSTEM', 'CUSTOM', 'TEMPORARY'
    is_system_role BOOLEAN DEFAULT FALSE,
    
    -- Permissions
    permissions JSONB DEFAULT '[]', -- Array of permission objects
    resource_access JSONB DEFAULT '{}', -- Resource-level access control
    
    -- Hierarchy
    parent_role_id UUID REFERENCES roles(id),
    hierarchy_level INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    
    -- Limits
    max_users INTEGER,
    current_user_count INTEGER DEFAULT 0,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

-- =====================================================
-- TABLE: user_roles
-- Description: User-role assignments
-- =====================================================
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    
    -- Assignment details
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    
    -- Scope
    scope_type VARCHAR(50), -- 'GLOBAL', 'BRANCH', 'DEPARTMENT', 'PROJECT'
    scope_value VARCHAR(100),
    
    -- Metadata
    assignment_reason TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, role_id, scope_type, scope_value)
);

-- =====================================================
-- TABLE: permissions
-- Description: System permissions catalog
-- =====================================================
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    permission_code VARCHAR(100) UNIQUE NOT NULL,
    permission_name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Categorization
    module VARCHAR(50) NOT NULL, -- 'PRODUCTS', 'LOANS', 'VAULT', 'REPORTS', etc.
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'CREATE', 'READ', 'UPDATE', 'DELETE', 'EXECUTE'
    
    -- Permission type
    permission_type VARCHAR(50) DEFAULT 'STANDARD', -- 'STANDARD', 'ADMIN', 'SYSTEM', 'CUSTOM'
    risk_level VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    
    -- Requirements
    requires_approval BOOLEAN DEFAULT FALSE,
    requires_mfa BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: audit_logs
-- Description: Comprehensive audit trail
-- =====================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL, -- 'USER_ACTION', 'SYSTEM_EVENT', 'SECURITY', 'DATA_CHANGE'
    event_name VARCHAR(200) NOT NULL,
    event_description TEXT,
    
    -- User context
    user_id UUID REFERENCES users(id),
    username VARCHAR(100),
    user_ip_address VARCHAR(50),
    user_agent TEXT,
    
    -- Resource details
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    resource_name VARCHAR(200),
    
    -- Action details
    action VARCHAR(50) NOT NULL,
    action_result VARCHAR(20) NOT NULL, -- 'SUCCESS', 'FAILURE', 'PARTIAL'
    
    -- Data changes
    old_values JSONB,
    new_values JSONB,
    changes JSONB,
    
    -- Request details
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    transaction_id VARCHAR(100),
    
    -- System context
    application_name VARCHAR(100),
    module_name VARCHAR(100),
    service_name VARCHAR(100),
    
    -- Location
    branch_id VARCHAR(50),
    department VARCHAR(100),
    
    -- Security
    security_level VARCHAR(20), -- 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
    requires_review BOOLEAN DEFAULT FALSE,
    is_sensitive BOOLEAN DEFAULT FALSE,
    
    -- Error details
    error_message TEXT,
    error_code VARCHAR(50),
    stack_trace TEXT,
    
    -- Performance
    duration_ms INTEGER,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for common queries
    INDEX idx_audit_logs_user (user_id, created_at DESC),
    INDEX idx_audit_logs_resource (resource_type, resource_id),
    INDEX idx_audit_logs_event (event_type, created_at DESC),
    INDEX idx_audit_logs_created (created_at DESC)
);

-- =====================================================
-- TABLE: system_health
-- Description: System health monitoring
-- =====================================================
CREATE TABLE IF NOT EXISTS system_health (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_code VARCHAR(50) UNIQUE NOT NULL,
    
    -- Check details
    check_name VARCHAR(200) NOT NULL,
    check_type VARCHAR(50) NOT NULL, -- 'SERVICE', 'DATABASE', 'INTEGRATION', 'RESOURCE', 'CUSTOM'
    component_name VARCHAR(100) NOT NULL,
    
    -- Health status
    health_status VARCHAR(20) NOT NULL, -- 'HEALTHY', 'DEGRADED', 'UNHEALTHY', 'UNKNOWN'
    previous_status VARCHAR(20),
    status_changed_at TIMESTAMPTZ,
    
    -- Metrics
    response_time_ms INTEGER,
    availability_percent NUMERIC(5,2),
    error_rate_percent NUMERIC(5,2),
    success_rate_percent NUMERIC(5,2),
    
    -- Thresholds
    warning_threshold JSONB,
    critical_threshold JSONB,
    
    -- Check execution
    last_check_at TIMESTAMPTZ NOT NULL,
    next_check_at TIMESTAMPTZ,
    check_frequency_minutes INTEGER DEFAULT 5,
    
    -- Results
    check_result JSONB,
    check_message TEXT,
    check_details JSONB,
    
    -- Error tracking
    consecutive_failures INTEGER DEFAULT 0,
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    
    -- Alert configuration
    alert_enabled BOOLEAN DEFAULT TRUE,
    alert_channels JSONB DEFAULT '[]',
    alert_recipients JSONB DEFAULT '[]',
    
    -- Status
    is_enabled BOOLEAN DEFAULT TRUE,
    is_critical BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: system_metrics
-- Description: System performance metrics
-- =====================================================
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Metric identity
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'COUNTER', 'GAUGE', 'HISTOGRAM', 'SUMMARY'
    metric_category VARCHAR(50) NOT NULL, -- 'PERFORMANCE', 'RESOURCE', 'BUSINESS', 'CUSTOM'
    
    -- Metric value
    metric_value NUMERIC(20,4) NOT NULL,
    metric_unit VARCHAR(50),
    
    -- Dimensions
    service_name VARCHAR(100),
    module_name VARCHAR(100),
    endpoint VARCHAR(200),
    
    -- Labels
    labels JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    
    -- Time details
    recorded_at TIMESTAMPTZ NOT NULL,
    time_bucket VARCHAR(20), -- 'MINUTE', 'HOUR', 'DAY'
    
    -- Aggregation
    is_aggregated BOOLEAN DEFAULT FALSE,
    sample_count INTEGER,
    min_value NUMERIC(20,4),
    max_value NUMERIC(20,4),
    avg_value NUMERIC(20,4),
    sum_value NUMERIC(20,4),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_system_metrics_name_time (metric_name, recorded_at DESC),
    INDEX idx_system_metrics_category (metric_category, recorded_at DESC),
    INDEX idx_system_metrics_service (service_name, recorded_at DESC)
);

-- =====================================================
-- TABLE: notification_templates
-- Description: Notification templates
-- =====================================================
CREATE TABLE IF NOT EXISTS notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_code VARCHAR(50) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Template details
    notification_type VARCHAR(50) NOT NULL, -- 'EMAIL', 'SMS', 'PUSH', 'IN_APP', 'WEBHOOK'
    template_category VARCHAR(50) NOT NULL, -- 'TRANSACTIONAL', 'MARKETING', 'SYSTEM', 'ALERT'
    
    -- Content
    subject_template TEXT,
    body_template TEXT NOT NULL,
    html_template TEXT,
    
    -- Template engine
    template_engine VARCHAR(50) DEFAULT 'JINJA2',
    template_variables JSONB DEFAULT '[]',
    
    -- Localization
    language VARCHAR(10) DEFAULT 'en',
    supports_localization BOOLEAN DEFAULT FALSE,
    
    -- Delivery settings
    priority VARCHAR(20) DEFAULT 'NORMAL', -- 'LOW', 'NORMAL', 'HIGH', 'URGENT'
    retry_policy JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    
    -- Version control
    version VARCHAR(20) DEFAULT '1.0',
    parent_template_id UUID REFERENCES notification_templates(id),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

-- =====================================================
-- TABLE: scheduled_jobs
-- Description: Background job scheduling
-- =====================================================
CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_code VARCHAR(50) UNIQUE NOT NULL,
    job_name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Job details
    job_type VARCHAR(50) NOT NULL, -- 'CRON', 'INTERVAL', 'ONE_TIME', 'TRIGGERED'
    job_category VARCHAR(50) NOT NULL, -- 'MAINTENANCE', 'REPORT', 'SYNC', 'CLEANUP', 'CUSTOM'
    
    -- Execution
    handler_class VARCHAR(200) NOT NULL,
    handler_method VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}',
    
    -- Schedule
    schedule_expression VARCHAR(100), -- Cron expression
    interval_minutes INTEGER,
    scheduled_time TIME,
    
    -- Execution window
    execution_window_start TIME,
    execution_window_end TIME,
    
    -- Status
    is_enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'SCHEDULED',
    
    -- Execution tracking
    last_execution_at TIMESTAMPTZ,
    last_execution_status VARCHAR(20),
    last_execution_duration_ms INTEGER,
    last_execution_error TEXT,
    next_execution_at TIMESTAMPTZ,
    
    -- Statistics
    total_executions INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms INTEGER,
    
    -- Retry policy
    max_retries INTEGER DEFAULT 3,
    retry_delay_minutes INTEGER DEFAULT 5,
    current_retry_count INTEGER DEFAULT 0,
    
    -- Timeout
    timeout_minutes INTEGER DEFAULT 60,
    
    -- Alerts
    alert_on_failure BOOLEAN DEFAULT TRUE,
    alert_recipients JSONB DEFAULT '[]',
    
    -- Priority
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    
    -- Dependencies
    depends_on_jobs JSONB DEFAULT '[]',
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

-- =====================================================
-- TABLE: job_executions
-- Description: Job execution history
-- =====================================================
CREATE TABLE IF NOT EXISTS job_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_code VARCHAR(50) UNIQUE NOT NULL,
    job_id UUID REFERENCES scheduled_jobs(id) ON DELETE CASCADE,
    
    -- Execution details
    execution_type VARCHAR(50) NOT NULL, -- 'SCHEDULED', 'MANUAL', 'RETRY', 'TRIGGERED'
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    
    -- Status
    execution_status VARCHAR(20) NOT NULL, -- 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', 'TIMEOUT'
    
    -- Results
    execution_result JSONB,
    rows_processed INTEGER,
    records_created INTEGER,
    records_updated INTEGER,
    records_deleted INTEGER,
    
    -- Error details
    error_message TEXT,
    error_details JSONB,
    stack_trace TEXT,
    
    -- Resource usage
    cpu_usage_percent NUMERIC(5,2),
    memory_usage_mb NUMERIC(10,2),
    
    -- Logs
    execution_logs TEXT,
    log_file_path TEXT,
    
    -- Triggered by
    triggered_by_user UUID REFERENCES users(id),
    trigger_context JSONB,
    
    -- Retry info
    is_retry BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0,
    parent_execution_id UUID REFERENCES job_executions(id),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_job_executions_job (job_id, started_at DESC),
    INDEX idx_job_executions_status (execution_status, started_at DESC)
);

-- =====================================================
-- TABLE: feature_flags
-- Description: Feature flag management
-- =====================================================
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_key VARCHAR(100) UNIQUE NOT NULL,
    flag_name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Flag details
    flag_type VARCHAR(50) DEFAULT 'BOOLEAN', -- 'BOOLEAN', 'STRING', 'NUMBER', 'JSON'
    flag_value TEXT NOT NULL,
    default_value TEXT,
    
    -- Status
    is_enabled BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'DRAFT',
    
    -- Targeting
    targeting_rules JSONB DEFAULT '[]',
    rollout_percentage INTEGER DEFAULT 0 CHECK (rollout_percentage BETWEEN 0 AND 100),
    
    -- Scope
    scope VARCHAR(50) DEFAULT 'GLOBAL', -- 'GLOBAL', 'BRANCH', 'USER', 'ROLE'
    scope_values JSONB DEFAULT '[]',
    
    -- Environment
    environment VARCHAR(50) DEFAULT 'PRODUCTION', -- 'DEVELOPMENT', 'STAGING', 'PRODUCTION'
    
    -- Lifecycle
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    
    -- Tracking
    usage_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    
    -- Dependencies
    depends_on_flags JSONB DEFAULT '[]',
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ
);

-- =====================================================
-- TABLE: api_keys
-- Description: API key management
-- =====================================================
CREATE TABLE IF NOT EXISTS api_keys_admin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_name VARCHAR(200) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL,
    
    -- Ownership
    user_id UUID REFERENCES users(id),
    application_name VARCHAR(200),
    
    -- Permissions
    allowed_permissions JSONB DEFAULT '[]',
    allowed_resources JSONB DEFAULT '[]',
    scope VARCHAR(50) DEFAULT 'FULL', -- 'FULL', 'READ_ONLY', 'WRITE_ONLY', 'CUSTOM'
    
    -- Rate limiting
    rate_limit_per_minute INTEGER DEFAULT 1000,
    rate_limit_per_hour INTEGER DEFAULT 10000,
    rate_limit_per_day INTEGER DEFAULT 100000,
    
    -- IP restrictions
    allowed_ip_addresses JSONB DEFAULT '[]',
    ip_whitelist_enabled BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    
    -- Expiry
    expires_at TIMESTAMPTZ,
    
    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    
    -- Rotation
    rotation_policy JSONB,
    last_rotated_at TIMESTAMPTZ,
    next_rotation_at TIMESTAMPTZ,
    
    -- Security
    requires_mfa BOOLEAN DEFAULT FALSE,
    allowed_endpoints JSONB DEFAULT '[]',
    
    -- Metadata
    description TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(id),
    revoked_reason TEXT
);

-- =====================================================
-- TABLE: login_history
-- Description: User login history
-- =====================================================
CREATE TABLE IF NOT EXISTS login_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- User details
    user_id UUID REFERENCES users(id),
    username VARCHAR(100),
    
    -- Login details
    login_type VARCHAR(50) NOT NULL, -- 'PASSWORD', 'SSO', 'API_KEY', 'MFA', 'BIOMETRIC'
    login_status VARCHAR(20) NOT NULL, -- 'SUCCESS', 'FAILED', 'BLOCKED'
    
    -- Session
    session_id VARCHAR(100),
    session_duration_minutes INTEGER,
    
    -- Location
    ip_address VARCHAR(50),
    user_agent TEXT,
    device_type VARCHAR(50),
    device_name VARCHAR(100),
    browser VARCHAR(100),
    os VARCHAR(100),
    
    -- Geolocation
    country VARCHAR(100),
    city VARCHAR(100),
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    
    -- Security
    is_suspicious BOOLEAN DEFAULT FALSE,
    risk_score INTEGER,
    risk_factors JSONB,
    
    -- MFA
    mfa_used BOOLEAN DEFAULT FALSE,
    mfa_method VARCHAR(50),
    
    -- Failure details
    failure_reason TEXT,
    failure_count INTEGER DEFAULT 0,
    
    -- Logout
    logout_at TIMESTAMPTZ,
    logout_reason VARCHAR(50),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    login_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_login_history_user (user_id, login_at DESC),
    INDEX idx_login_history_status (login_status, login_at DESC),
    INDEX idx_login_history_ip (ip_address, login_at DESC)
);

-- =====================================================
-- VIEWS
-- =====================================================

-- View: System health overview
CREATE OR REPLACE VIEW v_system_health_overview AS
SELECT 
    COUNT(*) as total_checks,
    COUNT(CASE WHEN health_status = 'HEALTHY' THEN 1 END) as healthy_checks,
    COUNT(CASE WHEN health_status = 'DEGRADED' THEN 1 END) as degraded_checks,
    COUNT(CASE WHEN health_status = 'UNHEALTHY' THEN 1 END) as unhealthy_checks,
    COUNT(CASE WHEN is_critical = TRUE THEN 1 END) as critical_checks,
    COUNT(CASE WHEN is_critical = TRUE AND health_status = 'UNHEALTHY' THEN 1 END) as critical_failures,
    AVG(response_time_ms) as avg_response_time_ms,
    AVG(availability_percent) as avg_availability_percent,
    MAX(last_check_at) as last_check_at
FROM system_health
WHERE is_enabled = TRUE;

-- View: Role statistics
CREATE OR REPLACE VIEW v_role_statistics AS
SELECT 
    r.id as role_id,
    r.role_code,
    r.role_name,
    r.role_type,
    r.is_active,
    COUNT(ur.id) as assigned_user_count,
    COUNT(CASE WHEN ur.is_active = TRUE THEN 1 END) as active_assignments,
    r.max_users,
    r.created_at
FROM roles r
LEFT JOIN user_roles ur ON r.id = ur.role_id AND ur.is_active = TRUE
WHERE r.deleted_at IS NULL
GROUP BY r.id, r.role_code, r.role_name, r.role_type, r.is_active, r.max_users, r.created_at;

-- View: Audit summary
CREATE OR REPLACE VIEW v_audit_summary AS
SELECT 
    DATE(created_at) as audit_date,
    event_category,
    event_type,
    COUNT(*) as event_count,
    COUNT(CASE WHEN action_result = 'SUCCESS' THEN 1 END) as success_count,
    COUNT(CASE WHEN action_result = 'FAILURE' THEN 1 END) as failure_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(duration_ms) as avg_duration_ms
FROM audit_logs
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at), event_category, event_type
ORDER BY audit_date DESC, event_count DESC;

-- View: Job execution summary
CREATE OR REPLACE VIEW v_job_execution_summary AS
SELECT 
    sj.id as job_id,
    sj.job_code,
    sj.job_name,
    sj.job_type,
    sj.is_enabled,
    sj.last_execution_at,
    sj.last_execution_status,
    sj.next_execution_at,
    sj.total_executions,
    sj.success_count,
    sj.failure_count,
    CASE 
        WHEN sj.total_executions > 0 THEN (sj.success_count::NUMERIC / sj.total_executions * 100)
        ELSE 0
    END as success_rate_percent,
    sj.avg_duration_ms,
    COUNT(je.id) as recent_executions,
    MAX(je.started_at) as last_run
FROM scheduled_jobs sj
LEFT JOIN job_executions je ON sj.id = je.job_id AND je.started_at >= CURRENT_DATE - INTERVAL '7 days'
WHERE sj.deleted_at IS NULL
GROUP BY sj.id, sj.job_code, sj.job_name, sj.job_type, sj.is_enabled, 
         sj.last_execution_at, sj.last_execution_status, sj.next_execution_at,
         sj.total_executions, sj.success_count, sj.failure_count, sj.avg_duration_ms;

-- =====================================================
-- INDEXES
-- =====================================================

-- system_settings indexes
CREATE INDEX idx_system_settings_key ON system_settings(setting_key);
CREATE INDEX idx_system_settings_category ON system_settings(category);
CREATE INDEX idx_system_settings_editable ON system_settings(is_editable);

-- roles indexes
CREATE INDEX idx_roles_code ON roles(role_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_roles_type ON roles(role_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_roles_status ON roles(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_roles_active ON roles(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_roles_parent ON roles(parent_role_id) WHERE deleted_at IS NULL;

-- user_roles indexes
CREATE INDEX idx_user_roles_user ON user_roles(user_id, is_active);
CREATE INDEX idx_user_roles_role ON user_roles(role_id, is_active);
CREATE INDEX idx_user_roles_expires ON user_roles(expires_at) WHERE expires_at IS NOT NULL;

-- permissions indexes
CREATE INDEX idx_permissions_code ON permissions(permission_code);
CREATE INDEX idx_permissions_module ON permissions(module);
CREATE INDEX idx_permissions_resource ON permissions(resource);
CREATE INDEX idx_permissions_action ON permissions(action);
CREATE INDEX idx_permissions_type ON permissions(permission_type);

-- system_health indexes
CREATE INDEX idx_system_health_code ON system_health(check_code);
CREATE INDEX idx_system_health_type ON system_health(check_type);
CREATE INDEX idx_system_health_status ON system_health(health_status);
CREATE INDEX idx_system_health_component ON system_health(component_name);
CREATE INDEX idx_system_health_last_check ON system_health(last_check_at DESC);
CREATE INDEX idx_system_health_next_check ON system_health(next_check_at) WHERE is_enabled = TRUE;

-- notification_templates indexes
CREATE INDEX idx_notification_templates_code ON notification_templates(template_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_notification_templates_type ON notification_templates(notification_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_notification_templates_category ON notification_templates(template_category) WHERE deleted_at IS NULL;
CREATE INDEX idx_notification_templates_active ON notification_templates(is_active) WHERE deleted_at IS NULL;

-- scheduled_jobs indexes
CREATE INDEX idx_scheduled_jobs_code ON scheduled_jobs(job_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_scheduled_jobs_type ON scheduled_jobs(job_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_scheduled_jobs_enabled ON scheduled_jobs(is_enabled) WHERE deleted_at IS NULL;
CREATE INDEX idx_scheduled_jobs_next_execution ON scheduled_jobs(next_execution_at) WHERE is_enabled = TRUE AND deleted_at IS NULL;

-- feature_flags indexes
CREATE INDEX idx_feature_flags_key ON feature_flags(flag_key) WHERE deleted_at IS NULL;
CREATE INDEX idx_feature_flags_enabled ON feature_flags(is_enabled) WHERE deleted_at IS NULL;
CREATE INDEX idx_feature_flags_environment ON feature_flags(environment) WHERE deleted_at IS NULL;

-- api_keys_admin indexes
CREATE INDEX idx_api_keys_admin_user ON api_keys_admin(user_id);
CREATE INDEX idx_api_keys_admin_active ON api_keys_admin(is_active);
CREATE INDEX idx_api_keys_admin_expires ON api_keys_admin(expires_at) WHERE expires_at IS NOT NULL;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Update system_settings timestamp
CREATE OR REPLACE FUNCTION update_system_settings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.last_modified_at = CURRENT_TIMESTAMP;
    -- Add to change history
    NEW.change_history = COALESCE(NEW.change_history, '[]'::jsonb) || 
        jsonb_build_object(
            'changed_at', CURRENT_TIMESTAMP,
            'changed_by', NEW.last_modified_by,
            'old_value', OLD.setting_value,
            'new_value', NEW.setting_value
        );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_system_settings_update
    BEFORE UPDATE ON system_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_system_settings_timestamp();

-- Trigger: Update roles timestamp
CREATE OR REPLACE FUNCTION update_roles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_roles_update
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_roles_timestamp();

-- Trigger: Update scheduled_jobs timestamp
CREATE OR REPLACE FUNCTION update_scheduled_jobs_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_scheduled_jobs_update
    BEFORE UPDATE ON scheduled_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_scheduled_jobs_timestamp();

-- Trigger: Update notification_templates timestamp
CREATE OR REPLACE FUNCTION update_notification_templates_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_notification_templates_update
    BEFORE UPDATE ON notification_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_templates_timestamp();

-- Trigger: Update feature_flags timestamp
CREATE OR REPLACE FUNCTION update_feature_flags_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_feature_flags_update
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION update_feature_flags_timestamp();

-- Trigger: Update system_health timestamp
CREATE OR REPLACE FUNCTION update_system_health_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    -- Track status changes
    IF OLD.health_status IS DISTINCT FROM NEW.health_status THEN
        NEW.previous_status = OLD.health_status;
        NEW.status_changed_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_system_health_update
    BEFORE UPDATE ON system_health
    FOR EACH ROW
    EXECUTE FUNCTION update_system_health_timestamp();

-- Trigger: Update api_keys_admin timestamp
CREATE OR REPLACE FUNCTION update_api_keys_admin_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_api_keys_admin_update
    BEFORE UPDATE ON api_keys_admin
    FOR EACH ROW
    EXECUTE FUNCTION update_api_keys_admin_timestamp();

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE system_settings IS 'Platform configuration settings';
COMMENT ON TABLE roles IS 'User roles and permissions management';
COMMENT ON TABLE user_roles IS 'User-role assignments';
COMMENT ON TABLE permissions IS 'System permissions catalog';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for all system actions';
COMMENT ON TABLE system_health IS 'System health monitoring and status';
COMMENT ON TABLE system_metrics IS 'System performance metrics and KPIs';
COMMENT ON TABLE notification_templates IS 'Notification templates for various channels';
COMMENT ON TABLE scheduled_jobs IS 'Background job scheduling and management';
COMMENT ON TABLE job_executions IS 'Job execution history and results';
COMMENT ON TABLE feature_flags IS 'Feature flag management for controlled rollouts';
COMMENT ON TABLE api_keys_admin IS 'API key management for external integrations';
COMMENT ON TABLE login_history IS 'User login history and security tracking';

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert default system roles
INSERT INTO roles (role_code, role_name, description, role_type, is_system_role, is_active) VALUES
('SUPER_ADMIN', 'Super Administrator', 'Full system access with all permissions', 'SYSTEM', TRUE, TRUE),
('ADMIN', 'Administrator', 'Administrative access with most permissions', 'SYSTEM', TRUE, TRUE),
('MANAGER', 'Manager', 'Management level access', 'SYSTEM', TRUE, TRUE),
('OFFICER', 'Officer', 'Operational level access', 'SYSTEM', TRUE, TRUE),
('VIEWER', 'Viewer', 'Read-only access', 'SYSTEM', TRUE, TRUE)
ON CONFLICT (role_code) DO NOTHING;

-- Insert default permissions
INSERT INTO permissions (permission_code, permission_name, module, resource, action, permission_type, risk_level) VALUES
-- User Management
('USER_CREATE', 'Create Users', 'ADMIN', 'USERS', 'CREATE', 'ADMIN', 'HIGH'),
('USER_READ', 'View Users', 'ADMIN', 'USERS', 'READ', 'STANDARD', 'LOW'),
('USER_UPDATE', 'Update Users', 'ADMIN', 'USERS', 'UPDATE', 'ADMIN', 'MEDIUM'),
('USER_DELETE', 'Delete Users', 'ADMIN', 'USERS', 'DELETE', 'ADMIN', 'HIGH'),

-- Role Management
('ROLE_CREATE', 'Create Roles', 'ADMIN', 'ROLES', 'CREATE', 'ADMIN', 'HIGH'),
('ROLE_READ', 'View Roles', 'ADMIN', 'ROLES', 'READ', 'STANDARD', 'LOW'),
('ROLE_UPDATE', 'Update Roles', 'ADMIN', 'ROLES', 'UPDATE', 'ADMIN', 'HIGH'),
('ROLE_DELETE', 'Delete Roles', 'ADMIN', 'ROLES', 'DELETE', 'ADMIN', 'CRITICAL'),

-- System Settings
('SETTINGS_READ', 'View Settings', 'ADMIN', 'SETTINGS', 'READ', 'ADMIN', 'LOW'),
('SETTINGS_UPDATE', 'Update Settings', 'ADMIN', 'SETTINGS', 'UPDATE', 'ADMIN', 'CRITICAL'),

-- Audit Logs
('AUDIT_READ', 'View Audit Logs', 'ADMIN', 'AUDIT', 'READ', 'ADMIN', 'MEDIUM'),
('AUDIT_EXPORT', 'Export Audit Logs', 'ADMIN', 'AUDIT', 'EXECUTE', 'ADMIN', 'HIGH')
ON CONFLICT (permission_code) DO NOTHING;

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, category, description, is_editable) VALUES
('PLATFORM_NAME', 'NBFC Gold Lending Suite', 'STRING', 'GENERAL', 'Platform name', TRUE),
('PLATFORM_VERSION', '1.0.0', 'STRING', 'GENERAL', 'Platform version', FALSE),
('SESSION_TIMEOUT_MINUTES', '30', 'INTEGER', 'SECURITY', 'Session timeout in minutes', TRUE),
('MAX_LOGIN_ATTEMPTS', '5', 'INTEGER', 'SECURITY', 'Maximum login attempts before lockout', TRUE),
('PASSWORD_MIN_LENGTH', '8', 'INTEGER', 'SECURITY', 'Minimum password length', TRUE),
('REQUIRE_MFA', 'false', 'BOOLEAN', 'SECURITY', 'Require multi-factor authentication', TRUE),
('ENABLE_API_RATE_LIMITING', 'true', 'BOOLEAN', 'SECURITY', 'Enable API rate limiting', TRUE),
('DEFAULT_PAGE_SIZE', '50', 'INTEGER', 'GENERAL', 'Default pagination size', TRUE)
ON CONFLICT (setting_key) DO NOTHING;
