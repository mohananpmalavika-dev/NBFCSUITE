-- Phase 2: Gold Customer Journey
-- Track customer interactions and application journey

-- Customer gold loan sessions (walk-in tracking)
CREATE TABLE IF NOT EXISTS gold_customer_sessions (
    id UUID PRIMARY KEY,
    session_number VARCHAR(40) UNIQUE NOT NULL,
    customer_id UUID,
    branch_id UUID,
    channel VARCHAR(40) NOT NULL DEFAULT 'branch', -- branch, mobile, web, partner
    session_type VARCHAR(40) NOT NULL DEFAULT 'new_loan', -- new_loan, renewal, release, inquiry
    status VARCHAR(40) NOT NULL DEFAULT 'initiated', -- initiated, cif_search, cif_created, product_selected, application_created, completed, abandoned
    initiated_by_user_id UUID,
    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    abandoned_at TIMESTAMP,
    abandonment_reason TEXT,
    session_data JSONB, -- Store journey metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_sessions_customer ON gold_customer_sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_gold_sessions_branch ON gold_customer_sessions(branch_id);
CREATE INDEX IF NOT EXISTS idx_gold_sessions_status ON gold_customer_sessions(status);
CREATE INDEX IF NOT EXISTS idx_gold_sessions_date ON gold_customer_sessions(initiated_at);

-- Customer search history for analytics
CREATE TABLE IF NOT EXISTS gold_customer_search_log (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES gold_customer_sessions(id),
    search_criteria JSONB NOT NULL, -- phone, aadhar, pan, name, customer_id
    results_found INTEGER DEFAULT 0,
    selected_customer_id UUID,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    searched_by_user_id UUID
);

CREATE INDEX IF NOT EXISTS idx_gold_search_session ON gold_customer_search_log(session_id);
CREATE INDEX IF NOT EXISTS idx_gold_search_customer ON gold_customer_search_log(selected_customer_id);

-- Product selection tracking
CREATE TABLE IF NOT EXISTS gold_product_selections (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES gold_customer_sessions(id),
    product_id UUID REFERENCES gold_products(id),
    customer_id UUID,
    requested_amount NUMERIC(18,2),
    estimated_gold_weight NUMERIC(12,3),
    selected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    selection_source VARCHAR(40), -- customer_choice, ai_recommendation, officer_suggestion
    recommendation_score NUMERIC(8,4), -- AI confidence score if AI recommended
    is_converted BOOLEAN DEFAULT false,
    application_id UUID -- Link to actual application if converted
);

CREATE INDEX IF NOT EXISTS idx_gold_product_sel_session ON gold_product_selections(session_id);
CREATE INDEX IF NOT EXISTS idx_gold_product_sel_product ON gold_product_selections(product_id);
CREATE INDEX IF NOT EXISTS idx_gold_product_sel_customer ON gold_product_selections(customer_id);

-- Customer eligibility checks
CREATE TABLE IF NOT EXISTS gold_eligibility_checks (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES gold_customer_sessions(id),
    customer_id UUID NOT NULL,
    product_id UUID REFERENCES gold_products(id) NOT NULL,
    check_type VARCHAR(60) NOT NULL, -- age, income, cibil, existing_loans, geographic, segment
    rule_id UUID, -- Reference to gold_product_eligibility
    is_passed BOOLEAN NOT NULL,
    check_value JSONB, -- Actual values checked
    failure_reason TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_eligibility_session ON gold_eligibility_checks(session_id);
CREATE INDEX IF NOT EXISTS idx_gold_eligibility_customer ON gold_eligibility_checks(customer_id);
CREATE INDEX IF NOT EXISTS idx_gold_eligibility_product ON gold_eligibility_checks(product_id);

-- KYC verification tracking for gold loans
CREATE TABLE IF NOT EXISTS gold_kyc_verifications (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES gold_customer_sessions(id),
    customer_id UUID NOT NULL,
    document_type VARCHAR(80) NOT NULL, -- aadhar, pan, address_proof, photo
    document_number VARCHAR(120),
    verification_method VARCHAR(60), -- manual, aadhaar_otp, digilocker, api, offline
    verification_status VARCHAR(40) NOT NULL, -- pending, verified, failed, expired
    verified_by_user_id UUID,
    verified_at TIMESTAMP,
    verification_response JSONB, -- API response or verification details
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_kyc_session ON gold_kyc_verifications(session_id);
CREATE INDEX IF NOT EXISTS idx_gold_kyc_customer ON gold_kyc_verifications(customer_id);
CREATE INDEX IF NOT EXISTS idx_gold_kyc_status ON gold_kyc_verifications(verification_status);

-- Journey steps tracking for analytics
CREATE TABLE IF NOT EXISTS gold_journey_steps (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES gold_customer_sessions(id) NOT NULL,
    step_number INTEGER NOT NULL,
    step_name VARCHAR(120) NOT NULL, -- customer_search, cif_creation, kyc, product_selection, eligibility_check, application_creation
    step_status VARCHAR(40) NOT NULL, -- started, completed, failed, skipped
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    step_data JSONB, -- Additional step-specific data
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_gold_journey_session ON gold_journey_steps(session_id);
CREATE INDEX IF NOT EXISTS idx_gold_journey_step ON gold_journey_steps(step_name);

-- Customer interaction notes
CREATE TABLE IF NOT EXISTS gold_customer_interactions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES gold_customer_sessions(id),
    customer_id UUID,
    interaction_type VARCHAR(60) NOT NULL, -- inquiry, objection, documentation, negotiation, feedback
    interaction_category VARCHAR(60), -- product_query, rate_negotiation, tenure_discussion, documentation_issue
    notes TEXT NOT NULL,
    officer_user_id UUID,
    interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sentiment VARCHAR(40), -- positive, neutral, negative (for AI analysis)
    follow_up_required BOOLEAN DEFAULT false,
    follow_up_date DATE
);

CREATE INDEX IF NOT EXISTS idx_gold_interactions_session ON gold_customer_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_gold_interactions_customer ON gold_customer_interactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_gold_interactions_type ON gold_customer_interactions(interaction_type);

-- Update gold_loan_applications to link to sessions
ALTER TABLE gold_loan_applications 
ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES gold_customer_sessions(id),
ADD COLUMN IF NOT EXISTS source_channel VARCHAR(40) DEFAULT 'branch',
ADD COLUMN IF NOT EXISTS referral_source VARCHAR(120),
ADD COLUMN IF NOT EXISTS campaign_id VARCHAR(80);

CREATE INDEX IF NOT EXISTS idx_gold_loan_app_session ON gold_loan_applications(session_id);

COMMENT ON TABLE gold_customer_sessions IS 'Track customer gold loan journey from walk-in to application';
COMMENT ON TABLE gold_customer_search_log IS 'Log customer searches for analytics and fraud detection';
COMMENT ON TABLE gold_product_selections IS 'Track product selections and AI recommendations';
COMMENT ON TABLE gold_eligibility_checks IS 'Record eligibility validation results per product';
COMMENT ON TABLE gold_kyc_verifications IS 'KYC verification status for gold loan customers';
COMMENT ON TABLE gold_journey_steps IS 'Detailed journey step tracking for conversion analysis';
COMMENT ON TABLE gold_customer_interactions IS 'Officer notes and customer interactions during journey';
