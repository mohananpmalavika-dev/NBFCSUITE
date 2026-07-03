-- =====================================================
-- Phase 14: Analytics & Business Intelligence
-- Migration: 031_analytics_bi.sql
-- Description: Complete analytics and BI infrastructure
-- =====================================================

-- =====================================================
-- TABLE: data_warehouses
-- Description: Data warehouse configurations
-- =====================================================
CREATE TABLE IF NOT EXISTS data_warehouses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_code VARCHAR(50) UNIQUE NOT NULL,
    warehouse_name VARCHAR(200) NOT NULL,
    warehouse_type VARCHAR(50) NOT NULL, -- 'OLAP', 'STAR_SCHEMA', 'SNOWFLAKE', 'DATA_VAULT'
    connection_config JSONB NOT NULL,
    refresh_schedule JSONB, -- cron expression and config
    last_refresh_at TIMESTAMPTZ,
    next_refresh_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    storage_size_gb DECIMAL(15,2),
    row_count BIGINT DEFAULT 0,
    
    -- Metadata
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    
    -- Maker-Checker
    maker_id UUID REFERENCES users(id),
    checker_id UUID REFERENCES users(id),
    maker_comment TEXT,
    checker_comment TEXT,
    approval_status VARCHAR(20) DEFAULT 'PENDING',
    approved_at TIMESTAMPTZ,
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: data_sources
-- Description: Analytics data sources and connections
-- =====================================================
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_code VARCHAR(50) UNIQUE NOT NULL,
    source_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- 'DATABASE', 'API', 'FILE', 'STREAM', 'EXTERNAL'
    connection_string TEXT,
    connection_config JSONB NOT NULL,
    authentication_type VARCHAR(50), -- 'BASIC', 'OAUTH', 'API_KEY', 'CERTIFICATE'
    credentials_encrypted TEXT,
    
    -- Data source properties
    schema_config JSONB,
    sync_frequency VARCHAR(50), -- 'REAL_TIME', 'HOURLY', 'DAILY', 'WEEKLY'
    last_sync_at TIMESTAMPTZ,
    next_sync_at TIMESTAMPTZ,
    sync_status VARCHAR(20) DEFAULT 'PENDING',
    
    -- Performance
    avg_response_time_ms INTEGER,
    data_volume_gb DECIMAL(15,2),
    record_count BIGINT DEFAULT 0,
    
    -- Health monitoring
    health_status VARCHAR(20) DEFAULT 'UNKNOWN',
    last_health_check_at TIMESTAMPTZ,
    health_check_config JSONB,
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: reports
-- Description: Custom report definitions
-- =====================================================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_code VARCHAR(50) UNIQUE NOT NULL,
    report_name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL, -- 'STANDARD', 'CUSTOM', 'ADHOC', 'SCHEDULED', 'REAL_TIME'
    category VARCHAR(100), -- 'FINANCIAL', 'OPERATIONAL', 'COMPLIANCE', 'EXECUTIVE'
    description TEXT,
    
    -- Report definition
    data_source_id UUID REFERENCES data_sources(id),
    query_definition JSONB NOT NULL, -- SQL, filters, joins, aggregations
    parameters JSONB DEFAULT '[]', -- User-configurable parameters
    
    -- Visualization
    visualization_type VARCHAR(50), -- 'TABLE', 'CHART', 'GRAPH', 'PIVOT', 'DASHBOARD'
    visualization_config JSONB,
    layout_config JSONB,
    
    -- Scheduling
    schedule_enabled BOOLEAN DEFAULT FALSE,
    schedule_config JSONB, -- cron, recipients, format
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    
    -- Performance
    avg_execution_time_ms INTEGER,
    cache_enabled BOOLEAN DEFAULT TRUE,
    cache_duration_minutes INTEGER DEFAULT 60,
    last_cached_at TIMESTAMPTZ,
    
    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    owner_id UUID REFERENCES users(id),
    shared_with JSONB DEFAULT '[]', -- user/role IDs
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: report_executions
-- Description: Report execution history and results
-- =====================================================
CREATE TABLE IF NOT EXISTS report_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_code VARCHAR(50) UNIQUE NOT NULL,
    report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
    
    -- Execution details
    execution_type VARCHAR(50), -- 'MANUAL', 'SCHEDULED', 'API', 'BATCH'
    parameters_used JSONB,
    filters_applied JSONB,
    
    -- Performance metrics
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    execution_time_ms INTEGER,
    rows_returned INTEGER,
    data_size_kb INTEGER,
    
    -- Results
    result_status VARCHAR(20), -- 'SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED'
    result_location TEXT, -- S3/file path to stored results
    result_format VARCHAR(20), -- 'JSON', 'CSV', 'EXCEL', 'PDF'
    result_preview JSONB, -- First few rows for preview
    
    -- Error handling
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    
    -- User context
    executed_by UUID REFERENCES users(id),
    execution_context JSONB, -- IP, user agent, etc.
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: dashboards
-- Description: Executive and operational dashboards
-- =====================================================
CREATE TABLE IF NOT EXISTS dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_code VARCHAR(50) UNIQUE NOT NULL,
    dashboard_name VARCHAR(200) NOT NULL,
    dashboard_type VARCHAR(50) NOT NULL, -- 'EXECUTIVE', 'OPERATIONAL', 'ANALYTICAL', 'REAL_TIME'
    category VARCHAR(100),
    description TEXT,
    
    -- Dashboard configuration
    layout_type VARCHAR(50), -- 'GRID', 'FLEX', 'MASONRY', 'CUSTOM'
    layout_config JSONB NOT NULL,
    widgets JSONB NOT NULL, -- Array of widget configurations
    
    -- Refresh settings
    auto_refresh BOOLEAN DEFAULT TRUE,
    refresh_interval_seconds INTEGER DEFAULT 300,
    last_refreshed_at TIMESTAMPTZ,
    
    -- Filters
    global_filters JSONB DEFAULT '[]',
    filter_config JSONB,
    
    -- Access control
    is_public BOOLEAN DEFAULT FALSE,
    owner_id UUID REFERENCES users(id),
    shared_with JSONB DEFAULT '[]',
    
    -- Display settings
    theme VARCHAR(50) DEFAULT 'LIGHT',
    display_config JSONB,
    mobile_optimized BOOLEAN DEFAULT TRUE,
    
    -- Analytics
    view_count INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMPTZ,
    avg_load_time_ms INTEGER,
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: widgets
-- Description: Dashboard widget definitions
-- =====================================================
CREATE TABLE IF NOT EXISTS widgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_code VARCHAR(50) UNIQUE NOT NULL,
    widget_name VARCHAR(200) NOT NULL,
    widget_type VARCHAR(50) NOT NULL, -- 'CHART', 'TABLE', 'KPI', 'MAP', 'GAUGE', 'TEXT'
    
    -- Data binding
    report_id UUID REFERENCES reports(id),
    data_source_id UUID REFERENCES data_sources(id),
    query_config JSONB,
    
    -- Visualization
    chart_type VARCHAR(50), -- 'LINE', 'BAR', 'PIE', 'SCATTER', 'HEATMAP', 'SANKEY'
    visualization_config JSONB NOT NULL,
    color_scheme VARCHAR(50),
    
    -- Interactivity
    drill_down_enabled BOOLEAN DEFAULT FALSE,
    drill_down_config JSONB,
    click_actions JSONB,
    
    -- Refresh
    auto_refresh BOOLEAN DEFAULT TRUE,
    refresh_interval_seconds INTEGER DEFAULT 300,
    cache_enabled BOOLEAN DEFAULT TRUE,
    
    -- Display
    size_config JSONB, -- width, height, min/max
    position_config JSONB,
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: ml_models
-- Description: Machine learning model registry
-- =====================================================
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_code VARCHAR(50) UNIQUE NOT NULL,
    model_name VARCHAR(200) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'REGRESSION', 'CLASSIFICATION', 'CLUSTERING', 'FORECASTING', 'NLP'
    algorithm VARCHAR(100), -- 'LINEAR_REGRESSION', 'RANDOM_FOREST', 'NEURAL_NETWORK', 'ARIMA'
    
    -- Model configuration
    framework VARCHAR(50), -- 'SCIKIT_LEARN', 'TENSORFLOW', 'PYTORCH', 'XGBOOST'
    version VARCHAR(20) NOT NULL,
    model_file_path TEXT,
    model_artifact_url TEXT,
    
    -- Training details
    training_data_source_id UUID REFERENCES data_sources(id),
    training_dataset_size INTEGER,
    training_started_at TIMESTAMPTZ,
    training_completed_at TIMESTAMPTZ,
    training_duration_minutes INTEGER,
    
    -- Model performance
    accuracy_score DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    rmse DECIMAL(15,4),
    mae DECIMAL(15,4),
    r2_score DECIMAL(5,4),
    performance_metrics JSONB,
    
    -- Hyperparameters
    hyperparameters JSONB,
    feature_importance JSONB,
    
    -- Deployment
    deployment_status VARCHAR(20) DEFAULT 'TRAINED', -- 'TRAINED', 'DEPLOYED', 'ARCHIVED'
    deployment_endpoint TEXT,
    deployed_at TIMESTAMPTZ,
    
    -- Usage tracking
    prediction_count INTEGER DEFAULT 0,
    last_prediction_at TIMESTAMPTZ,
    avg_prediction_time_ms INTEGER,
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: predictions
-- Description: ML model prediction history
-- =====================================================
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_code VARCHAR(50) UNIQUE NOT NULL,
    model_id UUID REFERENCES ml_models(id) ON DELETE CASCADE,
    
    -- Prediction details
    input_features JSONB NOT NULL,
    prediction_result JSONB NOT NULL,
    confidence_score DECIMAL(5,4),
    
    -- Performance
    prediction_time_ms INTEGER,
    model_version VARCHAR(20),
    
    -- Context
    prediction_type VARCHAR(50), -- 'BATCH', 'REAL_TIME', 'SCHEDULED'
    business_context JSONB,
    
    -- Validation
    actual_value JSONB, -- If ground truth is available
    prediction_error DECIMAL(15,4),
    is_accurate BOOLEAN,
    
    -- User tracking
    requested_by UUID REFERENCES users(id),
    request_context JSONB,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: data_streams
-- Description: Real-time data streaming configurations
-- =====================================================
CREATE TABLE IF NOT EXISTS data_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_code VARCHAR(50) UNIQUE NOT NULL,
    stream_name VARCHAR(200) NOT NULL,
    stream_type VARCHAR(50) NOT NULL, -- 'KAFKA', 'KINESIS', 'PUBSUB', 'RABBITMQ', 'WEBSOCKET'
    
    -- Stream configuration
    connection_config JSONB NOT NULL,
    topic_name VARCHAR(200),
    partition_key VARCHAR(100),
    
    -- Data format
    data_format VARCHAR(50), -- 'JSON', 'AVRO', 'PROTOBUF', 'CSV'
    schema_definition JSONB,
    
    -- Processing
    processing_mode VARCHAR(50), -- 'AT_LEAST_ONCE', 'EXACTLY_ONCE', 'AT_MOST_ONCE'
    batch_size INTEGER DEFAULT 100,
    batch_timeout_ms INTEGER DEFAULT 5000,
    
    -- Consumers
    consumer_groups JSONB DEFAULT '[]',
    consumer_config JSONB,
    
    -- Monitoring
    messages_per_second DECIMAL(10,2),
    total_messages_processed BIGINT DEFAULT 0,
    last_message_at TIMESTAMPTZ,
    lag_seconds INTEGER,
    
    -- Error handling
    error_handling_strategy VARCHAR(50), -- 'RETRY', 'DLQ', 'SKIP', 'STOP'
    dead_letter_queue VARCHAR(200),
    error_count INTEGER DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: analytics_alerts
-- Description: Analytics alert configurations
-- =====================================================
CREATE TABLE IF NOT EXISTS analytics_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_code VARCHAR(50) UNIQUE NOT NULL,
    alert_name VARCHAR(200) NOT NULL,
    alert_type VARCHAR(50) NOT NULL, -- 'THRESHOLD', 'ANOMALY', 'TREND', 'FORECAST'
    severity VARCHAR(20), -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    
    -- Alert configuration
    data_source_id UUID REFERENCES data_sources(id),
    metric_name VARCHAR(200),
    condition_config JSONB NOT NULL, -- threshold, operator, value
    
    -- Detection settings
    evaluation_frequency_minutes INTEGER DEFAULT 15,
    lookback_period_minutes INTEGER DEFAULT 60,
    detection_algorithm VARCHAR(50), -- 'SIMPLE', 'MOVING_AVERAGE', 'STATISTICAL', 'ML'
    sensitivity DECIMAL(3,2) DEFAULT 0.95,
    
    -- Notification
    notification_channels JSONB DEFAULT '[]', -- email, sms, slack, webhook
    notification_template TEXT,
    recipients JSONB DEFAULT '[]',
    
    -- State management
    last_evaluated_at TIMESTAMPTZ,
    next_evaluation_at TIMESTAMPTZ,
    is_triggered BOOLEAN DEFAULT FALSE,
    last_triggered_at TIMESTAMPTZ,
    trigger_count INTEGER DEFAULT 0,
    
    -- Suppression
    suppression_enabled BOOLEAN DEFAULT FALSE,
    suppression_duration_minutes INTEGER,
    suppressed_until TIMESTAMPTZ,
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- TABLE: alert_notifications
-- Description: Alert notification history
-- =====================================================
CREATE TABLE IF NOT EXISTS alert_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_code VARCHAR(50) UNIQUE NOT NULL,
    alert_id UUID REFERENCES analytics_alerts(id) ON DELETE CASCADE,
    
    -- Notification details
    notification_type VARCHAR(50), -- 'EMAIL', 'SMS', 'SLACK', 'WEBHOOK', 'PUSH'
    recipient VARCHAR(200),
    subject VARCHAR(500),
    message TEXT,
    
    -- Delivery
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    delivery_status VARCHAR(20), -- 'PENDING', 'SENT', 'DELIVERED', 'FAILED', 'BOUNCED'
    
    -- Metrics
    alert_value JSONB,
    threshold_value JSONB,
    deviation_percentage DECIMAL(10,2),
    
    -- Response tracking
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    resolution_notes TEXT,
    resolved_at TIMESTAMPTZ,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: data_quality_rules
-- Description: Data quality monitoring rules
-- =====================================================
CREATE TABLE IF NOT EXISTS data_quality_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code VARCHAR(50) UNIQUE NOT NULL,
    rule_name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- 'COMPLETENESS', 'ACCURACY', 'CONSISTENCY', 'VALIDITY', 'TIMELINESS'
    
    -- Rule configuration
    data_source_id UUID REFERENCES data_sources(id),
    table_name VARCHAR(200),
    column_name VARCHAR(200),
    rule_definition JSONB NOT NULL,
    
    -- Validation
    validation_query TEXT,
    expected_value JSONB,
    tolerance DECIMAL(5,4),
    
    -- Execution
    execution_frequency_minutes INTEGER DEFAULT 60,
    last_executed_at TIMESTAMPTZ,
    next_execution_at TIMESTAMPTZ,
    
    -- Results
    last_result_status VARCHAR(20), -- 'PASSED', 'FAILED', 'WARNING'
    pass_rate DECIMAL(5,2),
    failure_count INTEGER DEFAULT 0,
    
    -- Actions
    on_failure_action VARCHAR(50), -- 'ALERT', 'BLOCK', 'LOG', 'AUTO_FIX'
    notification_config JSONB,
    
    status VARCHAR(20) DEFAULT 'ACTIVE',
    metadata JSONB DEFAULT '{}',
    
    -- Audit fields
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ,
    version INTEGER DEFAULT 1
);

-- =====================================================
-- VIEWS
-- =====================================================

-- View: Analytics overview
CREATE OR REPLACE VIEW v_analytics_overview AS
SELECT 
    (SELECT COUNT(*) FROM data_sources WHERE deleted_at IS NULL) as total_data_sources,
    (SELECT COUNT(*) FROM data_sources WHERE status = 'ACTIVE' AND deleted_at IS NULL) as active_data_sources,
    (SELECT COUNT(*) FROM reports WHERE deleted_at IS NULL) as total_reports,
    (SELECT COUNT(*) FROM dashboards WHERE deleted_at IS NULL) as total_dashboards,
    (SELECT COUNT(*) FROM ml_models WHERE deleted_at IS NULL) as total_ml_models,
    (SELECT COUNT(*) FROM ml_models WHERE deployment_status = 'DEPLOYED' AND deleted_at IS NULL) as deployed_models,
    (SELECT COUNT(*) FROM data_streams WHERE deleted_at IS NULL) as total_streams,
    (SELECT COUNT(*) FROM data_streams WHERE status = 'ACTIVE' AND deleted_at IS NULL) as active_streams,
    (SELECT COUNT(*) FROM analytics_alerts WHERE status = 'ACTIVE' AND deleted_at IS NULL) as active_alerts,
    (SELECT COUNT(*) FROM analytics_alerts WHERE is_triggered = TRUE AND deleted_at IS NULL) as triggered_alerts,
    (SELECT SUM(view_count) FROM dashboards WHERE deleted_at IS NULL) as total_dashboard_views,
    (SELECT SUM(prediction_count) FROM ml_models WHERE deleted_at IS NULL) as total_predictions;

-- View: Report execution metrics
CREATE OR REPLACE VIEW v_report_execution_metrics AS
SELECT 
    r.id as report_id,
    r.report_code,
    r.report_name,
    r.report_type,
    COUNT(re.id) as total_executions,
    COUNT(CASE WHEN re.result_status = 'SUCCESS' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN re.result_status = 'FAILED' THEN 1 END) as failed_executions,
    AVG(re.execution_time_ms) as avg_execution_time_ms,
    MAX(re.execution_time_ms) as max_execution_time_ms,
    MIN(re.execution_time_ms) as min_execution_time_ms,
    AVG(re.rows_returned) as avg_rows_returned,
    MAX(re.started_at) as last_execution_at
FROM reports r
LEFT JOIN report_executions re ON r.id = re.report_id
WHERE r.deleted_at IS NULL
GROUP BY r.id, r.report_code, r.report_name, r.report_type;

-- View: ML model performance
CREATE OR REPLACE VIEW v_ml_model_performance AS
SELECT 
    m.id as model_id,
    m.model_code,
    m.model_name,
    m.model_type,
    m.algorithm,
    m.deployment_status,
    m.accuracy_score,
    m.precision_score,
    m.recall_score,
    m.f1_score,
    m.prediction_count,
    m.avg_prediction_time_ms,
    m.last_prediction_at,
    COUNT(p.id) as total_predictions_recorded,
    AVG(p.confidence_score) as avg_confidence_score,
    COUNT(CASE WHEN p.is_accurate = TRUE THEN 1 END) as accurate_predictions,
    COUNT(CASE WHEN p.is_accurate = FALSE THEN 1 END) as inaccurate_predictions
FROM ml_models m
LEFT JOIN predictions p ON m.id = p.model_id
WHERE m.deleted_at IS NULL
GROUP BY m.id, m.model_code, m.model_name, m.model_type, m.algorithm, 
         m.deployment_status, m.accuracy_score, m.precision_score, 
         m.recall_score, m.f1_score, m.prediction_count, 
         m.avg_prediction_time_ms, m.last_prediction_at;

-- View: Data stream health
CREATE OR REPLACE VIEW v_data_stream_health AS
SELECT 
    id as stream_id,
    stream_code,
    stream_name,
    stream_type,
    status,
    messages_per_second,
    total_messages_processed,
    last_message_at,
    lag_seconds,
    error_count,
    CASE 
        WHEN status != 'ACTIVE' THEN 'OFFLINE'
        WHEN lag_seconds > 300 THEN 'CRITICAL'
        WHEN lag_seconds > 60 THEN 'WARNING'
        WHEN error_count > 100 THEN 'WARNING'
        ELSE 'HEALTHY'
    END as health_status,
    created_at,
    updated_at
FROM data_streams
WHERE deleted_at IS NULL;

-- =====================================================
-- INDEXES
-- =====================================================

-- data_warehouses indexes
CREATE INDEX idx_data_warehouses_code ON data_warehouses(warehouse_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_warehouses_type ON data_warehouses(warehouse_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_warehouses_status ON data_warehouses(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_warehouses_refresh ON data_warehouses(next_refresh_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_warehouses_approval ON data_warehouses(approval_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_warehouses_created ON data_warehouses(created_at) WHERE deleted_at IS NULL;

-- data_sources indexes
CREATE INDEX idx_data_sources_code ON data_sources(source_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_sources_type ON data_sources(source_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_sources_status ON data_sources(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_sources_sync ON data_sources(next_sync_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_sources_health ON data_sources(health_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_sources_created ON data_sources(created_at) WHERE deleted_at IS NULL;

-- reports indexes
CREATE INDEX idx_reports_code ON reports(report_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_reports_type ON reports(report_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_reports_category ON reports(category) WHERE deleted_at IS NULL;
CREATE INDEX idx_reports_data_source ON reports(data_source_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_reports_owner ON reports(owner_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_reports_schedule ON reports(next_run_at) WHERE schedule_enabled = TRUE AND deleted_at IS NULL;
CREATE INDEX idx_reports_status ON reports(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_reports_created ON reports(created_at) WHERE deleted_at IS NULL;

-- report_executions indexes
CREATE INDEX idx_report_executions_code ON report_executions(execution_code);
CREATE INDEX idx_report_executions_report ON report_executions(report_id);
CREATE INDEX idx_report_executions_type ON report_executions(execution_type);
CREATE INDEX idx_report_executions_status ON report_executions(result_status);
CREATE INDEX idx_report_executions_user ON report_executions(executed_by);
CREATE INDEX idx_report_executions_started ON report_executions(started_at);
CREATE INDEX idx_report_executions_completed ON report_executions(completed_at);

-- dashboards indexes
CREATE INDEX idx_dashboards_code ON dashboards(dashboard_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_dashboards_type ON dashboards(dashboard_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_dashboards_category ON dashboards(category) WHERE deleted_at IS NULL;
CREATE INDEX idx_dashboards_owner ON dashboards(owner_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_dashboards_status ON dashboards(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_dashboards_created ON dashboards(created_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_dashboards_viewed ON dashboards(last_viewed_at) WHERE deleted_at IS NULL;

-- widgets indexes
CREATE INDEX idx_widgets_code ON widgets(widget_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_widgets_type ON widgets(widget_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_widgets_report ON widgets(report_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_widgets_data_source ON widgets(data_source_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_widgets_status ON widgets(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_widgets_created ON widgets(created_at) WHERE deleted_at IS NULL;

-- ml_models indexes
CREATE INDEX idx_ml_models_code ON ml_models(model_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_ml_models_type ON ml_models(model_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_ml_models_algorithm ON ml_models(algorithm) WHERE deleted_at IS NULL;
CREATE INDEX idx_ml_models_deployment ON ml_models(deployment_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_ml_models_training_source ON ml_models(training_data_source_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_ml_models_status ON ml_models(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_ml_models_created ON ml_models(created_at) WHERE deleted_at IS NULL;

-- predictions indexes
CREATE INDEX idx_predictions_code ON predictions(prediction_code);
CREATE INDEX idx_predictions_model ON predictions(model_id);
CREATE INDEX idx_predictions_type ON predictions(prediction_type);
CREATE INDEX idx_predictions_user ON predictions(requested_by);
CREATE INDEX idx_predictions_created ON predictions(created_at);
CREATE INDEX idx_predictions_accuracy ON predictions(is_accurate);

-- data_streams indexes
CREATE INDEX idx_data_streams_code ON data_streams(stream_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_streams_type ON data_streams(stream_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_streams_status ON data_streams(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_streams_last_message ON data_streams(last_message_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_streams_created ON data_streams(created_at) WHERE deleted_at IS NULL;

-- analytics_alerts indexes
CREATE INDEX idx_analytics_alerts_code ON analytics_alerts(alert_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_analytics_alerts_type ON analytics_alerts(alert_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_analytics_alerts_severity ON analytics_alerts(severity) WHERE deleted_at IS NULL;
CREATE INDEX idx_analytics_alerts_data_source ON analytics_alerts(data_source_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_analytics_alerts_evaluation ON analytics_alerts(next_evaluation_at) WHERE status = 'ACTIVE' AND deleted_at IS NULL;
CREATE INDEX idx_analytics_alerts_triggered ON analytics_alerts(is_triggered) WHERE deleted_at IS NULL;
CREATE INDEX idx_analytics_alerts_status ON analytics_alerts(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_analytics_alerts_created ON analytics_alerts(created_at) WHERE deleted_at IS NULL;

-- alert_notifications indexes
CREATE INDEX idx_alert_notifications_code ON alert_notifications(notification_code);
CREATE INDEX idx_alert_notifications_alert ON alert_notifications(alert_id);
CREATE INDEX idx_alert_notifications_type ON alert_notifications(notification_type);
CREATE INDEX idx_alert_notifications_recipient ON alert_notifications(recipient);
CREATE INDEX idx_alert_notifications_status ON alert_notifications(delivery_status);
CREATE INDEX idx_alert_notifications_sent ON alert_notifications(sent_at);
CREATE INDEX idx_alert_notifications_acknowledged ON alert_notifications(acknowledged_by);

-- data_quality_rules indexes
CREATE INDEX idx_data_quality_rules_code ON data_quality_rules(rule_code) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_quality_rules_type ON data_quality_rules(rule_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_quality_rules_data_source ON data_quality_rules(data_source_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_quality_rules_execution ON data_quality_rules(next_execution_at) WHERE status = 'ACTIVE' AND deleted_at IS NULL;
CREATE INDEX idx_data_quality_rules_status ON data_quality_rules(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_quality_rules_result ON data_quality_rules(last_result_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_data_quality_rules_created ON data_quality_rules(created_at) WHERE deleted_at IS NULL;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger: Update data_warehouses timestamp
CREATE OR REPLACE FUNCTION update_data_warehouses_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_data_warehouses_update
    BEFORE UPDATE ON data_warehouses
    FOR EACH ROW
    EXECUTE FUNCTION update_data_warehouses_timestamp();

-- Trigger: Update data_sources timestamp
CREATE OR REPLACE FUNCTION update_data_sources_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_data_sources_update
    BEFORE UPDATE ON data_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_data_sources_timestamp();

-- Trigger: Update reports timestamp
CREATE OR REPLACE FUNCTION update_reports_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_reports_update
    BEFORE UPDATE ON reports
    FOR EACH ROW
    EXECUTE FUNCTION update_reports_timestamp();

-- Trigger: Update dashboards timestamp
CREATE OR REPLACE FUNCTION update_dashboards_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_dashboards_update
    BEFORE UPDATE ON dashboards
    FOR EACH ROW
    EXECUTE FUNCTION update_dashboards_timestamp();

-- Trigger: Update widgets timestamp
CREATE OR REPLACE FUNCTION update_widgets_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_widgets_update
    BEFORE UPDATE ON widgets
    FOR EACH ROW
    EXECUTE FUNCTION update_widgets_timestamp();

-- Trigger: Update ml_models timestamp
CREATE OR REPLACE FUNCTION update_ml_models_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ml_models_update
    BEFORE UPDATE ON ml_models
    FOR EACH ROW
    EXECUTE FUNCTION update_ml_models_timestamp();

-- Trigger: Update data_streams timestamp
CREATE OR REPLACE FUNCTION update_data_streams_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_data_streams_update
    BEFORE UPDATE ON data_streams
    FOR EACH ROW
    EXECUTE FUNCTION update_data_streams_timestamp();

-- Trigger: Update analytics_alerts timestamp
CREATE OR REPLACE FUNCTION update_analytics_alerts_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_analytics_alerts_update
    BEFORE UPDATE ON analytics_alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_analytics_alerts_timestamp();

-- Trigger: Update data_quality_rules timestamp
CREATE OR REPLACE FUNCTION update_data_quality_rules_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_data_quality_rules_update
    BEFORE UPDATE ON data_quality_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_data_quality_rules_timestamp();

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE data_warehouses IS 'Data warehouse configurations for OLAP and analytical processing';
COMMENT ON TABLE data_sources IS 'Analytics data source connections and configurations';
COMMENT ON TABLE reports IS 'Custom report definitions and configurations';
COMMENT ON TABLE report_executions IS 'Report execution history and performance metrics';
COMMENT ON TABLE dashboards IS 'Executive and operational dashboard configurations';
COMMENT ON TABLE widgets IS 'Dashboard widget definitions and visualizations';
COMMENT ON TABLE ml_models IS 'Machine learning model registry and metadata';
COMMENT ON TABLE predictions IS 'ML model prediction history and validation';
COMMENT ON TABLE data_streams IS 'Real-time data streaming configurations';
COMMENT ON TABLE analytics_alerts IS 'Analytics alert rules and configurations';
COMMENT ON TABLE alert_notifications IS 'Alert notification delivery history';
COMMENT ON TABLE data_quality_rules IS 'Data quality monitoring and validation rules';

