-- Migration 027: Upgrade HRMS organization setup
-- Created: 2026-06-27

-- The older HRMS and EOM migrations both referenced an employees table with
-- different shapes. Add the HRMS columns defensively so existing deployments
-- can support tenant-scoped employee master, payroll, and position assignment.
ALTER TABLE employees ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(36) DEFAULT 'default' NOT NULL;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS department_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS designation_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS grade_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS position_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS manager_employee_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS official_email VARCHAR(255);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_code VARCHAR(100);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_name VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_employees_tenant_id ON employees(tenant_id);
CREATE INDEX IF NOT EXISTS idx_employees_department_id ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_designation_id ON employees(designation_id);
CREATE INDEX IF NOT EXISTS idx_employees_grade_id ON employees(grade_id);
CREATE INDEX IF NOT EXISTS idx_employees_position_id ON employees(position_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager_employee_id ON employees(manager_employee_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_employees_official_email ON employees(official_email) WHERE official_email IS NOT NULL;

CREATE TABLE IF NOT EXISTS hr_departments (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    department_code VARCHAR(100) NOT NULL,
    department_name VARCHAR(255) NOT NULL,
    parent_department_id VARCHAR(36),
    department_head_employee_id VARCHAR(36),
    cost_center_code VARCHAR(100),
    profit_center_code VARCHAR(100),
    budget_owner_employee_id VARCHAR(36),
    annual_budget DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_hr_departments_tenant_code UNIQUE (tenant_id, department_code)
);

CREATE INDEX IF NOT EXISTS idx_hr_departments_tenant_id ON hr_departments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_departments_parent_id ON hr_departments(parent_department_id);
CREATE INDEX IF NOT EXISTS idx_hr_departments_status ON hr_departments(status);

CREATE TABLE IF NOT EXISTS hr_grades (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    grade_code VARCHAR(100) NOT NULL,
    grade_name VARCHAR(255) NOT NULL,
    salary_band_min DOUBLE PRECISION DEFAULT 0.0,
    salary_band_max DOUBLE PRECISION DEFAULT 0.0,
    leave_entitlement_days INTEGER DEFAULT 0,
    benefits JSONB,
    approval_limit DOUBLE PRECISION DEFAULT 0.0,
    travel_class VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_hr_grades_tenant_code UNIQUE (tenant_id, grade_code)
);

CREATE INDEX IF NOT EXISTS idx_hr_grades_tenant_id ON hr_grades(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_grades_status ON hr_grades(status);

CREATE TABLE IF NOT EXISTS hr_designations (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    designation_code VARCHAR(100) NOT NULL,
    designation_name VARCHAR(255) NOT NULL,
    grade_id VARCHAR(36),
    salary_band_min DOUBLE PRECISION DEFAULT 0.0,
    salary_band_max DOUBLE PRECISION DEFAULT 0.0,
    approval_limit DOUBLE PRECISION DEFAULT 0.0,
    reporting_level INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_hr_designations_tenant_code UNIQUE (tenant_id, designation_code)
);

CREATE INDEX IF NOT EXISTS idx_hr_designations_tenant_id ON hr_designations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_designations_grade_id ON hr_designations(grade_id);
CREATE INDEX IF NOT EXISTS idx_hr_designations_status ON hr_designations(status);

CREATE TABLE IF NOT EXISTS hr_positions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    position_code VARCHAR(100) NOT NULL,
    position_title VARCHAR(255) NOT NULL,
    department_id VARCHAR(36),
    designation_id VARCHAR(36),
    grade_id VARCHAR(36),
    branch_id VARCHAR(36),
    reports_to_position_id VARCHAR(36),
    occupied_by_employee_id VARCHAR(36),
    approval_limit DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_hr_positions_tenant_code UNIQUE (tenant_id, position_code)
);

CREATE INDEX IF NOT EXISTS idx_hr_positions_tenant_id ON hr_positions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_department_id ON hr_positions(department_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_designation_id ON hr_positions(designation_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_grade_id ON hr_positions(grade_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_branch_id ON hr_positions(branch_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_status ON hr_positions(status);
