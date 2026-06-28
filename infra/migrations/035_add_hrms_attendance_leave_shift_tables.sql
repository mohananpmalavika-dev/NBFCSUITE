-- Migration 035: Add HRMS attendance, shift and leave tables
-- Created: 2026-06-28

CREATE TABLE IF NOT EXISTS hr_shifts (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    shift_code VARCHAR(100) NOT NULL,
    shift_name VARCHAR(255) NOT NULL,
    start_time VARCHAR(16) NOT NULL,
    end_time VARCHAR(16) NOT NULL,
    break_minutes INTEGER DEFAULT 0,
    grace_in INTEGER DEFAULT 0,
    grace_out INTEGER DEFAULT 0,
    weekly_off VARCHAR(64),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hr_shifts_tenant_id ON hr_shifts(tenant_id);

CREATE TABLE IF NOT EXISTS hr_employee_shifts (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    shift_id VARCHAR(36) NOT NULL,
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hr_employee_shifts_employee_id ON hr_employee_shifts(employee_id);
CREATE INDEX IF NOT EXISTS idx_hr_employee_shifts_shift_id ON hr_employee_shifts(shift_id);

CREATE TABLE IF NOT EXISTS hr_attendance (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    attendance_date DATE NOT NULL,
    check_in TIMESTAMP,
    check_out TIMESTAMP,
    working_hours DOUBLE PRECISION DEFAULT 0.0,
    late_minutes INTEGER DEFAULT 0,
    early_exit_minutes INTEGER DEFAULT 0,
    overtime_minutes INTEGER DEFAULT 0,
    attendance_status VARCHAR(50) DEFAULT 'present',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hr_attendance_emp_date ON hr_attendance(employee_id, attendance_date);

CREATE TABLE IF NOT EXISTS hr_attendance_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    attendance_id VARCHAR(36),
    device_ip VARCHAR(64),
    latitude VARCHAR(64),
    longitude VARCHAR(64),
    photo_url VARCHAR(512),
    device_id VARCHAR(128),
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hr_leave_types (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    code VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    is_paid VARCHAR(10) DEFAULT 'yes',
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hr_leave_balances (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    leave_type_id VARCHAR(36) NOT NULL,
    opening DOUBLE PRECISION DEFAULT 0.0,
    credited DOUBLE PRECISION DEFAULT 0.0,
    availed DOUBLE PRECISION DEFAULT 0.0,
    balance DOUBLE PRECISION DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hr_leave_applications (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    employee_id VARCHAR(36) NOT NULL,
    leave_type_id VARCHAR(36) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    reason VARCHAR(1000),
    status VARCHAR(50) DEFAULT 'pending',
    approved_by VARCHAR(36),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hr_holidays (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    holiday_name VARCHAR(255) NOT NULL,
    holiday_date DATE NOT NULL,
    branch VARCHAR(255),
    state VARCHAR(255),
    country VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hr_holidays_date ON hr_holidays(holiday_date);
