-- Migration 014: Create HRMS tables
-- Created: 2026-06-27

CREATE TABLE IF NOT EXISTS employees (
    id VARCHAR(36) PRIMARY KEY,
    employee_number VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(36) UNIQUE,
    branch_id VARCHAR(36),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    designation VARCHAR(150),
    department VARCHAR(150),
    employment_type VARCHAR(50) DEFAULT 'full_time',
    status VARCHAR(50) DEFAULT 'active',
    joining_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_employees_user_id ON employees(user_id);
CREATE INDEX IF NOT EXISTS idx_employees_branch_id ON employees(branch_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);
