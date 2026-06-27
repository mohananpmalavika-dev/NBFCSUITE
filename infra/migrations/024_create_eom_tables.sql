-- Migration 024: Enterprise Organization Management (EOM) - NBFC Brand/Entity/Zone/Region/Area/Cluster/Branch
-- Created: 2026-06-27

-- Notes
-- - Non-breaking approach: keep legacy banking offices (head_offices/zonal_offices/...) intact.
-- - This migration introduces an NBFC-focused EOM hierarchy under new tables:
--   brands -> legal_entities -> business_units -> eom_zones -> eom_regions -> eom_areas -> eom_clusters (optional) -> eom_branches -> departments -> employees.
-- - IDs use VARCHAR(36) to match existing migration style.

-- ============
-- Module 1: Brand
-- ============
CREATE TABLE IF NOT EXISTS brands (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    brand_code VARCHAR(100) NOT NULL,
    brand_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    short_name VARCHAR(50),
    logo_url TEXT,
    theme_color VARCHAR(50),
    website VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    gst VARCHAR(50),
    pan VARCHAR(20),
    cin VARCHAR(50),
    license_no VARCHAR(100),
    registration_no VARCHAR(100),
    country VARCHAR(100),
    state VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    currency VARCHAR(10) DEFAULT 'INR',
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_brands_tenant_code UNIQUE (tenant_id, brand_code),
    CONSTRAINT uq_brands_brand_code UNIQUE (brand_code)
);

CREATE INDEX IF NOT EXISTS idx_brands_tenant_id ON brands(tenant_id);
CREATE INDEX IF NOT EXISTS idx_brands_status ON brands(status);

-- =====================
-- Module 2: Legal Entity
-- =====================
CREATE TABLE IF NOT EXISTS legal_entities (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    brand_id VARCHAR(36) NOT NULL,
    entity_code VARCHAR(100) NOT NULL,
    entity_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) DEFAULT 'company',
    gst VARCHAR(50),
    pan VARCHAR(20),
    tan VARCHAR(20),
    cin VARCHAR(50),
    registered_address TEXT,
    state VARCHAR(100),
    country VARCHAR(100),
    license VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE,
    CONSTRAINT uq_legal_entities_brand_code UNIQUE (brand_id, entity_code),
    CONSTRAINT uq_legal_entities_tenant_code UNIQUE (tenant_id, entity_code)
);

CREATE INDEX IF NOT EXISTS idx_legal_entities_tenant_id ON legal_entities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_legal_entities_brand_id ON legal_entities(brand_id);

-- ==================
-- Module 3: Business Unit
-- ==================
CREATE TABLE IF NOT EXISTS business_units (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    legal_entity_id VARCHAR(36) NOT NULL,
    business_unit_code VARCHAR(100) NOT NULL,
    business_unit_name VARCHAR(255) NOT NULL,
    head VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',

    FOREIGN KEY (legal_entity_id) REFERENCES legal_entities(id) ON DELETE CASCADE,
    CONSTRAINT uq_business_units_entity_code UNIQUE (legal_entity_id, business_unit_code),
    CONSTRAINT uq_business_units_tenant_code UNIQUE (tenant_id, business_unit_code)
);

CREATE INDEX IF NOT EXISTS idx_business_units_tenant_id ON business_units(tenant_id);
CREATE INDEX IF NOT EXISTS idx_business_units_legal_entity_id ON business_units(legal_entity_id);

-- ============
-- Module 4: Zone
-- ============
CREATE TABLE IF NOT EXISTS eom_zones (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    business_unit_id VARCHAR(36) NOT NULL,
    zone_code VARCHAR(100) NOT NULL,
    zone_name VARCHAR(255) NOT NULL,
    zone_head VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON DELETE CASCADE,
    CONSTRAINT uq_eom_zones_bu_code UNIQUE (business_unit_id, zone_code),
    CONSTRAINT uq_eom_zones_tenant_code UNIQUE (tenant_id, zone_code)
);

CREATE INDEX IF NOT EXISTS idx_eom_zones_tenant_id ON eom_zones(tenant_id);
CREATE INDEX IF NOT EXISTS idx_eom_zones_business_unit_id ON eom_zones(business_unit_id);

-- ============
-- Module 5: Region
-- ============
CREATE TABLE IF NOT EXISTS eom_regions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    zone_id VARCHAR(36) NOT NULL,
    region_code VARCHAR(100) NOT NULL,
    region_name VARCHAR(255) NOT NULL,
    regional_manager VARCHAR(255),
    office_address TEXT,
    status VARCHAR(50) DEFAULT 'active',

    FOREIGN KEY (zone_id) REFERENCES eom_zones(id) ON DELETE CASCADE,
    CONSTRAINT uq_eom_regions_zone_code UNIQUE (zone_id, region_code),
    CONSTRAINT uq_eom_regions_tenant_code UNIQUE (tenant_id, region_code)
);

CREATE INDEX IF NOT EXISTS idx_eom_regions_tenant_id ON eom_regions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_eom_regions_zone_id ON eom_regions(zone_id);

-- ============
-- Module 6: Area
-- ============
CREATE TABLE IF NOT EXISTS eom_areas (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    region_id VARCHAR(36) NOT NULL,
    area_code VARCHAR(100) NOT NULL,
    area_name VARCHAR(255) NOT NULL,
    area_manager VARCHAR(255),
    office_address TEXT,
    status VARCHAR(50) DEFAULT 'active',

    FOREIGN KEY (region_id) REFERENCES eom_regions(id) ON DELETE CASCADE,
    CONSTRAINT uq_eom_areas_region_code UNIQUE (region_id, area_code),
    CONSTRAINT uq_eom_areas_tenant_code UNIQUE (tenant_id, area_code)
);

CREATE INDEX IF NOT EXISTS idx_eom_areas_tenant_id ON eom_areas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_eom_areas_region_id ON eom_areas(region_id);

-- =====================
-- Module 7: Cluster (Optional)
-- =====================
CREATE TABLE IF NOT EXISTS eom_clusters (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    area_id VARCHAR(36) NOT NULL,
    cluster_code VARCHAR(100) NOT NULL,
    cluster_name VARCHAR(255) NOT NULL,
    cluster_manager VARCHAR(255),

    FOREIGN KEY (area_id) REFERENCES eom_areas(id) ON DELETE CASCADE,
    CONSTRAINT uq_eom_clusters_area_code UNIQUE (area_id, cluster_code),
    CONSTRAINT uq_eom_clusters_tenant_code UNIQUE (tenant_id, cluster_code)
);

CREATE INDEX IF NOT EXISTS idx_eom_clusters_tenant_id ON eom_clusters(tenant_id);
CREATE INDEX IF NOT EXISTS idx_eom_clusters_area_id ON eom_clusters(area_id);

-- ============
-- Module 8: Branch
-- ============
CREATE TABLE IF NOT EXISTS eom_branches (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    branch_code VARCHAR(100) NOT NULL,

    -- Hierarchy
    zone_id VARCHAR(36),
    region_id VARCHAR(36),
    area_id VARCHAR(36) NOT NULL,
    cluster_id VARCHAR(36),

    -- Branch basics
    branch_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    branch_type VARCHAR(100),
    branch_category VARCHAR(100),
    branch_types JSONB,

    -- Address
    door_no VARCHAR(50),
    building VARCHAR(255),
    street VARCHAR(255),
    village VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    pincode VARCHAR(20),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),

    -- Contact
    contact_phone VARCHAR(50),
    mobile VARCHAR(50),
    email VARCHAR(255),
    whatsapp VARCHAR(50),
    website VARCHAR(255),

    -- Status
    status VARCHAR(50) DEFAULT 'draft',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Basic constraints
    CONSTRAINT uq_eom_branches_tenant_branch_code UNIQUE (tenant_id, branch_code),
    CONSTRAINT uq_eom_branches_branch_code UNIQUE (branch_code),

    FOREIGN KEY (zone_id) REFERENCES eom_zones(id) ON DELETE SET NULL,
    FOREIGN KEY (region_id) REFERENCES eom_regions(id) ON DELETE SET NULL,
    FOREIGN KEY (area_id) REFERENCES eom_areas(id) ON DELETE CASCADE,
    FOREIGN KEY (cluster_id) REFERENCES eom_clusters(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_eom_branches_tenant_id ON eom_branches(tenant_id);
CREATE INDEX IF NOT EXISTS idx_eom_branches_area_id ON eom_branches(area_id);
CREATE INDEX IF NOT EXISTS idx_eom_branches_status ON eom_branches(status);

-- ==================
-- Departments + Employees
-- ==================
CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    branch_id VARCHAR(36) NOT NULL,
    department_code VARCHAR(100) NOT NULL,
    department_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (branch_id) REFERENCES eom_branches(id) ON DELETE CASCADE,
    CONSTRAINT uq_departments_branch_code UNIQUE (branch_id, department_code),
    CONSTRAINT uq_departments_tenant_code UNIQUE (tenant_id, department_code)
);

CREATE INDEX IF NOT EXISTS idx_departments_tenant_id ON departments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_departments_branch_id ON departments(branch_id);

CREATE TABLE IF NOT EXISTS employees (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,

    employee_code VARCHAR(100),
    employee_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',

    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_employees_tenant_id ON employees(tenant_id);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);

-- Explicit hierarchy assignment for each employee.
CREATE TABLE IF NOT EXISTS employee_hierarchy (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,

    brand_id VARCHAR(36),
    legal_entity_id VARCHAR(36),
    business_unit_id VARCHAR(36),
    zone_id VARCHAR(36),
    region_id VARCHAR(36),
    area_id VARCHAR(36),
    cluster_id VARCHAR(36),
    branch_id VARCHAR(36),
    department_id VARCHAR(36),

    position_title VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,

    FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE SET NULL,
    FOREIGN KEY (legal_entity_id) REFERENCES legal_entities(id) ON DELETE SET NULL,
    FOREIGN KEY (business_unit_id) REFERENCES business_units(id) ON DELETE SET NULL,
    FOREIGN KEY (zone_id) REFERENCES eom_zones(id) ON DELETE SET NULL,
    FOREIGN KEY (region_id) REFERENCES eom_regions(id) ON DELETE SET NULL,
    FOREIGN KEY (area_id) REFERENCES eom_areas(id) ON DELETE SET NULL,
    FOREIGN KEY (cluster_id) REFERENCES eom_clusters(id) ON DELETE SET NULL,
    FOREIGN KEY (branch_id) REFERENCES eom_branches(id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_employee_hierarchy_tenant_id ON employee_hierarchy(tenant_id);
CREATE INDEX IF NOT EXISTS idx_employee_hierarchy_employee_id ON employee_hierarchy(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_hierarchy_branch_id ON employee_hierarchy(branch_id);

-- Customer mapping for branch ownership.
CREATE TABLE IF NOT EXISTS customer_branch_mapping (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    branch_id VARCHAR(36) NOT NULL,

    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP NULL,
    status VARCHAR(50) DEFAULT 'active',

    -- transfer history metadata
    transferred_from_branch_id VARCHAR(36) NULL,
    transferred_by VARCHAR(36),
    transferred_at TIMESTAMP,

    FOREIGN KEY (branch_id) REFERENCES eom_branches(id) ON DELETE CASCADE,
    FOREIGN KEY (transferred_from_branch_id) REFERENCES eom_branches(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_customer_branch_mapping_tenant ON customer_branch_mapping(tenant_id);
CREATE INDEX IF NOT EXISTS idx_customer_branch_mapping_customer ON customer_branch_mapping(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_branch_mapping_branch ON customer_branch_mapping(branch_id);

