-- Comprehensive CIF (Customer Information File) System
-- This migration implements all 18 stages of enterprise customer onboarding

-- Stage 1-2: Enhanced Customer & Prospect Tables with CIF
ALTER TABLE customers ADD COLUMN IF NOT EXISTS cif_id VARCHAR(15) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS cif_generated_at TIMESTAMP NULL;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_lifecycle VARCHAR(50) DEFAULT 'lead';
-- Values: lead -> prospect -> pending_verification -> kyc_in_progress -> kyc_approved -> active -> dormant -> closed
ALTER TABLE customers ADD COLUMN IF NOT EXISTS risk_level VARCHAR(50);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS onboarding_completion_percentage INT DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(20) DEFAULT 'en';

-- Stage 2: Prospect Fields Enhancement
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS onboarding_stage INT DEFAULT 1;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS conversion_date TIMESTAMP NULL;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS rejection_reason TEXT NULL;

-- Stage 3: Basic Details (Individual/Company)
CREATE TABLE IF NOT EXISTS customer_basic_details (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    customer_type VARCHAR(20) NOT NULL,
    -- Individual fields
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    marital_status VARCHAR(50),
    occupation VARCHAR(100),
    education_level VARCHAR(50),
    nationality VARCHAR(50),
    resident_status VARCHAR(50),
    -- Company fields
    company_name VARCHAR(255),
    company_registration_date DATE,
    company_type VARCHAR(50),
    industry VARCHAR(100),
    business_classification VARCHAR(100),
    -- Shared
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 4: Identity Verification with versioning
CREATE TABLE IF NOT EXISTS customer_identity_documents (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(100),
    document_value VARCHAR(255),
    document_url VARCHAR(500),
    document_file_name VARCHAR(255),
    file_size INT,
    mime_type VARCHAR(50),
    ocr_extracted_data JSON,
    ocr_confidence_score DECIMAL(5,2),
    verification_status VARCHAR(50) DEFAULT 'pending',
    verification_timestamp TIMESTAMP NULL,
    verified_by VARCHAR(36) NULL,
    expiry_date DATE NULL,
    version INT DEFAULT 1,
    is_primary BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_customer_doctype (customer_id, document_type)
);

-- Stage 5: Address Management
CREATE TABLE IF NOT EXISTS customer_addresses (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    address_type VARCHAR(50) NOT NULL,
    -- Address types: permanent, communication, office, branch, registered
    street_line1 VARCHAR(255),
    street_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    address_proof_type VARCHAR(50),
    address_proof_url VARCHAR(500),
    address_proof_verification_status VARCHAR(50) DEFAULT 'pending',
    is_primary BOOLEAN DEFAULT FALSE,
    years_at_residence INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_customer_address_type (customer_id, address_type)
);

-- Stage 6: Contact Information
CREATE TABLE IF NOT EXISTS customer_contacts (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    mobile_primary VARCHAR(20),
    mobile_alternate VARCHAR(20),
    email_primary VARCHAR(255),
    email_alternate VARCHAR(255),
    whatsapp_number VARCHAR(20),
    emergency_contact_name VARCHAR(100),
    emergency_contact_mobile VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    preferred_contact_method VARCHAR(50),
    preferred_language VARCHAR(20),
    communication_preference JSON,
    -- consent for email, sms, whatsapp, push, call
    do_not_call BOOLEAN DEFAULT FALSE,
    do_not_email BOOLEAN DEFAULT FALSE,
    do_not_sms BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 7: Family Information
CREATE TABLE IF NOT EXISTS customer_family_members (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    -- relationships: father, mother, spouse, child, sibling, dependent, nominee, guardian
    name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    occupation VARCHAR(100),
    mobile VARCHAR(20),
    email VARCHAR(255),
    address VARCHAR(500),
    is_dependent BOOLEAN DEFAULT FALSE,
    is_nominee BOOLEAN DEFAULT FALSE,
    is_guardian BOOLEAN DEFAULT FALSE,
    pan_number VARCHAR(20),
    aadhar_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 8: Employment Information
CREATE TABLE IF NOT EXISTS customer_employment (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    employment_type VARCHAR(50),
    -- employed, self-employed, retired, student, unemployed, housewife
    employer_name VARCHAR(255),
    employer_type VARCHAR(50),
    designation VARCHAR(100),
    department VARCHAR(100),
    current_salary DECIMAL(15,2),
    salary_frequency VARCHAR(20),
    salary_account_number VARCHAR(30),
    salary_account_ifsc VARCHAR(11),
    salary_account_bank VARCHAR(100),
    years_in_current_job DECIMAL(5,2),
    total_years_experience DECIMAL(5,2),
    date_of_joining DATE,
    employment_contract_type VARCHAR(50),
    income_verification_status VARCHAR(50) DEFAULT 'pending',
    income_verification_document_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 9: Business Profile (for business customers)
CREATE TABLE IF NOT EXISTS customer_business_profile (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    business_type VARCHAR(50),
    -- sole_proprietorship, partnership, llp, company, trust, society, huf
    business_name VARCHAR(255),
    business_registration_number VARCHAR(100),
    gstin VARCHAR(20),
    pan_number VARCHAR(20),
    cin_number VARCHAR(21),
    business_start_date DATE,
    nature_of_business VARCHAR(255),
    business_category VARCHAR(100),
    sub_category VARCHAR(100),
    number_of_partners INT,
    number_of_employees INT,
    annual_turnover DECIMAL(15,2),
    business_bank_accounts JSON,
    -- array of {account_number, ifsc, bank_name, account_type}
    average_monthly_turnover DECIMAL(15,2),
    cash_flow_pattern VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 10: Financial Profile
CREATE TABLE IF NOT EXISTS customer_financial_profile (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    annual_income DECIMAL(15,2),
    monthly_income DECIMAL(15,2),
    monthly_expenses DECIMAL(15,2),
    savings_per_month DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    total_liabilities DECIMAL(15,2),
    net_worth DECIMAL(15,2),
    liquid_assets DECIMAL(15,2),
    fixed_assets DECIMAL(15,2),
    investments_portfolio JSON,
    -- array of {type, value, instrument}
    existing_loans JSON,
    -- array of {lender, amount, emi, status}
    credit_cards JSON,
    -- array of {bank, limit, outstanding}
    insurance_policies JSON,
    -- array of {type, provider, sum_assured, premium}
    credit_score INT,
    credit_rating VARCHAR(20),
    bureau_check_status VARCHAR(50) DEFAULT 'pending',
    bureau_check_date TIMESTAMP NULL,
    risk_rating VARCHAR(20),
    financial_stress_indicator VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 11: Banking Profile
CREATE TABLE IF NOT EXISTS customer_banking_profile (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    primary_bank_account_number VARCHAR(30),
    primary_bank_ifsc VARCHAR(11),
    primary_bank_name VARCHAR(100),
    primary_account_type VARCHAR(50),
    accounts JSON,
    -- array of {account_number, ifsc, bank_name, account_type, is_salary_account}
    existing_relationship VARCHAR(50),
    relationship_since DATE,
    average_balance DECIMAL(15,2),
    last_6month_avg_balance DECIMAL(15,2),
    monthly_debit_transactions INT,
    monthly_credit_transactions INT,
    average_transaction_value DECIMAL(15,2),
    upi_handles JSON,
    net_banking_active BOOLEAN DEFAULT FALSE,
    mobile_banking_active BOOLEAN DEFAULT FALSE,
    standing_instructions JSON,
    last_bank_reconciliation_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 12: Compliance & Verification
CREATE TABLE IF NOT EXISTS customer_compliance (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    pan_verification_status VARCHAR(50) DEFAULT 'pending',
    pan_verified_at TIMESTAMP NULL,
    pan_verification_source VARCHAR(100),
    aadhar_verification_status VARCHAR(50) DEFAULT 'pending',
    aadhar_verified_at TIMESTAMP NULL,
    aadhar_verification_type VARCHAR(50),
    -- online_otp, in_person_otp, video_kyc
    ckyc_status VARCHAR(50) DEFAULT 'pending',
    ckyc_reference_number VARCHAR(100),
    ckyc_completed_at TIMESTAMP NULL,
    video_kyc_status VARCHAR(50) DEFAULT 'pending',
    video_kyc_url VARCHAR(500),
    video_kyc_completed_at TIMESTAMP NULL,
    aml_check_status VARCHAR(50) DEFAULT 'pending',
    aml_check_result VARCHAR(20),
    aml_checked_at TIMESTAMP NULL,
    pep_check_status VARCHAR(50) DEFAULT 'pending',
    pep_check_result VARCHAR(20),
    pep_checked_at TIMESTAMP NULL,
    sanction_list_screening_status VARCHAR(50) DEFAULT 'pending',
    sanction_list_result VARCHAR(20),
    sanction_checked_at TIMESTAMP NULL,
    negative_media_screening_status VARCHAR(50) DEFAULT 'pending',
    negative_media_result VARCHAR(20),
    negative_media_checked_at TIMESTAMP NULL,
    fraud_check_status VARCHAR(50) DEFAULT 'pending',
    fraud_check_result VARCHAR(20),
    fraud_checked_at TIMESTAMP NULL,
    watchlist_check_status VARCHAR(50) DEFAULT 'pending',
    watchlist_result VARCHAR(20),
    watchlist_checked_at TIMESTAMP NULL,
    geo_risk_assessment VARCHAR(50),
    geo_risk_score INT,
    kyc_documents_status JSON,
    compliance_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 13: Behavior Profile & FinDNA
CREATE TABLE IF NOT EXISTS customer_behavior_profile (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    risk_appetite VARCHAR(50),
    spending_pattern VARCHAR(50),
    saving_pattern VARCHAR(50),
    decision_style VARCHAR(50),
    financial_discipline_score INT,
    impulse_buying_tendency VARCHAR(50),
    income_stability_score INT,
    income_trend VARCHAR(50),
    stress_indicators JSON,
    -- array of stress signals detected
    behavior_score INT,
    trust_score INT,
    financial_dna VARCHAR(100),
    -- composite profile like "Conservative-Stable-High-Trust" or "Aggressive-Variable-Medium-Risk"
    product_affinity JSON,
    -- predicted interest in different products
    churn_risk_score INT,
    payment_discipline_score INT,
    communication_preference_index VARCHAR(50),
    digital_savviness INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Stage 14: Relationship Mapping (Graph model)
CREATE TABLE IF NOT EXISTS customer_relationships (
    id VARCHAR(36) PRIMARY KEY,
    primary_customer_id VARCHAR(36) NOT NULL,
    related_customer_id VARCHAR(36),
    relationship_type VARCHAR(50) NOT NULL,
    -- joint_holder, guarantor, family, business, introducer, rm, employee, agent, dealer, channel_partner
    relationship_strength VARCHAR(50),
    primary_contact BOOLEAN DEFAULT FALSE,
    shared_products JSON,
    shared_accounts JSON,
    relationship_since DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_customer_id) REFERENCES customers(id),
    FOREIGN KEY (related_customer_id) REFERENCES customers(id),
    INDEX idx_customer_relationships (primary_customer_id, relationship_type)
);

-- Stage 15: Document Vault with versioning
CREATE TABLE IF NOT EXISTS customer_documents (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    document_category VARCHAR(50) NOT NULL,
    -- identity, address, income, business, kyc_video, agreement, other
    document_type VARCHAR(100),
    document_description VARCHAR(255),
    document_name VARCHAR(255),
    document_url VARCHAR(500),
    file_path VARCHAR(500),
    file_size INT,
    mime_type VARCHAR(50),
    file_hash VARCHAR(64),
    -- SHA256 for integrity
    upload_timestamp TIMESTAMP,
    uploaded_by VARCHAR(36),
    version INT DEFAULT 1,
    is_latest BOOLEAN DEFAULT TRUE,
    expiry_date DATE NULL,
    document_status VARCHAR(50) DEFAULT 'active',
    storage_location VARCHAR(100),
    -- local, s3, azure_blob, etc
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_customer_doc_category (customer_id, document_category),
    INDEX idx_doc_expiry (expiry_date)
);

-- Stage 16: Approval Workflow
CREATE TABLE IF NOT EXISTS customer_approvals (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    workflow_stage INT,
    approval_status VARCHAR(50) DEFAULT 'pending',
    -- pending, approved, rejected, escalated
    initiated_at TIMESTAMP,
    initiated_by VARCHAR(36),
    checker_id VARCHAR(36),
    checker_approved_at TIMESTAMP NULL,
    checker_comments TEXT,
    manager_id VARCHAR(36),
    manager_approved_at TIMESTAMP NULL,
    manager_comments TEXT,
    compliance_officer_id VARCHAR(36),
    compliance_approved_at TIMESTAMP NULL,
    compliance_comments TEXT,
    final_approver_id VARCHAR(36),
    final_approval_at TIMESTAMP NULL,
    final_approval_comments TEXT,
    rejection_reason TEXT,
    escalation_reason TEXT,
    escalated_to VARCHAR(36),
    cif_generated_on TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_approval_status (customer_id, approval_status)
);

-- Stage 17 & 18: Customer 360 & Timeline
CREATE TABLE IF NOT EXISTS customer_timeline (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    -- kyc_update, product_opening, approval, branch_visit, call, complaint, transaction, etc
    event_description TEXT,
    event_timestamp TIMESTAMP,
    triggered_by VARCHAR(36),
    event_metadata JSON,
    document_reference_id VARCHAR(36),
    related_product_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_timeline (customer_id, event_timestamp)
);

-- Customer Household (for family-based servicing)
CREATE TABLE IF NOT EXISTS customer_households (
    id VARCHAR(36) PRIMARY KEY,
    household_name VARCHAR(255),
    primary_customer_id VARCHAR(36) NOT NULL,
    household_type VARCHAR(50),
    -- family, business, joint_venture
    primary_contact_name VARCHAR(100),
    total_relationship_value DECIMAL(15,2),
    household_income DECIMAL(15,2),
    household_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_customer_id) REFERENCES customers(id),
    UNIQUE KEY uk_household_primary (household_type, primary_customer_id)
);

-- Household members
CREATE TABLE IF NOT EXISTS customer_household_members (
    id VARCHAR(36) PRIMARY KEY,
    household_id VARCHAR(36) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    member_role VARCHAR(50),
    member_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (household_id) REFERENCES customer_households(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    UNIQUE KEY uk_household_member (household_id, customer_id)
);

-- Party Model (support individuals, companies, trusts, etc.)
CREATE TABLE IF NOT EXISTS customer_parties (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    party_type VARCHAR(50) NOT NULL,
    -- individual, sole_proprietor, partnership, llp, company, trust, society, government_entity, ngo
    party_name VARCHAR(255),
    party_code VARCHAR(50) UNIQUE,
    registration_number VARCHAR(100),
    registration_authority VARCHAR(100),
    party_status VARCHAR(50) DEFAULT 'active',
    tax_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Consent Management
CREATE TABLE IF NOT EXISTS customer_consents (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    consent_type VARCHAR(50) NOT NULL,
    -- marketing, data_sharing, account_aggregation, digital_communications, credit_bureau
    consent_status VARCHAR(20),
    -- given, withdrawn
    consent_date TIMESTAMP,
    consent_version VARCHAR(20),
    consent_document_url VARCHAR(500),
    consent_expiry_date DATE,
    withdrawn_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    INDEX idx_customer_consent (customer_id, consent_type)
);

-- Onboarding Workflow Configuration (for flexibility)
CREATE TABLE IF NOT EXISTS onboarding_workflows (
    id VARCHAR(36) PRIMARY KEY,
    workflow_name VARCHAR(255),
    product_type VARCHAR(100),
    -- savings_account, deposits, gold_loan, forex, corporate_customer
    customer_type VARCHAR(50),
    workflow_stages JSON,
    required_documents JSON,
    required_compliance_checks JSON,
    approval_levels INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_customers_cif_id ON customers(cif_id);
CREATE INDEX IF NOT EXISTS idx_customers_lifecycle ON customers(customer_lifecycle);
CREATE INDEX IF NOT EXISTS idx_customers_approval_status ON customers(approval_status);
CREATE INDEX IF NOT EXISTS idx_customers_phone_email ON customers(phone, email);
CREATE INDEX IF NOT EXISTS idx_prospects_phone ON prospects(phone);
CREATE INDEX IF NOT EXISTS idx_customer_household_members ON customer_household_members(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_relationships_graph ON customer_relationships(primary_customer_id, related_customer_id);

-- Add CIF numbering sequence
CREATE TABLE IF NOT EXISTS cif_sequence (
    id INT AUTO_INCREMENT PRIMARY KEY,
    last_cif_number BIGINT DEFAULT 1000000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT IGNORE INTO cif_sequence (last_cif_number) VALUES (1000000);
