-- Migration 029: Customer creation enterprise features
-- Created: 2026-06-28

CREATE TABLE IF NOT EXISTS customer_timeline (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_description TEXT,
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_by VARCHAR(36),
    event_metadata JSONB,
    document_reference_id VARCHAR(36),
    related_product_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_timeline_customer_time ON customer_timeline(customer_id, event_timestamp);
CREATE INDEX IF NOT EXISTS idx_customer_timeline_event_type ON customer_timeline(event_type);

CREATE TABLE IF NOT EXISTS customer_consents (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    consent_type VARCHAR(50) NOT NULL,
    consent_status VARCHAR(20) DEFAULT 'given',
    consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consent_version VARCHAR(20) DEFAULT '1.0',
    consent_document_url VARCHAR(500),
    consent_expiry_date TIMESTAMP,
    withdrawn_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_consents_customer_type ON customer_consents(customer_id, consent_type);
CREATE INDEX IF NOT EXISTS idx_customer_consents_status ON customer_consents(consent_status);

CREATE TABLE IF NOT EXISTS customer_parties (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    party_type VARCHAR(50) NOT NULL,
    party_name VARCHAR(255) NOT NULL,
    party_code VARCHAR(50) UNIQUE,
    registration_number VARCHAR(100),
    registration_authority VARCHAR(100),
    party_status VARCHAR(50) DEFAULT 'active',
    tax_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_parties_type ON customer_parties(party_type);
CREATE INDEX IF NOT EXISTS idx_customer_parties_tax_id ON customer_parties(tax_id);

CREATE TABLE IF NOT EXISTS onboarding_workflows (
    id VARCHAR(36) PRIMARY KEY,
    workflow_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(100) NOT NULL,
    customer_type VARCHAR(50),
    workflow_stages JSONB,
    required_documents JSONB,
    required_compliance_checks JSONB,
    approval_levels INTEGER,
    is_active VARCHAR(20) DEFAULT 'true',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_onboarding_workflows_product_type ON onboarding_workflows(product_type);
CREATE INDEX IF NOT EXISTS idx_onboarding_workflows_customer_type ON onboarding_workflows(customer_type);
CREATE INDEX IF NOT EXISTS idx_onboarding_workflows_active ON onboarding_workflows(is_active);
