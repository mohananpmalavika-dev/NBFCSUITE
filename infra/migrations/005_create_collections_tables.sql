-- Migration 005: Create Collections tables
-- Created: 2026-06-26

-- Collection buckets (DPD-based classification)
CREATE TABLE IF NOT EXISTS collection_buckets (
    id VARCHAR(36) PRIMARY KEY,
    bucket_name VARCHAR(100), -- 0-30 DPD, 30-60 DPD, 60-90 DPD, 90+ DPD
    min_dpd INTEGER,
    max_dpd INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collection assignments (loan to collector mapping)
CREATE TABLE IF NOT EXISTS collection_assignments (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL,
    customer_id VARCHAR(36),
    collector_user_id VARCHAR(36) NOT NULL,
    branch_id VARCHAR(36),
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bucket_id VARCHAR(36),
    days_past_due INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active', -- active, resolved, escalated
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, urgent
    outstanding_amount DECIMAL(15, 2),
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id),
    FOREIGN KEY (collector_user_id) REFERENCES users(id),
    FOREIGN KEY (bucket_id) REFERENCES collection_buckets(id)
);

-- Collection activity logs
CREATE TABLE IF NOT EXISTS collection_activities (
    id VARCHAR(36) PRIMARY KEY,
    assignment_id VARCHAR(36) NOT NULL,
    activity_type VARCHAR(50), -- call, sms, whatsapp, email, visit, promise_to_pay
    activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    promised_amount DECIMAL(15, 2),
    promised_date DATE,
    customer_response VARCHAR(50), -- committed, partial_commitment, no_response, refusal
    gps_location JSONB,
    call_duration_seconds INTEGER,
    call_recording_url VARCHAR(500),
    FOREIGN KEY (assignment_id) REFERENCES collection_assignments(id) ON DELETE CASCADE
);

-- Settlement negotiations
CREATE TABLE IF NOT EXISTS settlement_negotiations (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL,
    outstanding_amount DECIMAL(15, 2),
    offer_amount DECIMAL(15, 2),
    settlement_percentage DECIMAL(5, 2),
    offered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_response VARCHAR(50), -- accepted, rejected, counter_offered
    settlement_date DATE,
    status VARCHAR(50) DEFAULT 'pending', -- offered, accepted, completed, rejected
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id)
);

-- NPA (Non-Performing Asset) tracking
CREATE TABLE IF NOT EXISTS npa_records (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL UNIQUE,
    classification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    npa_type VARCHAR(50), -- substandard, doubtful, loss
    provision_percentage DECIMAL(5, 2),
    recovery_amount DECIMAL(15, 2),
    recovery_date DATE,
    write_off_date DATE,
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id)
);

-- Legal/Recovery cases
CREATE TABLE IF NOT EXISTS legal_cases (
    id VARCHAR(36) PRIMARY KEY,
    loan_account_id VARCHAR(36) NOT NULL,
    case_type VARCHAR(50), -- legal_notice, court_case, recovery_suit
    case_number VARCHAR(100),
    filing_date DATE,
    case_status VARCHAR(50), -- filed, hearing, judgment, appeal, settled, withdrawn
    assigned_lawyer_id VARCHAR(36),
    last_hearing_date DATE,
    next_hearing_date DATE,
    case_amount DECIMAL(15, 2),
    recovery_status VARCHAR(50),
    FOREIGN KEY (loan_account_id) REFERENCES loan_accounts(id),
    FOREIGN KEY (assigned_lawyer_id) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_collection_assignments_loan_account_id ON collection_assignments(loan_account_id);
CREATE INDEX idx_collection_assignments_customer_id ON collection_assignments(customer_id);
CREATE INDEX idx_collection_assignments_collector_id ON collection_assignments(collector_user_id);
CREATE INDEX idx_collection_assignments_branch_id ON collection_assignments(branch_id);
CREATE INDEX idx_collection_assignments_status ON collection_assignments(status);
CREATE INDEX idx_collection_activities_assignment_id ON collection_activities(assignment_id);
CREATE INDEX idx_collection_activities_date ON collection_activities(activity_date);
CREATE INDEX idx_settlement_negotiations_loan_account_id ON settlement_negotiations(loan_account_id);
CREATE INDEX idx_npa_records_loan_account_id ON npa_records(loan_account_id);
CREATE INDEX idx_legal_cases_loan_account_id ON legal_cases(loan_account_id);
