-- Phase 4: Enhanced Ornament Catalog
-- Detailed ornament lifecycle, photo management, stone cataloging

-- Ornament photos (separate table for better management)
CREATE TABLE IF NOT EXISTS gold_ornament_photos (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    photo_url VARCHAR(500) NOT NULL,
    photo_type VARCHAR(60) NOT NULL, -- general, hallmark, close_up, damage, stone, certificate
    file_name VARCHAR(255),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    width_pixels INTEGER,
    height_pixels INTEGER,
    uploaded_by_user_id UUID,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    photo_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT false,
    metadata JSONB, -- EXIF, GPS, device info
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_photo_ornament ON gold_ornament_photos(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_photo_type ON gold_ornament_photos(photo_type);
CREATE INDEX IF NOT EXISTS idx_gold_photo_primary ON gold_ornament_photos(ornament_id, is_primary);

-- Stone catalog (detailed stone information)
CREATE TABLE IF NOT EXISTS gold_ornament_stones (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    stone_number INTEGER NOT NULL, -- Sequence number for this ornament
    stone_type VARCHAR(80) NOT NULL, -- diamond, ruby, emerald, sapphire, pearl, etc.
    stone_shape VARCHAR(60), -- round, oval, square, pear, marquise, etc.
    stone_cut VARCHAR(60), -- brilliant, princess, emerald, cushion, etc.
    stone_color VARCHAR(60), -- For diamonds: D, E, F, G, H, etc.
    stone_clarity VARCHAR(60), -- For diamonds: IF, VVS1, VVS2, VS1, VS2, etc.
    carat_weight NUMERIC(10,4), -- Weight in carats
    gram_weight NUMERIC(12,6), -- Weight in grams
    count INTEGER DEFAULT 1, -- Number of similar stones
    estimated_value NUMERIC(18,2),
    is_certified BOOLEAN DEFAULT false,
    certificate_number VARCHAR(120),
    certificate_authority VARCHAR(120), -- GIA, IGI, HRD, etc.
    certificate_url VARCHAR(500),
    stone_quality VARCHAR(60), -- precious, semi_precious, synthetic
    stone_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_stone_ornament ON gold_ornament_stones(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_stone_type ON gold_ornament_stones(stone_type);
CREATE INDEX IF NOT EXISTS idx_gold_stone_certified ON gold_ornament_stones(is_certified);

-- Ornament status history (track lifecycle)
CREATE TABLE IF NOT EXISTS gold_ornament_status_history (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    from_status VARCHAR(40),
    to_status VARCHAR(40) NOT NULL,
    status_reason TEXT,
    changed_by_user_id UUID NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(255), -- Where status changed
    notes TEXT,
    metadata JSONB -- Additional context
);

CREATE INDEX IF NOT EXISTS idx_gold_status_hist_ornament ON gold_ornament_status_history(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_status_hist_date ON gold_ornament_status_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_gold_status_hist_status ON gold_ornament_status_history(to_status);

-- Ornament movements (detailed tracking)
CREATE TABLE IF NOT EXISTS gold_ornament_movements (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    movement_type VARCHAR(60) NOT NULL, -- received, appraised, vaulted, inspected, released, auctioned, returned
    from_location VARCHAR(255),
    to_location VARCHAR(255),
    moved_by_user_id UUID NOT NULL,
    verified_by_user_id UUID,
    movement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_timestamp TIMESTAMP,
    qr_scanned BOOLEAN DEFAULT false,
    gps_latitude NUMERIC(10,8),
    gps_longitude NUMERIC(11,8),
    device_info VARCHAR(255),
    movement_notes TEXT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_gold_movement_ornament ON gold_ornament_movements(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_movement_type ON gold_ornament_movements(movement_type);
CREATE INDEX IF NOT EXISTS idx_gold_movement_date ON gold_ornament_movements(movement_timestamp);

-- Ornament conditions (track damage/wear)
CREATE TABLE IF NOT EXISTS gold_ornament_conditions (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    inspection_date TIMESTAMP NOT NULL,
    inspector_user_id UUID NOT NULL,
    overall_condition VARCHAR(60) NOT NULL, -- excellent, good, fair, poor, damaged
    has_damage BOOLEAN DEFAULT false,
    damage_description TEXT,
    damage_photos JSONB, -- Array of photo URLs
    has_repair BOOLEAN DEFAULT false,
    repair_description TEXT,
    has_missing_parts BOOLEAN DEFAULT false,
    missing_parts_description TEXT,
    stone_condition VARCHAR(60), -- all_intact, some_loose, some_missing, all_missing
    clasp_condition VARCHAR(60), -- working, loose, broken, missing
    polish_level VARCHAR(60), -- excellent, good, dull, tarnished
    weight_verified BOOLEAN DEFAULT false,
    weight_variance_grams NUMERIC(12,3),
    condition_notes TEXT,
    next_inspection_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_condition_ornament ON gold_ornament_conditions(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_condition_date ON gold_ornament_conditions(inspection_date);
CREATE INDEX IF NOT EXISTS idx_gold_condition_overall ON gold_ornament_conditions(overall_condition);

-- Ornament tags (flexible categorization)
CREATE TABLE IF NOT EXISTS gold_ornament_tags (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    tag_category VARCHAR(80) NOT NULL, -- occasion, style, region, era, metal_work, etc.
    tag_value VARCHAR(120) NOT NULL,
    tag_confidence NUMERIC(5,2), -- For AI-detected tags (0-100)
    tagged_by VARCHAR(60), -- user, ai, system
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ornament_id, tag_category, tag_value)
);

CREATE INDEX IF NOT EXISTS idx_gold_tag_ornament ON gold_ornament_tags(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_tag_category ON gold_ornament_tags(tag_category);
CREATE INDEX IF NOT EXISTS idx_gold_tag_value ON gold_ornament_tags(tag_value);

-- Ornament comparisons (for fraud detection)
CREATE TABLE IF NOT EXISTS gold_ornament_comparisons (
    id UUID PRIMARY KEY,
    ornament_id_1 UUID REFERENCES gold_ornaments(id) NOT NULL,
    ornament_id_2 UUID REFERENCES gold_ornaments(id) NOT NULL,
    comparison_type VARCHAR(60) NOT NULL, -- duplicate_detection, similar_pattern, same_customer
    similarity_score NUMERIC(5,2), -- 0-100
    matching_attributes JSONB, -- What matched
    compared_by VARCHAR(60), -- ai, user, system
    comparison_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_flagged BOOLEAN DEFAULT false,
    investigation_status VARCHAR(40), -- pending, investigating, cleared, confirmed_fraud
    investigation_notes TEXT,
    resolved_by_user_id UUID,
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_comparison_orn1 ON gold_ornament_comparisons(ornament_id_1);
CREATE INDEX IF NOT EXISTS idx_gold_comparison_orn2 ON gold_ornament_comparisons(ornament_id_2);
CREATE INDEX IF NOT EXISTS idx_gold_comparison_flagged ON gold_ornament_comparisons(is_flagged);

-- Ornament certificates (hallmark, purity, valuation certificates)
CREATE TABLE IF NOT EXISTS gold_ornament_certificates (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    certificate_type VARCHAR(80) NOT NULL, -- hallmark, bis, purity_test, valuation, insurance
    certificate_number VARCHAR(120) UNIQUE,
    issuing_authority VARCHAR(200) NOT NULL,
    issued_date DATE NOT NULL,
    expiry_date DATE,
    certificate_url VARCHAR(500),
    certificate_hash VARCHAR(255), -- For verification
    is_verified BOOLEAN DEFAULT false,
    verified_by_user_id UUID,
    verified_at TIMESTAMP,
    verification_method VARCHAR(60), -- manual, api, qr_scan, blockchain
    certificate_data JSONB, -- Structured certificate data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_cert_ornament ON gold_ornament_certificates(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_cert_number ON gold_ornament_certificates(certificate_number);
CREATE INDEX IF NOT EXISTS idx_gold_cert_type ON gold_ornament_certificates(certificate_type);

-- Ornament insurance (track insurance details)
CREATE TABLE IF NOT EXISTS gold_ornament_insurance (
    id UUID PRIMARY KEY,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    policy_number VARCHAR(120) UNIQUE NOT NULL,
    insurance_provider VARCHAR(200) NOT NULL,
    insured_value NUMERIC(18,2) NOT NULL,
    premium_amount NUMERIC(18,2),
    policy_start_date DATE NOT NULL,
    policy_end_date DATE NOT NULL,
    coverage_type VARCHAR(80), -- comprehensive, theft, damage, loss
    is_active BOOLEAN DEFAULT true,
    policy_document_url VARCHAR(500),
    claim_history JSONB, -- Array of claims
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gold_insurance_ornament ON gold_ornament_insurance(ornament_id);
CREATE INDEX IF NOT EXISTS idx_gold_insurance_policy ON gold_ornament_insurance(policy_number);
CREATE INDEX IF NOT EXISTS idx_gold_insurance_active ON gold_ornament_insurance(is_active);

-- Ornament grouping (sets of ornaments)
CREATE TABLE IF NOT EXISTS gold_ornament_groups (
    id UUID PRIMARY KEY,
    group_name VARCHAR(200) NOT NULL,
    group_type VARCHAR(60), -- set, collection, inherited, gifted
    description TEXT,
    total_ornaments INTEGER DEFAULT 0,
    total_weight_grams NUMERIC(18,3),
    total_value NUMERIC(18,2),
    customer_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold_ornament_group_members (
    id UUID PRIMARY KEY,
    group_id UUID REFERENCES gold_ornament_groups(id) ON DELETE CASCADE NOT NULL,
    ornament_id UUID REFERENCES gold_ornaments(id) ON DELETE CASCADE NOT NULL,
    sequence_number INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, ornament_id)
);

CREATE INDEX IF NOT EXISTS idx_gold_group_customer ON gold_ornament_groups(customer_id);
CREATE INDEX IF NOT EXISTS idx_gold_group_member_group ON gold_ornament_group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_gold_group_member_orn ON gold_ornament_group_members(ornament_id);

-- Update gold_ornaments table with additional catalog fields
ALTER TABLE gold_ornaments
ADD COLUMN IF NOT EXISTS manufacture_year INTEGER,
ADD COLUMN IF NOT EXISTS origin_country VARCHAR(100),
ADD COLUMN IF NOT EXISTS design_style VARCHAR(100), -- traditional, modern, antique, contemporary
ADD COLUMN IF NOT EXISTS metal_finish VARCHAR(80), -- polished, matte, brushed, hammered, textured
ADD COLUMN IF NOT EXISTS chain_length_cm NUMERIC(10,2), -- For chains
ADD COLUMN IF NOT EXISTS ring_size VARCHAR(20), -- For rings
ADD COLUMN IF NOT EXISTS bangle_size VARCHAR(20), -- For bangles
ADD COLUMN IF NOT EXISTS engraving TEXT,
ADD COLUMN IF NOT EXISTS religious_symbol VARCHAR(80),
ADD COLUMN IF NOT EXISTS occasion VARCHAR(80), -- wedding, engagement, daily_wear, festive
ADD COLUMN IF NOT EXISTS estimated_age_years INTEGER,
ADD COLUMN IF NOT EXISTS is_antique BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS is_designer BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS designer_name VARCHAR(200),
ADD COLUMN IF NOT EXISTS brand_name VARCHAR(200),
ADD COLUMN IF NOT EXISTS purchase_invoice_number VARCHAR(120),
ADD COLUMN IF NOT EXISTS purchase_date DATE,
ADD COLUMN IF NOT EXISTS purchase_value NUMERIC(18,2),
ADD COLUMN IF NOT EXISTS last_inspection_date DATE,
ADD COLUMN IF NOT EXISTS next_inspection_due DATE;

-- Add indexes for new fields
CREATE INDEX IF NOT EXISTS idx_gold_ornament_occasion ON gold_ornaments(occasion);
CREATE INDEX IF NOT EXISTS idx_gold_ornament_antique ON gold_ornaments(is_antique);
CREATE INDEX IF NOT EXISTS idx_gold_ornament_designer ON gold_ornaments(is_designer);
CREATE INDEX IF NOT EXISTS idx_gold_ornament_inspection ON gold_ornaments(next_inspection_due);

COMMENT ON TABLE gold_ornament_photos IS 'Detailed photo management with metadata';
COMMENT ON TABLE gold_ornament_stones IS 'Comprehensive stone catalog with certification';
COMMENT ON TABLE gold_ornament_status_history IS 'Complete status lifecycle tracking';
COMMENT ON TABLE gold_ornament_movements IS 'Physical movement tracking with GPS';
COMMENT ON TABLE gold_ornament_conditions IS 'Condition inspection history';
COMMENT ON TABLE gold_ornament_tags IS 'Flexible categorization and tagging';
COMMENT ON TABLE gold_ornament_comparisons IS 'Fraud detection through comparison';
COMMENT ON TABLE gold_ornament_certificates IS 'Certificate management and verification';
COMMENT ON TABLE gold_ornament_insurance IS 'Insurance policy tracking';
COMMENT ON TABLE gold_ornament_groups IS 'Group related ornaments (sets, collections)';
