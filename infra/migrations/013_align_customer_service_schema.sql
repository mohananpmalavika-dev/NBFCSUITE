-- Migration 013: Align customer-service tables with SQLAlchemy models
-- Created: 2026-06-27

ALTER TABLE customers ADD COLUMN IF NOT EXISTS dob VARCHAR(50);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS pan VARCHAR(20) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS aadhar VARCHAR(20) UNIQUE;

UPDATE customers SET dob = date_of_birth::VARCHAR WHERE dob IS NULL AND date_of_birth IS NOT NULL;
UPDATE customers SET pan = pan_number WHERE pan IS NULL AND pan_number IS NOT NULL;
UPDATE customers SET aadhar = aadhar_number WHERE aadhar IS NULL AND aadhar_number IS NOT NULL;

ALTER TABLE customer_addresses ADD COLUMN IF NOT EXISTS street VARCHAR(255);
UPDATE customer_addresses SET street = street_address WHERE street IS NULL AND street_address IS NOT NULL;

ALTER TABLE kyc_documents ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
UPDATE kyc_documents SET uploaded_at = created_at WHERE uploaded_at IS NULL AND created_at IS NOT NULL;

ALTER TABLE customer_financial_profiles ADD COLUMN IF NOT EXISTS employer VARCHAR(255);
ALTER TABLE customer_financial_profiles ADD COLUMN IF NOT EXISTS assets JSON;
ALTER TABLE customer_financial_profiles ADD COLUMN IF NOT EXISTS liabilities JSON;

UPDATE customer_financial_profiles SET employer = employer_name WHERE employer IS NULL AND employer_name IS NOT NULL;
