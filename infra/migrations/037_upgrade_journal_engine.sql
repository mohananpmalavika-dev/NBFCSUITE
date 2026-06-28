-- Phase 3: enterprise Journal Engine.
-- Journals are permanent accounting documents; reversal and cancellation are state transitions.

CREATE TABLE IF NOT EXISTS journal_batches (
    id VARCHAR PRIMARY KEY,
    batch_no VARCHAR NOT NULL,
    tenant_id VARCHAR NOT NULL,
    posting_date TIMESTAMP NOT NULL,
    financial_year VARCHAR NOT NULL,
    period VARCHAR NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'draft',
    created_by VARCHAR,
    approved_by VARCHAR,
    total_amount DOUBLE PRECISION NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_journal_batches_tenant_number UNIQUE (tenant_id, batch_no),
    CONSTRAINT ck_journal_batches_status CHECK (status IN ('draft', 'pending', 'approved', 'posted', 'closed', 'cancelled'))
);

CREATE TABLE IF NOT EXISTS journal_number_counters (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    financial_year VARCHAR NOT NULL,
    sequence_type VARCHAR NOT NULL,
    current_value INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT uq_journal_number_counter_scope UNIQUE (tenant_id, financial_year, sequence_type)
);

ALTER TABLE journal_entries
    ADD COLUMN IF NOT EXISTS batch_id VARCHAR,
    ADD COLUMN IF NOT EXISTS journal_no VARCHAR,
    ADD COLUMN IF NOT EXISTS voucher_type VARCHAR DEFAULT 'journal',
    ADD COLUMN IF NOT EXISTS period VARCHAR,
    ADD COLUMN IF NOT EXISTS currency VARCHAR DEFAULT 'INR',
    ADD COLUMN IF NOT EXISTS exchange_rate DOUBLE PRECISION DEFAULT 1,
    ADD COLUMN IF NOT EXISTS reversal_of VARCHAR,
    ADD COLUMN IF NOT EXISTS created_by VARCHAR,
    ADD COLUMN IF NOT EXISTS approved_by VARCHAR,
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP,
    ADD COLUMN IF NOT EXISTS validation_result JSON,
    ADD COLUMN IF NOT EXISTS template_id VARCHAR;

UPDATE journal_entries
SET voucher_type = COALESCE(voucher_type, 'journal'),
    currency = COALESCE(currency, 'INR'),
    exchange_rate = COALESCE(exchange_rate, 1),
    posting_status = COALESCE(posting_status, 'posted');

ALTER TABLE journal_lines
    ADD COLUMN IF NOT EXISTS sequence INTEGER DEFAULT 1;

CREATE TABLE IF NOT EXISTS journal_attachments (
    id VARCHAR PRIMARY KEY,
    journal_id VARCHAR NOT NULL REFERENCES journal_entries(id),
    document_id VARCHAR,
    file_name VARCHAR NOT NULL,
    uploaded_by VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journal_approvals (
    id VARCHAR PRIMARY KEY,
    journal_id VARCHAR NOT NULL REFERENCES journal_entries(id),
    level VARCHAR NOT NULL,
    approver VARCHAR NOT NULL,
    decision VARCHAR NOT NULL,
    remarks VARCHAR,
    approved_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_journal_approval_decision CHECK (decision IN ('submitted', 'approved', 'rejected'))
);

CREATE TABLE IF NOT EXISTS journal_templates (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    template_name VARCHAR NOT NULL,
    description VARCHAR,
    voucher_type VARCHAR DEFAULT 'journal',
    currency VARCHAR DEFAULT 'INR',
    lines JSON NOT NULL,
    status VARCHAR DEFAULT 'active',
    created_by VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_journal_templates_tenant_name UNIQUE (tenant_id, template_name)
);

CREATE TABLE IF NOT EXISTS accounting_dimensions (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    dimension_type VARCHAR NOT NULL,
    code VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_accounting_dimensions_scope UNIQUE (tenant_id, dimension_type, code)
);

CREATE TABLE IF NOT EXISTS accounting_budgets (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    financial_year VARCHAR NOT NULL,
    period VARCHAR NOT NULL,
    gl_account_id VARCHAR NOT NULL REFERENCES gl_accounts(id),
    cost_center VARCHAR,
    amount DOUBLE PRECISION NOT NULL,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_accounting_budgets_scope UNIQUE (tenant_id, financial_year, period, gl_account_id, cost_center),
    CONSTRAINT ck_accounting_budget_amount CHECK (amount >= 0)
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_journal_entries_batch') THEN
        ALTER TABLE journal_entries ADD CONSTRAINT fk_journal_entries_batch
            FOREIGN KEY (batch_id) REFERENCES journal_batches(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_journal_entries_reversal') THEN
        ALTER TABLE journal_entries ADD CONSTRAINT fk_journal_entries_reversal
            FOREIGN KEY (reversal_of) REFERENCES journal_entries(id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_journal_entries_tenant_number') THEN
        ALTER TABLE journal_entries ADD CONSTRAINT uq_journal_entries_tenant_number
            UNIQUE (tenant_id, journal_no);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_journal_batches_tenant_status ON journal_batches (tenant_id, status, posting_date DESC);
CREATE INDEX IF NOT EXISTS ix_journal_entries_tenant_status_date ON journal_entries (tenant_id, posting_status, entry_date DESC);
CREATE INDEX IF NOT EXISTS ix_journal_entries_batch_id ON journal_entries (batch_id);
CREATE INDEX IF NOT EXISTS ix_journal_entries_journal_no ON journal_entries (journal_no);
CREATE INDEX IF NOT EXISTS ix_journal_entries_reversal_of ON journal_entries (reversal_of);
CREATE INDEX IF NOT EXISTS ix_journal_attachments_journal_id ON journal_attachments (journal_id);
CREATE INDEX IF NOT EXISTS ix_journal_approvals_journal_time ON journal_approvals (journal_id, approved_time);
CREATE INDEX IF NOT EXISTS ix_journal_templates_tenant_status ON journal_templates (tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_accounting_dimensions_lookup ON accounting_dimensions (tenant_id, dimension_type, code, status);
CREATE INDEX IF NOT EXISTS ix_accounting_budgets_lookup ON accounting_budgets (tenant_id, financial_year, period, gl_account_id, cost_center, status);
