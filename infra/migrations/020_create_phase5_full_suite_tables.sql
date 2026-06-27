-- Migration 020: Phase 5 full suite and continuous improvement tables
-- Created: 2026-06-27

-- Wealth Management: mutual funds, SIPs, and portfolio transactions.
CREATE TABLE IF NOT EXISTS wealth_mutual_fund_schemes (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    scheme_code VARCHAR(100) NOT NULL,
    scheme_name VARCHAR(255) NOT NULL,
    fund_house VARCHAR(255),
    category VARCHAR(100),
    risk_level VARCHAR(50) DEFAULT 'moderate',
    nav DECIMAL(18, 6) DEFAULT 10.0,
    expense_ratio DECIMAL(9, 4) DEFAULT 0.0,
    is_active VARCHAR(20) DEFAULT 'true',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_wealth_scheme_tenant_code UNIQUE (tenant_id, scheme_code)
);

CREATE TABLE IF NOT EXISTS wealth_investments (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    scheme_id VARCHAR(36) NOT NULL,
    transaction_type VARCHAR(50) DEFAULT 'purchase',
    amount DECIMAL(18, 2) DEFAULT 0.0,
    nav DECIMAL(18, 6) DEFAULT 0.0,
    units DECIMAL(18, 6) DEFAULT 0.0,
    folio_number VARCHAR(100),
    reference VARCHAR(100),
    status VARCHAR(50) DEFAULT 'posted',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wealth_sip_mandates (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    scheme_id VARCHAR(36) NOT NULL,
    amount DECIMAL(18, 2),
    frequency VARCHAR(50) DEFAULT 'monthly',
    start_date TIMESTAMP,
    next_run_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wealth_schemes_tenant_id ON wealth_mutual_fund_schemes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_wealth_schemes_tenant_code ON wealth_mutual_fund_schemes(tenant_id, scheme_code);
CREATE INDEX IF NOT EXISTS idx_wealth_investments_tenant_customer ON wealth_investments(tenant_id, customer_id);
CREATE INDEX IF NOT EXISTS idx_wealth_investments_scheme_id ON wealth_investments(scheme_id);
CREATE INDEX IF NOT EXISTS idx_wealth_sips_tenant_customer ON wealth_sip_mandates(tenant_id, customer_id);

-- Insurance: policies, premium collection, and claims.
CREATE TABLE IF NOT EXISTS insurance_policies (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    policy_number VARCHAR(100) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    product_type VARCHAR(100),
    insurer_name VARCHAR(255),
    sum_assured DECIMAL(18, 2),
    premium_amount DECIMAL(18, 2),
    premium_frequency VARCHAR(50) DEFAULT 'monthly',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    next_premium_due_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_insurance_policy_tenant_number UNIQUE (tenant_id, policy_number)
);

CREATE TABLE IF NOT EXISTS insurance_premium_payments (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    policy_id VARCHAR(36) NOT NULL,
    amount DECIMAL(18, 2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_mode VARCHAR(50),
    reference VARCHAR(100),
    status VARCHAR(50) DEFAULT 'success'
);

CREATE TABLE IF NOT EXISTS insurance_claims (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    policy_id VARCHAR(36) NOT NULL,
    claim_number VARCHAR(100),
    claim_type VARCHAR(100),
    claim_amount DECIMAL(18, 2),
    approved_amount DECIMAL(18, 2),
    incident_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'submitted',
    documents JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insurance_policies_tenant_customer ON insurance_policies(tenant_id, customer_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_status ON insurance_policies(status);
CREATE INDEX IF NOT EXISTS idx_insurance_payments_tenant_policy ON insurance_premium_payments(tenant_id, policy_id);
CREATE INDEX IF NOT EXISTS idx_insurance_claims_tenant_policy ON insurance_claims(tenant_id, policy_id);
CREATE INDEX IF NOT EXISTS idx_insurance_claims_status ON insurance_claims(status);

-- Procurement and vendor management.
CREATE TABLE IF NOT EXISTS procurement_vendors (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    vendor_code VARCHAR(100) NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    phone VARCHAR(50),
    gstin VARCHAR(50),
    payment_terms VARCHAR(50) DEFAULT 'net_30',
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vendor_tenant_code UNIQUE (tenant_id, vendor_code)
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    po_number VARCHAR(100) NOT NULL,
    vendor_id VARCHAR(36) NOT NULL,
    department VARCHAR(100),
    requested_by VARCHAR(100),
    items JSONB NOT NULL,
    subtotal DECIMAL(18, 2) DEFAULT 0.0,
    tax_amount DECIMAL(18, 2) DEFAULT 0.0,
    total_amount DECIMAL(18, 2) DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    CONSTRAINT uq_po_tenant_number UNIQUE (tenant_id, po_number)
);

CREATE TABLE IF NOT EXISTS goods_receipts (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    po_id VARCHAR(36) NOT NULL,
    received_by VARCHAR(100),
    received_items JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'received',
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendor_invoices (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    vendor_id VARCHAR(36) NOT NULL,
    po_id VARCHAR(36),
    invoice_number VARCHAR(100) NOT NULL,
    invoice_date TIMESTAMP,
    amount DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2) DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'submitted',
    payment_reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vendor_invoice_tenant_number UNIQUE (tenant_id, invoice_number)
);

CREATE INDEX IF NOT EXISTS idx_procurement_vendors_tenant_id ON procurement_vendors(tenant_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_tenant_vendor ON purchase_orders(tenant_id, vendor_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_goods_receipts_tenant_po ON goods_receipts(tenant_id, po_id);
CREATE INDEX IF NOT EXISTS idx_vendor_invoices_tenant_vendor ON vendor_invoices(tenant_id, vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendor_invoices_status ON vendor_invoices(status);

-- HRMS payroll.
ALTER TABLE employees ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_tenant_id ON employees(tenant_id);

CREATE TABLE IF NOT EXISTS payroll_runs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    run_name VARCHAR(255),
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft',
    gross_pay DECIMAL(18, 2) DEFAULT 0.0,
    total_deductions DECIMAL(18, 2) DEFAULT 0.0,
    net_pay DECIMAL(18, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalized_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payroll_slips (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    payroll_run_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    employee_number VARCHAR(100),
    employee_name VARCHAR(255),
    basic_pay DECIMAL(18, 2) DEFAULT 0.0,
    allowances JSONB,
    deductions JSONB,
    tax_amount DECIMAL(18, 2) DEFAULT 0.0,
    gross_pay DECIMAL(18, 2) DEFAULT 0.0,
    total_deductions DECIMAL(18, 2) DEFAULT 0.0,
    net_pay DECIMAL(18, 2) DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payroll_runs_tenant_id ON payroll_runs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payroll_runs_status ON payroll_runs(status);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_tenant_run ON payroll_slips(tenant_id, payroll_run_id);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_employee_id ON payroll_slips(employee_id);

-- FinDNA continuous improvement.
CREATE TABLE IF NOT EXISTS ai_training_datasets (
    id VARCHAR(36) PRIMARY KEY,
    dataset_name VARCHAR(255) NOT NULL,
    source_window_start TIMESTAMP,
    source_window_end TIMESTAMP,
    row_count INTEGER DEFAULT 0,
    feature_schema JSONB,
    label_schema JSONB,
    status VARCHAR(50) DEFAULT 'prepared',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_model_versions (
    id VARCHAR(36) PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    version VARCHAR(100) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'candidate',
    metrics JSONB,
    training_dataset_id VARCHAR(36),
    promoted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_model_feedback (
    id VARCHAR(36) PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(100),
    subject_type VARCHAR(100),
    subject_id VARCHAR(255),
    prediction JSONB,
    actual_outcome JSONB,
    feedback_source VARCHAR(100),
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_training_runs (
    id VARCHAR(36) PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    base_model_version VARCHAR(100),
    candidate_model_version VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    metrics JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_datasets_status ON ai_training_datasets(status);
CREATE INDEX IF NOT EXISTS idx_ai_model_versions_name_status ON ai_model_versions(model_name, status);
CREATE INDEX IF NOT EXISTS idx_ai_model_feedback_model ON ai_model_feedback(model_name, model_version);
CREATE INDEX IF NOT EXISTS idx_ai_model_feedback_subject ON ai_model_feedback(subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_ai_training_runs_model ON ai_training_runs(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_training_runs_dataset ON ai_training_runs(dataset_id);
