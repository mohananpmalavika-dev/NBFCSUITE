-- Migration 022: Create Prospects tables for CIF onboarding flow
-- Created: 2026-06-27

-- Prospect lifecycle: lead -> prospect -> pending_verification -> customer
-- On approval, prospect data is copied into authoritative customers (CIF).

CREATE TABLE IF NOT EXISTS prospects (
    id VARCHAR(36) PRIMARY KEY,
    status VARCHAR(50) NOT NULL DEFAULT 'lead',
    source VARCHAR(255),
    campaign VARCHAR(255),
    branch_id VARCHAR(36),
    assigned_rm VARCHAR(36),

    -- minimal identity/contact snapshot
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),

    pan_number VARCHAR(20) UNIQUE,
    aadhar_number VARCHAR(20) UNIQUE,
    nationality VARCHAR(100),
    resident_status VARCHAR(100),

    -- simplified risk/compliance staging fields
    kyc_status VARCHAR(50) DEFAULT 'pending',
    risk_level VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- link to final customer (CIF)
    customer_id VARCHAR(36)
);

CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status);
CREATE INDEX IF NOT EXISTS idx_prospects_phone ON prospects(phone);
CREATE INDEX IF NOT EXISTS idx_prospects_email ON prospects(email);
CREATE INDEX IF NOT EXISTS idx_prospects_pan ON prospects(pan_number);
CREATE INDEX IF NOT EXISTS idx_prospects_aadhar ON prospects(aadhar_number);
CREATE INDEX IF NOT EXISTS idx_prospects_branch_id ON prospects(branch_id);

-- Prospect addresses (minimal)
CREATE TABLE IF NOT EXISTS prospect_addresses (
    id VARCHAR(36) PRIMARY KEY,
    prospect_id VARCHAR(36) NOT NULL,
    address_type VARCHAR(50),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_prospect_addresses_prospect_id ON prospect_addresses(prospect_id);

-- Prospect KYC documents (minimal)
CREATE TABLE IF NOT EXISTS prospect_kyc_documents (
    id VARCHAR(36) PRIMARY KEY,
    prospect_id VARCHAR(36) NOT NULL,
    document_type VARCHAR(50),
    document_number VARCHAR(100),
    document_url VARCHAR(500),
    verification_status VARCHAR(50) DEFAULT 'pending',
    verified_at TIMESTAMP,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_prospect_kyc_documents_prospect_id ON prospect_kyc_documents(prospect_id);

