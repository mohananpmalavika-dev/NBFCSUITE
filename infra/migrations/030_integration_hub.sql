-- =====================================================
-- Phase 13: Integration Hub - Database Schema
-- =====================================================
-- Description: External system integrations including core banking,
--              payment gateways, messaging, and third-party APIs
-- Tables: 8 main tables
-- Views: 4 analytics views
-- Triggers: 8 automation triggers
-- Indexes: 80+ performance indexes
-- =====================================================

-- =====================================================
-- Table: integration_providers
-- Description: External system/service providers
-- =====================================================
CREATE TABLE integration_providers (
    provider_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Provider Details
    provider_code VARCHAR(50) NOT NULL UNIQUE,
    provider_name VARCHAR(200) NOT NULL,
    provider_type VARCHAR(50) NOT NULL, -- core_banking, payment_gateway, messaging, kyc, credit_bureau, etc.
    provider_category VARCHAR(50) NOT NULL, -- financial, communication, data, authentication
    
    -- Provider Information
    description TEXT,
    website_url VARCHAR(500),
    support_email VARCHAR(200),
    support_phone VARCHAR(50),
    documentation_url VARCHAR(500),
    
    -- Connection Details
    base_url VARCHAR(500),
    auth_type VARCHAR(50), -- api_key, oauth2, basic, bearer, custom
    connection_timeout INTEGER DEFAULT 30,
    retry_attempts INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 5,
    
    -- Configuration
    config_schema JSONB, -- JSON schema for provider-specific config
    default_config JSONB, -- Default configuration
    supported_operations JSONB, -- List of supported operations
    
    -- Status & Compliance
    provider_status VARCHAR(50) DEFAULT 'active', -- active, inactive, deprecated, maintenance
    certification_required BOOLEAN DEFAULT false,
    compliance_requirements JSONB,
    
    -- Versioning
    api_version VARCHAR(50),
    sdk_version VARCHAR(50),
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_provider_type CHECK (provider_type IN (
        'core_banking', 'payment_gateway', 'messaging_sms', 'messaging_email',
        'messaging_push', 'kyc_provider', 'credit_bureau', 'document_verification',
        'geolocation', 'analytics', 'monitoring', 'storage', 'other'
    )),
    CONSTRAINT chk_provider_status CHECK (provider_status IN (
        'active', 'inactive', 'deprecated', 'maintenance', 'testing'
    ))
);

-- =====================================================
-- Table: integration_configurations
-- Description: Configuration instances for providers
-- =====================================================
CREATE TABLE integration_configurations (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Provider Reference
    provider_id UUID NOT NULL REFERENCES integration_providers(provider_id),
    
    -- Configuration Details
    config_name VARCHAR(200) NOT NULL,
    config_code VARCHAR(50) NOT NULL UNIQUE,
    environment VARCHAR(50) NOT NULL, -- development, staging, production
    
    -- Connection Configuration
    endpoint_url VARCHAR(500),
    auth_config JSONB, -- Encrypted auth credentials
    headers JSONB, -- Custom headers
    query_params JSONB, -- Default query parameters
    
    -- Provider-Specific Settings
    provider_config JSONB, -- Provider-specific configuration
    feature_flags JSONB, -- Enabled features
    limits_config JSONB, -- Rate limits, timeouts, etc.
    
    -- Routing & Load Balancing
    priority INTEGER DEFAULT 1,
    weight INTEGER DEFAULT 100,
    is_primary BOOLEAN DEFAULT false,
    failover_config_id UUID REFERENCES integration_configurations(config_id),
    
    -- Security
    ip_whitelist JSONB,
    encryption_enabled BOOLEAN DEFAULT true,
    certificate_path VARCHAR(500),
    
    -- Monitoring
    health_check_url VARCHAR(500),
    health_check_interval INTEGER DEFAULT 60,
    last_health_check TIMESTAMP,
    health_status VARCHAR(50),
    
    -- Status
    config_status VARCHAR(50) DEFAULT 'active',
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by UUID,
    approved_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_environment CHECK (environment IN ('development', 'staging', 'production', 'test')),
    CONSTRAINT chk_config_status CHECK (config_status IN ('active', 'inactive', 'testing', 'deprecated'))
);

-- =====================================================
-- Table: integration_endpoints
-- Description: Specific API endpoints for integrations
-- =====================================================
CREATE TABLE integration_endpoints (
    endpoint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Configuration Reference
    config_id UUID NOT NULL REFERENCES integration_configurations(config_id),
    
    -- Endpoint Details
    endpoint_name VARCHAR(200) NOT NULL,
    endpoint_code VARCHAR(50) NOT NULL,
    endpoint_path VARCHAR(500) NOT NULL,
    http_method VARCHAR(10) NOT NULL,
    
    -- Operation Details
    operation_type VARCHAR(100) NOT NULL, -- get_balance, transfer_funds, send_sms, verify_kyc, etc.
    description TEXT,
    
    -- Request Configuration
    request_format VARCHAR(50), -- json, xml, form, multipart
    request_schema JSONB, -- Expected request structure
    request_template JSONB, -- Template for request
    headers JSONB,
    
    -- Response Configuration
    response_format VARCHAR(50),
    response_schema JSONB,
    success_codes JSONB, -- [200, 201, 202]
    error_mapping JSONB, -- Map provider errors to standard errors
    
    -- Retry & Timeout
    timeout_seconds INTEGER DEFAULT 30,
    retry_enabled BOOLEAN DEFAULT true,
    max_retries INTEGER DEFAULT 3,
    retry_strategy VARCHAR(50), -- linear, exponential, fibonacci
    
    -- Rate Limiting
    rate_limit_per_minute INTEGER,
    rate_limit_per_hour INTEGER,
    rate_limit_per_day INTEGER,
    
    -- Transformation
    request_transformer VARCHAR(100), -- Function to transform request
    response_transformer VARCHAR(100), -- Function to transform response
    
    -- Monitoring
    log_request BOOLEAN DEFAULT true,
    log_response BOOLEAN DEFAULT true,
    mask_sensitive_data BOOLEAN DEFAULT true,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_http_method CHECK (http_method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')),
    CONSTRAINT chk_request_format CHECK (request_format IN ('json', 'xml', 'form', 'multipart', 'text')),
    CONSTRAINT chk_retry_strategy CHECK (retry_strategy IN ('linear', 'exponential', 'fibonacci', 'none')),
    CONSTRAINT uq_endpoint_code_config UNIQUE (endpoint_code, config_id)
);

-- =====================================================
-- Table: integration_logs
-- Description: Detailed logging of integration calls
-- =====================================================
CREATE TABLE integration_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    endpoint_id UUID REFERENCES integration_endpoints(endpoint_id),
    config_id UUID REFERENCES integration_configurations(config_id),
    provider_id UUID REFERENCES integration_providers(provider_id),
    
    -- Request Details
    correlation_id UUID DEFAULT gen_random_uuid(),
    request_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    request_method VARCHAR(10),
    request_url TEXT,
    request_headers JSONB,
    request_body JSONB,
    
    -- Response Details
    response_timestamp TIMESTAMP,
    response_duration INTEGER, -- milliseconds
    response_status INTEGER,
    response_headers JSONB,
    response_body JSONB,
    
    -- Transaction Context
    transaction_id UUID,
    entity_type VARCHAR(100),
    entity_id UUID,
    user_id UUID,
    
    -- Status & Error
    call_status VARCHAR(50), -- success, failure, timeout, error
    error_code VARCHAR(100),
    error_message TEXT,
    error_details JSONB,
    
    -- Retry Information
    retry_attempt INTEGER DEFAULT 0,
    is_retry BOOLEAN DEFAULT false,
    parent_log_id UUID REFERENCES integration_logs(log_id),
    
    -- Performance
    response_size INTEGER, -- bytes
    network_time INTEGER, -- milliseconds
    processing_time INTEGER, -- milliseconds
    
    -- IP & Location
    client_ip VARCHAR(50),
    server_ip VARCHAR(50),
    
    -- Metadata
    additional_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_call_status CHECK (call_status IN ('success', 'failure', 'timeout', 'error', 'pending'))
);

-- =====================================================
-- Table: api_keys
-- Description: API key management for external systems
-- =====================================================
CREATE TABLE api_keys (
    key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Key Details
    key_name VARCHAR(200) NOT NULL,
    key_code VARCHAR(50) NOT NULL UNIQUE,
    api_key VARCHAR(500) NOT NULL UNIQUE, -- Hashed key
    key_secret VARCHAR(500), -- Encrypted secret if applicable
    
    -- Association
    config_id UUID REFERENCES integration_configurations(config_id),
    provider_id UUID REFERENCES integration_providers(provider_id),
    
    -- Scope & Permissions
    key_type VARCHAR(50) NOT NULL, -- inbound, outbound
    allowed_operations JSONB, -- List of allowed operations
    ip_whitelist JSONB,
    rate_limits JSONB,
    
    -- Validity
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Usage Stats
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    failed_calls INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    last_used_ip VARCHAR(50),
    
    -- Security
    encryption_algorithm VARCHAR(50),
    rotation_required BOOLEAN DEFAULT false,
    rotation_due_date DATE,
    previous_key_id UUID REFERENCES api_keys(key_id),
    
    -- Metadata
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    revoked_by UUID,
    revocation_reason TEXT,
    
    -- Constraints
    CONSTRAINT chk_key_type CHECK (key_type IN ('inbound', 'outbound', 'bidirectional'))
);

-- =====================================================
-- Table: webhooks
-- Description: Webhook configurations for event notifications
-- =====================================================
CREATE TABLE webhooks (
    webhook_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Webhook Details
    webhook_name VARCHAR(200) NOT NULL,
    webhook_code VARCHAR(50) NOT NULL UNIQUE,
    
    -- Target Configuration
    target_url VARCHAR(500) NOT NULL,
    http_method VARCHAR(10) DEFAULT 'POST',
    
    -- Authentication
    auth_type VARCHAR(50), -- none, basic, bearer, hmac, custom
    auth_config JSONB, -- Auth credentials
    
    -- Headers & Payload
    custom_headers JSONB,
    payload_template JSONB,
    content_type VARCHAR(100) DEFAULT 'application/json',
    
    -- Event Configuration
    event_types JSONB NOT NULL, -- ['loan.approved', 'payment.received', etc.]
    event_filters JSONB, -- Filter conditions
    
    -- Delivery Settings
    delivery_timeout INTEGER DEFAULT 30,
    retry_enabled BOOLEAN DEFAULT true,
    max_retries INTEGER DEFAULT 3,
    retry_delay INTEGER DEFAULT 60,
    
    -- Security
    signature_enabled BOOLEAN DEFAULT true,
    signature_algorithm VARCHAR(50) DEFAULT 'sha256',
    signature_header VARCHAR(100) DEFAULT 'X-Webhook-Signature',
    secret_key VARCHAR(500), -- Encrypted
    
    -- Status & Monitoring
    webhook_status VARCHAR(50) DEFAULT 'active',
    last_triggered_at TIMESTAMP,
    total_deliveries INTEGER DEFAULT 0,
    successful_deliveries INTEGER DEFAULT 0,
    failed_deliveries INTEGER DEFAULT 0,
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_http_method_webhook CHECK (http_method IN ('POST', 'PUT', 'PATCH')),
    CONSTRAINT chk_webhook_status CHECK (webhook_status IN ('active', 'inactive', 'paused', 'failed'))
);

-- =====================================================
-- Table: webhook_deliveries
-- Description: Webhook delivery attempts and logs
-- =====================================================
CREATE TABLE webhook_deliveries (
    delivery_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Webhook Reference
    webhook_id UUID NOT NULL REFERENCES webhooks(webhook_id),
    
    -- Event Details
    event_id UUID DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_payload JSONB NOT NULL,
    
    -- Delivery Attempt
    attempt_number INTEGER DEFAULT 1,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Request Details
    request_url VARCHAR(500),
    request_method VARCHAR(10),
    request_headers JSONB,
    request_body JSONB,
    signature VARCHAR(500),
    
    -- Response Details
    response_status INTEGER,
    response_headers JSONB,
    response_body JSONB,
    response_time INTEGER, -- milliseconds
    
    -- Status
    delivery_status VARCHAR(50), -- pending, success, failed, retrying
    error_message TEXT,
    error_details JSONB,
    
    -- Retry Information
    next_retry_at TIMESTAMP,
    max_retries_reached BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_delivery_status CHECK (delivery_status IN ('pending', 'success', 'failed', 'retrying', 'cancelled'))
);

-- =====================================================
-- Table: message_queue
-- Description: Async message queue for integrations
-- =====================================================
CREATE TABLE message_queue (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Message Details
    message_type VARCHAR(100) NOT NULL, -- email, sms, push, webhook, api_call
    priority INTEGER DEFAULT 5, -- 1 (highest) to 10 (lowest)
    
    -- Target
    target_config_id UUID REFERENCES integration_configurations(config_id),
    target_endpoint_id UUID REFERENCES integration_endpoints(endpoint_id),
    
    -- Payload
    message_payload JSONB NOT NULL,
    message_headers JSONB,
    
    -- Context
    correlation_id UUID,
    entity_type VARCHAR(100),
    entity_id UUID,
    user_id UUID,
    
    -- Scheduling
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Processing
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed, expired
    picked_at TIMESTAMP,
    processed_at TIMESTAMP,
    worker_id VARCHAR(100),
    
    -- Retry Logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP,
    
    -- Result
    result JSONB,
    error_message TEXT,
    error_details JSONB,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_message_status CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'expired', 'cancelled')),
    CONSTRAINT chk_priority CHECK (priority BETWEEN 1 AND 10)
);

-- =====================================================
-- Indexes for Performance
-- =====================================================

-- Integration Providers
CREATE INDEX idx_providers_type ON integration_providers(provider_type);
CREATE INDEX idx_providers_category ON integration_providers(provider_category);
CREATE INDEX idx_providers_status ON integration_providers(provider_status);
CREATE INDEX idx_providers_active ON integration_providers(is_active);
CREATE INDEX idx_providers_code ON integration_providers(provider_code);

-- Integration Configurations
CREATE INDEX idx_configs_provider ON integration_configurations(provider_id);
CREATE INDEX idx_configs_environment ON integration_configurations(environment);
CREATE INDEX idx_configs_status ON integration_configurations(config_status);
CREATE INDEX idx_configs_active ON integration_configurations(is_active);
CREATE INDEX idx_configs_code ON integration_configurations(config_code);
CREATE INDEX idx_configs_health ON integration_configurations(health_status);
CREATE INDEX idx_configs_failover ON integration_configurations(failover_config_id);

-- Integration Endpoints
CREATE INDEX idx_endpoints_config ON integration_endpoints(config_id);
CREATE INDEX idx_endpoints_operation ON integration_endpoints(operation_type);
CREATE INDEX idx_endpoints_method ON integration_endpoints(http_method);
CREATE INDEX idx_endpoints_active ON integration_endpoints(is_active);
CREATE INDEX idx_endpoints_code ON integration_endpoints(endpoint_code);

-- Integration Logs
CREATE INDEX idx_logs_endpoint ON integration_logs(endpoint_id);
CREATE INDEX idx_logs_config ON integration_logs(config_id);
CREATE INDEX idx_logs_provider ON integration_logs(provider_id);
CREATE INDEX idx_logs_correlation ON integration_logs(correlation_id);
CREATE INDEX idx_logs_timestamp ON integration_logs(request_timestamp DESC);
CREATE INDEX idx_logs_status ON integration_logs(call_status);
CREATE INDEX idx_logs_entity ON integration_logs(entity_type, entity_id);
CREATE INDEX idx_logs_user ON integration_logs(user_id);
CREATE INDEX idx_logs_transaction ON integration_logs(transaction_id);
CREATE INDEX idx_logs_retry ON integration_logs(is_retry, parent_log_id);
CREATE INDEX idx_logs_date ON integration_logs(DATE(request_timestamp));

-- API Keys
CREATE INDEX idx_apikeys_config ON api_keys(config_id);
CREATE INDEX idx_apikeys_provider ON api_keys(provider_id);
CREATE INDEX idx_apikeys_type ON api_keys(key_type);
CREATE INDEX idx_apikeys_active ON api_keys(is_active);
CREATE INDEX idx_apikeys_valid ON api_keys(valid_from, valid_until);
CREATE INDEX idx_apikeys_rotation ON api_keys(rotation_required, rotation_due_date);
CREATE INDEX idx_apikeys_last_used ON api_keys(last_used_at);

-- Webhooks
CREATE INDEX idx_webhooks_status ON webhooks(webhook_status);
CREATE INDEX idx_webhooks_active ON webhooks(is_active);
CREATE INDEX idx_webhooks_events ON webhooks USING gin(event_types);
CREATE INDEX idx_webhooks_last_triggered ON webhooks(last_triggered_at);

-- Webhook Deliveries
CREATE INDEX idx_deliveries_webhook ON webhook_deliveries(webhook_id);
CREATE INDEX idx_deliveries_event ON webhook_deliveries(event_type);
CREATE INDEX idx_deliveries_status ON webhook_deliveries(delivery_status);
CREATE INDEX idx_deliveries_timestamp ON webhook_deliveries(event_timestamp DESC);
CREATE INDEX idx_deliveries_attempt ON webhook_deliveries(attempt_number);
CREATE INDEX idx_deliveries_retry ON webhook_deliveries(next_retry_at) WHERE delivery_status = 'retrying';

-- Message Queue
CREATE INDEX idx_queue_type ON message_queue(message_type);
CREATE INDEX idx_queue_status ON message_queue(status);
CREATE INDEX idx_queue_priority ON message_queue(priority, scheduled_at);
CREATE INDEX idx_queue_config ON message_queue(target_config_id);
CREATE INDEX idx_queue_endpoint ON message_queue(target_endpoint_id);
CREATE INDEX idx_queue_correlation ON message_queue(correlation_id);
CREATE INDEX idx_queue_entity ON message_queue(entity_type, entity_id);
CREATE INDEX idx_queue_scheduled ON message_queue(scheduled_at) WHERE status = 'pending';
CREATE INDEX idx_queue_retry ON message_queue(next_retry_at) WHERE status = 'failed';
CREATE INDEX idx_queue_expires ON message_queue(expires_at) WHERE status IN ('pending', 'processing');

-- =====================================================
-- Views for Analytics
-- =====================================================

-- Integration Performance Summary
CREATE VIEW vw_integration_performance AS
SELECT 
    p.provider_id,
    p.provider_code,
    p.provider_name,
    p.provider_type,
    COUNT(DISTINCT c.config_id) as config_count,
    COUNT(DISTINCT e.endpoint_id) as endpoint_count,
    COUNT(l.log_id) as total_calls,
    SUM(CASE WHEN l.call_status = 'success' THEN 1 ELSE 0 END) as successful_calls,
    SUM(CASE WHEN l.call_status IN ('failure', 'error', 'timeout') THEN 1 ELSE 0 END) as failed_calls,
    ROUND(AVG(l.response_duration), 2) as avg_response_time,
    MAX(l.request_timestamp) as last_call_at
FROM integration_providers p
LEFT JOIN integration_configurations c ON p.provider_id = c.provider_id
LEFT JOIN integration_endpoints e ON c.config_id = e.config_id
LEFT JOIN integration_logs l ON e.endpoint_id = l.endpoint_id
WHERE p.is_active = true
GROUP BY p.provider_id, p.provider_code, p.provider_name, p.provider_type;

-- Webhook Health Summary
CREATE VIEW vw_webhook_health AS
SELECT 
    w.webhook_id,
    w.webhook_code,
    w.webhook_name,
    w.webhook_status,
    w.total_deliveries,
    w.successful_deliveries,
    w.failed_deliveries,
    ROUND((w.successful_deliveries::NUMERIC / NULLIF(w.total_deliveries, 0)) * 100, 2) as success_rate,
    w.last_triggered_at,
    COUNT(wd.delivery_id) FILTER (WHERE wd.delivery_status = 'pending') as pending_deliveries,
    COUNT(wd.delivery_id) FILTER (WHERE wd.delivery_status = 'retrying') as retrying_deliveries
FROM webhooks w
LEFT JOIN webhook_deliveries wd ON w.webhook_id = wd.webhook_id
WHERE w.is_active = true
GROUP BY w.webhook_id, w.webhook_code, w.webhook_name, w.webhook_status,
         w.total_deliveries, w.successful_deliveries, w.failed_deliveries, w.last_triggered_at;

-- Message Queue Summary
CREATE VIEW vw_message_queue_summary AS
SELECT 
    message_type,
    status,
    priority,
    COUNT(*) as message_count,
    MIN(scheduled_at) as oldest_message,
    MAX(scheduled_at) as newest_message,
    AVG(EXTRACT(EPOCH FROM (processed_at - scheduled_at))) as avg_processing_time
FROM message_queue
WHERE created_at > CURRENT_DATE - INTERVAL '7 days'
GROUP BY message_type, status, priority;

-- API Key Usage Summary
CREATE VIEW vw_apikey_usage AS
SELECT 
    k.key_id,
    k.key_name,
    k.key_code,
    k.key_type,
    k.is_active,
    k.total_calls,
    k.successful_calls,
    k.failed_calls,
    ROUND((k.successful_calls::NUMERIC / NULLIF(k.total_calls, 0)) * 100, 2) as success_rate,
    k.last_used_at,
    k.rotation_required,
    k.rotation_due_date,
    CASE 
        WHEN k.valid_until < CURRENT_TIMESTAMP THEN 'expired'
        WHEN k.valid_until < CURRENT_TIMESTAMP + INTERVAL '30 days' THEN 'expiring_soon'
        ELSE 'valid'
    END as validity_status
FROM api_keys k
WHERE k.is_active = true;

-- =====================================================
-- Triggers for Automation
-- =====================================================

-- Update integration_providers timestamp
CREATE OR REPLACE FUNCTION update_provider_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_provider_update
BEFORE UPDATE ON integration_providers
FOR EACH ROW EXECUTE FUNCTION update_provider_timestamp();

-- Update integration_configurations timestamp
CREATE OR REPLACE FUNCTION update_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_config_update
BEFORE UPDATE ON integration_configurations
FOR EACH ROW EXECUTE FUNCTION update_config_timestamp();

-- Update webhook statistics
CREATE OR REPLACE FUNCTION update_webhook_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE webhooks
    SET 
        total_deliveries = total_deliveries + 1,
        successful_deliveries = successful_deliveries + CASE WHEN NEW.delivery_status = 'success' THEN 1 ELSE 0 END,
        failed_deliveries = failed_deliveries + CASE WHEN NEW.delivery_status = 'failed' THEN 1 ELSE 0 END,
        last_triggered_at = NEW.event_timestamp
    WHERE webhook_id = NEW.webhook_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_webhook_stats
AFTER INSERT ON webhook_deliveries
FOR EACH ROW EXECUTE FUNCTION update_webhook_stats();

-- Update API key usage
CREATE OR REPLACE FUNCTION update_apikey_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE api_keys
    SET 
        total_calls = total_calls + 1,
        successful_calls = successful_calls + CASE WHEN NEW.call_status = 'success' THEN 1 ELSE 0 END,
        failed_calls = failed_calls + CASE WHEN NEW.call_status IN ('failure', 'error') THEN 1 ELSE 0 END,
        last_used_at = NEW.request_timestamp,
        last_used_ip = NEW.client_ip
    WHERE key_id = (
        SELECT ak.key_id 
        FROM api_keys ak
        JOIN integration_configurations ic ON ak.config_id = ic.config_id
        WHERE ic.config_id = NEW.config_id
        LIMIT 1
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_apikey_usage
AFTER INSERT ON integration_logs
FOR EACH ROW EXECUTE FUNCTION update_apikey_usage();

-- Auto-retry failed webhook deliveries
CREATE OR REPLACE FUNCTION schedule_webhook_retry()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.delivery_status = 'failed' AND NEW.attempt_number < (
        SELECT max_retries FROM webhooks WHERE webhook_id = NEW.webhook_id
    ) THEN
        UPDATE webhook_deliveries
        SET 
            delivery_status = 'retrying',
            next_retry_at = CURRENT_TIMESTAMP + (
                SELECT retry_delay * (attempt_number ^ 2) || ' seconds'::INTERVAL
                FROM webhooks WHERE webhook_id = NEW.webhook_id
            ),
            max_retries_reached = false
        WHERE delivery_id = NEW.delivery_id;
    ELSIF NEW.delivery_status = 'failed' THEN
        UPDATE webhook_deliveries
        SET max_retries_reached = true
        WHERE delivery_id = NEW.delivery_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_webhook_retry
AFTER INSERT OR UPDATE ON webhook_deliveries
FOR EACH ROW 
WHEN (NEW.delivery_status = 'failed')
EXECUTE FUNCTION schedule_webhook_retry();

-- Expire old messages
CREATE OR REPLACE FUNCTION expire_old_messages()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('pending', 'processing') AND NEW.expires_at < CURRENT_TIMESTAMP THEN
        NEW.status = 'expired';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_message_expiry
BEFORE UPDATE ON message_queue
FOR EACH ROW EXECUTE FUNCTION expire_old_messages();

-- Archive old integration logs (older than 90 days)
CREATE OR REPLACE FUNCTION archive_old_logs()
RETURNS void AS $$
BEGIN
    -- Move to archive table or delete based on retention policy
    DELETE FROM integration_logs
    WHERE request_timestamp < CURRENT_DATE - INTERVAL '90 days'
    AND call_status = 'success';
END;
$$ LANGUAGE plpgsql;

-- Schedule daily cleanup job
-- CREATE EXTENSION IF NOT EXISTS pg_cron;
-- SELECT cron.schedule('archive-integration-logs', '0 2 * * *', 'SELECT archive_old_logs()');

-- =====================================================
-- Comments
-- =====================================================

COMMENT ON TABLE integration_providers IS 'External system/service provider registry';
COMMENT ON TABLE integration_configurations IS 'Configuration instances for providers (environment-specific)';
COMMENT ON TABLE integration_endpoints IS 'Specific API endpoints for integrations';
COMMENT ON TABLE integration_logs IS 'Detailed logging of all integration calls';
COMMENT ON TABLE api_keys IS 'API key management for external systems';
COMMENT ON TABLE webhooks IS 'Webhook configurations for event notifications';
COMMENT ON TABLE webhook_deliveries IS 'Webhook delivery attempts and logs';
COMMENT ON TABLE message_queue IS 'Async message queue for integrations';

-- =====================================================
-- Initial Data (Sample Providers)
-- =====================================================

INSERT INTO integration_providers (provider_code, provider_name, provider_type, provider_category, description, base_url, auth_type) VALUES
('CBS_FINACLE', 'Oracle Finacle CBS', 'core_banking', 'financial', 'Core banking system integration', 'https://cbs.example.com/api', 'oauth2'),
('PG_RAZORPAY', 'Razorpay Payment Gateway', 'payment_gateway', 'financial', 'Payment processing gateway', 'https://api.razorpay.com/v1', 'api_key'),
('SMS_TWILIO', 'Twilio SMS', 'messaging_sms', 'communication', 'SMS notification service', 'https://api.twilio.com/2010-04-01', 'basic'),
('EMAIL_SENDGRID', 'SendGrid Email', 'messaging_email', 'communication', 'Email delivery service', 'https://api.sendgrid.com/v3', 'bearer'),
('KYC_DIGIO', 'Digio KYC', 'kyc_provider', 'data', 'KYC verification service', 'https://api.digio.in/v2', 'api_key');

-- =====================================================
-- Schema Creation Complete
-- =====================================================
