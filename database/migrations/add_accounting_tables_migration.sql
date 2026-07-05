-- ============================================================================
-- NBFC Financial Suite - Accounting Module Migration
-- Description: Create all accounting tables for double-entry bookkeeping
-- Version: 1.0
-- Date: 2026-01-05
-- ============================================================================

-- ============================================================================
-- Chart of Accounts (CoA)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chart_of_accounts (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Account identification
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('asset', 'liability', 'equity', 'income', 'expense')),
    account_sub_type VARCHAR(50) NOT NULL,
    
    -- Hierarchy
    parent_account_id INTEGER REFERENCES chart_of_accounts(id),
    level INTEGER DEFAULT 1 CHECK (level >= 1 AND level <= 5),
    is_group BOOLEAN DEFAULT FALSE,
    
    -- Properties
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    allow_manual_entry BOOLEAN DEFAULT TRUE,
    
    -- Balance tracking
    opening_balance NUMERIC(15, 2) DEFAULT 0.00,
    current_balance NUMERIC(15, 2) DEFAULT 0.00,
    debit_balance NUMERIC(15, 2) DEFAULT 0.00,
    credit_balance NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Description
    description TEXT,
    notes TEXT,
    
    -- Audit fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    
    CONSTRAINT uk_coa_tenant_code UNIQUE (tenant_id, account_code)
);

CREATE INDEX idx_coa_tenant_id ON chart_of_accounts(tenant_id);
CREATE INDEX idx_coa_account_code ON chart_of_accounts(account_code);
CREATE INDEX idx_coa_account_type ON chart_of_accounts(tenant_id, account_type);
CREATE INDEX idx_coa_parent ON chart_of_accounts(parent_account_id);
CREATE INDEX idx_coa_is_active ON chart_of_accounts(is_active);

COMMENT ON TABLE chart_of_accounts IS 'Master list of all general ledger accounts';

-- ============================================================================
-- Journal Entries Header
-- ============================================================================
CREATE TABLE IF NOT EXISTS journal_entries (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Entry identification
    entry_number VARCHAR(50) NOT NULL UNIQUE,
    entry_date DATE NOT NULL,
    posting_date DATE,
    
    -- Entry classification
    entry_type VARCHAR(30) NOT NULL DEFAULT 'manual',
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'posted', 'reversed', 'void')),
    
    -- Reference
    reference_type VARCHAR(50),
    reference_id INTEGER,
    reference_number VARCHAR(100),
    
    -- Description
    narration TEXT NOT NULL,
    internal_notes TEXT,
    
    -- Totals (must balance)
    total_debit NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    total_credit NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    
    -- Reversal support
    is_reversal BOOLEAN DEFAULT FALSE,
    reversed_entry_id INTEGER REFERENCES journal_entries(id),
    reversal_date DATE,
    
    -- Approval
    approved_by INTEGER,
    approved_at TIMESTAMP,
    
    -- Audit fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    
    CONSTRAINT chk_je_balanced CHECK (total_debit >= 0 AND total_credit >= 0)
);

CREATE INDEX idx_je_tenant_id ON journal_entries(tenant_id);
CREATE INDEX idx_je_entry_number ON journal_entries(entry_number);
CREATE INDEX idx_je_entry_date ON journal_entries(tenant_id, entry_date);
CREATE INDEX idx_je_status ON journal_entries(status);
CREATE INDEX idx_je_reference ON journal_entries(reference_type, reference_id);
CREATE INDEX idx_je_created_at ON journal_entries(created_at);

COMMENT ON TABLE journal_entries IS 'Journal entry headers grouping related debits and credits';

-- ============================================================================
-- Journal Entry Line Items
-- ============================================================================
CREATE TABLE IF NOT EXISTS journal_entry_lines (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Link to header
    journal_entry_id INTEGER NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    
    -- Account link
    account_id INTEGER NOT NULL REFERENCES chart_of_accounts(id),
    account_code VARCHAR(20) NOT NULL,
    
    -- Debit or Credit
    debit_amount NUMERIC(15, 2) DEFAULT 0.00,
    credit_amount NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Description
    description VARCHAR(500),
    
    -- Cost center / department
    cost_center VARCHAR(50),
    department VARCHAR(50),
    
    -- Reference to source
    transaction_type VARCHAR(50),
    transaction_id INTEGER,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_jel_debit_or_credit CHECK (
        (debit_amount > 0 AND credit_amount = 0) OR 
        (credit_amount > 0 AND debit_amount = 0)
    )
);

CREATE INDEX idx_jel_journal_entry ON journal_entry_lines(journal_entry_id, line_number);
CREATE INDEX idx_jel_account ON journal_entry_lines(account_id);
CREATE INDEX idx_jel_tenant ON journal_entry_lines(tenant_id);

COMMENT ON TABLE journal_entry_lines IS 'Individual debit/credit lines within journal entries';

-- ============================================================================
-- General Ledger
-- ============================================================================
CREATE TABLE IF NOT EXISTS general_ledger (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Account reference
    account_id INTEGER NOT NULL REFERENCES chart_of_accounts(id),
    account_code VARCHAR(20) NOT NULL,
    
    -- Transaction details
    transaction_date DATE NOT NULL,
    posting_date DATE NOT NULL,
    
    -- Journal entry reference
    journal_entry_id INTEGER NOT NULL REFERENCES journal_entries(id),
    journal_entry_number VARCHAR(50) NOT NULL,
    line_item_id INTEGER NOT NULL REFERENCES journal_entry_lines(id),
    
    -- Amounts
    debit_amount NUMERIC(15, 2) DEFAULT 0.00,
    credit_amount NUMERIC(15, 2) DEFAULT 0.00,
    balance NUMERIC(15, 2) NOT NULL,
    
    -- Description
    description TEXT,
    narration TEXT,
    
    -- Reference to source document
    reference_type VARCHAR(50),
    reference_id INTEGER,
    reference_number VARCHAR(100),
    
    -- Financial period
    financial_year INTEGER NOT NULL,
    financial_period VARCHAR(20) NOT NULL,
    
    -- Cost center
    cost_center VARCHAR(50),
    department VARCHAR(50),
    
    -- Reconciliation
    is_reconciled BOOLEAN DEFAULT FALSE,
    reconciled_date DATE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL
);

CREATE INDEX idx_gl_tenant_id ON general_ledger(tenant_id);
CREATE INDEX idx_gl_account_date ON general_ledger(account_id, transaction_date);
CREATE INDEX idx_gl_tenant_account ON general_ledger(tenant_id, account_id);
CREATE INDEX idx_gl_posting_date ON general_ledger(posting_date);
CREATE INDEX idx_gl_period ON general_ledger(financial_year, financial_period);
CREATE INDEX idx_gl_reference ON general_ledger(reference_type, reference_id);
CREATE INDEX idx_gl_je ON general_ledger(journal_entry_id);

COMMENT ON TABLE general_ledger IS 'Posted journal entries - master record of all transactions';

-- ============================================================================
-- Trial Balance Snapshots
-- ============================================================================
CREATE TABLE IF NOT EXISTS trial_balances (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Period identification
    balance_date DATE NOT NULL,
    financial_year INTEGER NOT NULL,
    financial_period VARCHAR(20) NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('monthly', 'quarterly', 'half_yearly', 'yearly')),
    
    -- Account reference
    account_id INTEGER NOT NULL REFERENCES chart_of_accounts(id),
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    
    -- Balances
    opening_balance NUMERIC(15, 2) DEFAULT 0.00,
    total_debit NUMERIC(15, 2) DEFAULT 0.00,
    total_credit NUMERIC(15, 2) DEFAULT 0.00,
    closing_balance NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Debit or Credit nature
    debit_balance NUMERIC(15, 2) DEFAULT 0.00,
    credit_balance NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Status
    is_finalized BOOLEAN DEFAULT FALSE,
    finalized_at TIMESTAMP,
    finalized_by INTEGER,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    
    CONSTRAINT uk_tb_tenant_date_account UNIQUE (tenant_id, balance_date, account_id)
);

CREATE INDEX idx_tb_tenant_date ON trial_balances(tenant_id, balance_date);
CREATE INDEX idx_tb_period ON trial_balances(financial_year, financial_period);
CREATE INDEX idx_tb_account ON trial_balances(account_id);

COMMENT ON TABLE trial_balances IS 'Periodic snapshots of account balances';

-- ============================================================================
-- Accounting Periods
-- ============================================================================
CREATE TABLE IF NOT EXISTS accounting_periods (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Period identification
    period_name VARCHAR(100) NOT NULL,
    period_code VARCHAR(20) NOT NULL,
    financial_year INTEGER NOT NULL,
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('monthly', 'quarterly', 'half_yearly', 'yearly')),
    
    -- Date range
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT FALSE,
    is_closed BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    
    -- Closing process
    closed_at TIMESTAMP,
    closed_by INTEGER,
    locked_at TIMESTAMP,
    locked_by INTEGER,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    updated_by INTEGER,
    
    CONSTRAINT uk_ap_tenant_code UNIQUE (tenant_id, period_code)
);

CREATE INDEX idx_ap_tenant_code ON accounting_periods(tenant_id, period_code);
CREATE INDEX idx_ap_dates ON accounting_periods(start_date, end_date);
CREATE INDEX idx_ap_year ON accounting_periods(financial_year);
CREATE INDEX idx_ap_active ON accounting_periods(is_active);

COMMENT ON TABLE accounting_periods IS 'Manages financial period opening, closing, and locking';

-- ============================================================================
-- Insert Default Chart of Accounts (System Accounts)
-- ============================================================================

-- Asset Accounts
INSERT INTO chart_of_accounts (tenant_id, account_code, account_name, account_type, account_sub_type, level, is_group, is_system, opening_balance, created_by)
VALUES 
(1, '1000', 'Assets', 'asset', 'current_asset', 1, TRUE, TRUE, 0.00, 1),
(1, '1001', 'Cash and Bank', 'asset', 'cash_bank', 2, FALSE, TRUE, 0.00, 1),
(1, '1100', 'Loan Assets', 'asset', 'loan_asset', 2, FALSE, TRUE, 0.00, 1),
(1, '1105', 'Interest Receivable', 'asset', 'current_asset', 2, FALSE, TRUE, 0.00, 1);

-- Liability Accounts
INSERT INTO chart_of_accounts (tenant_id, account_code, account_name, account_type, account_sub_type, level, is_group, is_system, opening_balance, created_by)
VALUES 
(1, '2000', 'Liabilities', 'liability', 'current_liability', 1, TRUE, TRUE, 0.00, 1),
(1, '2100', 'Customer Deposits', 'liability', 'deposit', 2, FALSE, TRUE, 0.00, 1),
(1, '2200', 'Borrowings', 'liability', 'borrowing', 2, FALSE, TRUE, 0.00, 1);

-- Equity Accounts
INSERT INTO chart_of_accounts (tenant_id, account_code, account_name, account_type, account_sub_type, level, is_group, is_system, opening_balance, created_by)
VALUES 
(1, '3000', 'Equity', 'equity', 'capital', 1, TRUE, TRUE, 0.00, 1),
(1, '3100', 'Share Capital', 'equity', 'capital', 2, FALSE, TRUE, 0.00, 1),
(1, '3200', 'Retained Earnings', 'equity', 'retained_earnings', 2, FALSE, TRUE, 0.00, 1);

-- Income Accounts
INSERT INTO chart_of_accounts (tenant_id, account_code, account_name, account_type, account_sub_type, level, is_group, is_system, opening_balance, created_by)
VALUES 
(1, '4000', 'Income', 'income', 'interest_income', 1, TRUE, TRUE, 0.00, 1),
(1, '4001', 'Interest Income on Loans', 'income', 'interest_income', 2, FALSE, TRUE, 0.00, 1),
(1, '4010', 'Fee and Commission Income', 'income', 'fee_income', 2, FALSE, TRUE, 0.00, 1),
(1, '4020', 'Other Income', 'income', 'other_income', 2, FALSE, TRUE, 0.00, 1);

-- Expense Accounts
INSERT INTO chart_of_accounts (tenant_id, account_code, account_name, account_type, account_sub_type, level, is_group, is_system, opening_balance, created_by)
VALUES 
(1, '5000', 'Expenses', 'expense', 'operating_expense', 1, TRUE, TRUE, 0.00, 1),
(1, '5100', 'Interest Expense', 'expense', 'interest_expense', 2, FALSE, TRUE, 0.00, 1),
(1, '5200', 'Operating Expenses', 'expense', 'operating_expense', 2, FALSE, TRUE, 0.00, 1),
(1, '5300', 'Administrative Expenses', 'expense', 'administrative_expense', 2, FALSE, TRUE, 0.00, 1);

-- ============================================================================
-- Grant Permissions
-- ============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nbfc_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nbfc_app;

-- ============================================================================
-- Migration Complete
-- ============================================================================
COMMENT ON SCHEMA public IS 'NBFC Accounting Module - Migration completed successfully';
