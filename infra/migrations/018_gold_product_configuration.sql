-- Phase 1: Gold Product Configuration Engine
-- Enables multiple configurable gold loan products with rich business rules

-- Core product definitions
CREATE TABLE IF NOT EXISTS gold_products (
    id UUID PRIMARY KEY,
    product_code VARCHAR(40) UNIQUE NOT NULL,
    product_name VARCHAR(120) NOT NULL,
    product_type VARCHAR(60) NOT NULL, -- jewel_loan, bullet_loan, od, sme, agri, digital, instant
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

CREATE INDEX IF NOT EXISTS idx_gold_products_code ON gold_products(product_code);
CREATE INDEX IF NOT EXISTS idx_gold_products_type ON gold_products(product_type);
CREATE INDEX IF NOT EXISTS idx_gold_products_active ON gold_products(is_active);

-- Interest configuration per product
CREATE TABLE IF NOT EXISTS gold_product_interest (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    interest_type VARCHAR(40) NOT NULL, -- flat, reducing, simple
    rate_type VARCHAR(40) NOT NULL, -- fixed, floating, tiered
    base_rate NUMERIC(8,4) NOT NULL, -- annual percentage
    min_rate NUMERIC(8,4),
    max_rate NUMERIC(8,4),
    penal_interest NUMERIC(8,4) DEFAULT 0,
    compounding_frequency VARCHAR(40), -- daily, monthly, quarterly, none
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id)
);

-- Tenure configuration
CREATE TABLE IF NOT EXISTS gold_product_tenure (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    min_tenure_months INTEGER NOT NULL,
    max_tenure_months INTEGER NOT NULL,
    default_tenure_months INTEGER NOT NULL,
    tenure_unit VARCHAR(20) DEFAULT 'months', -- days, months, years
    renewal_allowed BOOLEAN DEFAULT true,
    max_renewals INTEGER,
    auto_renewal BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id)
);

-- LTV and loan amount limits
CREATE TABLE IF NOT EXISTS gold_product_limits (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    min_loan_amount NUMERIC(18,2) NOT NULL,
    max_loan_amount NUMERIC(18,2) NOT NULL,
    ltv_percent NUMERIC(8,2) NOT NULL DEFAULT 75.00,
    min_ltv NUMERIC(8,2),
    max_ltv NUMERIC(8,2),
    min_gold_weight_grams NUMERIC(12,3) NOT NULL DEFAULT 5.000,
    max_gold_weight_grams NUMERIC(12,3),
    purity_threshold_karat NUMERIC(8,2) DEFAULT 18.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id)
);

-- Charges and fees
CREATE TABLE IF NOT EXISTS gold_product_charges (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    charge_code VARCHAR(40) NOT NULL, -- processing, appraisal, vault, insurance, documentation
    charge_name VARCHAR(120) NOT NULL,
    charge_type VARCHAR(40) NOT NULL, -- flat, percentage, slab
    charge_amount NUMERIC(18,2),
    charge_percentage NUMERIC(8,4),
    min_charge NUMERIC(18,2),
    max_charge NUMERIC(18,2),
    charge_frequency VARCHAR(40), -- one_time, monthly, quarterly, yearly
    is_mandatory BOOLEAN DEFAULT true,
    is_refundable BOOLEAN DEFAULT false,
    tax_applicable BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_product_charges_product ON gold_product_charges(product_id);
CREATE INDEX IF NOT EXISTS idx_gold_product_charges_code ON gold_product_charges(charge_code);

-- Document requirements per product
CREATE TABLE IF NOT EXISTS gold_product_documents (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    document_type VARCHAR(80) NOT NULL, -- aadhar, pan, address_proof, income_proof, photo, etc
    document_name VARCHAR(120) NOT NULL,
    is_mandatory BOOLEAN DEFAULT true,
    verification_required BOOLEAN DEFAULT true,
    document_category VARCHAR(60), -- kyc, income, property, others
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_product_docs_product ON gold_product_documents(product_id);

-- Eligibility rules (customer segment, branch type, etc)
CREATE TABLE IF NOT EXISTS gold_product_eligibility (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    rule_type VARCHAR(60) NOT NULL, -- customer_segment, age, income, cibil, branch_type, geography
    rule_name VARCHAR(120) NOT NULL,
    rule_operator VARCHAR(40) NOT NULL, -- eq, ne, gt, lt, gte, lte, in, not_in, contains
    rule_value JSONB NOT NULL,
    is_mandatory BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_product_eligibility_product ON gold_product_eligibility(product_id);
CREATE INDEX IF NOT EXISTS idx_gold_product_eligibility_type ON gold_product_eligibility(rule_type);

-- Workflow configuration (approval matrix)
CREATE TABLE IF NOT EXISTS gold_product_workflow (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    stage_order INTEGER NOT NULL,
    stage_name VARCHAR(120) NOT NULL,
    stage_type VARCHAR(60) NOT NULL, -- system, user, role, ai
    approver_role VARCHAR(80),
    amount_min NUMERIC(18,2),
    amount_max NUMERIC(18,2),
    sla_hours INTEGER,
    is_parallel BOOLEAN DEFAULT false,
    auto_approve_conditions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_product_workflow_product ON gold_product_workflow(product_id);
CREATE INDEX IF NOT EXISTS idx_gold_product_workflow_order ON gold_product_workflow(product_id, stage_order);

-- Branch and channel eligibility
CREATE TABLE IF NOT EXISTS gold_product_channel (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    channel_type VARCHAR(60) NOT NULL, -- branch, mobile, web, partner, dsa
    is_enabled BOOLEAN DEFAULT true,
    requires_verification BOOLEAN DEFAULT true,
    instant_approval_limit NUMERIC(18,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_product_channel_product ON gold_product_channel(product_id);

-- Tax configuration
CREATE TABLE IF NOT EXISTS gold_product_tax (
    id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES gold_products(id) ON DELETE CASCADE,
    tax_type VARCHAR(60) NOT NULL, -- gst, service_tax, stamp_duty
    tax_name VARCHAR(120) NOT NULL,
    tax_percentage NUMERIC(8,4) NOT NULL,
    tax_category VARCHAR(60), -- interest, charges, both
    hsn_sac_code VARCHAR(40),
    is_active BOOLEAN DEFAULT true,
    effective_from DATE,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_product_tax_product ON gold_product_tax(product_id);

-- Link application to product
ALTER TABLE gold_loan_applications 
ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES gold_products(id);

CREATE INDEX IF NOT EXISTS idx_gold_loan_app_product ON gold_loan_applications(product_id);

COMMENT ON TABLE gold_products IS 'Master table for gold loan product definitions';
COMMENT ON TABLE gold_product_interest IS 'Interest rate configuration per product';
COMMENT ON TABLE gold_product_tenure IS 'Tenure and renewal rules per product';
COMMENT ON TABLE gold_product_limits IS 'LTV, amount and weight limits per product';
COMMENT ON TABLE gold_product_charges IS 'Charges and fees configuration per product';
COMMENT ON TABLE gold_product_documents IS 'Required documents per product';
COMMENT ON TABLE gold_product_eligibility IS 'Customer eligibility rules per product';
COMMENT ON TABLE gold_product_workflow IS 'Approval workflow configuration per product';
COMMENT ON TABLE gold_product_channel IS 'Channel availability per product';
COMMENT ON TABLE gold_product_tax IS 'Tax configuration per product';
