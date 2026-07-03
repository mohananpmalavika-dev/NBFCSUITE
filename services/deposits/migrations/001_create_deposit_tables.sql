-- Deposit Operating System - Database Migration
-- Version 1.0.0 - Initial Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== ENUMS ====================

CREATE TYPE deposit_type AS ENUM (
    'FIXED_DEPOSIT',
    'RECURRING_DEPOSIT',
    'CASA',
    'FLEXI_DEPOSIT'
);

CREATE TYPE interest_method AS ENUM (
    'SIMPLE',
    'COMPOUND_MONTHLY',
    'COMPOUND_QUARTERLY',
    'COMPOUND_HALF_YEARLY',
    'COMPOUND_YEARLY'
);

CREATE TYPE payout_frequency AS ENUM (
    'MONTHLY',
    'QUARTERLY',
    'HALF_YEARLY',
    'YEARLY',
    'ON_MATURITY',
    'CUMULATIVE'
);

CREATE TYPE deposit_account_status AS ENUM (
    'DRAFT',
    'PENDING_APPROVAL',
    'ACTIVE',
    'MATURED',
    'PREMATURELY_CLOSED',
    'RENEWED',
    'CLOSED',
    'SUSPENDED'
);

CREATE TYPE rd_installment_status AS ENUM (
    'SCHEDULED',
    'PAID',
    'OVERDUE',
    'WAIVED'
);

-- ==================== DEPOSIT PRODUCTS ====================

CREATE TABLE deposit_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    deposit_type deposit_type NOT NULL,
    
    -- Amount constraints
    min_amount NUMERIC(15, 2) NOT NULL,
    max_amount NUMERIC(15, 2),
    
    -- Tenure constraints
    min_tenure_days INTEGER,
    max_tenure_days INTEGER,
    
    -- Interest configuration
    interest_method interest_method NOT NULL,
    default_interest_rate NUMERIC(5, 2),
    senior_citizen_rate_bonus NUMERIC(5, 2) DEFAULT 0.5,
    
    -- Payout
    payout_frequency payout_frequency NOT NULL,
    
    -- Features
    premature_allowed BOOLEAN DEFAULT TRUE,
    premature_penalty_percentage NUMERIC(5, 2) DEFAULT 1.0,
    auto_renewal_allowed BOOLEAN DEFAULT TRUE,
    loan_against_deposit_allowed BOOLEAN DEFAULT TRUE,
    nomination_mandatory BOOLEAN DEFAULT FALSE,
    
    -- Tax
    tds_applicable BOOLEAN DEFAULT TRUE,
    tds_rate NUMERIC(5, 2) DEFAULT 10.0,
    
    -- Business rules
    business_rules JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'ACTIVE',
    effective_from DATE,
    effective_to DATE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP,
    updated_by VARCHAR(100)
);

CREATE INDEX idx_product_type_status ON deposit_products(deposit_type, status);
CREATE INDEX idx_product_code ON deposit_products(code);

-- ==================== INTEREST SLABS ====================

CREATE TABLE interest_slabs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES deposit_products(id) ON DELETE CASCADE,
    
    -- Slab criteria
    min_amount NUMERIC(15, 2),
    max_amount NUMERIC(15, 2),
    min_tenure_days INTEGER,
    max_tenure_days INTEGER,
    
    -- Rate
    interest_rate NUMERIC(5, 2) NOT NULL,
    senior_citizen_rate NUMERIC(5, 2),
    
    -- Special rates
    special_rate_applicable BOOLEAN DEFAULT FALSE,
    special_rate_conditions JSONB,
    
    effective_from DATE,
    effective_to DATE
);

CREATE INDEX idx_slab_product ON interest_slabs(product_id);
CREATE INDEX idx_slab_dates ON interest_slabs(effective_from, effective_to);

-- ==================== DEPOSIT ACCOUNTS ====================

CREATE TABLE deposit_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Customer linkage
    customer_id UUID NOT NULL,
    cif_number VARCHAR(50) NOT NULL,
    
    -- Product
    product_id UUID NOT NULL REFERENCES deposit_products(id),
    deposit_type deposit_type NOT NULL,
    
    -- Account details
    principal_amount NUMERIC(15, 2) NOT NULL,
    interest_rate NUMERIC(5, 2) NOT NULL,
    is_senior_citizen BOOLEAN DEFAULT FALSE,
    
    -- Dates
    open_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    actual_closure_date DATE,
    
    -- Maturity
    maturity_amount NUMERIC(15, 2),
    maturity_instruction VARCHAR(50),
    
    -- Interest configuration
    interest_method interest_method,
    payout_frequency payout_frequency,
    interest_payout_account VARCHAR(50),
    
    -- Features
    auto_renewal BOOLEAN DEFAULT FALSE,
    loan_facility BOOLEAN DEFAULT FALSE,
    
    -- Status
    status deposit_account_status NOT NULL DEFAULT 'DRAFT',
    
    -- Financial summary
    total_interest_earned NUMERIC(15, 2) DEFAULT 0,
    total_interest_paid NUMERIC(15, 2) DEFAULT 0,
    total_tds_deducted NUMERIC(15, 2) DEFAULT 0,
    last_interest_calculated_date DATE,
    
    -- Branch & maker-checker
    branch_code VARCHAR(20),
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB
);

CREATE INDEX idx_account_number ON deposit_accounts(account_number);
CREATE INDEX idx_account_customer ON deposit_accounts(customer_id);
CREATE INDEX idx_account_cif ON deposit_accounts(cif_number);
CREATE INDEX idx_account_status ON deposit_accounts(status);
CREATE INDEX idx_account_maturity ON deposit_accounts(maturity_date, status);
CREATE INDEX idx_account_branch ON deposit_accounts(branch_code);

-- ==================== NOMINEES ====================

CREATE TABLE nominees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES deposit_accounts(id) ON DELETE CASCADE,
    
    -- Nominee details
    name VARCHAR(200) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    date_of_birth DATE,
    age INTEGER,
    
    -- Contact
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    
    -- Identification
    id_proof_type VARCHAR(50),
    id_proof_number VARCHAR(100),
    
    -- Allocation
    allocation_percentage NUMERIC(5, 2) DEFAULT 100.00,
    is_minor BOOLEAN DEFAULT FALSE,
    guardian_name VARCHAR(200),
    guardian_relationship VARCHAR(50),
    
    -- Priority
    nominee_order INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_nominee_account ON nominees(account_id);

-- ==================== INTEREST POSTINGS ====================

CREATE TABLE interest_postings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES deposit_accounts(id) ON DELETE CASCADE,
    
    -- Period
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    days INTEGER NOT NULL,
    
    -- Calculation
    principal_amount NUMERIC(15, 2) NOT NULL,
    interest_rate NUMERIC(5, 2) NOT NULL,
    interest_amount NUMERIC(15, 2) NOT NULL,
    
    -- Tax
    tds_amount NUMERIC(15, 2) DEFAULT 0,
    tds_rate NUMERIC(5, 2),
    net_interest NUMERIC(15, 2),
    
    -- Posting
    posting_date DATE,
    is_paid BOOLEAN DEFAULT FALSE,
    payment_date DATE,
    payment_reference VARCHAR(100),
    
    -- Accounting
    journal_entry_id VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interest_account ON interest_postings(account_id);
CREATE INDEX idx_interest_period ON interest_postings(from_date, to_date);
CREATE INDEX idx_interest_posting ON interest_postings(posting_date, is_paid);

-- ==================== RD SCHEDULES ====================

CREATE TABLE rd_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES deposit_accounts(id) ON DELETE CASCADE,
    
    -- Installment details
    installment_number INTEGER NOT NULL,
    installment_amount NUMERIC(15, 2) NOT NULL,
    due_date DATE NOT NULL,
    
    -- Status
    status rd_installment_status DEFAULT 'SCHEDULED',
    
    -- Payment
    paid_amount NUMERIC(15, 2) DEFAULT 0,
    paid_date DATE,
    payment_mode VARCHAR(50),
    payment_reference VARCHAR(100),
    
    -- Penalty
    penalty_amount NUMERIC(15, 2) DEFAULT 0,
    penalty_waived BOOLEAN DEFAULT FALSE,
    waiver_reason TEXT,
    
    -- Grace period
    grace_period_days INTEGER DEFAULT 7,
    overdue_days INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_rd_account ON rd_schedules(account_id);
CREATE INDEX idx_rd_due_date ON rd_schedules(due_date, status);
CREATE INDEX idx_rd_installment ON rd_schedules(account_id, installment_number);

-- ==================== DEPOSIT TRANSACTIONS ====================

CREATE TABLE deposit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES deposit_accounts(id) ON DELETE CASCADE,
    
    -- Transaction details
    transaction_type VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    value_date DATE,
    
    -- Amount
    debit_amount NUMERIC(15, 2) DEFAULT 0,
    credit_amount NUMERIC(15, 2) DEFAULT 0,
    balance NUMERIC(15, 2),
    
    -- Reference
    reference_number VARCHAR(100) UNIQUE,
    payment_mode VARCHAR(50),
    narration TEXT,
    
    -- Accounting
    journal_entry_id VARCHAR(100),
    
    -- Maker-checker
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_txn_account ON deposit_transactions(account_id);
CREATE INDEX idx_txn_date ON deposit_transactions(transaction_date);
CREATE INDEX idx_txn_type ON deposit_transactions(transaction_type);
CREATE INDEX idx_txn_reference ON deposit_transactions(reference_number);

-- ==================== DEPOSIT CERTIFICATES ====================

CREATE TABLE deposit_certificates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES deposit_accounts(id) ON DELETE CASCADE,
    
    certificate_type VARCHAR(50) NOT NULL,
    certificate_number VARCHAR(100) UNIQUE,
    
    -- Document reference
    document_id VARCHAR(100),
    document_url VARCHAR(500),
    
    -- Period
    from_date DATE,
    to_date DATE,
    financial_year VARCHAR(10),
    
    -- Status
    status VARCHAR(20) DEFAULT 'GENERATED',
    generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_date TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cert_account ON deposit_certificates(account_id);
CREATE INDEX idx_cert_type ON deposit_certificates(certificate_type);
CREATE INDEX idx_cert_number ON deposit_certificates(certificate_number);

-- ==================== RENEWAL HISTORY ====================

CREATE TABLE renewal_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    old_account_id UUID NOT NULL REFERENCES deposit_accounts(id),
    new_account_id UUID,
    
    -- Renewal details
    renewal_date DATE NOT NULL,
    renewal_type VARCHAR(50),
    
    -- Amounts
    maturity_amount NUMERIC(15, 2),
    renewed_principal NUMERIC(15, 2),
    interest_paid_out NUMERIC(15, 2),
    
    -- New terms
    new_interest_rate NUMERIC(5, 2),
    new_tenure_days INTEGER,
    new_maturity_date DATE,
    
    -- AI recommendation
    ai_recommended BOOLEAN DEFAULT FALSE,
    ai_confidence_score NUMERIC(5, 2),
    ai_reasoning TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

CREATE INDEX idx_renewal_old_account ON renewal_history(old_account_id);
CREATE INDEX idx_renewal_new_account ON renewal_history(new_account_id);
CREATE INDEX idx_renewal_date ON renewal_history(renewal_date);

-- ==================== PREMATURE CLOSURES ====================

CREATE TABLE premature_closures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL,
    
    -- Request
    request_date DATE NOT NULL,
    requested_by VARCHAR(100),
    closure_reason TEXT,
    
    -- Calculation
    principal_amount NUMERIC(15, 2),
    days_completed INTEGER,
    applicable_interest_rate NUMERIC(5, 2),
    interest_earned NUMERIC(15, 2),
    penalty_percentage NUMERIC(5, 2),
    penalty_amount NUMERIC(15, 2),
    tds_amount NUMERIC(15, 2),
    net_payout NUMERIC(15, 2),
    
    -- Approval
    status VARCHAR(20) DEFAULT 'PENDING',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Closure
    closure_date DATE,
    payment_mode VARCHAR(50),
    payment_reference VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_closure_account ON premature_closures(account_id);
CREATE INDEX idx_closure_status ON premature_closures(status);
CREATE INDEX idx_closure_request_date ON premature_closures(request_date);

-- ==================== AI INTELLIGENCE ====================

CREATE TABLE deposit_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL,
    account_id UUID,
    
    -- Analysis type
    analysis_type VARCHAR(50) NOT NULL,
    
    -- Prediction
    prediction VARCHAR(100),
    confidence_score NUMERIC(5, 2),
    probability NUMERIC(5, 2),
    
    -- Insights
    insights JSONB,
    behavioral_patterns JSONB,
    recommendations JSONB,
    
    -- Context
    data_points_analyzed INTEGER,
    model_version VARCHAR(50),
    
    -- Validity
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_intelligence_customer ON deposit_intelligence(customer_id);
CREATE INDEX idx_intelligence_account ON deposit_intelligence(account_id);
CREATE INDEX idx_intelligence_type ON deposit_intelligence(analysis_type);
CREATE INDEX idx_intelligence_created ON deposit_intelligence(created_at);

-- ==================== MATURITY PIPELINE ====================

CREATE TABLE maturity_pipeline (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL,
    customer_id UUID NOT NULL,
    
    maturity_date DATE NOT NULL,
    maturity_amount NUMERIC(15, 2),
    
    -- Customer preference
    customer_instruction VARCHAR(50),
    contact_attempted BOOLEAN DEFAULT FALSE,
    contact_date DATE,
    contact_method VARCHAR(50),
    
    -- AI recommendation
    ai_recommended_action VARCHAR(50),
    renewal_probability NUMERIC(5, 2),
    
    -- Status
    status VARCHAR(20) DEFAULT 'UPCOMING',
    processed_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_maturity_pipeline_date ON maturity_pipeline(maturity_date);
CREATE INDEX idx_maturity_pipeline_status ON maturity_pipeline(status);
CREATE INDEX idx_maturity_pipeline_customer ON maturity_pipeline(customer_id);

-- ==================== COMMENTS ====================

COMMENT ON TABLE deposit_products IS 'Configurable deposit product catalog';
COMMENT ON TABLE deposit_accounts IS 'Core deposit account management';
COMMENT ON TABLE rd_schedules IS 'RD installment schedule and tracking';
COMMENT ON TABLE deposit_intelligence IS 'AI-powered deposit insights and predictions';
COMMENT ON TABLE maturity_pipeline IS 'Proactive maturity management';

-- ==================== FUNCTIONS ====================

-- Function to calculate days between dates
CREATE OR REPLACE FUNCTION calculate_days(start_date DATE, end_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN end_date - start_date;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to mark overdue RD installments
CREATE OR REPLACE FUNCTION mark_overdue_rd_installments()
RETURNS VOID AS $$
BEGIN
    UPDATE rd_schedules
    SET status = 'OVERDUE',
        overdue_days = CURRENT_DATE - due_date - grace_period_days
    WHERE status = 'SCHEDULED'
    AND due_date + grace_period_days < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mark_overdue_rd_installments() IS 'Mark RD installments as overdue';
