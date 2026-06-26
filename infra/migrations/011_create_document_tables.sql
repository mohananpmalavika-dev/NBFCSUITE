-- Migration 011: Create Document tables
-- Created: 2026-06-26

CREATE TABLE IF NOT EXISTS document_records (
    id VARCHAR(36) PRIMARY KEY,
    subject_type VARCHAR(100),
    subject_id VARCHAR(36),
    document_type VARCHAR(100),
    document_name VARCHAR(255),
    document_url VARCHAR(500),
    version VARCHAR(50) DEFAULT '1.0',
    status VARCHAR(50) DEFAULT 'pending',
    expiry_date TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_document_records_subject_type ON document_records(subject_type);
CREATE INDEX IF NOT EXISTS idx_document_records_subject_id ON document_records(subject_id);
CREATE INDEX IF NOT EXISTS idx_document_records_document_type ON document_records(document_type);
CREATE INDEX IF NOT EXISTS idx_document_records_status ON document_records(status);
