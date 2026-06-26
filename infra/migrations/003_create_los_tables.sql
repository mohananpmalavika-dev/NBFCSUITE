-- Migration 003: Create LOS (Loan Origination System) tables
-- Created: 2026-06-26

-- Loan products
CREATE TABLE IF NOT EXISTS loan_products (
    id VARCHAR(36) PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(50), -- personal_loan, home_loan, auto_loan, gold_loan
    min_amount DECIMAL(15, 2),
    max_amount DECIMAL(15, 2),
    min_tenor INTEGER, -- in months
    max_tenor INTEGER,
    base_rate DECIMAL(5, 3),
    processing_fee_percent DECIMAL(5, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loan applications
CREATE TABLE IF NOT EXISTS loan_applications (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    application_status VARCHAR(50) DEFAULT 'draft', -- draft, submitted, under_review, approved, rejected, disbursed
    applied_amount DECIMAL(15, 2) NOT NULL,
    sanctioned_amount DECIMAL(15, 2),
    tenure_months INTEGER,
    applied_interest_rate DECIMAL(5, 3),
    final_interest_rate DECIMAL(5, 3),
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_date TIMESTAMP,
    decision_date TIMESTAMP,
    disbursed_date TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES loan_products(id)
);

-- Application documents
CREATE TABLE IF NOT EXISTS application_documents (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) NOT NULL,
    document_type VARCHAR(50), -- identity, income_proof, bank_statement, itv_return, gst_return
    document_url VARCHAR(500),
    document_hash VARCHAR(255),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_status VARCHAR(50) DEFAULT 'pending', -- pending, verified, rejected
    ocr_extracted_data JSONB,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id) ON DELETE CASCADE
);

-- Application scorecards
CREATE TABLE IF NOT EXISTS application_scorecards (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) NOT NULL UNIQUE,
    credit_score INTEGER,
    bureau_score INTEGER,
    behavior_score DECIMAL(5, 2),
    income_verification_status VARCHAR(50),
    fraud_score DECIMAL(5, 2),
    overall_score DECIMAL(5, 2),
    recommendation VARCHAR(50), -- approve, reject, manual_review
    scoring_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES loan_applications(id) ON DELETE CASCADE
);

-- Underwriting assignments
CREATE TABLE IF NOT EXISTS underwriting_assignments (
    id VARCHAR(36) PRIMARY KEY,
    application_id VARCHAR(36) NOT NULL,
    assigned_to_user_id VARCHAR(36) NOT NULL,
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP,
    comments TEXT,
    decision VARCHAR(50), -- approved, rejected, pending_more_info
    FOREIGN KEY (application_id) REFERENCES loan_applications(id),
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_loan_applications_customer_id ON loan_applications(customer_id);
CREATE INDEX idx_loan_applications_status ON loan_applications(application_status);
CREATE INDEX idx_loan_applications_applied_date ON loan_applications(application_date);
CREATE INDEX idx_application_documents_application_id ON application_documents(application_id);
CREATE INDEX idx_application_scorecards_application_id ON application_scorecards(application_id);
CREATE INDEX idx_underwriting_assignments_application_id ON underwriting_assignments(application_id);
CREATE INDEX idx_underwriting_assignments_assigned_to ON underwriting_assignments(assigned_to_user_id);
