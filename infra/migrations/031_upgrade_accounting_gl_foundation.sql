-- Migration 031: Upgrade Accounting and GL foundation
-- Created: 2026-06-28

ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS parent_account_id VARCHAR(36);
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS category VARCHAR(100);
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'INR';
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS branch_id VARCHAR(36);
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS branch_specific VARCHAR(20) DEFAULT 'false';
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS posting_allowed VARCHAR(20) DEFAULT 'true';
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS opening_balance DECIMAL(18, 2) DEFAULT 0.0;
ALTER TABLE gl_accounts ADD COLUMN IF NOT EXISTS financial_year VARCHAR(20);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_gl_accounts_parent_account_id') THEN
        ALTER TABLE gl_accounts
            ADD CONSTRAINT fk_gl_accounts_parent_account_id FOREIGN KEY (parent_account_id) REFERENCES gl_accounts(id) ON DELETE SET NULL;
    END IF;
END $$;

ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS business_date TIMESTAMP;
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS financial_year VARCHAR(20);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS branch_id VARCHAR(36);
ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS voucher_id VARCHAR(36);

ALTER TABLE journal_lines ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'INR';
ALTER TABLE journal_lines ADD COLUMN IF NOT EXISTS branch_id VARCHAR(36);
ALTER TABLE journal_lines ADD COLUMN IF NOT EXISTS cost_center VARCHAR(100);
ALTER TABLE journal_lines ADD COLUMN IF NOT EXISTS profit_center VARCHAR(100);

CREATE TABLE IF NOT EXISTS gl_balances (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    gl_account_id VARCHAR(36) NOT NULL,
    branch_id VARCHAR(36),
    currency VARCHAR(10) DEFAULT 'INR',
    financial_year VARCHAR(20) NOT NULL,
    opening_balance DECIMAL(18, 2) DEFAULT 0.0,
    total_debit DECIMAL(18, 2) DEFAULT 0.0,
    total_credit DECIMAL(18, 2) DEFAULT 0.0,
    closing_balance DECIMAL(18, 2) DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gl_account_id) REFERENCES gl_accounts(id) ON DELETE CASCADE
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_gl_balances_scope') THEN
        ALTER TABLE gl_balances
            ADD CONSTRAINT uq_gl_balances_scope UNIQUE (tenant_id, gl_account_id, branch_id, currency, financial_year);
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS vouchers (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    voucher_number VARCHAR(100) NOT NULL,
    voucher_type VARCHAR(50) NOT NULL,
    voucher_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    reference VARCHAR(255),
    branch_id VARCHAR(36),
    currency VARCHAR(10) DEFAULT 'INR',
    status VARCHAR(50) DEFAULT 'draft',
    created_by VARCHAR(100),
    verified_by VARCHAR(100),
    approved_by VARCHAR(100),
    posted_journal_entry_id VARCHAR(36),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (posted_journal_entry_id) REFERENCES journal_entries(id)
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_vouchers_tenant_number') THEN
        ALTER TABLE vouchers
            ADD CONSTRAINT uq_vouchers_tenant_number UNIQUE (tenant_id, voucher_number);
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS voucher_lines (
    id VARCHAR(36) PRIMARY KEY,
    voucher_id VARCHAR(36) NOT NULL,
    gl_account_id VARCHAR(36) NOT NULL,
    debit DECIMAL(18, 2) DEFAULT 0.0,
    credit DECIMAL(18, 2) DEFAULT 0.0,
    description TEXT,
    cost_center VARCHAR(100),
    profit_center VARCHAR(100),
    FOREIGN KEY (voucher_id) REFERENCES vouchers(id) ON DELETE CASCADE,
    FOREIGN KEY (gl_account_id) REFERENCES gl_accounts(id)
);

CREATE TABLE IF NOT EXISTS day_end_closes (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    business_date TIMESTAMP NOT NULL,
    branch_id VARCHAR(36),
    status VARCHAR(50) DEFAULT 'closed',
    trial_balance_debit DECIMAL(18, 2) DEFAULT 0.0,
    trial_balance_credit DECIMAL(18, 2) DEFAULT 0.0,
    is_balanced VARCHAR(20) DEFAULT 'true',
    checks JSONB,
    closed_by VARCHAR(100),
    closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uq_day_end_tenant_date_branch') THEN
        ALTER TABLE day_end_closes
            ADD CONSTRAINT uq_day_end_tenant_date_branch UNIQUE (tenant_id, business_date, branch_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_gl_accounts_parent ON gl_accounts(parent_account_id);
CREATE INDEX IF NOT EXISTS idx_gl_accounts_branch ON gl_accounts(branch_id);
CREATE INDEX IF NOT EXISTS idx_gl_accounts_status ON gl_accounts(status);
CREATE INDEX IF NOT EXISTS idx_journal_entries_branch_id ON journal_entries(branch_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_voucher_id ON journal_entries(voucher_id);
CREATE INDEX IF NOT EXISTS idx_journal_lines_branch_id ON journal_lines(branch_id);
CREATE INDEX IF NOT EXISTS idx_gl_balances_tenant_id ON gl_balances(tenant_id);
CREATE INDEX IF NOT EXISTS idx_gl_balances_scope ON gl_balances(tenant_id, financial_year, branch_id);
CREATE INDEX IF NOT EXISTS idx_vouchers_tenant_id ON vouchers(tenant_id);
CREATE INDEX IF NOT EXISTS idx_vouchers_status ON vouchers(status);
CREATE INDEX IF NOT EXISTS idx_vouchers_type ON vouchers(voucher_type);
CREATE INDEX IF NOT EXISTS idx_voucher_lines_voucher_id ON voucher_lines(voucher_id);
CREATE INDEX IF NOT EXISTS idx_day_end_tenant_id ON day_end_closes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_day_end_business_date ON day_end_closes(business_date);
