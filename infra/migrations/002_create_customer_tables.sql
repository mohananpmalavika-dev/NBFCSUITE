-- Migration 002: Create Customer & KYC tables
-- Created: 2026-06-26

-- Customer Information File (CIF)
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    kyc_status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
    kyc_completed_at TIMESTAMP,
    pan_number VARCHAR(20) UNIQUE,
    aadhar_number VARCHAR(20) UNIQUE,
    branch_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer addresses
CREATE TABLE IF NOT EXISTS customer_addresses (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    address_type VARCHAR(50), -- residential, office, temporary
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- KYC documents
CREATE TABLE IF NOT EXISTS kyc_documents (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    document_type VARCHAR(50), -- aadhar, pan, driving_license, passport
    document_number VARCHAR(100),
    document_url VARCHAR(500),
    verification_status VARCHAR(50) DEFAULT 'pending', -- pending, verified, rejected
    verified_at TIMESTAMP,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Customer financial profiles
CREATE TABLE IF NOT EXISTS customer_financial_profiles (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL UNIQUE,
    annual_income DECIMAL(15, 2),
    employment_type VARCHAR(50), -- salaried, self_employed, business
    employer_name VARCHAR(255),
    occupation VARCHAR(100),
    credit_score INTEGER,
    behavior_score DECIMAL(5, 2),
    risk_level VARCHAR(50), -- low, medium, high
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Banking office hierarchy
CREATE TABLE IF NOT EXISTS head_offices (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(100) UNIQUE,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS zonal_offices (
    id VARCHAR(36) PRIMARY KEY,
    head_office_id VARCHAR(36) NOT NULL,
    name VARCHAR(255),
    code VARCHAR(100) UNIQUE,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (head_office_id) REFERENCES head_offices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS regional_offices (
    id VARCHAR(36) PRIMARY KEY,
    zonal_office_id VARCHAR(36) NOT NULL,
    name VARCHAR(255),
    code VARCHAR(100) UNIQUE,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (zonal_office_id) REFERENCES zonal_offices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS area_offices (
    id VARCHAR(36) PRIMARY KEY,
    regional_office_id VARCHAR(36) NOT NULL,
    name VARCHAR(255),
    code VARCHAR(100) UNIQUE,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (regional_office_id) REFERENCES regional_offices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS branches (
    id VARCHAR(36) PRIMARY KEY,
    area_office_id VARCHAR(36) NOT NULL,
    name VARCHAR(255),
    code VARCHAR(100) UNIQUE,
    branch_type VARCHAR(100),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_office_id) REFERENCES area_offices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS customer_branch_transactions (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    branch_id VARCHAR(36) NOT NULL,
    transaction_type VARCHAR(100),
    amount DECIMAL(18, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    status VARCHAR(50) DEFAULT 'completed',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_pan ON customers(pan_number);
CREATE INDEX idx_customers_kyc_status ON customers(kyc_status);
CREATE INDEX idx_customer_addresses_customer_id ON customer_addresses(customer_id);
CREATE INDEX idx_kyc_documents_customer_id ON kyc_documents(customer_id);
CREATE INDEX idx_customer_financial_profiles_customer_id ON customer_financial_profiles(customer_id);
CREATE INDEX idx_customer_branch_transactions_customer_id ON customer_branch_transactions(customer_id);
CREATE INDEX idx_customer_branch_transactions_branch_id ON customer_branch_transactions(branch_id);
CREATE INDEX idx_branches_area_office_id ON branches(area_office_id);
CREATE INDEX idx_area_offices_regional_office_id ON area_offices(regional_office_id);
CREATE INDEX idx_regional_offices_zonal_office_id ON regional_offices(zonal_office_id);
CREATE INDEX idx_zonal_offices_head_office_id ON zonal_offices(head_office_id);
