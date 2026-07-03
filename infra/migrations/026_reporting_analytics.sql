-- =====================================================
-- Phase 9: Reporting & Analytics
-- Migration: 026_reporting_analytics.sql
-- Description: Comprehensive reporting, analytics, and dashboard system
-- =====================================================

-- =====================================================
-- 1. Report Definitions Table
-- =====================================================
CREATE TABLE report_definitions (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL, -- 'financial', 'operational', 'regulatory', 'custom'
    report_type VARCHAR(50) NOT NULL, -- 'standard', 'custom', 'ad_hoc', 'regulatory'
    data_source VARCHAR(100), -- 'loan_accounts', 'repayments', 'collections', 'customers', etc.
    query_template TEXT, -- SQL query template with parameters
    output_formats JSONB DEFAULT '["pdf", "excel", "csv"]'::jsonb, -- Supported formats
    parameters JSONB, -- Report parameters definition
    filters JSONB, -- Available filters
    columns JSONB, -- Column definitions
    sorting JSONB, -- Default sorting
    grouping JSONB, -- Grouping configuration
    aggregations JSONB, -- Aggregation functions
    styling JSONB, -- Report styling (colors, fonts, layout)
    access_roles JSONB, -- Roles that can access this report
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE, -- System-defined reports
    created_by BIGINT REFERENCES users(id),
    updated_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_report_category CHECK (category IN ('financial', 'operational', 'regulatory', 'custom', 'compliance', 'audit')),
    CONSTRAINT chk_report_type CHECK (report_type IN ('standard', 'custom', 'ad_hoc', 'regulatory', 'statutory'))
);

CREATE INDEX idx_report_definitions_code ON report_definitions(code);
CREATE INDEX idx_report_definitions_category ON report_definitions(category);
CREATE INDEX idx_report_definitions_type ON report_definitions(report_type);
CREATE INDEX idx_report_definitions_active ON report_definitions(is_active);
CREATE INDEX idx_report_definitions_created_at ON report_definitions(created_at);

-- =====================================================
-- 2. Report Templates Table
-- =====================================================
CREATE TABLE report_templates (
    id BIGSERIAL PRIMARY KEY,
    report_definition_id BIGINT NOT NULL REFERENCES report_definitions(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL, -- 'pdf', 'excel', 'html', 'email'
    template_content TEXT, -- Template markup (HTML, LaTeX, etc.)
    header_content TEXT,
    footer_content TEXT,
    styles TEXT, -- CSS or styling definitions
    page_size VARCHAR(20) DEFAULT 'A4', -- 'A4', 'Letter', 'Legal', 'A3'
    orientation VARCHAR(20) DEFAULT 'portrait', -- 'portrait', 'landscape'
    margins JSONB, -- {top, right, bottom, left}
    fonts JSONB, -- Font configurations
    colors JSONB, -- Color scheme
    logo_url VARCHAR(500),
    watermark TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_template_type CHECK (template_type IN ('pdf', 'excel', 'html', 'email', 'csv', 'json')),
    CONSTRAINT chk_page_size CHECK (page_size IN ('A4', 'A3', 'Letter', 'Legal', 'Tabloid')),
    CONSTRAINT chk_orientation CHECK (orientation IN ('portrait', 'landscape'))
);

CREATE INDEX idx_report_templates_definition ON report_templates(report_definition_id);
CREATE INDEX idx_report_templates_type ON report_templates(template_type);
CREATE INDEX idx_report_templates_active ON report_templates(is_active);
CREATE INDEX idx_report_templates_default ON report_templates(is_default);

-- =====================================================
-- 3. Report Schedules Table
-- =====================================================
CREATE TABLE report_schedules (
    id BIGSERIAL PRIMARY KEY,
    report_definition_id BIGINT NOT NULL REFERENCES report_definitions(id),
    template_id BIGINT REFERENCES report_templates(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    schedule_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'cron'
    frequency VARCHAR(100), -- Cron expression or frequency details
    start_date DATE NOT NULL,
    end_date DATE,
    execution_time TIME DEFAULT '00:00:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    parameters JSONB, -- Fixed parameters for scheduled run
    output_format VARCHAR(20) DEFAULT 'pdf',
    delivery_method VARCHAR(50), -- 'email', 'ftp', 'sftp', 's3', 'download'
    delivery_config JSONB, -- Email addresses, FTP credentials, etc.
    recipients JSONB, -- List of recipients
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'completed', 'failed'
    last_execution_at TIMESTAMP,
    next_execution_at TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_schedule_type CHECK (schedule_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'cron', 'on_demand')),
    CONSTRAINT chk_schedule_status CHECK (status IN ('active', 'paused', 'completed', 'failed', 'disabled')),
    CONSTRAINT chk_schedule_dates CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE INDEX idx_report_schedules_definition ON report_schedules(report_definition_id);
CREATE INDEX idx_report_schedules_status ON report_schedules(status);
CREATE INDEX idx_report_schedules_active ON report_schedules(is_active);
CREATE INDEX idx_report_schedules_next_execution ON report_schedules(next_execution_at);
CREATE INDEX idx_report_schedules_created_by ON report_schedules(created_by);

-- =====================================================
-- 4. Report Executions Table
-- =====================================================
CREATE TABLE report_executions (
    id BIGSERIAL PRIMARY KEY,
    report_definition_id BIGINT NOT NULL REFERENCES report_definitions(id),
    schedule_id BIGINT REFERENCES report_schedules(id),
    template_id BIGINT REFERENCES report_templates(id),
    execution_type VARCHAR(50) NOT NULL, -- 'scheduled', 'manual', 'api'
    parameters JSONB, -- Parameters used for this execution
    filters JSONB, -- Filters applied
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    output_format VARCHAR(20),
    file_path VARCHAR(500), -- Path to generated report file
    file_size BIGINT, -- File size in bytes
    file_url VARCHAR(500), -- URL to download report
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    rows_processed INTEGER,
    error_message TEXT,
    error_details JSONB,
    executed_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_execution_type CHECK (execution_type IN ('scheduled', 'manual', 'api', 'batch')),
    CONSTRAINT chk_execution_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout'))
);

CREATE INDEX idx_report_executions_definition ON report_executions(report_definition_id);
CREATE INDEX idx_report_executions_schedule ON report_executions(schedule_id);
CREATE INDEX idx_report_executions_status ON report_executions(status);
CREATE INDEX idx_report_executions_executed_by ON report_executions(executed_by);
CREATE INDEX idx_report_executions_created_at ON report_executions(created_at);
CREATE INDEX idx_report_executions_completed_at ON report_executions(completed_at);

-- =====================================================
-- 5. Report Parameters Table
-- =====================================================
CREATE TABLE report_parameters (
    id BIGSERIAL PRIMARY KEY,
    report_definition_id BIGINT NOT NULL REFERENCES report_definitions(id),
    parameter_name VARCHAR(100) NOT NULL,
    parameter_label VARCHAR(200) NOT NULL,
    parameter_type VARCHAR(50) NOT NULL, -- 'string', 'number', 'date', 'daterange', 'select', 'multiselect', 'boolean'
    data_type VARCHAR(50), -- 'text', 'integer', 'decimal', 'date', 'datetime'
    default_value TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    validation_rules JSONB, -- Min, max, regex, etc.
    options JSONB, -- For select/multiselect types
    options_query TEXT, -- SQL query to fetch options dynamically
    depends_on VARCHAR(100), -- Parent parameter dependency
    display_order INTEGER DEFAULT 0,
    help_text TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_parameter_type CHECK (parameter_type IN ('string', 'number', 'date', 'daterange', 'datetime', 'select', 'multiselect', 'boolean', 'autocomplete')),
    CONSTRAINT uq_report_parameter UNIQUE (report_definition_id, parameter_name)
);

CREATE INDEX idx_report_parameters_definition ON report_parameters(report_definition_id);
CREATE INDEX idx_report_parameters_name ON report_parameters(parameter_name);
CREATE INDEX idx_report_parameters_active ON report_parameters(is_active);
CREATE INDEX idx_report_parameters_order ON report_parameters(display_order);


-- =====================================================
-- 6. Report Exports Table
-- =====================================================
CREATE TABLE report_exports (
    id BIGSERIAL PRIMARY KEY,
    execution_id BIGINT NOT NULL REFERENCES report_executions(id),
    export_format VARCHAR(20) NOT NULL, -- 'pdf', 'excel', 'csv', 'json'
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    file_url VARCHAR(500),
    download_count INTEGER DEFAULT 0,
    last_downloaded_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_public BOOLEAN DEFAULT FALSE,
    access_token VARCHAR(255),
    status VARCHAR(20) DEFAULT 'available', -- 'available', 'expired', 'deleted'
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_export_format CHECK (export_format IN ('pdf', 'excel', 'csv', 'json', 'xml', 'html')),
    CONSTRAINT chk_export_status CHECK (status IN ('available', 'expired', 'deleted', 'processing'))
);

CREATE INDEX idx_report_exports_execution ON report_exports(execution_id);
CREATE INDEX idx_report_exports_format ON report_exports(export_format);
CREATE INDEX idx_report_exports_status ON report_exports(status);
CREATE INDEX idx_report_exports_created_by ON report_exports(created_by);
CREATE INDEX idx_report_exports_expires_at ON report_exports(expires_at);
CREATE INDEX idx_report_exports_token ON report_exports(access_token);

-- =====================================================
-- 7. Dashboard Definitions Table
-- =====================================================
CREATE TABLE dashboard_definitions (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    dashboard_type VARCHAR(50) NOT NULL, -- 'executive', 'operational', 'analytical', 'custom'
    category VARCHAR(50), -- 'lending', 'collections', 'risk', 'finance', 'operations'
    layout JSONB, -- Grid layout configuration
    theme JSONB, -- Color scheme, fonts
    refresh_interval INTEGER, -- Auto-refresh interval in seconds
    access_roles JSONB, -- Roles that can access
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_by BIGINT REFERENCES users(id),
    updated_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_dashboard_type CHECK (dashboard_type IN ('executive', 'operational', 'analytical', 'custom', 'realtime'))
);

CREATE INDEX idx_dashboard_definitions_code ON dashboard_definitions(code);
CREATE INDEX idx_dashboard_definitions_type ON dashboard_definitions(dashboard_type);
CREATE INDEX idx_dashboard_definitions_category ON dashboard_definitions(category);
CREATE INDEX idx_dashboard_definitions_active ON dashboard_definitions(is_active);
CREATE INDEX idx_dashboard_definitions_order ON dashboard_definitions(display_order);

-- =====================================================
-- 8. Dashboard Widgets Table
-- =====================================================
CREATE TABLE dashboard_widgets (
    id BIGSERIAL PRIMARY KEY,
    dashboard_id BIGINT NOT NULL REFERENCES dashboard_definitions(id) ON DELETE CASCADE,
    widget_type VARCHAR(50) NOT NULL, -- 'chart', 'table', 'metric', 'gauge', 'map', 'list'
    chart_type VARCHAR(50), -- 'line', 'bar', 'pie', 'area', 'scatter', 'heatmap'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    data_source VARCHAR(100), -- Table or view name
    query TEXT, -- SQL query for data
    parameters JSONB, -- Widget parameters
    filters JSONB, -- Widget-specific filters
    position JSONB NOT NULL, -- {x, y, width, height} in grid
    styling JSONB, -- Widget-specific styling
    refresh_interval INTEGER, -- Widget refresh interval
    drill_down JSONB, -- Drill-down configuration
    is_visible BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_widget_type CHECK (widget_type IN ('chart', 'table', 'metric', 'gauge', 'map', 'list', 'kpi', 'sparkline', 'progress')),
    CONSTRAINT chk_chart_type CHECK (chart_type IS NULL OR chart_type IN ('line', 'bar', 'pie', 'area', 'scatter', 'heatmap', 'funnel', 'radar', 'treemap'))
);

CREATE INDEX idx_dashboard_widgets_dashboard ON dashboard_widgets(dashboard_id);
CREATE INDEX idx_dashboard_widgets_type ON dashboard_widgets(widget_type);
CREATE INDEX idx_dashboard_widgets_visible ON dashboard_widgets(is_visible);
CREATE INDEX idx_dashboard_widgets_order ON dashboard_widgets(display_order);

-- =====================================================
-- 9. Data Snapshots Table
-- =====================================================
CREATE TABLE data_snapshots (
    id BIGSERIAL PRIMARY KEY,
    snapshot_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    snapshot_date DATE NOT NULL,
    snapshot_period VARCHAR(50), -- 'Q1-2026', '2026-01', etc.
    entity_type VARCHAR(50) NOT NULL, -- 'portfolio', 'collections', 'disbursements', 'customers'
    metrics JSONB NOT NULL, -- All metrics for this snapshot
    aggregations JSONB, -- Pre-calculated aggregations
    comparisons JSONB, -- Comparison with previous periods
    trends JSONB, -- Trend analysis
    status VARCHAR(20) DEFAULT 'active',
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_snapshot_type CHECK (snapshot_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'adhoc')),
    CONSTRAINT chk_snapshot_status CHECK (status IN ('active', 'archived', 'superseded')),
    CONSTRAINT uq_snapshot UNIQUE (snapshot_type, snapshot_date, entity_type)
);

CREATE INDEX idx_data_snapshots_type ON data_snapshots(snapshot_type);
CREATE INDEX idx_data_snapshots_date ON data_snapshots(snapshot_date);
CREATE INDEX idx_data_snapshots_entity ON data_snapshots(entity_type);
CREATE INDEX idx_data_snapshots_period ON data_snapshots(snapshot_period);
CREATE INDEX idx_data_snapshots_status ON data_snapshots(status);

-- =====================================================
-- 10. Analytics Metrics Table
-- =====================================================
CREATE TABLE analytics_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_code VARCHAR(100) UNIQUE NOT NULL,
    metric_name VARCHAR(200) NOT NULL,
    metric_category VARCHAR(50) NOT NULL, -- 'portfolio', 'collection', 'risk', 'finance', 'operations'
    metric_type VARCHAR(50) NOT NULL, -- 'count', 'sum', 'average', 'percentage', 'ratio'
    description TEXT,
    calculation_formula TEXT, -- SQL expression or formula
    unit VARCHAR(50), -- 'currency', 'percentage', 'count', 'days'
    data_source VARCHAR(100),
    aggregation_level VARCHAR(50), -- 'branch', 'product', 'customer_segment', 'region'
    time_granularity VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'quarterly'
    threshold_warning DECIMAL(15,2),
    threshold_critical DECIMAL(15,2),
    target_value DECIMAL(15,2),
    trend_direction VARCHAR(20), -- 'higher_better', 'lower_better', 'neutral'
    is_kpi BOOLEAN DEFAULT FALSE, -- Key Performance Indicator
    display_format VARCHAR(50), -- Number formatting
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    
    CONSTRAINT chk_metric_category CHECK (metric_category IN ('portfolio', 'collection', 'risk', 'finance', 'operations', 'compliance', 'customer')),
    CONSTRAINT chk_metric_type CHECK (metric_type IN ('count', 'sum', 'average', 'percentage', 'ratio', 'rate', 'index')),
    CONSTRAINT chk_trend_direction CHECK (trend_direction IN ('higher_better', 'lower_better', 'neutral'))
);

CREATE INDEX idx_analytics_metrics_code ON analytics_metrics(metric_code);
CREATE INDEX idx_analytics_metrics_category ON analytics_metrics(metric_category);
CREATE INDEX idx_analytics_metrics_type ON analytics_metrics(metric_type);
CREATE INDEX idx_analytics_metrics_kpi ON analytics_metrics(is_kpi);
CREATE INDEX idx_analytics_metrics_active ON analytics_metrics(is_active);


-- =====================================================
-- VIEWS
-- =====================================================

-- View: Active Reports with Execution Stats
CREATE OR REPLACE VIEW vw_active_reports AS
SELECT 
    rd.id,
    rd.code,
    rd.name,
    rd.category,
    rd.report_type,
    rd.is_system,
    rd.created_at,
    COUNT(DISTINCT re.id) as total_executions,
    COUNT(DISTINCT CASE WHEN re.status = 'completed' THEN re.id END) as successful_executions,
    COUNT(DISTINCT CASE WHEN re.status = 'failed' THEN re.id END) as failed_executions,
    MAX(re.completed_at) as last_execution_at,
    AVG(CASE WHEN re.status = 'completed' THEN re.duration_seconds END) as avg_duration_seconds,
    COUNT(DISTINCT rs.id) as active_schedules
FROM report_definitions rd
LEFT JOIN report_executions re ON rd.id = re.report_definition_id
LEFT JOIN report_schedules rs ON rd.id = rs.report_definition_id AND rs.is_active = true
WHERE rd.is_active = true
GROUP BY rd.id, rd.code, rd.name, rd.category, rd.report_type, rd.is_system, rd.created_at;

-- View: Scheduled Reports Summary
CREATE OR REPLACE VIEW vw_scheduled_reports AS
SELECT 
    rs.id,
    rs.name as schedule_name,
    rd.name as report_name,
    rd.category,
    rs.schedule_type,
    rs.frequency,
    rs.status,
    rs.last_execution_at,
    rs.next_execution_at,
    rs.execution_count,
    rs.success_count,
    rs.failure_count,
    CASE 
        WHEN rs.execution_count > 0 THEN (rs.success_count::float / rs.execution_count * 100)
        ELSE 0 
    END as success_rate,
    rs.created_by,
    u.username as created_by_name
FROM report_schedules rs
INNER JOIN report_definitions rd ON rs.report_definition_id = rd.id
LEFT JOIN users u ON rs.created_by = u.id
WHERE rs.is_active = true;

-- View: Dashboard Analytics
CREATE OR REPLACE VIEW vw_dashboard_analytics AS
SELECT 
    dd.id,
    dd.code,
    dd.name,
    dd.dashboard_type,
    dd.category,
    dd.is_default,
    COUNT(dw.id) as widget_count,
    COUNT(CASE WHEN dw.widget_type = 'chart' THEN 1 END) as chart_count,
    COUNT(CASE WHEN dw.widget_type = 'metric' THEN 1 END) as metric_count,
    COUNT(CASE WHEN dw.widget_type = 'table' THEN 1 END) as table_count,
    dd.created_at,
    dd.updated_at
FROM dashboard_definitions dd
LEFT JOIN dashboard_widgets dw ON dd.id = dw.dashboard_id AND dw.is_visible = true
WHERE dd.is_active = true
GROUP BY dd.id, dd.code, dd.name, dd.dashboard_type, dd.category, dd.is_default, dd.created_at, dd.updated_at;

-- View: Report Execution Performance
CREATE OR REPLACE VIEW vw_report_execution_performance AS
SELECT 
    rd.id as report_id,
    rd.code as report_code,
    rd.name as report_name,
    rd.category,
    DATE_TRUNC('day', re.created_at) as execution_date,
    COUNT(*) as execution_count,
    COUNT(CASE WHEN re.status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN re.status = 'failed' THEN 1 END) as failed_count,
    AVG(CASE WHEN re.status = 'completed' THEN re.duration_seconds END) as avg_duration,
    MIN(CASE WHEN re.status = 'completed' THEN re.duration_seconds END) as min_duration,
    MAX(CASE WHEN re.status = 'completed' THEN re.duration_seconds END) as max_duration,
    SUM(CASE WHEN re.status = 'completed' THEN re.rows_processed ELSE 0 END) as total_rows
FROM report_definitions rd
INNER JOIN report_executions re ON rd.id = re.report_definition_id
WHERE re.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY rd.id, rd.code, rd.name, rd.category, DATE_TRUNC('day', re.created_at);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Update report_definitions updated_at
CREATE OR REPLACE FUNCTION update_report_definition_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_report_definition_timestamp
    BEFORE UPDATE ON report_definitions
    FOR EACH ROW
    EXECUTE FUNCTION update_report_definition_timestamp();

-- Trigger: Update report execution duration
CREATE OR REPLACE FUNCTION calculate_execution_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND NEW.started_at IS NOT NULL AND NEW.completed_at IS NOT NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_calculate_execution_duration
    BEFORE UPDATE ON report_executions
    FOR EACH ROW
    WHEN (NEW.status = 'completed')
    EXECUTE FUNCTION calculate_execution_duration();

-- Trigger: Update schedule execution counts
CREATE OR REPLACE FUNCTION update_schedule_execution_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' THEN
        UPDATE report_schedules
        SET 
            execution_count = execution_count + 1,
            success_count = success_count + 1,
            last_execution_at = NEW.completed_at
        WHERE id = NEW.schedule_id;
    ELSIF NEW.status = 'failed' THEN
        UPDATE report_schedules
        SET 
            execution_count = execution_count + 1,
            failure_count = failure_count + 1,
            last_execution_at = NEW.completed_at
        WHERE id = NEW.schedule_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_schedule_execution_stats
    AFTER UPDATE ON report_executions
    FOR EACH ROW
    WHEN (NEW.status IN ('completed', 'failed') AND OLD.status != NEW.status)
    EXECUTE FUNCTION update_schedule_execution_stats();

-- Trigger: Auto-expire old report exports
CREATE OR REPLACE FUNCTION auto_expire_report_exports()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expires_at IS NULL THEN
        -- Default expiry: 30 days from creation
        NEW.expires_at = NEW.created_at + INTERVAL '30 days';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_expire_report_exports
    BEFORE INSERT ON report_exports
    FOR EACH ROW
    EXECUTE FUNCTION auto_expire_report_exports();

-- =====================================================
-- SEED DATA: Standard Report Definitions
-- =====================================================

-- Portfolio Reports
INSERT INTO report_definitions (code, name, description, category, report_type, data_source, is_system, is_active) VALUES
('RPT_PORTFOLIO_SUMMARY', 'Portfolio Summary Report', 'Comprehensive portfolio overview with key metrics', 'operational', 'standard', 'loan_accounts', true, true),
('RPT_LOAN_AGING', 'Loan Aging Analysis', 'Analysis of loans by age buckets', 'operational', 'standard', 'loan_accounts', true, true),
('RPT_DPD_ANALYSIS', 'DPD Analysis Report', 'Days Past Due analysis across portfolio', 'operational', 'standard', 'loan_accounts', true, true),
('RPT_DISBURSEMENT_SUMMARY', 'Disbursement Summary', 'Summary of loan disbursements', 'operational', 'standard', 'disbursement_transactions', true, true),
('RPT_REPAYMENT_SUMMARY', 'Repayment Summary', 'Summary of loan repayments', 'operational', 'standard', 'repayment_transactions', true, true);

-- Financial Reports
INSERT INTO report_definitions (code, name, description, category, report_type, data_source, is_system, is_active) VALUES
('RPT_BALANCE_SHEET', 'Balance Sheet', 'Balance sheet financial statement', 'financial', 'standard', 'journal_entries', true, true),
('RPT_INCOME_STATEMENT', 'Income Statement', 'Profit & loss statement', 'financial', 'standard', 'journal_entries', true, true),
('RPT_CASH_FLOW', 'Cash Flow Statement', 'Cash flow analysis', 'financial', 'standard', 'journal_entries', true, true),
('RPT_TRIAL_BALANCE', 'Trial Balance', 'Trial balance report', 'financial', 'standard', 'journal_entries', true, true),
('RPT_GENERAL_LEDGER', 'General Ledger', 'Detailed general ledger', 'financial', 'standard', 'journal_entries', true, true);

-- Collection Reports
INSERT INTO report_definitions (code, name, description, category, report_type, data_source, is_system, is_active) VALUES
('RPT_COLLECTION_PERFORMANCE', 'Collection Performance', 'Collection team performance metrics', 'operational', 'standard', 'collection_cases', true, true),
('RPT_RECOVERY_ANALYSIS', 'Recovery Analysis', 'Analysis of recovery actions and outcomes', 'operational', 'standard', 'recovery_actions', true, true),
('RPT_LEGAL_NOTICES', 'Legal Notices Report', 'Summary of legal notices issued', 'operational', 'standard', 'legal_notices', true, true),
('RPT_AUCTION_SUMMARY', 'Auction Summary', 'Summary of auctions conducted', 'operational', 'standard', 'auction_lots', true, true);

-- Regulatory Reports
INSERT INTO report_definitions (code, name, description, category, report_type, data_source, is_system, is_active) VALUES
('RPT_RBI_RETURN_1', 'RBI Return - NBS1', 'Non-Banking Financial Companies Returns', 'regulatory', 'regulatory', 'loan_accounts', true, true),
('RPT_NPA_REPORT', 'NPA Report', 'Non-Performing Assets report', 'regulatory', 'regulatory', 'loan_accounts', true, true),
('RPT_PRUDENTIAL_NORMS', 'Prudential Norms', 'Prudential norms compliance report', 'regulatory', 'regulatory', 'loan_accounts', true, true),
('RPT_ALM_REPORT', 'ALM Report', 'Asset Liability Management report', 'regulatory', 'regulatory', 'loan_accounts', true, true);

-- =====================================================
-- SEED DATA: Dashboard Definitions
-- =====================================================

INSERT INTO dashboard_definitions (code, name, description, dashboard_type, category, is_default, is_active, display_order) VALUES
('DASH_EXECUTIVE', 'Executive Dashboard', 'High-level executive overview', 'executive', 'operations', true, true, 1),
('DASH_BRANCH', 'Branch Manager Dashboard', 'Branch operations dashboard', 'operational', 'operations', false, true, 2),
('DASH_COLLECTION', 'Collections Dashboard', 'Collections team dashboard', 'operational', 'collections', false, true, 3),
('DASH_RISK', 'Risk Management Dashboard', 'Risk analysis dashboard', 'analytical', 'risk', false, true, 4),
('DASH_FINANCE', 'Finance Dashboard', 'Financial metrics dashboard', 'analytical', 'finance', false, true, 5),
('DASH_LENDING', 'Lending Operations Dashboard', 'Loan origination and servicing', 'operational', 'lending', false, true, 6);

-- =====================================================
-- SEED DATA: Analytics Metrics
-- =====================================================

INSERT INTO analytics_metrics (metric_code, metric_name, metric_category, metric_type, unit, is_kpi, trend_direction, display_order) VALUES
('MTR_TOTAL_PORTFOLIO', 'Total Portfolio Value', 'portfolio', 'sum', 'currency', true, 'higher_better', 1),
('MTR_ACTIVE_LOANS', 'Active Loans Count', 'portfolio', 'count', 'count', true, 'higher_better', 2),
('MTR_AVG_LOAN_SIZE', 'Average Loan Size', 'portfolio', 'average', 'currency', true, 'neutral', 3),
('MTR_DISBURSEMENT_AMOUNT', 'Disbursement Amount', 'operations', 'sum', 'currency', true, 'higher_better', 4),
('MTR_COLLECTION_RATE', 'Collection Rate', 'collection', 'percentage', 'percentage', true, 'higher_better', 5),
('MTR_NPA_RATIO', 'NPA Ratio', 'risk', 'percentage', 'percentage', true, 'lower_better', 6),
('MTR_PAR_30', 'Portfolio at Risk (30+)', 'risk', 'percentage', 'percentage', true, 'lower_better', 7),
('MTR_YIELD', 'Portfolio Yield', 'finance', 'percentage', 'percentage', true, 'higher_better', 8),
('MTR_RECOVERY_RATE', 'Recovery Rate', 'collection', 'percentage', 'percentage', true, 'higher_better', 9),
('MTR_CUSTOMER_COUNT', 'Total Customers', 'customer', 'count', 'count', true, 'higher_better', 10);

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE report_definitions IS 'Master table for report definitions and configurations';
COMMENT ON TABLE report_templates IS 'Report templates for different output formats';
COMMENT ON TABLE report_schedules IS 'Scheduled report execution configurations';
COMMENT ON TABLE report_executions IS 'Report execution history and results';
COMMENT ON TABLE report_parameters IS 'Report parameter definitions';
COMMENT ON TABLE report_exports IS 'Generated report files and exports';
COMMENT ON TABLE dashboard_definitions IS 'Dashboard layout and configuration';
COMMENT ON TABLE dashboard_widgets IS 'Dashboard widget definitions';
COMMENT ON TABLE data_snapshots IS 'Point-in-time data snapshots for historical analysis';
COMMENT ON TABLE analytics_metrics IS 'Business metrics and KPI definitions';

-- =====================================================
-- END OF MIGRATION
-- =====================================================
