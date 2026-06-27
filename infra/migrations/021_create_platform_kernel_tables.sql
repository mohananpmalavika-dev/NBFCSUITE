-- Migration 021: Platform kernel for product factory, rules, workflows, and domain events
-- Created: 2026-06-27

CREATE TABLE IF NOT EXISTS platform_product_definitions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    product_code VARCHAR(100) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_family VARCHAR(100) NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft',
    parameters JSONB,
    eligibility_rules JSONB,
    pricing_rules JSONB,
    fee_rules JSONB,
    lifecycle_workflow_code VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_platform_product_tenant_code_version UNIQUE (tenant_id, product_code, version)
);

CREATE TABLE IF NOT EXISTS platform_rule_sets (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    rule_set_code VARCHAR(100) NOT NULL,
    rule_set_name VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active',
    rules JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_platform_rule_set_tenant_code_version UNIQUE (tenant_id, rule_set_code, version)
);

CREATE TABLE IF NOT EXISTS platform_workflow_definitions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    workflow_code VARCHAR(100) NOT NULL,
    workflow_name VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active',
    initial_state VARCHAR(100) NOT NULL,
    terminal_states JSONB,
    transitions JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_platform_workflow_tenant_code_version UNIQUE (tenant_id, workflow_code, version)
);

CREATE TABLE IF NOT EXISTS platform_workflow_instances (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    workflow_definition_id VARCHAR(36) NOT NULL,
    workflow_code VARCHAR(100) NOT NULL,
    subject_type VARCHAR(100) NOT NULL,
    subject_id VARCHAR(100) NOT NULL,
    business_key VARCHAR(150),
    current_state VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    context JSONB,
    history JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS platform_domain_events (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(150) NOT NULL,
    source_service VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    idempotency_key VARCHAR(150),
    status VARCHAR(50) DEFAULT 'published',
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    CONSTRAINT uq_platform_event_tenant_idempotency UNIQUE (tenant_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_platform_products_tenant_family ON platform_product_definitions(tenant_id, product_family);
CREATE INDEX IF NOT EXISTS idx_platform_products_tenant_code ON platform_product_definitions(tenant_id, product_code);
CREATE INDEX IF NOT EXISTS idx_platform_rule_sets_tenant_code ON platform_rule_sets(tenant_id, rule_set_code);
CREATE INDEX IF NOT EXISTS idx_platform_workflows_tenant_code ON platform_workflow_definitions(tenant_id, workflow_code);
CREATE INDEX IF NOT EXISTS idx_platform_workflow_instances_subject ON platform_workflow_instances(tenant_id, subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_platform_workflow_instances_status ON platform_workflow_instances(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_platform_events_tenant_type ON platform_domain_events(tenant_id, event_type);
CREATE INDEX IF NOT EXISTS idx_platform_events_aggregate ON platform_domain_events(tenant_id, aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_platform_events_status ON platform_domain_events(tenant_id, status);
