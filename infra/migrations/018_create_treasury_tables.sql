-- Phase 3 Treasury and Forex tables.

CREATE TABLE IF NOT EXISTS exchange_rates (
    id UUID PRIMARY KEY,
    base_currency VARCHAR(3) NOT NULL,
    quote_currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    buy_rate NUMERIC(18,6) NOT NULL,
    sell_rate NUMERIC(18,6) NOT NULL,
    provider VARCHAR(80) NOT NULL DEFAULT 'manual',
    effective_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exchange_rates_pair ON exchange_rates(base_currency, quote_currency, effective_at DESC);

CREATE TABLE IF NOT EXISTS cash_inventory (
    id UUID PRIMARY KEY,
    branch_id UUID NOT NULL,
    currency VARCHAR(3) NOT NULL,
    cash_on_hand NUMERIC(18,2) NOT NULL DEFAULT 0,
    reserved_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cash_inventory_branch_currency UNIQUE(branch_id, currency)
);

CREATE INDEX IF NOT EXISTS idx_cash_inventory_branch_id ON cash_inventory(branch_id);

CREATE TABLE IF NOT EXISTS forex_transactions (
    id UUID PRIMARY KEY,
    branch_id UUID NOT NULL,
    customer_id UUID,
    transaction_type VARCHAR(20) NOT NULL,
    base_currency VARCHAR(3) NOT NULL,
    quote_currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    base_amount NUMERIC(18,2) NOT NULL,
    quote_amount NUMERIC(18,2) NOT NULL,
    rate_applied NUMERIC(18,6) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'completed',
    reference VARCHAR(120) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_forex_transactions_branch_id ON forex_transactions(branch_id);
CREATE INDEX IF NOT EXISTS idx_forex_transactions_customer_id ON forex_transactions(customer_id);
