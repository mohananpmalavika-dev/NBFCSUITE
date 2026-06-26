-- Phase 3 Gold Loan specialized product tables.

CREATE TABLE IF NOT EXISTS gold_loan_applications (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    branch_id UUID,
    requested_amount NUMERIC(18,2) NOT NULL,
    gold_rate_per_gram NUMERIC(18,2) NOT NULL,
    ltv_percent NUMERIC(8,2) NOT NULL DEFAULT 75,
    eligible_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
    approved_amount NUMERIC(18,2),
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_loan_customer_id ON gold_loan_applications(customer_id);
CREATE INDEX IF NOT EXISTS idx_gold_loan_branch_id ON gold_loan_applications(branch_id);
CREATE INDEX IF NOT EXISTS idx_gold_loan_status ON gold_loan_applications(status);

CREATE TABLE IF NOT EXISTS gold_ornaments (
    id UUID PRIMARY KEY,
    application_id UUID NOT NULL REFERENCES gold_loan_applications(id),
    ornament_type VARCHAR(80) NOT NULL,
    description TEXT,
    gross_weight_grams NUMERIC(12,3) NOT NULL,
    stone_weight_grams NUMERIC(12,3) NOT NULL DEFAULT 0,
    net_weight_grams NUMERIC(12,3) NOT NULL,
    purity_karat NUMERIC(8,2) NOT NULL DEFAULT 22,
    purity_percent NUMERIC(8,2) NOT NULL DEFAULT 91.6,
    appraised_value NUMERIC(18,2) NOT NULL,
    cataloged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_ornaments_application_id ON gold_ornaments(application_id);

CREATE TABLE IF NOT EXISTS gold_vault_packets (
    id UUID PRIMARY KEY,
    application_id UUID UNIQUE NOT NULL REFERENCES gold_loan_applications(id),
    packet_number VARCHAR(80) UNIQUE NOT NULL,
    branch_id UUID,
    vault_location VARCHAR(120) NOT NULL,
    sealed_by_user_id UUID NOT NULL,
    seal_reference VARCHAR(120) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'stored',
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_vault_packets_branch_id ON gold_vault_packets(branch_id);

CREATE TABLE IF NOT EXISTS gold_auction_cases (
    id UUID PRIMARY KEY,
    application_id UUID NOT NULL REFERENCES gold_loan_applications(id),
    trigger_reason TEXT NOT NULL,
    reserve_price NUMERIC(18,2) NOT NULL,
    auction_date TIMESTAMP NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_auction_application_id ON gold_auction_cases(application_id);
