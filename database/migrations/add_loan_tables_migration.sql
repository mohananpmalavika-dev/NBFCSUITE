-- Loan Management Tables Migration
-- Created: July 4, 2026
-- Module: Loan Management - Complete loan lifecycle tables

-- ============================================================================
-- 1. LOAN PRODUCTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_products (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    
    -- Product Identification
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    loan_category VARCHAR(50) NOT NULL,
    
    -- Interest Configuration
    interest_rate_type VARCHAR(50) NOT NULL,
    min_interest_rate NUMERIC(5,2) NOT NULL,
    max_interest_rate NUMERIC(5,2) NOT NULL,
    default_interest_rate NUMERIC(5,2) NOT NULL,
    
    -- Loan Amount
    min_loan_amount NUMERIC(15,2) NOT NULL,
    max_loan_amount NUMERIC(15,2) NOT NULL,
    
    -- Tenure
    min_tenure_months INTEGER NOT NULL,
    max_tenure_months INTEGER NOT NULL,
    allowed_tenures INTEGER[],
    
    -- Fees & Charges
    processing_fee_type VARCHAR(50) NOT NULL,
    processing_fee_value NUMERIC(15,2) NOT NULL,
    documentation_charges NUMERIC(15,2),
    insurance_applicable BOOLEAN DEFAULT false,
    insurance_percentage NUMERIC(5,2),
    
    -- Penal Interest
    penal_interest_rate NUMERIC(5,2) NOT NULL,
    grace_period_days INTEGER DEFAULT 3,
    
    -- Eligibility Criteria
    min_age INTEGER DEFAULT 21,
    max_age INTEGER DEFAULT 65,
    min_monthly_income NUMERIC(15,2),
    min_cibil_score INTEGER DEFAULT 650,
    employment_types VARCHAR[],
    
    -- Documentation
    required_documents INTEGER[],
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    
    -- Description
    description TEXT,
    features VARCHAR[],
    terms_and_conditions TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_loan_product_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_loan_products_tenant ON loan_products(tenant_id);
CREATE INDEX idx_loan_products_code ON loan_products(product_code);
CREATE INDEX idx_loan_products_type ON loan_products(product_type);
CREATE INDEX idx_loan_products_active ON loan_products(is_active) WHERE is_deleted = false;

-- ============================================================================
-- 2. LOAN APPLICATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_applications (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    application_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Customer & Product
    customer_id INTEGER NOT NULL,
    loan_product_id INTEGER NOT NULL,
    
    -- Loan Details
    requested_amount NUMERIC(15,2) NOT NULL,
    approved_amount NUMERIC(15,2),
    tenure_months INTEGER NOT NULL,
    interest_rate NUMERIC(5,2) NOT NULL,
    
    -- EMI Calculation
    emi_amount NUMERIC(15,2),
    total_interest NUMERIC(15,2),
    total_repayment NUMERIC(15,2),
    
    -- Purpose
    loan_purpose_id INTEGER,
    purpose_description TEXT,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    sub_status VARCHAR(100),
    status_reason TEXT,
    
    -- Workflow
    current_approver_id INTEGER,
    approval_level INTEGER DEFAULT 0,
    
    -- Dates
    application_date DATE NOT NULL,
    submission_date DATE,
    approval_date DATE,
    rejection_date DATE,
    disbursement_date DATE,
    
    -- Credit Assessment
    credit_score INTEGER,
    debt_to_income_ratio NUMERIC(5,2),
    monthly_income NUMERIC(15,2),
    monthly_obligations NUMERIC(15,2),
    risk_rating VARCHAR(50),
    
    -- Documents
    documents_verified BOOLEAN DEFAULT false,
    kyc_verified BOOLEAN DEFAULT false,
    
    -- Fees
    processing_fee NUMERIC(15,2),
    documentation_charges NUMERIC(15,2),
    insurance_amount NUMERIC(15,2),
    other_charges NUMERIC(15,2),
    total_deductions NUMERIC(15,2),
    net_disbursement NUMERIC(15,2),
    
    -- Disbursement Details
    disbursement_bank_account_id INTEGER,
    disbursement_mode VARCHAR(50),
    disbursement_reference VARCHAR(100),
    
    -- Notes
    applicant_remarks TEXT,
    internal_notes TEXT,
    rejection_reason TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_loan_app_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_loan_app_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_loan_app_product FOREIGN KEY (loan_product_id) REFERENCES loan_products(id),
    CONSTRAINT fk_loan_app_purpose FOREIGN KEY (loan_purpose_id) REFERENCES loan_purposes(id),
    CONSTRAINT fk_loan_app_bank_account FOREIGN KEY (disbursement_bank_account_id) 
        REFERENCES customer_bank_accounts(id)
);

CREATE INDEX idx_loan_apps_tenant ON loan_applications(tenant_id);
CREATE INDEX idx_loan_apps_customer ON loan_applications(customer_id);
CREATE INDEX idx_loan_apps_product ON loan_applications(loan_product_id);
CREATE INDEX idx_loan_apps_status ON loan_applications(status);
CREATE INDEX idx_loan_apps_number ON loan_applications(application_number);
CREATE INDEX idx_loan_apps_date ON loan_applications(application_date);

-- ============================================================================
-- 3. LOAN APPLICATION CO-APPLICANTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_application_co_applicants (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_application_id INTEGER NOT NULL,
    family_member_id INTEGER NOT NULL,
    
    co_applicant_type VARCHAR(50) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    relationship VARCHAR(100),
    monthly_income NUMERIC(15,2),
    occupation VARCHAR(200),
    
    consent_given BOOLEAN DEFAULT false,
    consent_date DATE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_co_app_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_co_app_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id) ON DELETE CASCADE,
    CONSTRAINT fk_co_app_family FOREIGN KEY (family_member_id) 
        REFERENCES customer_family_members(id)
);

CREATE INDEX idx_co_apps_application ON loan_application_co_applicants(loan_application_id);
CREATE INDEX idx_co_apps_family ON loan_application_co_applicants(family_member_id);

-- ============================================================================
-- 4. LOAN APPLICATION DOCUMENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_application_documents (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_application_id INTEGER NOT NULL,
    document_type_id INTEGER NOT NULL,
    customer_document_id INTEGER,
    
    document_number VARCHAR(100),
    file_path VARCHAR(500),
    file_url VARCHAR(500),
    
    status VARCHAR(50) DEFAULT 'pending',
    verified_by INTEGER,
    verified_at TIMESTAMP,
    remarks TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_app_doc_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_app_doc_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id) ON DELETE CASCADE,
    CONSTRAINT fk_app_doc_type FOREIGN KEY (document_type_id) REFERENCES document_types(id),
    CONSTRAINT fk_app_doc_customer_doc FOREIGN KEY (customer_document_id) 
        REFERENCES customer_documents(id)
);

CREATE INDEX idx_app_docs_application ON loan_application_documents(loan_application_id);
CREATE INDEX idx_app_docs_type ON loan_application_documents(document_type_id);

-- ============================================================================
-- 5. LOAN APPROVAL WORKFLOWS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_approval_workflows (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_application_id INTEGER NOT NULL,
    
    approval_level INTEGER NOT NULL,
    approver_role VARCHAR(100) NOT NULL,
    approver_id INTEGER,
    
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    action_date TIMESTAMP,
    decision VARCHAR(50),
    comments TEXT,
    conditions VARCHAR[],
    
    -- Limits
    max_approval_amount NUMERIC(15,2),
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_workflow_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_workflow_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id) ON DELETE CASCADE
);

CREATE INDEX idx_workflows_application ON loan_approval_workflows(loan_application_id);
CREATE INDEX idx_workflows_approver ON loan_approval_workflows(approver_id, status);
CREATE INDEX idx_workflows_level ON loan_approval_workflows(approval_level);

-- ============================================================================
-- 6. LOAN ACCOUNTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_accounts (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_account_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Application Link
    loan_application_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    loan_product_id INTEGER NOT NULL,
    
    -- Loan Details
    sanctioned_amount NUMERIC(15,2) NOT NULL,
    disbursed_amount NUMERIC(15,2) NOT NULL,
    outstanding_principal NUMERIC(15,2) NOT NULL,
    outstanding_interest NUMERIC(15,2) NOT NULL,
    outstanding_charges NUMERIC(15,2) DEFAULT 0,
    total_outstanding NUMERIC(15,2) NOT NULL,
    
    -- Terms
    tenure_months INTEGER NOT NULL,
    interest_rate NUMERIC(5,2) NOT NULL,
    emi_amount NUMERIC(15,2) NOT NULL,
    emi_day INTEGER NOT NULL,
    
    -- Dates
    disbursement_date DATE NOT NULL,
    first_emi_date DATE NOT NULL,
    last_emi_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    closure_date DATE,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    overdue_days INTEGER DEFAULT 0,
    dpd INTEGER DEFAULT 0,
    
    -- Collections
    last_payment_date DATE,
    last_payment_amount NUMERIC(15,2),
    next_due_date DATE,
    next_due_amount NUMERIC(15,2),
    
    -- NPA Classification
    npa_status VARCHAR(50),
    npa_date DATE,
    
    -- Prepayment
    prepayment_allowed BOOLEAN DEFAULT true,
    prepayment_charges_percentage NUMERIC(5,2),
    
    -- Penal Interest
    penal_interest_outstanding NUMERIC(15,2) DEFAULT 0,
    
    -- Accounting
    interest_accrued NUMERIC(15,2) DEFAULT 0,
    interest_received NUMERIC(15,2) DEFAULT 0,
    principal_received NUMERIC(15,2) DEFAULT 0,
    
    -- Notes
    internal_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT false,
    
    CONSTRAINT fk_loan_acc_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_loan_acc_application FOREIGN KEY (loan_application_id) 
        REFERENCES loan_applications(id),
    CONSTRAINT fk_loan_acc_customer FOREIGN KEY (customer_id) REFERENCES customers(id),
    CONSTRAINT fk_loan_acc_product FOREIGN KEY (loan_product_id) REFERENCES loan_products(id)
);

CREATE INDEX idx_loan_accs_tenant ON loan_accounts(tenant_id);
CREATE INDEX idx_loan_accs_customer ON loan_accounts(customer_id);
CREATE INDEX idx_loan_accs_status ON loan_accounts(status);
CREATE INDEX idx_loan_accs_number ON loan_accounts(loan_account_number);
CREATE INDEX idx_loan_accs_overdue ON loan_accounts(overdue_days) WHERE overdue_days > 0;

-- ============================================================================
-- 7. LOAN EMI SCHEDULES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_emi_schedules (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_account_id INTEGER NOT NULL,
    
    -- EMI Details
    installment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    
    -- Amount Breakdown
    emi_amount NUMERIC(15,2) NOT NULL,
    principal_component NUMERIC(15,2) NOT NULL,
    interest_component NUMERIC(15,2) NOT NULL,
    
    -- Balance
    opening_principal NUMERIC(15,2) NOT NULL,
    closing_principal NUMERIC(15,2) NOT NULL,
    
    -- Payment Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    paid_amount NUMERIC(15,2) DEFAULT 0,
    paid_principal NUMERIC(15,2) DEFAULT 0,
    paid_interest NUMERIC(15,2) DEFAULT 0,
    payment_date DATE,
    
    -- Overdue
    overdue_days INTEGER DEFAULT 0,
    penal_interest NUMERIC(15,2) DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_emi_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_emi_loan_account FOREIGN KEY (loan_account_id) 
        REFERENCES loan_accounts(id) ON DELETE CASCADE,
    
    UNIQUE (loan_account_id, installment_number)
);

CREATE INDEX idx_emi_loan_account ON loan_emi_schedules(loan_account_id);
CREATE INDEX idx_emi_due_date ON loan_emi_schedules(due_date);
CREATE INDEX idx_emi_status ON loan_emi_schedules(status);
CREATE INDEX idx_emi_overdue ON loan_emi_schedules(overdue_days) WHERE overdue_days > 0;

-- ============================================================================
-- 8. LOAN REPAYMENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS loan_repayments (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    loan_account_id INTEGER NOT NULL,
    
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Payment Details
    payment_date DATE NOT NULL,
    payment_amount NUMERIC(15,2) NOT NULL,
    payment_mode VARCHAR(50) NOT NULL,
    
    -- Allocation
    allocated_to_principal NUMERIC(15,2) NOT NULL,
    allocated_to_interest NUMERIC(15,2) NOT NULL,
    allocated_to_penal_interest NUMERIC(15,2) DEFAULT 0,
    allocated_to_charges NUMERIC(15,2) DEFAULT 0,
    
    -- Reference
    reference_number VARCHAR(100),
    bank_name VARCHAR(200),
    transaction_date DATE,
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'success',
    reversal_reason TEXT,
    reversed_at TIMESTAMP,
    reversed_by INTEGER,
    
    -- Receipt
    receipt_generated BOOLEAN DEFAULT false,
    receipt_url VARCHAR(500),
    
    -- EMI Links
    emi_schedule_ids INTEGER[],
    
    -- Notes
    remarks TEXT,
    collected_by INTEGER,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    
    CONSTRAINT fk_repay_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT fk_repay_loan_account FOREIGN KEY (loan_account_id) 
        REFERENCES loan_accounts(id)
);

CREATE INDEX idx_repays_loan_account ON loan_repayments(loan_account_id);
CREATE INDEX idx_repays_date ON loan_repayments(payment_date);
CREATE INDEX idx_repays_receipt ON loan_repayments(receipt_number);
CREATE INDEX idx_repays_status ON loan_repayments(status);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE loan_products IS 'Loan product configuration and eligibility criteria';
COMMENT ON TABLE loan_applications IS 'Loan applications with complete lifecycle tracking';
COMMENT ON TABLE loan_application_co_applicants IS 'Co-applicants and guarantors for loan applications';
COMMENT ON TABLE loan_application_documents IS 'Documents submitted with loan applications';
COMMENT ON TABLE loan_approval_workflows IS 'Multi-level approval workflow tracking';
COMMENT ON TABLE loan_accounts IS 'Active loan accounts with balance tracking';
COMMENT ON TABLE loan_emi_schedules IS 'EMI schedule with payment tracking';
COMMENT ON TABLE loan_repayments IS 'Loan repayment and payment records';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Total Tables Created: 8
-- Total Indexes Created: 30+
-- Total Foreign Keys: 15+
