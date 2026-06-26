-- Migration 019: Phase 4 enterprise readiness and ecosystem support
-- Created: 2026-06-27

-- Auth: tenant context and tenant branding/configuration.
ALTER TABLE users ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36);
ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id VARCHAR(36);
ALTER TABLE users ADD COLUMN IF NOT EXISTS zone_id VARCHAR(36);
ALTER TABLE users ADD COLUMN IF NOT EXISTS region_id VARCHAR(36);
ALTER TABLE users ADD COLUMN IF NOT EXISTS area_id VARCHAR(36);
ALTER TABLE users ADD COLUMN IF NOT EXISTS branch_id VARCHAR(36);

CREATE TABLE IF NOT EXISTS tenant_configurations (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    primary_color VARCHAR(50),
    logo_url TEXT,
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_zone_id ON users(zone_id);
CREATE INDEX IF NOT EXISTS idx_users_region_id ON users(region_id);
CREATE INDEX IF NOT EXISTS idx_users_area_id ON users(area_id);
CREATE INDEX IF NOT EXISTS idx_users_branch_id ON users(branch_id);
CREATE INDEX IF NOT EXISTS idx_tenant_configurations_tenant_id ON tenant_configurations(tenant_id);

-- Accounting: tenant scoping, per-tenant uniqueness, automated posting metadata, tax MVP.
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS posting_status VARCHAR(50) DEFAULT 'posted';
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS source_module VARCHAR(100);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS source_event VARCHAR(100);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS source_reference VARCHAR(255);
ALTER TABLE bank_statement_transactions ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;

ALTER TABLE gl_accounts DROP CONSTRAINT IF EXISTS gl_accounts_account_code_key;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_gl_accounts_tenant_code'
    ) THEN
        ALTER TABLE gl_accounts
            ADD CONSTRAINT uq_gl_accounts_tenant_code UNIQUE (tenant_id, account_code);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_journal_entries_tenant_idempotency'
    ) THEN
        ALTER TABLE journal_entries
            ADD CONSTRAINT uq_journal_entries_tenant_idempotency UNIQUE (tenant_id, idempotency_key);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_bank_statement_transactions_tenant_reference'
    ) THEN
        ALTER TABLE bank_statement_transactions
            ADD CONSTRAINT uq_bank_statement_transactions_tenant_reference UNIQUE (tenant_id, reference);
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS tax_rules (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    tax_code VARCHAR(100) NOT NULL,
    tax_type VARCHAR(50) NOT NULL,
    rate_percent DECIMAL(9, 4) NOT NULL,
    payable_gl_account_id VARCHAR(36),
    payable_gl_account_code VARCHAR(100),
    expense_gl_account_code VARCHAR(100),
    is_active VARCHAR(20) DEFAULT 'true',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payable_gl_account_id) REFERENCES gl_accounts(id)
);

CREATE TABLE IF NOT EXISTS tax_computations (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    tax_rule_id VARCHAR(36) NOT NULL,
    journal_entry_id VARCHAR(36),
    source_module VARCHAR(100),
    source_reference VARCHAR(255),
    taxable_amount DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2),
    breakdown JSONB,
    status VARCHAR(50) DEFAULT 'computed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tax_rule_id) REFERENCES tax_rules(id),
    FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id)
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_tax_rules_tenant_code'
    ) THEN
        ALTER TABLE tax_rules
            ADD CONSTRAINT uq_tax_rules_tenant_code UNIQUE (tenant_id, tax_code);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_gl_accounts_tenant_id ON gl_accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_gl_accounts_tenant_code ON gl_accounts(tenant_id, account_code);
CREATE INDEX IF NOT EXISTS idx_journal_entries_tenant_id ON journal_entries(tenant_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_posting_status ON journal_entries(posting_status);
CREATE INDEX IF NOT EXISTS idx_journal_entries_idempotency_key ON journal_entries(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_journal_entries_source_module ON journal_entries(source_module);
CREATE INDEX IF NOT EXISTS idx_journal_entries_source_event ON journal_entries(source_event);
CREATE INDEX IF NOT EXISTS idx_journal_entries_source_reference ON journal_entries(source_reference);
CREATE INDEX IF NOT EXISTS idx_bank_statement_transactions_tenant_id ON bank_statement_transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tax_rules_tenant_id ON tax_rules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tax_rules_tenant_code ON tax_rules(tenant_id, tax_code);
CREATE INDEX IF NOT EXISTS idx_tax_computations_tenant_id ON tax_computations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tax_computations_source ON tax_computations(source_module, source_reference);

-- CRM: tenant scoping plus report/dashboard builder persistence.
ALTER TABLE crm_leads ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;
ALTER TABLE crm_leads ADD COLUMN IF NOT EXISTS metadata JSONB;
ALTER TABLE crm_campaigns ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;
ALTER TABLE crm_opportunities ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;

CREATE TABLE IF NOT EXISTS crm_report_definitions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    data_source VARCHAR(100) NOT NULL,
    columns JSONB NOT NULL,
    filters JSONB,
    group_by JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crm_dashboards (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    widgets JSONB NOT NULL,
    is_default VARCHAR(20) DEFAULT 'false',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_crm_leads_tenant_id ON crm_leads(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_leads_tenant_status ON crm_leads(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_crm_campaigns_tenant_id ON crm_campaigns(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_opportunities_tenant_id ON crm_opportunities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_opportunities_tenant_stage ON crm_opportunities(tenant_id, stage);
CREATE INDEX IF NOT EXISTS idx_crm_report_definitions_tenant_id ON crm_report_definitions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_dashboards_tenant_id ON crm_dashboards(tenant_id);
