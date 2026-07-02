-- Phase 5: Vault & Packet Management
-- Hierarchical vault structure with QR codes, packet tracking, and security management
-- Date: July 3, 2026

-- ============================================================================
-- VAULT HIERARCHY
-- ============================================================================

-- Main vault locations (building level)
CREATE TABLE IF NOT EXISTS gold_vaults (
    id VARCHAR(50) PRIMARY KEY,
    vault_code VARCHAR(20) UNIQUE NOT NULL,
    vault_name VARCHAR(100) NOT NULL,
    branch_id VARCHAR(50) NOT NULL,
    location_description TEXT,
    vault_type VARCHAR(30) NOT NULL, -- main, satellite, temporary
    security_level VARCHAR(30) NOT NULL, -- high, medium, standard
    capacity_packets INTEGER DEFAULT 0,
    current_occupancy INTEGER DEFAULT 0,
    temperature_controlled BOOLEAN DEFAULT FALSE,
    humidity_controlled BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    installed_date DATE,
    last_audit_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    CONSTRAINT chk_occupancy CHECK (current_occupancy >= 0 AND current_occupancy <= capacity_packets)
);

CREATE INDEX idx_vaults_branch ON gold_vaults(branch_id);
CREATE INDEX idx_vaults_active ON gold_vaults(is_active);
CREATE INDEX idx_vaults_type ON gold_vaults(vault_type);

-- Racks within vaults
CREATE TABLE IF NOT EXISTS gold_vault_racks (
    id VARCHAR(50) PRIMARY KEY,
    vault_id VARCHAR(50) NOT NULL,
    rack_code VARCHAR(20) NOT NULL,
    rack_number INTEGER NOT NULL,
    capacity_lockers INTEGER DEFAULT 0,
    current_occupancy INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (vault_id) REFERENCES gold_vaults(id) ON DELETE CASCADE,
    UNIQUE(vault_id, rack_number),
    CONSTRAINT chk_rack_occupancy CHECK (current_occupancy >= 0 AND current_occupancy <= capacity_lockers)
);

CREATE INDEX idx_racks_vault ON gold_vault_racks(vault_id);
CREATE INDEX idx_racks_active ON gold_vault_racks(is_active);

-- Lockers within racks
CREATE TABLE IF NOT EXISTS gold_vault_lockers (
    id VARCHAR(50) PRIMARY KEY,
    rack_id VARCHAR(50) NOT NULL,
    locker_code VARCHAR(20) NOT NULL,
    locker_number INTEGER NOT NULL,
    capacity_trays INTEGER DEFAULT 0,
    current_occupancy INTEGER DEFAULT 0,
    lock_type VARCHAR(30), -- key, combination, electronic, biometric
    lock_serial_number VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rack_id) REFERENCES gold_vault_racks(id) ON DELETE CASCADE,
    UNIQUE(rack_id, locker_number),
    CONSTRAINT chk_locker_occupancy CHECK (current_occupancy >= 0 AND current_occupancy <= capacity_trays)
);

CREATE INDEX idx_lockers_rack ON gold_vault_lockers(rack_id);
CREATE INDEX idx_lockers_active ON gold_vault_lockers(is_active);

-- Trays within lockers
CREATE TABLE IF NOT EXISTS gold_vault_trays (
    id VARCHAR(50) PRIMARY KEY,
    locker_id VARCHAR(50) NOT NULL,
    tray_code VARCHAR(20) NOT NULL,
    tray_number INTEGER NOT NULL,
    capacity_packets INTEGER DEFAULT 0,
    current_occupancy INTEGER DEFAULT 0,
    tray_size VARCHAR(20), -- small, medium, large
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (locker_id) REFERENCES gold_vault_lockers(id) ON DELETE CASCADE,
    UNIQUE(locker_id, tray_number),
    CONSTRAINT chk_tray_occupancy CHECK (current_occupancy >= 0 AND current_occupancy <= capacity_packets)
);

CREATE INDEX idx_trays_locker ON gold_vault_trays(locker_id);
CREATE INDEX idx_trays_active ON gold_vault_trays(is_active);

-- ============================================================================
-- PACKET MANAGEMENT
-- ============================================================================

-- Main packet table
CREATE TABLE IF NOT EXISTS gold_packets (
    id VARCHAR(50) PRIMARY KEY,
    packet_number VARCHAR(50) UNIQUE NOT NULL,
    appraisal_session_id VARCHAR(50),
    customer_id VARCHAR(50) NOT NULL,
    branch_id VARCHAR(50) NOT NULL,
    
    -- Current location
    current_location_type VARCHAR(30) NOT NULL, -- vault, transit, counter, audit
    vault_id VARCHAR(50),
    rack_id VARCHAR(50),
    locker_id VARCHAR(50),
    tray_id VARCHAR(50),
    
    -- Packet details
    total_ornaments INTEGER DEFAULT 0,
    total_weight_grams DECIMAL(10,3),
    total_value DECIMAL(15,2),
    
    -- QR code
    qr_code VARCHAR(100) UNIQUE NOT NULL,
    qr_generated_at TIMESTAMP,
    
    -- Security seal
    seal_number VARCHAR(50) UNIQUE,
    seal_type VARCHAR(30), -- paper, plastic, electronic, tamper_evident
    sealed_by_user_id VARCHAR(50),
    sealed_at TIMESTAMP,
    seal_verified_by_user_id VARCHAR(50),
    seal_verified_at TIMESTAMP,
    seal_status VARCHAR(30), -- intact, broken, tampered, missing
    
    -- Status
    packet_status VARCHAR(30) NOT NULL DEFAULT 'created', -- created, sealed, vaulted, in_transit, released, auctioned
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id VARCHAR(50),
    
    FOREIGN KEY (vault_id) REFERENCES gold_vaults(id) ON DELETE SET NULL,
    FOREIGN KEY (rack_id) REFERENCES gold_vault_racks(id) ON DELETE SET NULL,
    FOREIGN KEY (locker_id) REFERENCES gold_vault_lockers(id) ON DELETE SET NULL,
    FOREIGN KEY (tray_id) REFERENCES gold_vault_trays(id) ON DELETE SET NULL
);

CREATE INDEX idx_packets_number ON gold_packets(packet_number);
CREATE INDEX idx_packets_qr ON gold_packets(qr_code);
CREATE INDEX idx_packets_customer ON gold_packets(customer_id);
CREATE INDEX idx_packets_branch ON gold_packets(branch_id);
CREATE INDEX idx_packets_status ON gold_packets(packet_status);
CREATE INDEX idx_packets_vault ON gold_packets(vault_id);
CREATE INDEX idx_packets_location_type ON gold_packets(current_location_type);

-- Ornament to packet mapping
CREATE TABLE IF NOT EXISTS gold_packet_ornaments (
    id VARCHAR(50) PRIMARY KEY,
    packet_id VARCHAR(50) NOT NULL,
    ornament_id VARCHAR(50) NOT NULL,
    sequence_number INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by_user_id VARCHAR(50),
    
    FOREIGN KEY (packet_id) REFERENCES gold_packets(id) ON DELETE CASCADE,
    UNIQUE(packet_id, ornament_id)
);

CREATE INDEX idx_packet_ornaments_packet ON gold_packet_ornaments(packet_id);
CREATE INDEX idx_packet_ornaments_ornament ON gold_packet_ornaments(ornament_id);

-- ============================================================================
-- PACKET MOVEMENT HISTORY
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_packet_movements (
    id VARCHAR(50) PRIMARY KEY,
    packet_id VARCHAR(50) NOT NULL,
    movement_type VARCHAR(40) NOT NULL, -- vault_in, vault_out, transfer, inspection, audit
    
    -- Location details
    from_location_type VARCHAR(30),
    from_vault_id VARCHAR(50),
    from_rack_id VARCHAR(50),
    from_locker_id VARCHAR(50),
    from_tray_id VARCHAR(50),
    
    to_location_type VARCHAR(30),
    to_vault_id VARCHAR(50),
    to_rack_id VARCHAR(50),
    to_locker_id VARCHAR(50),
    to_tray_id VARCHAR(50),
    
    -- Movement details
    moved_by_user_id VARCHAR(50) NOT NULL,
    verified_by_user_id VARCHAR(50),
    movement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verification_timestamp TIMESTAMP,
    
    -- Security
    qr_scanned BOOLEAN DEFAULT FALSE,
    seal_checked BOOLEAN DEFAULT FALSE,
    seal_status_at_movement VARCHAR(30),
    
    -- GPS and device
    gps_latitude DECIMAL(10,8),
    gps_longitude DECIMAL(11,8),
    device_info VARCHAR(255),
    
    -- Notes
    movement_reason TEXT,
    movement_notes TEXT,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (packet_id) REFERENCES gold_packets(id) ON DELETE CASCADE
);

CREATE INDEX idx_packet_movements_packet ON gold_packet_movements(packet_id);
CREATE INDEX idx_packet_movements_timestamp ON gold_packet_movements(movement_timestamp);
CREATE INDEX idx_packet_movements_type ON gold_packet_movements(movement_type);
CREATE INDEX idx_packet_movements_from_vault ON gold_packet_movements(from_vault_id);
CREATE INDEX idx_packet_movements_to_vault ON gold_packet_movements(to_vault_id);

-- ============================================================================
-- VAULT AUDITS
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_vault_audits (
    id VARCHAR(50) PRIMARY KEY,
    audit_number VARCHAR(50) UNIQUE NOT NULL,
    vault_id VARCHAR(50) NOT NULL,
    
    -- Audit details
    audit_type VARCHAR(30) NOT NULL, -- scheduled, surprise, regulatory, internal
    audit_date DATE NOT NULL,
    audit_started_at TIMESTAMP,
    audit_completed_at TIMESTAMP,
    
    -- Team
    lead_auditor_user_id VARCHAR(50) NOT NULL,
    auditor_team JSONB, -- Array of user IDs
    
    -- Findings
    total_packets_expected INTEGER,
    total_packets_found INTEGER,
    discrepancies_found INTEGER DEFAULT 0,
    
    -- Status
    audit_status VARCHAR(30) NOT NULL DEFAULT 'scheduled', -- scheduled, in_progress, completed, report_pending, closed
    
    -- Results
    audit_result VARCHAR(30), -- clean, minor_issues, major_issues, critical
    findings_summary TEXT,
    recommendations TEXT,
    
    -- Approvals
    reviewed_by_user_id VARCHAR(50),
    reviewed_at TIMESTAMP,
    approved_by_user_id VARCHAR(50),
    approved_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (vault_id) REFERENCES gold_vaults(id) ON DELETE CASCADE
);

CREATE INDEX idx_audits_vault ON gold_vault_audits(vault_id);
CREATE INDEX idx_audits_date ON gold_vault_audits(audit_date);
CREATE INDEX idx_audits_status ON gold_vault_audits(audit_status);
CREATE INDEX idx_audits_type ON gold_vault_audits(audit_type);

-- Audit findings for individual packets
CREATE TABLE IF NOT EXISTS gold_audit_findings (
    id VARCHAR(50) PRIMARY KEY,
    audit_id VARCHAR(50) NOT NULL,
    packet_id VARCHAR(50),
    
    -- Finding details
    finding_type VARCHAR(40) NOT NULL, -- missing, damaged, seal_broken, location_mismatch, weight_variance
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    finding_description TEXT NOT NULL,
    
    -- Expected vs actual
    expected_location VARCHAR(255),
    actual_location VARCHAR(255),
    expected_seal_number VARCHAR(50),
    actual_seal_number VARCHAR(50),
    
    -- Resolution
    resolution_status VARCHAR(30) DEFAULT 'open', -- open, investigating, resolved, escalated
    resolution_notes TEXT,
    resolved_by_user_id VARCHAR(50),
    resolved_at TIMESTAMP,
    
    -- Photos
    photo_urls JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (audit_id) REFERENCES gold_vault_audits(id) ON DELETE CASCADE,
    FOREIGN KEY (packet_id) REFERENCES gold_packets(id) ON DELETE SET NULL
);

CREATE INDEX idx_findings_audit ON gold_audit_findings(audit_id);
CREATE INDEX idx_findings_packet ON gold_audit_findings(packet_id);
CREATE INDEX idx_findings_severity ON gold_audit_findings(severity);
CREATE INDEX idx_findings_status ON gold_audit_findings(resolution_status);

-- ============================================================================
-- VAULT ACCESS LOG
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_vault_access_log (
    id VARCHAR(50) PRIMARY KEY,
    vault_id VARCHAR(50) NOT NULL,
    
    -- Access details
    access_type VARCHAR(30) NOT NULL, -- entry, exit, inspection, maintenance
    user_id VARCHAR(50) NOT NULL,
    access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Authorization
    authorized_by_user_id VARCHAR(50),
    authorization_reason TEXT,
    
    -- Security
    biometric_verified BOOLEAN DEFAULT FALSE,
    access_card_number VARCHAR(50),
    access_granted BOOLEAN DEFAULT TRUE,
    access_denied_reason TEXT,
    
    -- Duration
    exit_timestamp TIMESTAMP,
    duration_minutes INTEGER,
    
    -- GPS and device
    gps_latitude DECIMAL(10,8),
    gps_longitude DECIMAL(11,8),
    device_info VARCHAR(255),
    
    -- Notes
    purpose TEXT,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (vault_id) REFERENCES gold_vaults(id) ON DELETE CASCADE
);

CREATE INDEX idx_access_vault ON gold_vault_access_log(vault_id);
CREATE INDEX idx_access_user ON gold_vault_access_log(user_id);
CREATE INDEX idx_access_timestamp ON gold_vault_access_log(access_timestamp);
CREATE INDEX idx_access_type ON gold_vault_access_log(access_type);

-- ============================================================================
-- SEAL INVENTORY
-- ============================================================================

CREATE TABLE IF NOT EXISTS gold_security_seals (
    id VARCHAR(50) PRIMARY KEY,
    seal_number VARCHAR(50) UNIQUE NOT NULL,
    seal_type VARCHAR(30) NOT NULL,
    seal_batch_number VARCHAR(50),
    
    -- Status
    seal_status VARCHAR(30) NOT NULL DEFAULT 'available', -- available, issued, used, damaged, destroyed
    
    -- Assignment
    issued_to_branch_id VARCHAR(50),
    issued_to_user_id VARCHAR(50),
    issued_at TIMESTAMP,
    
    -- Usage
    used_on_packet_id VARCHAR(50),
    used_at TIMESTAMP,
    used_by_user_id VARCHAR(50),
    
    -- Disposal
    disposed_at TIMESTAMP,
    disposed_by_user_id VARCHAR(50),
    disposal_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (used_on_packet_id) REFERENCES gold_packets(id) ON DELETE SET NULL
);

CREATE INDEX idx_seals_number ON gold_security_seals(seal_number);
CREATE INDEX idx_seals_status ON gold_security_seals(seal_status);
CREATE INDEX idx_seals_branch ON gold_security_seals(issued_to_branch_id);
CREATE INDEX idx_seals_packet ON gold_security_seals(used_on_packet_id);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- Vault capacity summary
CREATE OR REPLACE VIEW gold_vault_capacity_summary AS
SELECT 
    v.id as vault_id,
    v.vault_code,
    v.vault_name,
    v.branch_id,
    v.capacity_packets,
    v.current_occupancy,
    ROUND((v.current_occupancy::DECIMAL / NULLIF(v.capacity_packets, 0) * 100), 2) as occupancy_percentage,
    v.capacity_packets - v.current_occupancy as available_capacity,
    COUNT(DISTINCT r.id) as total_racks,
    COUNT(DISTINCT l.id) as total_lockers,
    COUNT(DISTINCT t.id) as total_trays,
    COUNT(DISTINCT p.id) as total_packets
FROM gold_vaults v
LEFT JOIN gold_vault_racks r ON v.id = r.vault_id AND r.is_active = TRUE
LEFT JOIN gold_vault_lockers l ON r.id = l.rack_id AND l.is_active = TRUE
LEFT JOIN gold_vault_trays t ON l.id = t.locker_id AND t.is_active = TRUE
LEFT JOIN gold_packets p ON v.id = p.vault_id AND p.packet_status = 'vaulted'
WHERE v.is_active = TRUE
GROUP BY v.id, v.vault_code, v.vault_name, v.branch_id, v.capacity_packets, v.current_occupancy;

-- Packet location hierarchy
CREATE OR REPLACE VIEW gold_packet_locations AS
SELECT 
    p.id as packet_id,
    p.packet_number,
    p.qr_code,
    p.current_location_type,
    v.vault_code,
    v.vault_name,
    r.rack_code,
    l.locker_code,
    t.tray_code,
    CONCAT(v.vault_code, '-', r.rack_code, '-', l.locker_code, '-', t.tray_code) as full_location_code,
    p.packet_status,
    p.seal_number,
    p.seal_status,
    p.total_ornaments,
    p.total_weight_grams,
    p.total_value
FROM gold_packets p
LEFT JOIN gold_vaults v ON p.vault_id = v.id
LEFT JOIN gold_vault_racks r ON p.rack_id = r.id
LEFT JOIN gold_vault_lockers l ON p.locker_id = l.id
LEFT JOIN gold_vault_trays t ON p.tray_id = t.id;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE gold_vaults IS 'Main vault locations at building level';
COMMENT ON TABLE gold_vault_racks IS 'Racks within vaults';
COMMENT ON TABLE gold_vault_lockers IS 'Lockers within racks with lock types';
COMMENT ON TABLE gold_vault_trays IS 'Trays within lockers for packet storage';
COMMENT ON TABLE gold_packets IS 'Main packet records with QR codes and security seals';
COMMENT ON TABLE gold_packet_ornaments IS 'Mapping of ornaments to packets';
COMMENT ON TABLE gold_packet_movements IS 'Complete movement history with GPS tracking';
COMMENT ON TABLE gold_vault_audits IS 'Scheduled and surprise audit records';
COMMENT ON TABLE gold_audit_findings IS 'Individual findings from audits';
COMMENT ON TABLE gold_vault_access_log IS 'Access control and entry/exit logs';
COMMENT ON TABLE gold_security_seals IS 'Seal inventory and usage tracking';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
