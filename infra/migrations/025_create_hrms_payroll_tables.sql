-- Migration 025: Create HRMS payroll tables
-- Created: 2026-06-27

CREATE TABLE IF NOT EXISTS payroll_runs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    run_name VARCHAR(255),
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    gross_pay DOUBLE PRECISION DEFAULT 0.0,
    total_deductions DOUBLE PRECISION DEFAULT 0.0,
    net_pay DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalized_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payroll_runs_tenant_id ON payroll_runs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payroll_runs_status ON payroll_runs(status);
CREATE INDEX IF NOT EXISTS idx_payroll_runs_period_end ON payroll_runs(period_end);

CREATE TABLE IF NOT EXISTS payroll_slips (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    payroll_run_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    employee_number VARCHAR(100),
    employee_name VARCHAR(255),
    basic_pay DOUBLE PRECISION DEFAULT 0.0,
    allowances JSONB,
    deductions JSONB,
    tax_amount DOUBLE PRECISION DEFAULT 0.0,
    gross_pay DOUBLE PRECISION DEFAULT 0.0,
    total_deductions DOUBLE PRECISION DEFAULT 0.0,
    net_pay DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payroll_slips_tenant_id ON payroll_slips(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_run_id ON payroll_slips(payroll_run_id);
CREATE INDEX IF NOT EXISTS idx_payroll_slips_employee_id ON payroll_slips(employee_id);

