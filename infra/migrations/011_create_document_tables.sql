-- Migration 011: Create Document tables
-- Created: 2026-06-26

CREATE TABLE IF NOT EXISTS document_records (
    id VARCHAR(36) PRIMARY KEY,
    subject_type VARCHAR(100),
    subject_id VARCHAR(36),
    document_category VARCHAR(100),
    document_type VARCHAR(100),
    document_name VARCHAR(255),
    document_url VARCHAR(500),
    version VARCHAR(50) DEFAULT '1',
    status VARCHAR(50) DEFAULT 'active',
    expiry_date TIMESTAMP,
    metadata JSONB,
    is_latest BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    storage_location VARCHAR(100) DEFAULT 'local',
    storage_path VARCHAR(1000),
    ocr_extracted_data JSONB,
    ocr_status VARCHAR(50) DEFAULT 'pending',
    signature_status VARCHAR(50) DEFAULT 'unsigned',
    watermark_applied BOOLEAN DEFAULT FALSE,
    expiry_alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_document_records_subject_type ON document_records(subject_type);
CREATE INDEX IF NOT EXISTS idx_document_records_subject_id ON document_records(subject_id);
CREATE INDEX IF NOT EXISTS idx_document_records_document_category ON document_records(document_category);
CREATE INDEX IF NOT EXISTS idx_document_records_document_type ON document_records(document_type);
CREATE INDEX IF NOT EXISTS idx_document_records_status ON document_records(status);
CREATE INDEX IF NOT EXISTS idx_document_records_expiry ON document_records(expiry_date);
