-- Migration: Phase 6 - Loan Origination & Disbursement
-- Description: Complete loan lifecycle from application to disbursement
-- Dependencies: Phases 1-5 (products, appraisal, vault)
-- Version: 1.0
-- Date: 2026-07-03

-- ============================================================================
-- 1. LOAN APPLICATIONS
-- ============================================================================

CREATE TABLE gold_loan_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_number VARCHAR(100) UNIQUE NOT NULL,
    
    -- References
    customer_id UUID NOT NULL REFERENCES customers(id),
    product_id UUID NOT NULL REFERENCES gold_products(id),
    journey_session_id UUID REFERENCES gold_journey_sessions(id),
    appraisal_session_id UUID REFERENCES gold_appraisal_sessions(id),
    branch_id UUID REFERENCES branches(id),
    
    -- Application details
    loan_amount DECIMAL(15,2) NOT NULL,
    requested_tenure INTEGER NOT NULL, -- in months
    purpose TEXT,
    
    -- Customer information (snapshot at application time)
    customer_name VARCHAR(200) NOT NULL,
    customer_mobile VARCHAR(15) NOT NULL,
    customer_email VARCHAR(100),
    customer_pan VARCHAR(10),
    customer_address TEXT,
    
    -- Ornament details (snapshot)
    total_ornaments INTEGER NOT NULL,
    total_gross_weight DECIMAL(10,3) NOT NULL,
    total_net_weight DECIMAL(10,3) NOT NULL,
    total_valuation DECIMAL(15,2) NOT NULL,
    ltv_percentage DECIMAL(5,2) NOT NULL,
    
    -- Application status
    status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, under_review, approved, rejected, cancelled
    stage VARCHAR(50) DEFAULT 'application', -- application, credit_check, approval, disbursement, completed
    
    -- Timestamps
    submitted_at TIMESTAMP,
    submitted_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT check_loan_amount CHECK (loan_amount > 0),
    CONSTRAINT check_tenure CHECK (requested_tenure > 0),
    CONSTRAINT check_ltv CHECK (ltv_percentage >= 0 AND ltv_percentage <= 100)
);

CREATE INDEX idx_loan_applications_customer ON gold_loan_applications(customer_id);
CREATE INDEX idx_loan_applications_status ON gold_loan_applications(status);
CREATE INDEX idx_loan_applications_submitted_at ON gold_loan_applications(submitted_at);
CREATE INDEX idx_loan_applications_branch ON gold_loan_applications(branch_id);

-- ============================================================================
-- 2. APPLICATION ORNAMENTS (Link applications to pledged ornaments)
-- ============================================================================

CREATE TABLE gold_application_ornaments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES gold_loan_applications(id) ON DELETE CASCADE,
    ornament_id UUID NOT NULL REFERENCES gold_ornaments(id),
    packet_id UUID REFERENCES gold_packets(id),
    
    -- Ornament details at application time (snapshot)
    ornament_type VARCHAR(100) NOT NULL,
    gross_weight DECIMAL(10,3) NOT NULL,
    net_weight DECIMAL(10,3) NOT NULL,
    purity DECIMAL(5,2) NOT NULL,
    valuation_amount DECIMAL(15,2) NOT NULL,
    market_rate DECIMAL(10,2),
    
    -- Lien status
    lien_marked BOOLEAN DEFAULT FALSE,
    lien_marked_at TIMESTAMP,
    lien_marked_by UUID REFERENCES users(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(application_id, ornament_id)
);

CREATE INDEX idx_application_ornaments_app ON gold_application_ornaments(application_id);
CREATE INDEX idx_application_ornaments_ornament ON gold_application_ornaments(ornament_id);

-- ============================================================================
-- 3. CREDIT EVALUATION
-- ============================================================================

CREATE TABLE gold_credit_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES gold_loan_applications(id) ON DELETE CASCADE,
    
    -- Evaluation details
    evaluation_type VARCHAR(50) NOT NULL, -- auto, manual, hybrid
    evaluation_status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed
    
    -- Credit scores
    cibil_score INTEGER,
    cibil_fetched_at TIMESTAMP,
    internal_credit_score DECIMAL(5,2),
    
    -- Risk assessment
    risk_category VARCHAR(50), -- low, medium, high, very_high
    risk_score DECIMAL(5,2),
    risk_factors JSONB, -- Array of identified risk factors
    
    -- Borrower assessment
    existing_loans_count INTEGER DEFAULT 0,
    existing_loans_amount DECIMAL(15,2) DEFAULT 0,
    repayment_history VARCHAR(50), -- excellent, good, fair, poor
    bounce_count INTEGER DEFAULT 0,
    
    -- Decisioning
    recommended_amount DECIMAL(15,2),
    recommended_tenure INTEGER,
    recommended_interest_rate DECIMAL(5,2),
    recommended_decision VARCHAR(50), -- approve, reject, refer
    decision_reason TEXT,
    
    -- AI/ML insights
    ai_recommendation VARCHAR(50), -- approve, reject, refer
    ai_confidence_score DECIMAL(5,2),
    ai_factors JSONB,
    
    -- Evaluation metadata
    evaluated_by UUID REFERENCES users(id),
    evaluated_at TIMESTAMP,
    evaluation_duration INTEGER, -- seconds
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_credit_evaluations_app ON gold_credit_evaluations(application_id);
CREATE INDEX idx_credit_evaluations_status ON gold_credit_evaluations(evaluation_status);
CREATE INDEX idx_credit_evaluations_risk ON gold_credit_evaluations(risk_category);

-- ============================================================================
-- 4. APPROVAL WORKFLOW
-- ============================================================================

CREATE TABLE gold_loan_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES gold_loan_applications(id) ON DELETE CASCADE,
    
    -- Approval level
    approval_level INTEGER NOT NULL, -- 1, 2, 3, etc. (based on amount/risk)
    approver_role VARCHAR(100) NOT NULL, -- branch_manager, regional_manager, credit_head, etc.
    approver_id UUID REFERENCES users(id),
    
    -- Approval details
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, referred, on_hold
    decision VARCHAR(50), -- approve, reject, refer, hold
    
    -- Approved/modified terms
    approved_amount DECIMAL(15,2),
    approved_tenure INTEGER,
    approved_interest_rate DECIMAL(5,2),
    approved_conditions TEXT,
    
    -- Remarks and reasoning
    remarks TEXT,
    rejection_reason TEXT,
    conditions JSONB, -- Special conditions if any
    
    -- Timestamps
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    sla_deadline TIMESTAMP,
    is_overdue BOOLEAN DEFAULT FALSE,
    
    -- Sequence
    sequence_order INTEGER NOT NULL,
    is_final_approval BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loan_approvals_app ON gold_loan_approvals(application_id);
CREATE INDEX idx_loan_approvals_approver ON gold_loan_approvals(approver_id);
CREATE INDEX idx_loan_approvals_status ON gold_loan_approvals(status);
CREATE INDEX idx_loan_approvals_level ON gold_loan_approvals(approval_level);

-- ============================================================================
-- 5. LOAN ACCOUNTS (Active loans)
-- ============================================================================

CREATE TABLE gold_loan_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_number VARCHAR(100) UNIQUE NOT NULL,
    
    -- References
    application_id UUID NOT NULL REFERENCES gold_loan_applications(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    product_id UUID NOT NULL REFERENCES gold_products(id),
    branch_id UUID REFERENCES branches(id),
    
    -- Loan terms
    principal_amount DECIMAL(15,2) NOT NULL,
    tenure_months INTEGER NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    interest_type VARCHAR(50) NOT NULL, -- flat, reducing, simple
    
    -- Calculated amounts
    processing_fee DECIMAL(15,2) DEFAULT 0,
    documentation_charges DECIMAL(15,2) DEFAULT 0,
    valuation_charges DECIMAL(15,2) DEFAULT 0,
    other_charges DECIMAL(15,2) DEFAULT 0,
    total_charges DECIMAL(15,2) DEFAULT 0,
    
    -- Loan status
    status VARCHAR(50) DEFAULT 'active', -- active, closed, npa, written_off
    disbursement_status VARCHAR(50) DEFAULT 'pending', -- pending, partial, completed, failed
    
    -- Important dates
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    closed_date DATE,
    
    -- Outstanding
    outstanding_principal DECIMAL(15,2) NOT NULL,
    outstanding_interest DECIMAL(15,2) DEFAULT 0,
    total_outstanding DECIMAL(15,2) NOT NULL,
    
    -- Payments tracking
    total_paid DECIMAL(15,2) DEFAULT 0,
    last_payment_date DATE,
    next_due_date DATE,
    
    -- Overdue tracking
    days_overdue INTEGER DEFAULT 0,
    overdue_interest DECIMAL(15,2) DEFAULT 0,
    is_npa BOOLEAN DEFAULT FALSE,
    npa_date DATE,
    
    -- Linked entities
    linked_packets JSONB, -- Array of packet IDs
    linked_ornaments JSONB, -- Array of ornament IDs
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    
    -- Metadata
    metadata JSONB,
    
    CONSTRAINT check_principal CHECK (principal_amount > 0),
    CONSTRAINT check_interest_rate CHECK (interest_rate >= 0),
    CONSTRAINT check_outstanding CHECK (outstanding_principal >= 0)
);

CREATE INDEX idx_loan_accounts_customer ON gold_loan_accounts(customer_id);
CREATE INDEX idx_loan_accounts_status ON gold_loan_accounts(status);
CREATE INDEX idx_loan_accounts_due_date ON gold_loan_accounts(due_date);
CREATE INDEX idx_loan_accounts_branch ON gold_loan_accounts(branch_id);
CREATE INDEX idx_loan_accounts_npa ON gold_loan_accounts(is_npa);

-- ============================================================================
-- 6. DISBURSEMENTS
-- ============================================================================

CREATE TABLE gold_disbursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    disbursement_number VARCHAR(100) UNIQUE NOT NULL,
    
    -- References
    application_id UUID NOT NULL REFERENCES gold_loan_applications(id),
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    
    -- Disbursement details
    disbursement_amount DECIMAL(15,2) NOT NULL,
    disbursement_mode VARCHAR(50) NOT NULL, -- cash, neft, imps, rtgs, upi, cheque
    disbursement_date DATE NOT NULL,
    disbursement_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Payment details
    payment_reference VARCHAR(200),
    beneficiary_name VARCHAR(200),
    beneficiary_account VARCHAR(100),
    beneficiary_ifsc VARCHAR(20),
    beneficiary_bank VARCHAR(200),
    upi_id VARCHAR(100),
    cheque_number VARCHAR(50),
    
    -- Status
    status VARCHAR(50) DEFAULT 'initiated', -- initiated, processing, completed, failed, cancelled
    failure_reason TEXT,
    
    -- Verification
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP,
    verification_notes TEXT,
    
    -- UTR/Transaction details
    utr_number VARCHAR(100),
    transaction_id VARCHAR(100),
    bank_reference VARCHAR(100),
    
    -- Processed by
    processed_by UUID REFERENCES users(id),
    processed_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    metadata JSONB
);

CREATE INDEX idx_disbursements_application ON gold_disbursements(application_id);
CREATE INDEX idx_disbursements_loan_account ON gold_disbursements(loan_account_id);
CREATE INDEX idx_disbursements_status ON gold_disbursements(status);
CREATE INDEX idx_disbursements_date ON gold_disbursements(disbursement_date);

-- ============================================================================
-- 7. LOAN DOCUMENTS
-- ============================================================================

CREATE TABLE gold_loan_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID REFERENCES gold_loan_applications(id),
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    
    -- Document details
    document_type VARCHAR(100) NOT NULL, -- loan_agreement, pledge_receipt, kyc, income_proof, etc.
    document_category VARCHAR(50) NOT NULL, -- application, disbursement, closure
    document_name VARCHAR(200) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    
    -- Document metadata
    document_number VARCHAR(100),
    is_signed BOOLEAN DEFAULT FALSE,
    signed_at TIMESTAMP,
    signed_by UUID REFERENCES users(id),
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, verified, rejected
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_loan_documents_application ON gold_loan_documents(application_id);
CREATE INDEX idx_loan_documents_loan_account ON gold_loan_documents(loan_account_id);
CREATE INDEX idx_loan_documents_type ON gold_loan_documents(document_type);

-- ============================================================================
-- 8. LOAN CHARGES (Breakdown of all charges)
-- ============================================================================

CREATE TABLE gold_loan_charges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_account_id UUID NOT NULL REFERENCES gold_loan_accounts(id) ON DELETE CASCADE,
    
    -- Charge details
    charge_type VARCHAR(100) NOT NULL, -- processing_fee, valuation, documentation, insurance, etc.
    charge_name VARCHAR(200) NOT NULL,
    charge_amount DECIMAL(15,2) NOT NULL,
    
    -- Tax details
    tax_type VARCHAR(50), -- gst, service_tax
    tax_percentage DECIMAL(5,2),
    tax_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,
    
    -- Payment status
    is_paid BOOLEAN DEFAULT FALSE,
    paid_date DATE,
    payment_mode VARCHAR(50),
    payment_reference VARCHAR(100),
    
    -- Waiver
    is_waived BOOLEAN DEFAULT FALSE,
    waived_amount DECIMAL(15,2) DEFAULT 0,
    waived_by UUID REFERENCES users(id),
    waived_at TIMESTAMP,
    waiver_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loan_charges_loan_account ON gold_loan_charges(loan_account_id);
CREATE INDEX idx_loan_charges_type ON gold_loan_charges(charge_type);

-- ============================================================================
-- 9. LOAN STATUS HISTORY
-- ============================================================================

CREATE TABLE gold_loan_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Can track status for application OR loan account
    application_id UUID REFERENCES gold_loan_applications(id),
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    
    -- Status change
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    stage VARCHAR(50),
    
    -- Change details
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    notes TEXT,
    
    -- Metadata
    metadata JSONB,
    
    CHECK (application_id IS NOT NULL OR loan_account_id IS NOT NULL)
);

CREATE INDEX idx_loan_status_history_application ON gold_loan_status_history(application_id);
CREATE INDEX idx_loan_status_history_loan_account ON gold_loan_status_history(loan_account_id);
CREATE INDEX idx_loan_status_history_changed_at ON gold_loan_status_history(changed_at);

-- ============================================================================
-- 10. LMS INTEGRATION LOG
-- ============================================================================

CREATE TABLE gold_lms_integration_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- References
    application_id UUID REFERENCES gold_loan_applications(id),
    loan_account_id UUID REFERENCES gold_loan_accounts(id),
    
    -- Integration details
    integration_type VARCHAR(50) NOT NULL, -- create_loan, update_loan, disburse, payment, etc.
    lms_system VARCHAR(50) NOT NULL, -- finacle, flexcube, temenos, etc.
    
    -- Request/Response
    request_payload JSONB NOT NULL,
    response_payload JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, success, failed, retry
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- External references
    lms_loan_id VARCHAR(100),
    lms_reference_number VARCHAR(100),
    
    -- Timestamps
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    next_retry_at TIMESTAMP
);

CREATE INDEX idx_lms_integration_application ON gold_lms_integration_log(application_id);
CREATE INDEX idx_lms_integration_loan_account ON gold_lms_integration_log(loan_account_id);
CREATE INDEX idx_lms_integration_status ON gold_lms_integration_log(status);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Application Pipeline View
CREATE VIEW gold_application_pipeline AS
SELECT 
    a.status,
    a.stage,
    a.branch_id,
    COUNT(*) as count,
    SUM(a.loan_amount) as total_amount,
    AVG(a.ltv_percentage) as avg_ltv,
    AVG(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - a.created_at))/3600) as avg_age_hours
FROM gold_loan_applications a
WHERE a.status NOT IN ('cancelled', 'rejected')
GROUP BY a.status, a.stage, a.branch_id;

-- Loan Portfolio View
CREATE VIEW gold_loan_portfolio AS
SELECT 
    l.status,
    l.branch_id,
    l.product_id,
    COUNT(*) as loan_count,
    SUM(l.principal_amount) as total_principal,
    SUM(l.outstanding_principal) as total_outstanding,
    SUM(l.outstanding_interest) as total_interest_outstanding,
    AVG(l.days_overdue) as avg_days_overdue,
    SUM(CASE WHEN l.is_npa THEN 1 ELSE 0 END) as npa_count,
    SUM(CASE WHEN l.is_npa THEN l.outstanding_principal ELSE 0 END) as npa_amount
FROM gold_loan_accounts l
GROUP BY l.status, l.branch_id, l.product_id;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE gold_loan_applications IS 'Loan applications from customers';
COMMENT ON TABLE gold_application_ornaments IS 'Ornaments pledged for loan applications';
COMMENT ON TABLE gold_credit_evaluations IS 'Credit assessment and risk evaluation';
COMMENT ON TABLE gold_loan_approvals IS 'Multi-level approval workflow';
COMMENT ON TABLE gold_loan_accounts IS 'Active loan accounts';
COMMENT ON TABLE gold_disbursements IS 'Loan disbursement records';
COMMENT ON TABLE gold_loan_documents IS 'Application and loan documents';
COMMENT ON TABLE gold_loan_charges IS 'Detailed breakdown of loan charges';
COMMENT ON TABLE gold_loan_status_history IS 'Complete status change audit trail';
COMMENT ON TABLE gold_lms_integration_log IS 'Integration with external LMS systems';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
