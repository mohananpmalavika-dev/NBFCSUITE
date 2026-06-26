-- Migration 009: Create Accounting tables
-- Created: 2026-06-26

CREATE TABLE IF NOT EXISTS gl_accounts (
    id VARCHAR(36) PRIMARY KEY,
    account_code VARCHAR(100) UNIQUE NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(100),
    balance DECIMAL(18, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id VARCHAR(36) PRIMARY KEY,
    entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    reference VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS journal_lines (
    id VARCHAR(36) PRIMARY KEY,
    journal_entry_id VARCHAR(36) NOT NULL,
    gl_account_id VARCHAR(36) NOT NULL,
    debit DECIMAL(18, 2) DEFAULT 0.0,
    credit DECIMAL(18, 2) DEFAULT 0.0,
    description TEXT,
    FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (gl_account_id) REFERENCES gl_accounts(id)
);

CREATE TABLE IF NOT EXISTS bank_statement_transactions (
    id VARCHAR(36) PRIMARY KEY,
    reference VARCHAR(255) NOT NULL,
    transaction_date TIMESTAMP,
    amount DECIMAL(18, 2),
    description TEXT,
    status VARCHAR(50) DEFAULT 'unmatched',
    matched_journal_id VARCHAR(36),
    FOREIGN KEY (matched_journal_id) REFERENCES journal_entries(id)
);

CREATE INDEX IF NOT EXISTS idx_gl_accounts_account_code ON gl_accounts(account_code);
CREATE INDEX IF NOT EXISTS idx_journal_lines_entry_id ON journal_lines(journal_entry_id);
CREATE INDEX IF NOT EXISTS idx_journal_lines_gl_account_id ON journal_lines(gl_account_id);
CREATE INDEX IF NOT EXISTS idx_bank_statement_transactions_reference ON bank_statement_transactions(reference);
CREATE INDEX IF NOT EXISTS idx_bank_statement_transactions_date ON bank_statement_transactions(transaction_date);
