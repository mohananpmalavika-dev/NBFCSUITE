-- Migration 032: Universal Posting Rule Engine
-- Created: 2026-06-28

ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS rule_name VARCHAR(255);
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS priority DECIMAL(12, 2) DEFAULT 100.0;
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS effective_from TIMESTAMP;
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS effective_to TIMESTAMP;
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS requires_approval VARCHAR(20) DEFAULT 'false';
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS conditions JSONB;
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS created_by VARCHAR(100);
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS metadata JSONB;
ALTER TABLE posting_rules ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_posting_rules_tenant_source') THEN
        ALTER TABLE posting_rules DROP CONSTRAINT uq_posting_rules_tenant_source;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS posting_execution_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    rule_id VARCHAR(36),
    source_module VARCHAR(100) NOT NULL,
    source_event VARCHAR(100) NOT NULL,
    source_reference VARCHAR(255),
    status VARCHAR(50) DEFAULT 'success',
    execution_time_ms DECIMAL(18, 2) DEFAULT 0.0,
    journal_id VARCHAR(36),
    error_message TEXT,
    input_payload JSONB,
    generated_lines JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES posting_rules(id) ON DELETE SET NULL,
    FOREIGN KEY (journal_id) REFERENCES journal_entries(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_posting_rules_tenant_module_event ON posting_rules(tenant_id, source_module, source_event);
CREATE INDEX IF NOT EXISTS idx_posting_rules_status ON posting_rules(status);
CREATE INDEX IF NOT EXISTS idx_posting_rules_priority ON posting_rules(priority);
CREATE INDEX IF NOT EXISTS idx_posting_execution_logs_tenant_id ON posting_execution_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_posting_execution_logs_rule_id ON posting_execution_logs(rule_id);
CREATE INDEX IF NOT EXISTS idx_posting_execution_logs_source ON posting_execution_logs(source_module, source_event, source_reference);
CREATE INDEX IF NOT EXISTS idx_posting_execution_logs_status ON posting_execution_logs(status);
