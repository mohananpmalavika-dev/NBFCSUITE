-- Migration 010: Create Deposits tables
-- Created: 2026-06-26

CREATE TABLE IF NOT EXISTS deposit_types (
    id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    interest_rate DECIMAL(5, 2),
    min_balance DECIMAL(18, 2),
    tenor_months INTEGER,
    payout_frequency VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deposit_accounts (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    deposit_type_id VARCHAR(36) NOT NULL,
    account_number VARCHAR(100) UNIQUE NOT NULL,
    principal_amount DECIMAL(18, 2),
    current_balance DECIMAL(18, 2),
    interest_rate DECIMAL(5, 2),
    start_date TIMESTAMP,
    maturity_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deposit_type_id) REFERENCES deposit_types(id)
);

CREATE TABLE IF NOT EXISTS deposit_transactions (
    id VARCHAR(36) PRIMARY KEY,
    deposit_account_id VARCHAR(36) NOT NULL,
    transaction_type VARCHAR(50),
    amount DECIMAL(18, 2),
    running_balance DECIMAL(18, 2),
    description TEXT,
    reference VARCHAR(100),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deposit_account_id) REFERENCES deposit_accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS standing_instructions (
    id VARCHAR(36) PRIMARY KEY,
    deposit_account_id VARCHAR(36) NOT NULL,
    instruction_type VARCHAR(100),
    amount DECIMAL(18, 2),
    frequency VARCHAR(50),
    next_run_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deposit_account_id) REFERENCES deposit_accounts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_deposit_accounts_customer_id ON deposit_accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_deposit_accounts_deposit_type_id ON deposit_accounts(deposit_type_id);
CREATE INDEX IF NOT EXISTS idx_deposit_transactions_account_id ON deposit_transactions(deposit_account_id);
CREATE INDEX IF NOT EXISTS idx_deposit_transactions_reference ON deposit_transactions(reference);
CREATE INDEX IF NOT EXISTS idx_deposit_transactions_date ON deposit_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_standing_instructions_account_id ON standing_instructions(deposit_account_id);
