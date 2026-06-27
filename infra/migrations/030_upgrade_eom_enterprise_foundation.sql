-- Migration 030: Upgrade EOM to Enterprise Organization Management foundation
-- Created: 2026-06-28

CREATE TABLE IF NOT EXISTS enterprises (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    enterprise_code VARCHAR(100) NOT NULL,
    enterprise_name VARCHAR(255) NOT NULL,
    logo_url TEXT,
    vision TEXT,
    mission TEXT,
    corporate_address TEXT,
    corporate_office TEXT,
    country VARCHAR(100) DEFAULT 'India',
    currency VARCHAR(10) DEFAULT 'INR',
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    financial_year_start VARCHAR(10) DEFAULT '04-01',
    financial_year_end VARCHAR(10) DEFAULT '03-31',
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_enterprises_tenant_code UNIQUE (tenant_id, enterprise_code)
);

CREATE INDEX IF NOT EXISTS idx_enterprises_tenant_id ON enterprises(tenant_id);
CREATE INDEX IF NOT EXISTS idx_enterprises_status ON enterprises(status);

ALTER TABLE brands ADD COLUMN IF NOT EXISTS enterprise_id VARCHAR(36);
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_brands_enterprise_id') THEN
        ALTER TABLE brands ADD CONSTRAINT fk_brands_enterprise_id FOREIGN KEY (enterprise_id) REFERENCES enterprises(id) ON DELETE SET NULL;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_brands_enterprise_id ON brands(enterprise_id);

ALTER TABLE business_units ADD COLUMN IF NOT EXISTS created_by VARCHAR(36);
ALTER TABLE business_units ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE business_units ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE TABLE IF NOT EXISTS divisions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    business_unit_id VARCHAR(36) NOT NULL,
    division_code VARCHAR(100) NOT NULL,
    division_name VARCHAR(255) NOT NULL,
    division_head VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON DELETE CASCADE,
    CONSTRAINT uq_divisions_bu_code UNIQUE (business_unit_id, division_code),
    CONSTRAINT uq_divisions_tenant_code UNIQUE (tenant_id, division_code)
);

CREATE INDEX IF NOT EXISTS idx_divisions_tenant_id ON divisions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_divisions_business_unit_id ON divisions(business_unit_id);

ALTER TABLE eom_zones ADD COLUMN IF NOT EXISTS division_id VARCHAR(36);
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_eom_zones_division_id') THEN
        ALTER TABLE eom_zones ADD CONSTRAINT fk_eom_zones_division_id FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE SET NULL;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_eom_zones_division_id ON eom_zones(division_id);

CREATE TABLE IF NOT EXISTS teams (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    department_id VARCHAR(36) NOT NULL,
    team_code VARCHAR(100) NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    team_lead_employee_id VARCHAR(36),
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY (team_lead_employee_id) REFERENCES employees(id) ON DELETE SET NULL,
    CONSTRAINT uq_teams_department_code UNIQUE (department_id, team_code),
    CONSTRAINT uq_teams_tenant_code UNIQUE (tenant_id, team_code)
);

CREATE INDEX IF NOT EXISTS idx_teams_tenant_id ON teams(tenant_id);
CREATE INDEX IF NOT EXISTS idx_teams_department_id ON teams(department_id);

CREATE TABLE IF NOT EXISTS positions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    department_id VARCHAR(36),
    team_id VARCHAR(36),
    position_code VARCHAR(100) NOT NULL,
    position_title VARCHAR(255) NOT NULL,
    reports_to_position_id VARCHAR(36),
    grade VARCHAR(100),
    employment_type VARCHAR(50) DEFAULT 'full_time',
    status VARCHAR(50) DEFAULT 'open',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL,
    FOREIGN KEY (reports_to_position_id) REFERENCES positions(id) ON DELETE SET NULL,
    CONSTRAINT uq_positions_tenant_code UNIQUE (tenant_id, position_code)
);

CREATE INDEX IF NOT EXISTS idx_positions_tenant_id ON positions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_positions_department_id ON positions(department_id);
CREATE INDEX IF NOT EXISTS idx_positions_team_id ON positions(team_id);

CREATE TABLE IF NOT EXISTS vendors (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    vendor_code VARCHAR(100) NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_type VARCHAR(100),
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    gst VARCHAR(50),
    pan VARCHAR(20),
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vendors_tenant_code UNIQUE (tenant_id, vendor_code)
);

CREATE INDEX IF NOT EXISTS idx_vendors_tenant_id ON vendors(tenant_id);
CREATE INDEX IF NOT EXISTS idx_vendors_status ON vendors(status);

CREATE TABLE IF NOT EXISTS assets (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    asset_code VARCHAR(100) NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(100),
    branch_id VARCHAR(36),
    department_id VARCHAR(36),
    assigned_employee_id VARCHAR(36),
    vendor_id VARCHAR(36),
    purchase_value NUMERIC(18, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES eom_branches(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_employee_id) REFERENCES employees(id) ON DELETE SET NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL,
    CONSTRAINT uq_assets_tenant_code UNIQUE (tenant_id, asset_code)
);

CREATE INDEX IF NOT EXISTS idx_assets_tenant_id ON assets(tenant_id);
CREATE INDEX IF NOT EXISTS idx_assets_branch_id ON assets(branch_id);
CREATE INDEX IF NOT EXISTS idx_assets_department_id ON assets(department_id);
CREATE INDEX IF NOT EXISTS idx_assets_vendor_id ON assets(vendor_id);

ALTER TABLE employee_hierarchy ADD COLUMN IF NOT EXISTS division_id VARCHAR(36);
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_employee_hierarchy_division_id') THEN
        ALTER TABLE employee_hierarchy ADD CONSTRAINT fk_employee_hierarchy_division_id FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE SET NULL;
    END IF;
END $$;
CREATE INDEX IF NOT EXISTS idx_employee_hierarchy_division_id ON employee_hierarchy(division_id);
