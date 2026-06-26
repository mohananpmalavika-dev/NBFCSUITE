-- Phase 3 FinDNA AI integration tables.

CREATE TABLE IF NOT EXISTS bank_statement_analyses (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    application_id UUID,
    statement_url TEXT,
    average_balance NUMERIC(18,2) NOT NULL DEFAULT 0,
    monthly_income NUMERIC(18,2) NOT NULL DEFAULT 0,
    recurring_debits NUMERIC(18,2) NOT NULL DEFAULT 0,
    volatility_score NUMERIC(8,4) NOT NULL DEFAULT 0,
    bounced_payment_count INTEGER NOT NULL DEFAULT 0,
    extracted_cashflows JSONB,
    insights JSONB,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bank_statement_analyses_customer_id ON bank_statement_analyses(customer_id);
CREATE INDEX IF NOT EXISTS idx_bank_statement_analyses_application_id ON bank_statement_analyses(application_id);

CREATE TABLE IF NOT EXISTS ai_credit_decisions (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    application_id UUID UNIQUE NOT NULL,
    requested_amount NUMERIC(18,2) NOT NULL,
    tenure_months INTEGER NOT NULL,
    rule_score NUMERIC(8,2),
    behavioral_score NUMERIC(8,2),
    statement_score NUMERIC(8,2),
    fraud_penalty NUMERIC(8,2),
    ai_risk_score NUMERIC(8,2),
    default_probability_90d NUMERIC(8,4),
    recommendation VARCHAR(30),
    risk_grade VARCHAR(5),
    reasons JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_credit_decisions_customer_id ON ai_credit_decisions(customer_id);
CREATE INDEX IF NOT EXISTS idx_ai_credit_decisions_application_id ON ai_credit_decisions(application_id);

ALTER TABLE application_scorecards ADD COLUMN IF NOT EXISTS ai_risk_score NUMERIC(8,2);
ALTER TABLE application_scorecards ADD COLUMN IF NOT EXISTS ai_recommendation VARCHAR(30);
ALTER TABLE application_scorecards ADD COLUMN IF NOT EXISTS ai_risk_grade VARCHAR(5);
ALTER TABLE application_scorecards ADD COLUMN IF NOT EXISTS ai_reasons JSONB;
