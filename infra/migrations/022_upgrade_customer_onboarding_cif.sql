-- Migration 022: Enterprise customer onboarding and CIF identity upgrades
-- Created: 2026-06-27

ALTER TABLE customers ADD COLUMN IF NOT EXISTS passport VARCHAR(50) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS voter_id VARCHAR(50) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS driving_licence VARCHAR(50) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS gstin VARCHAR(50) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS cin VARCHAR(50) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_type VARCHAR(50) DEFAULT 'individual';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS lifecycle_status VARCHAR(50) DEFAULT 'active';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS source_prospect_id VARCHAR(36);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS onboarding_metadata JSONB;

ALTER TABLE prospects ADD COLUMN IF NOT EXISTS passport_number VARCHAR(50) UNIQUE;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS voter_id VARCHAR(50) UNIQUE;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS driving_licence VARCHAR(50) UNIQUE;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS gstin VARCHAR(50) UNIQUE;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS cin VARCHAR(50) UNIQUE;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS customer_type VARCHAR(50) DEFAULT 'individual';
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS occupation VARCHAR(100);
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS marital_status VARCHAR(50);
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS education VARCHAR(100);
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS annual_income VARCHAR(50);
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS company_name VARCHAR(255);
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS contact_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS family_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS employment_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS business_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS financial_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS banking_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS compliance_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS behavior_profile JSONB;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS relationship_profile JSONB;

CREATE INDEX IF NOT EXISTS idx_customers_lifecycle_status ON customers(lifecycle_status);
CREATE INDEX IF NOT EXISTS idx_customers_type_branch ON customers(customer_type, branch_id);
CREATE INDEX IF NOT EXISTS idx_customers_source_prospect ON customers(source_prospect_id);
CREATE INDEX IF NOT EXISTS idx_prospects_status_branch ON prospects(status, branch_id);
CREATE INDEX IF NOT EXISTS idx_prospects_type_branch ON prospects(customer_type, branch_id);
