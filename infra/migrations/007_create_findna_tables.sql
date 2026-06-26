-- Migration 007: Create FinDNA / AI service tables
-- Created: 2026-06-26

CREATE TABLE IF NOT EXISTS behavioral_scores (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) UNIQUE NOT NULL,
    score DOUBLE PRECISION,
    score_segments JSONB,
    payment_discipline DOUBLE PRECISION,
    credit_utilization DOUBLE PRECISION,
    credit_age DOUBLE PRECISION,
    delinquency_history DOUBLE PRECISION,
    inquiry_frequency DOUBLE PRECISION,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fraud_detection_records (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    application_id VARCHAR(36),
    fraud_score DOUBLE PRECISION,
    risk_level VARCHAR(50),
    risk_factors JSONB,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'flagged'
);

CREATE TABLE IF NOT EXISTS churn_predictions (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    churn_probability DOUBLE PRECISION,
    risk_factors JSONB,
    recommended_action VARCHAR(200),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embedding_vectors (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) UNIQUE NOT NULL,
    embedding JSONB,
    vector_dimension INTEGER,
    embedding_model VARCHAR(100),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_behavioral_scores_customer_id ON behavioral_scores(customer_id);
CREATE INDEX IF NOT EXISTS idx_fraud_detection_records_customer_id ON fraud_detection_records(customer_id);
CREATE INDEX IF NOT EXISTS idx_churn_predictions_customer_id ON churn_predictions(customer_id);
CREATE INDEX IF NOT EXISTS idx_embedding_vectors_customer_id ON embedding_vectors(customer_id);
