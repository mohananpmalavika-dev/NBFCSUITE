-- Phase 3: Gold Appraisal Engine
-- Advanced ornament cataloging, purity testing, and valuation

-- Ornament types master
CREATE TABLE IF NOT EXISTS gold_ornament_types (
    id UUID PRIMARY KEY,
    type_code VARCHAR(40) UNIQUE NOT NULL,
    type_name VARCHAR(120) NOT NULL,
    category VARCHAR(60), -- jewellery, coin, biscuit, bar
    typical_stone_percentage NUMERIC(8,2) DEFAULT 0, -- Typical stone weight %
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO gold_ornament_types (id, type_code, type_name, category, typical_stone_percentage, display_order) VALUES
(gen_random_uuid(), 'CHAIN', 'Chain', 'jewellery', 0, 1),
(gen_random_uuid(), 'RING', 'Ring', 'jewellery', 5, 2),
(gen_random_uuid(), 'BANGLE', 'Bangle', 'jewellery', 0, 3),
(gen_random_uuid(), 'BRACELET', 'Bracelet', 'jewellery', 2, 4),
(gen_random_uuid(), 'NECKLACE', 'Necklace', 'jewellery', 8, 5),
(gen_random_uuid(), 'EARRING', 'Ear Ring', 'jewellery', 10, 6),
(gen_random_uuid(), 'PENDANT', 'Pendant', 'jewellery', 15, 7),
(gen_random_uuid(), 'ANKLET', 'Anklet', 'jewellery', 0, 8),
(gen_random_uuid(), 'MANGALSUTRA', 'Mangalsutra', 'jewellery', 3, 9),
(gen_random_uuid(), 'WAIST_BELT', 'Waist Belt', 'jewellery', 5, 10),
(gen_random_uuid(), 'NOSE_PIN', 'Nose Pin', 'jewellery', 8, 11),
(gen_random_uuid(), 'TOE_RING', 'Toe Ring', 'jewellery', 0, 12),
(gen_random_uuid(), 'COIN', 'Gold Coin', 'coin', 0, 13),
(gen_random_uuid(), 'BISCUIT', 'Gold Biscuit', 'biscuit', 0, 14),
(gen_random_uuid(), 'BAR', 'Gold Bar', 'bar', 0, 15);

-- Enhanced ornament table (expand existing)
ALTER TABLE gold_ornaments 
ADD COLUMN IF NOT EXISTS ornament_type_id UUID REFERENCES gold_ornament_types(id),
ADD COLUMN IF NOT EXISTS barcode VARCHAR(120) UNIQUE,
ADD COLUMN IF NOT EXISTS qr_code VARCHAR(255),
ADD COLUMN IF NOT EXISTS photo_urls JSONB, -- Array of image URLs
ADD COLUMN IF NOT EXISTS photo_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS is_hallmarked BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS hallmark_id VARCHAR(120),
ADD COLUMN IF NOT EXISTS hallmark_center VARCHAR(120),
ADD COLUMN IF NOT EXISTS making_charges NUMERIC(18,2),
ADD COLUMN IF NOT EXISTS wastage_grams NUMERIC(12,3) DEFAULT 0,
ADD COLUMN IF NOT EXISTS stone_details JSONB, -- Detailed stone information
ADD COLUMN IF NOT EXISTS status VARCHAR(40) DEFAULT 'received', -- received, appraised, verified, vaulted, released
ADD COLUMN IF NOT EXISTS appraised_by_user_id UUID,
ADD COLUMN IF NOT EXISTS verified_by_user_id UUID,
ADD COLUMN IF NOT EXISTS tags JSONB; -- Additional tags/metadata

CREATE INDEX IF NOT EXISTS idx_gold_ornament_type ON gold_ornaments(ornament_type_id);
CREATE INDEX IF NOT EXISTS idx_gold_ornament_barcode ON gold_ornaments(barcode);
CREATE INDEX IF NOT EXISTS idx_gold_ornament_status ON gold_ornaments(status);

-- Purity testing records (multi-step testing)
CREATE TABLE IF NOT EXISTS gold_purity_tests (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) NOT NULL,
    test_number INTEGER NOT NULL, -- Allow multiple tests per ornament
    test_method VARCHAR(60) NOT NULL, -- touchstone, xrf, fire_assay, acid_test
    tested_karat NUMERIC(8,2) NOT NULL,
    tested_purity_percent NUMERIC(8,4) NOT NULL,
    test_equipment VARCHAR(120),
    test_location VARCHAR(120), -- Which part of ornament was tested
    tested_by_user_id UUID,
    tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    test_results JSONB, -- Detailed test results
    test_certificate_url VARCHAR(255),
    is_verified BOOLEAN DEFAULT false,
    verified_by_user_id UUID,
    verified_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_purity_ornament ON gold_purity_tests(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_purity_date ON gold_purity_tests(tested_at);

-- Gold market rates
CREATE TABLE IF NOT EXISTS gold_market_rates (
    id UUID PRIMARY KEY,
    rate_date DATE NOT NULL,
    rate_source VARCHAR(80) NOT NULL, -- india_bullion, mcx, international, manual
    purity_karat NUMERIC(8,2) NOT NULL,
    rate_per_gram NUMERIC(18,2) NOT NULL,
    rate_per_10gram NUMERIC(18,2),
    currency VARCHAR(10) DEFAULT 'INR',
    city VARCHAR(120), -- City-specific rates
    branch_id UUID, -- Branch-specific overrides
    is_active BOOLEAN DEFAULT true,
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id UUID,
    rate_metadata JSONB, -- Additional rate information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_rate_date ON gold_market_rates(rate_date, purity_karat);
CREATE INDEX IF NOT EXISTS idx_gold_rate_active ON gold_market_rates(is_active, effective_from);
CREATE INDEX IF NOT EXISTS idx_gold_rate_branch ON gold_market_rates(branch_id);

-- Appraisal sessions (group multiple ornaments)
CREATE TABLE IF NOT EXISTS gold_appraisal_sessions (
    id UUID PRIMARY KEY,
    application_id UUID REFERENCES gold_loan_applications(id) NOT NULL,
    session_number VARCHAR(40) UNIQUE NOT NULL,
    customer_id UUID NOT NULL,
    appraiser_user_id UUID,
    session_status VARCHAR(40) DEFAULT 'in_progress', -- in_progress, completed, verified, rejected
    total_ornaments INTEGER DEFAULT 0,
    total_gross_weight NUMERIC(18,3) DEFAULT 0,
    total_net_weight NUMERIC(18,3) DEFAULT 0,
    total_appraised_value NUMERIC(18,2) DEFAULT 0,
    average_purity_karat NUMERIC(8,2),
    gold_rate_id UUID REFERENCES gold_market_rates(id),
    ltv_percent NUMERIC(8,2),
    eligible_loan_amount NUMERIC(18,2),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    verified_by_user_id UUID,
    session_notes TEXT,
    session_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_appraisal_app ON gold_appraisal_sessions(application_id);
CREATE INDEX IF NOT EXISTS idx_gold_appraisal_customer ON gold_appraisal_sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_gold_appraisal_status ON gold_appraisal_sessions(session_status);

-- Valuation history (track value changes over time)
CREATE TABLE IF NOT EXISTS gold_ornament_valuations (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) NOT NULL,
    valuation_date DATE NOT NULL,
    valuation_type VARCHAR(60) NOT NULL, -- initial, periodic, pre_auction, release
    gold_rate_per_gram NUMERIC(18,2) NOT NULL,
    purity_percent NUMERIC(8,4) NOT NULL,
    net_weight_grams NUMERIC(12,3) NOT NULL,
    calculated_value NUMERIC(18,2) NOT NULL,
    market_value NUMERIC(18,2), -- Current market value
    forced_sale_value NUMERIC(18,2), -- Auction/distress sale value
    valued_by_user_id UUID,
    valuation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_valuation_ornament ON gold_ornament_valuations(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_valuation_date ON gold_ornament_valuations(valuation_date);

-- Weight verification (maker-checker for critical weights)
CREATE TABLE IF NOT EXISTS gold_weight_verifications (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) NOT NULL,
    measurement_type VARCHAR(60) NOT NULL, -- gross_weight, net_weight, stone_weight
    measured_by_user_id UUID NOT NULL,
    measured_weight NUMERIC(12,3) NOT NULL,
    weighing_scale_id VARCHAR(120),
    measurement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_by_user_id UUID,
    verified_weight NUMERIC(12,3),
    verification_timestamp TIMESTAMP,
    variance_grams NUMERIC(12,3),
    is_accepted BOOLEAN,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_weight_ornament ON gold_weight_verifications(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_weight_verified ON gold_weight_verifications(verified_by_user_id);

-- Appraisal anomalies (fraud detection)
CREATE TABLE IF NOT EXISTS gold_appraisal_anomalies (
    id UUID PRIMARY KEY,
    appraisal_session_id UUID REFERENCES gold_appraisal_sessions(id),
    ornament_id UUID REFERENCES gold_ornaments(id),
    anomaly_type VARCHAR(80) NOT NULL, -- weight_mismatch, purity_variance, hallmark_fake, duplicate_barcode, suspicious_pattern
    severity VARCHAR(40) NOT NULL, -- low, medium, high, critical
    anomaly_description TEXT NOT NULL,
    detected_by VARCHAR(60), -- system, user, ai
    detection_data JSONB,
    status VARCHAR(40) DEFAULT 'open', -- open, investigating, resolved, false_positive
    resolution_notes TEXT,
    resolved_by_user_id UUID,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_anomaly_session ON gold_appraisal_anomalies(appraisal_session_id);
CREATE INDEX IF NOT EXISTS idx_gold_anomaly_status ON gold_appraisal_anomalies(status);
CREATE INDEX IF NOT EXISTS idx_gold_anomaly_severity ON gold_appraisal_anomalies(severity);

-- Link appraisal session to ornaments
ALTER TABLE gold_ornaments 
ADD COLUMN IF NOT EXISTS appraisal_session_id UUID REFERENCES gold_appraisal_sessions(id);

CREATE INDEX IF NOT EXISTS idx_gold_ornament_appraisal ON gold_ornaments(appraisal_session_id);

COMMENT ON TABLE gold_ornament_types IS 'Master table of ornament types (chain, ring, bangle, etc.)';
COMMENT ON TABLE gold_purity_tests IS 'Multi-step purity testing records for quality assurance';
COMMENT ON TABLE gold_market_rates IS 'Daily gold rates by purity, city, and branch';
COMMENT ON TABLE gold_appraisal_sessions IS 'Appraisal sessions grouping multiple ornaments per application';
COMMENT ON TABLE gold_ornament_valuations IS 'Historical valuation tracking for ornaments';
COMMENT ON TABLE gold_weight_verifications IS 'Maker-checker weight verification for accuracy';
COMMENT ON TABLE gold_appraisal_anomalies IS 'Fraud detection and anomaly tracking';
