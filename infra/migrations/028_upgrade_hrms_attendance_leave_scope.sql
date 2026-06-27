-- Migration 028: Upgrade HRMS scope, attendance, and leave workflows
-- Created: 2026-06-28

ALTER TABLE employees ADD COLUMN IF NOT EXISTS organization_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS zone_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS region_id VARCHAR(36);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS area_id VARCHAR(36);

CREATE INDEX IF NOT EXISTS idx_employees_organization_id ON employees(organization_id);
CREATE INDEX IF NOT EXISTS idx_employees_zone_id ON employees(zone_id);
CREATE INDEX IF NOT EXISTS idx_employees_region_id ON employees(region_id);
CREATE INDEX IF NOT EXISTS idx_employees_area_id ON employees(area_id);

ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS organization_id VARCHAR(36);
ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS zone_id VARCHAR(36);
ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS region_id VARCHAR(36);
ALTER TABLE hr_positions ADD COLUMN IF NOT EXISTS area_id VARCHAR(36);

CREATE INDEX IF NOT EXISTS idx_hr_positions_organization_id ON hr_positions(organization_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_zone_id ON hr_positions(zone_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_region_id ON hr_positions(region_id);
CREATE INDEX IF NOT EXISTS idx_hr_positions_area_id ON hr_positions(area_id);

ALTER TABLE payroll_runs ADD COLUMN IF NOT EXISTS organization_id VARCHAR(36);
ALTER TABLE payroll_runs ADD COLUMN IF NOT EXISTS zone_id VARCHAR(36);
ALTER TABLE payroll_runs ADD COLUMN IF NOT EXISTS region_id VARCHAR(36);
ALTER TABLE payroll_runs ADD COLUMN IF NOT EXISTS area_id VARCHAR(36);
ALTER TABLE payroll_runs ADD COLUMN IF NOT EXISTS branch_id VARCHAR(36);

CREATE INDEX IF NOT EXISTS idx_payroll_runs_organization_id ON payroll_runs(organization_id);
CREATE INDEX IF NOT EXISTS idx_payroll_runs_zone_id ON payroll_runs(zone_id);
CREATE INDEX IF NOT EXISTS idx_payroll_runs_region_id ON payroll_runs(region_id);
CREATE INDEX IF NOT EXISTS idx_payroll_runs_area_id ON payroll_runs(area_id);
CREATE INDEX IF NOT EXISTS idx_payroll_runs_branch_id ON payroll_runs(branch_id);

ALTER TABLE payroll_slips ADD COLUMN IF NOT EXISTS organization_id VARCHAR(36);
ALTER TABLE payroll_slips ADD COLUMN IF NOT EXISTS zone_id VARCHAR(36);
ALTER TABLE payroll_slips ADD COLUMN IF NOT EXISTS region_id VARCHAR(36);
ALTER TABLE payroll_slips ADD COLUMN IF NOT EXISTS area_id VARCHAR(36);
ALTER TABLE payroll_slips ADD COLUMN IF NOT EXISTS branch_id VARCHAR(36);

CREATE INDEX IF NOT EXISTS idx_payroll_slips_organization_id ON payroll_slips(organization_id);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_zone_id ON payroll_slips(zone_id);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_region_id ON payroll_slips(region_id);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_area_id ON payroll_slips(area_id);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_branch_id ON payroll_slips(branch_id);

CREATE TABLE IF NOT EXISTS attendance_records (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    employee_number VARCHAR(100),
    employee_name VARCHAR(255),
    organization_id VARCHAR(36),
    zone_id VARCHAR(36),
    region_id VARCHAR(36),
    area_id VARCHAR(36),
    branch_id VARCHAR(36),
    attendance_date DATE NOT NULL,
    check_in_at TIMESTAMP,
    check_out_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'present',
    work_hours DOUBLE PRECISION DEFAULT 0.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_attendance_employee_date UNIQUE (tenant_id, employee_id, attendance_date)
);

CREATE INDEX IF NOT EXISTS idx_attendance_records_tenant_id ON attendance_records(tenant_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_employee_id ON attendance_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_branch_id ON attendance_records(branch_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_status ON attendance_records(status);
CREATE INDEX IF NOT EXISTS idx_attendance_records_date ON attendance_records(attendance_date);

CREATE TABLE IF NOT EXISTS leave_requests (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    employee_number VARCHAR(100),
    employee_name VARCHAR(255),
    organization_id VARCHAR(36),
    zone_id VARCHAR(36),
    region_id VARCHAR(36),
    area_id VARCHAR(36),
    branch_id VARCHAR(36),
    leave_type VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days DOUBLE PRECISION DEFAULT 0.0,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    approver_employee_id VARCHAR(36),
    decision_notes TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_leave_requests_tenant_id ON leave_requests(tenant_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_employee_id ON leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_branch_id ON leave_requests(branch_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status);
CREATE INDEX IF NOT EXISTS idx_leave_requests_dates ON leave_requests(start_date, end_date);
