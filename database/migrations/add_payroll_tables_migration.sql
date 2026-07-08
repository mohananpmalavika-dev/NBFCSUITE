-- ============================================
-- HRMS Payroll Management Module Migration
-- Version: 1.0
-- Date: July 8, 2026
-- Description: Creates 11 tables for payroll management
-- ============================================

-- Table 1: Salary Components Master
CREATE TABLE IF NOT EXISTS salary_components (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    component_code VARCHAR(50) NOT NULL UNIQUE,
    component_name VARCHAR(200) NOT NULL,
    component_type VARCHAR(30) NOT NULL,
    calculation_type VARCHAR(30) NOT NULL,
    default_value NUMERIC(15, 2) DEFAULT 0.00,
    percentage NUMERIC(5, 2),
    formula TEXT,
    display_order INTEGER DEFAULT 0,
    is_taxable BOOLEAN DEFAULT TRUE,
    is_part_of_ctc BOOLEAN DEFAULT TRUE,
    is_statutory BOOLEAN DEFAULT FALSE,
    statutory_type VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_system_component BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for salary_components
CREATE INDEX idx_salary_components_tenant ON salary_components(tenant_id);
CREATE INDEX idx_salary_components_code ON salary_components(component_code);
CREATE INDEX idx_salary_components_type ON salary_components(component_type);
CREATE INDEX idx_salary_components_active ON salary_components(is_active);
CREATE INDEX idx_salary_components_statutory ON salary_components(is_statutory);

-- Table 2: Salary Structures
CREATE TABLE IF NOT EXISTS salary_structures (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    structure_code VARCHAR(50) NOT NULL UNIQUE,
    structure_name VARCHAR(200) NOT NULL,
    grade_level VARCHAR(50),
    department VARCHAR(100),
    designation VARCHAR(100),
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for salary_structures
CREATE INDEX idx_salary_structures_tenant ON salary_structures(tenant_id);
CREATE INDEX idx_salary_structures_code ON salary_structures(structure_code);
CREATE INDEX idx_salary_structures_active ON salary_structures(is_active);
CREATE INDEX idx_salary_structures_effective ON salary_structures(effective_from, effective_to);


-- Table 3: Salary Structure Components (Junction Table)
CREATE TABLE IF NOT EXISTS salary_structure_components (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    structure_id INTEGER NOT NULL REFERENCES salary_structures(id),
    component_id INTEGER NOT NULL REFERENCES salary_components(id),
    calculation_type VARCHAR(30) NOT NULL,
    default_value NUMERIC(15, 2),
    percentage NUMERIC(5, 2),
    formula TEXT,
    is_mandatory BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for salary_structure_components
CREATE INDEX idx_structure_components_tenant ON salary_structure_components(tenant_id);
CREATE INDEX idx_structure_components_structure ON salary_structure_components(structure_id);
CREATE INDEX idx_structure_components_component ON salary_structure_components(component_id);

-- Table 4: Employee Salaries
CREATE TABLE IF NOT EXISTS employee_salaries (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    structure_id INTEGER NOT NULL REFERENCES salary_structures(id),
    ctc_annual NUMERIC(15, 2) NOT NULL,
    gross_monthly NUMERIC(15, 2) NOT NULL,
    net_monthly NUMERIC(15, 2) NOT NULL,
    bank_name VARCHAR(200),
    bank_account_number VARCHAR(50),
    bank_ifsc_code VARCHAR(20),
    bank_branch VARCHAR(200),
    payment_mode VARCHAR(20) DEFAULT 'BANK_TRANSFER',
    tax_regime VARCHAR(10) DEFAULT 'OLD',
    pan_number VARCHAR(20),
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for employee_salaries
CREATE INDEX idx_employee_salaries_tenant ON employee_salaries(tenant_id);
CREATE INDEX idx_employee_salaries_employee ON employee_salaries(employee_id);
CREATE INDEX idx_employee_salaries_structure ON employee_salaries(structure_id);
CREATE INDEX idx_employee_salaries_active ON employee_salaries(is_active);
CREATE INDEX idx_employee_salaries_effective ON employee_salaries(effective_from, effective_to);

-- Table 5: Employee Salary Components
CREATE TABLE IF NOT EXISTS employee_salary_components (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    employee_salary_id INTEGER NOT NULL REFERENCES employee_salaries(id),
    component_id INTEGER NOT NULL REFERENCES salary_components(id),
    monthly_amount NUMERIC(15, 2) NOT NULL,
    annual_amount NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for employee_salary_components
CREATE INDEX idx_emp_salary_comps_tenant ON employee_salary_components(tenant_id);
CREATE INDEX idx_emp_salary_comps_emp_salary ON employee_salary_components(employee_salary_id);
CREATE INDEX idx_emp_salary_comps_component ON employee_salary_components(component_id);


-- Table 6: Payroll Runs
CREATE TABLE IF NOT EXISTS payroll_runs (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    run_code VARCHAR(50) NOT NULL UNIQUE,
    run_name VARCHAR(200) NOT NULL,
    payroll_month INTEGER NOT NULL,
    payroll_year INTEGER NOT NULL,
    pay_date DATE NOT NULL,
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    total_employees INTEGER DEFAULT 0,
    processed_employees INTEGER DEFAULT 0,
    total_gross NUMERIC(15, 2) DEFAULT 0.00,
    total_deductions NUMERIC(15, 2) DEFAULT 0.00,
    total_net_pay NUMERIC(15, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'DRAFT',
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    approved_by INTEGER,
    approved_at TIMESTAMP,
    approval_remarks TEXT,
    include_arrears BOOLEAN DEFAULT FALSE,
    include_bonus BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for payroll_runs
CREATE INDEX idx_payroll_runs_tenant ON payroll_runs(tenant_id);
CREATE INDEX idx_payroll_runs_code ON payroll_runs(run_code);
CREATE INDEX idx_payroll_runs_month_year ON payroll_runs(payroll_month, payroll_year);
CREATE INDEX idx_payroll_runs_status ON payroll_runs(status);
CREATE INDEX idx_payroll_runs_date ON payroll_runs(pay_date);

-- Table 7: Payslips
CREATE TABLE IF NOT EXISTS payslips (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    payroll_run_id INTEGER NOT NULL REFERENCES payroll_runs(id),
    employee_id INTEGER NOT NULL,
    payslip_number VARCHAR(50) NOT NULL UNIQUE,
    payroll_month INTEGER NOT NULL,
    payroll_year INTEGER NOT NULL,
    pay_date DATE NOT NULL,
    employee_code VARCHAR(50),
    employee_name VARCHAR(200),
    designation VARCHAR(100),
    department VARCHAR(100),
    pan_number VARCHAR(20),
    uan_number VARCHAR(20),
    esi_number VARCHAR(20),
    days_in_month INTEGER NOT NULL,
    days_worked NUMERIC(5, 2) NOT NULL,
    days_lop NUMERIC(5, 2) DEFAULT 0.00,
    basic_salary NUMERIC(15, 2) NOT NULL,
    gross_earnings NUMERIC(15, 2) NOT NULL,
    total_deductions NUMERIC(15, 2) NOT NULL,
    net_salary NUMERIC(15, 2) NOT NULL,
    pf_employee NUMERIC(15, 2) DEFAULT 0.00,
    pf_employer NUMERIC(15, 2) DEFAULT 0.00,
    esi_employee NUMERIC(15, 2) DEFAULT 0.00,
    esi_employer NUMERIC(15, 2) DEFAULT 0.00,
    pt_deduction NUMERIC(15, 2) DEFAULT 0.00,
    tds_deduction NUMERIC(15, 2) DEFAULT 0.00,
    payment_mode VARCHAR(20) DEFAULT 'BANK_TRANSFER',
    payment_status VARCHAR(20) DEFAULT 'PENDING',
    payment_date DATE,
    payment_reference VARCHAR(100),
    bank_account_number VARCHAR(50),
    bank_ifsc_code VARCHAR(20),
    payslip_pdf_url VARCHAR(500),
    is_hold BOOLEAN DEFAULT FALSE,
    hold_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for payslips
CREATE INDEX idx_payslips_tenant ON payslips(tenant_id);
CREATE INDEX idx_payslips_run ON payslips(payroll_run_id);
CREATE INDEX idx_payslips_employee ON payslips(employee_id);
CREATE INDEX idx_payslips_number ON payslips(payslip_number);
CREATE INDEX idx_payslips_month_year ON payslips(payroll_month, payroll_year);
CREATE INDEX idx_payslips_status ON payslips(payment_status);


-- Table 6: Payroll Runs
CREATE TABLE IF NOT EXISTS payroll_runs (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    run_code VARCHAR(50) NOT NULL UNIQUE,
    run_name VARCHAR(200) NOT NULL,
    payroll_month INTEGER NOT NULL CHECK (payroll_month >= 1 AND payroll_month <= 12),
    payroll_year INTEGER NOT NULL,
    pay_date DATE NOT NULL,
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    total_employees INTEGER DEFAULT 0,
    processed_employees INTEGER DEFAULT 0,
    total_gross NUMERIC(15, 2) DEFAULT 0.00,
    total_deductions NUMERIC(15, 2) DEFAULT 0.00,
    total_net_pay NUMERIC(15, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'DRAFT',
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    approved_by INTEGER,
    approved_at TIMESTAMP,
    approval_remarks TEXT,
    include_arrears BOOLEAN DEFAULT FALSE,
    include_bonus BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for payroll_runs
CREATE INDEX idx_payroll_runs_tenant ON payroll_runs(tenant_id);
CREATE INDEX idx_payroll_runs_code ON payroll_runs(run_code);
CREATE INDEX idx_payroll_runs_status ON payroll_runs(status);
CREATE INDEX idx_payroll_runs_month_year ON payroll_runs(payroll_month, payroll_year);
CREATE INDEX idx_payroll_runs_period ON payroll_runs(period_start_date, period_end_date);

-- Table 7: Payslips
CREATE TABLE IF NOT EXISTS payslips (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    payroll_run_id INTEGER NOT NULL REFERENCES payroll_runs(id),
    employee_id INTEGER NOT NULL,
    payslip_number VARCHAR(50) NOT NULL UNIQUE,
    payroll_month INTEGER NOT NULL,
    payroll_year INTEGER NOT NULL,
    pay_date DATE NOT NULL,
    employee_code VARCHAR(50),
    employee_name VARCHAR(200),
    designation VARCHAR(100),
    department VARCHAR(100),
    pan_number VARCHAR(20),
    uan_number VARCHAR(20),
    esi_number VARCHAR(20),
    days_in_month INTEGER NOT NULL,
    days_worked NUMERIC(5, 2) NOT NULL,
    days_lop NUMERIC(5, 2) DEFAULT 0.00,
    basic_salary NUMERIC(15, 2) NOT NULL,
    gross_earnings NUMERIC(15, 2) NOT NULL,
    total_deductions NUMERIC(15, 2) NOT NULL,
    net_salary NUMERIC(15, 2) NOT NULL,
    pf_employee NUMERIC(15, 2) DEFAULT 0.00,
    pf_employer NUMERIC(15, 2) DEFAULT 0.00,
    esi_employee NUMERIC(15, 2) DEFAULT 0.00,
    esi_employer NUMERIC(15, 2) DEFAULT 0.00,
    pt_deduction NUMERIC(15, 2) DEFAULT 0.00,
    tds_deduction NUMERIC(15, 2) DEFAULT 0.00,
    payment_mode VARCHAR(20) DEFAULT 'BANK_TRANSFER',
    payment_status VARCHAR(20) DEFAULT 'PENDING',
    payment_date DATE,
    payment_reference VARCHAR(100),
    bank_account_number VARCHAR(50),
    bank_ifsc_code VARCHAR(20),
    payslip_pdf_url VARCHAR(500),
    is_hold BOOLEAN DEFAULT FALSE,
    hold_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for payslips
CREATE INDEX idx_payslips_tenant ON payslips(tenant_id);
CREATE INDEX idx_payslips_number ON payslips(payslip_number);
CREATE INDEX idx_payslips_run ON payslips(payroll_run_id);
CREATE INDEX idx_payslips_employee ON payslips(employee_id);
CREATE INDEX idx_payslips_month_year ON payslips(payroll_month, payroll_year);
CREATE INDEX idx_payslips_status ON payslips(payment_status);


-- Table 8: Payslip Components
CREATE TABLE IF NOT EXISTS payslip_components (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    payslip_id INTEGER NOT NULL REFERENCES payslips(id),
    component_id INTEGER NOT NULL,
    component_code VARCHAR(50) NOT NULL,
    component_name VARCHAR(200) NOT NULL,
    component_type VARCHAR(30) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for payslip_components
CREATE INDEX idx_payslip_components_tenant ON payslip_components(tenant_id);
CREATE INDEX idx_payslip_components_payslip ON payslip_components(payslip_id);
CREATE INDEX idx_payslip_components_component ON payslip_components(component_id);

-- Table 9: Statutory Compliance
CREATE TABLE IF NOT EXISTS statutory_compliance (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    payroll_run_id INTEGER REFERENCES payroll_runs(id),
    compliance_month INTEGER NOT NULL CHECK (compliance_month >= 1 AND compliance_month <= 12),
    compliance_year INTEGER NOT NULL,
    statutory_type VARCHAR(20) NOT NULL,
    employee_contribution NUMERIC(15, 2) DEFAULT 0.00,
    employer_contribution NUMERIC(15, 2) DEFAULT 0.00,
    total_amount NUMERIC(15, 2) NOT NULL,
    challan_number VARCHAR(100),
    payment_date DATE,
    due_date DATE,
    is_paid BOOLEAN DEFAULT FALSE,
    payment_reference VARCHAR(100),
    return_filed BOOLEAN DEFAULT FALSE,
    return_file_date DATE,
    return_acknowledgement VARCHAR(100),
    challan_pdf_url VARCHAR(500),
    return_pdf_url VARCHAR(500),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for statutory_compliance
CREATE INDEX idx_statutory_compliance_tenant ON statutory_compliance(tenant_id);
CREATE INDEX idx_statutory_compliance_run ON statutory_compliance(payroll_run_id);
CREATE INDEX idx_statutory_compliance_type ON statutory_compliance(statutory_type);
CREATE INDEX idx_statutory_compliance_month_year ON statutory_compliance(compliance_month, compliance_year);
CREATE INDEX idx_statutory_compliance_paid ON statutory_compliance(is_paid);
CREATE INDEX idx_statutory_compliance_filed ON statutory_compliance(return_filed);

-- Table 10: Form 16
CREATE TABLE IF NOT EXISTS form16 (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    financial_year VARCHAR(10) NOT NULL,
    form16_number VARCHAR(50) NOT NULL UNIQUE,
    employee_code VARCHAR(50),
    employee_name VARCHAR(200),
    pan_number VARCHAR(20) NOT NULL,
    designation VARCHAR(100),
    employer_name VARCHAR(200),
    employer_tan VARCHAR(20),
    employer_address TEXT,
    total_tds_deposited NUMERIC(15, 2) DEFAULT 0.00,
    gross_salary NUMERIC(15, 2) NOT NULL,
    exemptions NUMERIC(15, 2) DEFAULT 0.00,
    taxable_salary NUMERIC(15, 2) NOT NULL,
    deduction_80c NUMERIC(15, 2) DEFAULT 0.00,
    deduction_80d NUMERIC(15, 2) DEFAULT 0.00,
    deduction_80g NUMERIC(15, 2) DEFAULT 0.00,
    deduction_80e NUMERIC(15, 2) DEFAULT 0.00,
    other_deductions NUMERIC(15, 2) DEFAULT 0.00,
    total_deductions NUMERIC(15, 2) DEFAULT 0.00,
    total_income NUMERIC(15, 2) NOT NULL,
    tax_on_total_income NUMERIC(15, 2) NOT NULL,
    surcharge NUMERIC(15, 2) DEFAULT 0.00,
    education_cess NUMERIC(15, 2) DEFAULT 0.00,
    total_tax_payable NUMERIC(15, 2) NOT NULL,
    relief_under_89 NUMERIC(15, 2) DEFAULT 0.00,
    net_tax_payable NUMERIC(15, 2) NOT NULL,
    tds_deducted NUMERIC(15, 2) NOT NULL,
    tax_regime VARCHAR(10) DEFAULT 'OLD',
    generated_date DATE NOT NULL,
    generated_by INTEGER,
    form16_pdf_url VARCHAR(500),
    is_issued BOOLEAN DEFAULT FALSE,
    issued_date DATE,
    is_digitally_signed BOOLEAN DEFAULT FALSE,
    signature_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for form16
CREATE INDEX idx_form16_tenant ON form16(tenant_id);
CREATE INDEX idx_form16_number ON form16(form16_number);
CREATE INDEX idx_form16_employee ON form16(employee_id);
CREATE INDEX idx_form16_financial_year ON form16(financial_year);
CREATE INDEX idx_form16_issued ON form16(is_issued);

-- Table 11: Payment Files
CREATE TABLE IF NOT EXISTS payment_files (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    payroll_run_id INTEGER NOT NULL REFERENCES payroll_runs(id),
    file_code VARCHAR(50) NOT NULL UNIQUE,
    file_name VARCHAR(200) NOT NULL,
    file_format VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    file_size INTEGER,
    total_records INTEGER DEFAULT 0,
    total_amount NUMERIC(15, 2) DEFAULT 0.00,
    bank_name VARCHAR(200),
    payment_month INTEGER NOT NULL,
    payment_year INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    uploaded_to_bank BOOLEAN DEFAULT FALSE,
    upload_date TIMESTAMP,
    uploaded_by INTEGER,
    bank_reference_number VARCHAR(100),
    bank_response_date TIMESTAMP,
    bank_response_message TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Indexes for payment_files
CREATE INDEX idx_payment_files_tenant ON payment_files(tenant_id);
CREATE INDEX idx_payment_files_code ON payment_files(file_code);
CREATE INDEX idx_payment_files_run ON payment_files(payroll_run_id);
CREATE INDEX idx_payment_files_status ON payment_files(status);
CREATE INDEX idx_payment_files_month_year ON payment_files(payment_month, payment_year);
CREATE INDEX idx_payment_files_uploaded ON payment_files(uploaded_to_bank);

-- ============================================
-- Sample Data for System Components
-- ============================================

-- Insert standard earnings components
INSERT INTO salary_components (tenant_id, component_code, component_name, component_type, calculation_type, is_system_component, is_taxable, is_part_of_ctc, display_order)
VALUES 
(1, 'BASIC', 'Basic Salary', 'EARNING', 'FIXED', TRUE, TRUE, TRUE, 1),
(1, 'HRA', 'House Rent Allowance', 'EARNING', 'PERCENTAGE_OF_BASIC', TRUE, TRUE, TRUE, 2),
(1, 'CONVEYANCE', 'Conveyance Allowance', 'EARNING', 'FIXED', TRUE, TRUE, TRUE, 3),
(1, 'SPECIAL', 'Special Allowance', 'EARNING', 'FIXED', TRUE, TRUE, TRUE, 4),
(1, 'MEDICAL', 'Medical Allowance', 'EARNING', 'FIXED', TRUE, TRUE, TRUE, 5);

-- Insert standard deductions
INSERT INTO salary_components (tenant_id, component_code, component_name, component_type, calculation_type, is_system_component, is_statutory, statutory_type, display_order)
VALUES 
(1, 'PF_EMP', 'PF - Employee Contribution', 'DEDUCTION', 'PERCENTAGE_OF_BASIC', TRUE, TRUE, 'PF', 1),
(1, 'ESI_EMP', 'ESI - Employee Contribution', 'DEDUCTION', 'PERCENTAGE_OF_GROSS', TRUE, TRUE, 'ESI', 2),
(1, 'PT', 'Professional Tax', 'DEDUCTION', 'FIXED', TRUE, TRUE, 'PT', 3),
(1, 'TDS', 'Tax Deducted at Source', 'DEDUCTION', 'FORMULA', TRUE, TRUE, 'TDS', 4);

-- Insert employer contributions
INSERT INTO salary_components (tenant_id, component_code, component_name, component_type, calculation_type, is_system_component, is_statutory, statutory_type, is_part_of_ctc, display_order)
VALUES 
(1, 'PF_EMP_CONT', 'PF - Employer Contribution', 'EMPLOYER_CONTRIBUTION', 'PERCENTAGE_OF_BASIC', TRUE, TRUE, 'PF', TRUE, 1),
(1, 'ESI_EMP_CONT', 'ESI - Employer Contribution', 'EMPLOYER_CONTRIBUTION', 'PERCENTAGE_OF_GROSS', TRUE, TRUE, 'ESI', TRUE, 2);

-- ============================================
-- Migration Complete
-- ============================================

-- Verify table creation
SELECT 
    'salary_components' as table_name, COUNT(*) as row_count FROM salary_components
UNION ALL
SELECT 'salary_structures', COUNT(*) FROM salary_structures
UNION ALL
SELECT 'employee_salaries', COUNT(*) FROM employee_salaries
UNION ALL
SELECT 'payroll_runs', COUNT(*) FROM payroll_runs
UNION ALL
SELECT 'payslips', COUNT(*) FROM payslips
UNION ALL
SELECT 'statutory_compliance', COUNT(*) FROM statutory_compliance
UNION ALL
SELECT 'form16', COUNT(*) FROM form16
UNION ALL
SELECT 'payment_files', COUNT(*) FROM payment_files;

-- End of migration
