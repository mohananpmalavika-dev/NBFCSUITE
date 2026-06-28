-- Migration 034: Add HRMS workforce foundation tables and position fields
-- Created: 2026-06-28

ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS job_role_id VARCHAR(36);
ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS organization_unit_id VARCHAR(36);
ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS budgeted_salary DOUBLE PRECISION DEFAULT 0.0;
ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS effective_from TIMESTAMP NULL;
ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS effective_to TIMESTAMP NULL;

CREATE INDEX IF NOT EXISTS idx_hr_positions_job_role_id ON hr_positions(job_role_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_organization_unit_id ON hr_positions(organization_unit_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_effective_from ON hr_positions(effective_from);
CREATE INDEX IF NOT EXISTS idx_hr_positions_effective_to ON hr_positions(effective_to);

CREATE TABLE IF NOT EXISTS hr_job_families (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    family_code VARCHAR(100) NOT NULL,
    family_name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_hr_job_families_tenant_code UNIQUE (tenant_id, family_code)
);

CREATE INDEX IF NOT EXISTS idx_hr_job_families_tenant_id ON hr_job_families(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_job_families_status ON hr_job_families(status);

CREATE TABLE IF NOT EXISTS hr_job_roles (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    role_code VARCHAR(100) NOT NULL,
    role_name VARCHAR(255) NOT NULL,
    job_family_id VARCHAR(36),
    description VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_hr_job_roles_tenant_code UNIQUE (tenant_id, role_code)
);

CREATE INDEX IF NOT EXISTS idx_hr_job_roles_tenant_id ON hr_job_roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_job_roles_job_family_id ON hr_job_roles(job_family_id);
CREATE INDEX IF NOT EXISTS idx_hr_job_roles_status ON hr_job_roles(status);

CREATE TABLE IF NOT EXISTS hr_employee_assignments (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    position_id VARCHAR(36) NOT NULL,
    assignment_type VARCHAR(50) DEFAULT 'primary',
    status VARCHAR(50) DEFAULT 'active',
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    assigned_by VARCHAR(36),
    notes VARCHAR(1000),
    organization_id VARCHAR(36),
    zone_id VARCHAR(36),
    region_id VARCHAR(36),
    area_id VARCHAR(36),
    branch_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hr_employee_assignments_employee FOREIGN KEY (employee_id) REFERENCES employees(id),
    CONSTRAINT fk_hr_employee_assignments_position FOREIGN KEY (position_id) REFERENCES hr_positions(id)
);

CREATE INDEX IF NOT EXISTS idx_hr_employee_assignments_tenant_id ON hr_employee_assignments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_assignments_employee_id ON hr_employee_assignments(employee_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_assignments_position_id ON hr_employee_assignments(position_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_assignments_status ON hr_employee_assignments(status);

CREATE TABLE IF NOT EXISTS hr_employee_timelines (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_title VARCHAR(255),
    event_details JSONB,
    notes VARCHAR(1000),
    organization_id VARCHAR(36),
    zone_id VARCHAR(36),
    region_id VARCHAR(36),
    area_id VARCHAR(36),
    branch_id VARCHAR(36),
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hr_employee_timelines_employee FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE INDEX IF NOT EXISTS idx_hr_employee_timelines_tenant_id ON hr_employee_timelines(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_timelines_employee_id ON hr_employee_timelines(employee_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_timelines_event_timestamp ON hr_employee_timelines(event_timestamp);
*** End Patch