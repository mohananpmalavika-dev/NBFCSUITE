-- Accounting controls and posting-rule governance upgrade.
-- Adds multi-currency account metadata, richer posting dimensions, period locks,
-- rule versioning/approval/dependencies, and execution rollback tracing.

ALTER TABLE gl_accounts
    ADD COLUMN IF NOT EXISTS base_currency VARCHAR DEFAULT 'INR',
    ADD COLUMN IF NOT EXISTS normal_balance VARCHAR,
    ADD COLUMN IF NOT EXISTS allow_manual_posting VARCHAR DEFAULT 'true',
    ADD COLUMN IF NOT EXISTS allow_auto_posting VARCHAR DEFAULT 'true',
    ADD COLUMN IF NOT EXISTS requires_approval VARCHAR DEFAULT 'false',
    ADD COLUMN IF NOT EXISTS freeze_status VARCHAR DEFAULT 'open',
    ADD COLUMN IF NOT EXISTS exchange_gain_loss_account_code VARCHAR,
    ADD COLUMN IF NOT EXISTS revaluation_account_code VARCHAR,
    ADD COLUMN IF NOT EXISTS metadata JSON;

UPDATE gl_accounts
SET base_currency = COALESCE(base_currency, currency, 'INR'),
    freeze_status = COALESCE(freeze_status, 'open'),
    allow_manual_posting = COALESCE(allow_manual_posting, 'true'),
    allow_auto_posting = COALESCE(allow_auto_posting, 'true'),
    requires_approval = COALESCE(requires_approval, 'false');

ALTER TABLE journal_lines
    ADD COLUMN IF NOT EXISTS transaction_currency VARCHAR,
    ADD COLUMN IF NOT EXISTS transaction_amount DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS exchange_rate DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS department_id VARCHAR,
    ADD COLUMN IF NOT EXISTS project_id VARCHAR,
    ADD COLUMN IF NOT EXISTS employee_id VARCHAR,
    ADD COLUMN IF NOT EXISTS product_id VARCHAR,
    ADD COLUMN IF NOT EXISTS business_unit_id VARCHAR;

ALTER TABLE voucher_lines
    ADD COLUMN IF NOT EXISTS department_id VARCHAR,
    ADD COLUMN IF NOT EXISTS project_id VARCHAR,
    ADD COLUMN IF NOT EXISTS employee_id VARCHAR,
    ADD COLUMN IF NOT EXISTS product_id VARCHAR,
    ADD COLUMN IF NOT EXISTS business_unit_id VARCHAR;

ALTER TABLE posting_rules
    ADD COLUMN IF NOT EXISTS version DOUBLE PRECISION DEFAULT 1,
    ADD COLUMN IF NOT EXISTS supersedes_rule_id VARCHAR,
    ADD COLUMN IF NOT EXISTS approval_status VARCHAR DEFAULT 'draft',
    ADD COLUMN IF NOT EXISTS maker_by VARCHAR,
    ADD COLUMN IF NOT EXISTS checker_by VARCHAR,
    ADD COLUMN IF NOT EXISTS finance_head_by VARCHAR,
    ADD COLUMN IF NOT EXISTS approved_by VARCHAR,
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS dependency_rule_ids JSON,
    ADD COLUMN IF NOT EXISTS rollback_strategy VARCHAR DEFAULT 'reverse_journal';

UPDATE posting_rules
SET version = COALESCE(version, 1),
    approval_status = COALESCE(approval_status, CASE WHEN status IN ('active', 'published') THEN 'published' ELSE 'draft' END),
    rollback_strategy = COALESCE(rollback_strategy, 'reverse_journal');

ALTER TABLE posting_execution_logs
    ADD COLUMN IF NOT EXISTS rollback_journal_id VARCHAR;

ALTER TABLE sub_ledger_entries
    ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'active',
    ADD COLUMN IF NOT EXISTS reversal_entry_id VARCHAR,
    ADD COLUMN IF NOT EXISTS reversed_at TIMESTAMP;

UPDATE sub_ledger_entries
SET status = COALESCE(status, 'active');

CREATE TABLE IF NOT EXISTS accounting_periods (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    financial_year VARCHAR NOT NULL,
    period_name VARCHAR NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    branch_id VARCHAR,
    status VARCHAR DEFAULT 'open',
    locked_by VARCHAR,
    unlocked_by VARCHAR,
    approved_by VARCHAR,
    unlock_requested_by VARCHAR,
    lock_reason VARCHAR,
    unlock_reason VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_accounting_periods_tenant_period UNIQUE (tenant_id, financial_year, period_name)
);

CREATE INDEX IF NOT EXISTS ix_accounting_periods_tenant_id ON accounting_periods (tenant_id);
CREATE INDEX IF NOT EXISTS ix_accounting_periods_financial_year ON accounting_periods (financial_year);
CREATE INDEX IF NOT EXISTS ix_accounting_periods_branch_id ON accounting_periods (branch_id);
CREATE INDEX IF NOT EXISTS ix_accounting_periods_status ON accounting_periods (status);
