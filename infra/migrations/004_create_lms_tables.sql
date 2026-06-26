-- Migration 004: Create LMS (Loan Management System) tables
-- Created: 2026-06-26

-- Disbursement / Loan accounts
CREATE TABLE IF NOT EXISTS loan_accounts (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) NOT NULL UNIQUE,
    customer_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    loan_account_number VARCHAR(50) UNIQUE NOT NULL,
    sanction_amount DECIMAL(15, 2) NOT NULL,
    disbursed_amount DECIMAL(15, 2) DEFAULT 0,
    tenure_months INTEGER NOT NULL,
    interest_rate DECIMAL(5, 3) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    emi_amount DECIMAL(15, 2) NOT NULL,
    outstanding_principal DECIMAL(15, 2),
    outstanding_interest DECIMAL(15, 2),
    status VARCHAR(50) DEFAULT 'active', -- active, closed, foreclosed, npa, moratorium
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES loan_products(id)
);

-- EMI Schedule
CREATE TABLE IF NOT EXISTS emi_schedule (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL,
    emi_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    emi_amount DECIMAL(15, 2),
    principal_amount DECIMAL(15, 2),
    interest_amount DECIMAL(15, 2),
    penalty_amount DECIMAL(15, 2) DEFAULT 0,
    paid_date DATE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, paid, overdue, waived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id) ON DELETE CASCADE,
    UNIQUE(loan_account_id, emi_number)
);

-- Payment transactions
CREATE TABLE IF NOT EXISTS payment_transactions (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_mode VARCHAR(50), -- upi, neft, check, cash, auto_debit
    amount DECIMAL(15, 2) NOT NULL,
    principal_paid DECIMAL(15, 2),
    interest_paid DECIMAL(15, 2),
    penalty_paid DECIMAL(15, 2),
    transaction_reference VARCHAR(100),
    payment_status VARCHAR(50), -- success, pending, failed, reversed
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id)
);

-- Loan modifications (top-up, restructuring, etc.)
CREATE TABLE IF NOT EXISTS loan_modifications (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL,
    modification_type VARCHAR(50), -- topup, restructure, foreclosure, moratorium
    modification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    additional_amount DECIMAL(15, 2),
    new_tenure_months INTEGER,
    new_emi_amount DECIMAL(15, 2),
    approval_status VARCHAR(50),
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id)
);

-- Charges & Penalties
CREATE TABLE IF NOT EXISTS loan_charges (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL,
    charge_type VARCHAR(50), -- late_fee, processing_fee, prepayment_penalty
    charge_amount DECIMAL(15, 2),
    charge_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recovery_status VARCHAR(50) DEFAULT 'pending', -- pending, recovered, waived
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id)
);

-- Create indexes
CREATE INDEX idx_loan_accounts_customer_id ON loan_accounts(customer_id);
CREATE INDEX idx_loan_accounts_status ON loan_accounts(status);
CREATE INDEX idx_loan_accounts_account_number ON loan_accounts(loan_account_number);
CREATE INDEX idx_emi_schedule_loan_account_id ON emi_schedule(loan_account_id);
CREATE INDEX idx_emi_schedule_due_date ON emi_schedule(due_date);
CREATE INDEX idx_emi_schedule_status ON emi_schedule(status);
CREATE INDEX idx_payment_transactions_loan_account_id ON payment_transactions(loan_account_id);
CREATE INDEX idx_payment_transactions_date ON payment_transactions(transaction_date);
CREATE INDEX idx_loan_modifications_loan_account_id ON loan_modifications(loan_account_id);
