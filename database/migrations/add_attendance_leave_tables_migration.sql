-- ============================================================================
-- HRMS Attendance & Leave Management Module - Database Migration
-- Description: Shift management, attendance tracking, biometric integration, leave management
-- Version: 1.0.0
-- Date: 2026-07-08
-- ============================================================================

-- ============================================================================
-- 1. SHIFTS TABLE
-- Purpose: Define work shifts for employees
-- ============================================================================
CREATE TABLE IF NOT EXISTS shifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Shift Details
    shift_code VARCHAR(50) NOT NULL UNIQUE,
    shift_name VARCHAR(200) NOT NULL,
    shift_type VARCHAR(20) NOT NULL, -- REGULAR, ROTATING, FLEXIBLE, NIGHT, SPLIT
    
    -- Timing
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    grace_period_minutes INTEGER DEFAULT 15,
    half_day_hours DECIMAL(4,2) DEFAULT 4.0,
    full_day_hours DECIMAL(4,2) DEFAULT 8.0,
    
    -- Break Configuration
    break_duration_minutes INTEGER DEFAULT 60,
    break_start_time TIME,
    break_end_time TIME,
    
    -- Week Off Configuration
    week_off_1 VARCHAR(20), -- e.g., SUNDAY
    week_off_2 VARCHAR(20), -- Optional second week off
    
    -- Overtime
    allow_overtime BOOLEAN DEFAULT FALSE,
    overtime_start_after_minutes INTEGER DEFAULT 30,
    
    -- Active Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE,
    effective_to DATE,
    
    -- Description
    description TEXT,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_shift_per_tenant UNIQUE (tenant_id, shift_code)
);

CREATE INDEX idx_shifts_tenant ON shifts(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_shifts_active ON shifts(is_active) WHERE is_deleted = FALSE;

-- ============================================================================
-- 2. EMPLOYEE SHIFTS TABLE
-- Purpose: Link employees to shifts
-- ============================================================================
CREATE TABLE IF NOT EXISTS employee_shifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Employee and Shift
    employee_id UUID NOT NULL REFERENCES employees(id),
    shift_id UUID NOT NULL REFERENCES shifts(id),
    
    -- Effective Period
    effective_from DATE NOT NULL,
    effective_to DATE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_emp_shifts_tenant ON employee_shifts(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_emp_shifts_employee ON employee_shifts(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_emp_shifts_shift ON employee_shifts(shift_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_emp_shifts_active ON employee_shifts(is_active, effective_from, effective_to) WHERE is_deleted = FALSE;

-- ============================================================================
-- 3. ATTENDANCE TABLE
-- Purpose: Daily attendance records
-- ============================================================================
CREATE TABLE IF NOT EXISTS attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Employee and Date
    employee_id UUID NOT NULL REFERENCES employees(id),
    attendance_date DATE NOT NULL,
    
    -- Shift Information
    shift_id UUID REFERENCES shifts(id),
    scheduled_start_time TIME,
    scheduled_end_time TIME,
    
    -- Check-in/out Times
    actual_check_in TIMESTAMP,
    actual_check_out TIMESTAMP,
    
    -- Time Calculations
    late_by_minutes INTEGER DEFAULT 0,
    early_out_minutes INTEGER DEFAULT 0,
    total_work_hours DECIMAL(5,2) DEFAULT 0.0,
    overtime_hours DECIMAL(5,2) DEFAULT 0.0,
    break_hours DECIMAL(5,2) DEFAULT 0.0,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'ABSENT', -- PRESENT, ABSENT, HALF_DAY, LEAVE, HOLIDAY, WEEK_OFF, ON_DUTY
    
    -- Location (for mobile check-in)
    check_in_location TEXT, -- JSON: {lat, lng, address}
    check_out_location TEXT, -- JSON: {lat, lng, address}
    
    -- Device Information
    check_in_device VARCHAR(200),
    check_out_device VARCHAR(200),
    check_in_method VARCHAR(20), -- BIOMETRIC, MOBILE, WEB, RFID, MANUAL
    check_out_method VARCHAR(20),
    
    -- Remarks
    remarks TEXT,
    is_manual_entry BOOLEAN DEFAULT FALSE,
    manual_entry_reason TEXT,
    
    -- Approval
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(36),
    approved_at TIMESTAMP,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_attendance_per_day UNIQUE (tenant_id, employee_id, attendance_date)
);

CREATE INDEX idx_attendance_tenant ON attendance(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_attendance_employee ON attendance(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_attendance_date ON attendance(attendance_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_attendance_emp_date ON attendance(employee_id, attendance_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_attendance_status ON attendance(status) WHERE is_deleted = FALSE;

-- ============================================================================
-- 4. BIOMETRIC LOGS TABLE
-- Purpose: Raw data from biometric devices
-- ============================================================================
CREATE TABLE IF NOT EXISTS biometric_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Employee
    employee_id UUID NOT NULL REFERENCES employees(id),
    biometric_id VARCHAR(50), -- Employee's biometric ID/enrollment number
    
    -- Log Details
    log_datetime TIMESTAMP NOT NULL,
    check_type VARCHAR(20) NOT NULL, -- CHECK_IN, CHECK_OUT, BREAK_START, BREAK_END
    
    -- Device Information
    device_id VARCHAR(100),
    device_name VARCHAR(200),
    device_location VARCHAR(200),
    
    -- Biometric Data (optional)
    biometric_data TEXT, -- JSON: fingerprint template, face data, etc.
    verification_method VARCHAR(50), -- FINGERPRINT, FACE, IRIS, CARD
    verification_score DECIMAL(5,2), -- Match confidence score
    
    -- Linked Attendance
    attendance_id UUID REFERENCES attendance(id),
    
    -- Processing Status
    is_processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_biometric_tenant ON biometric_logs(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_biometric_employee ON biometric_logs(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_biometric_datetime ON biometric_logs(log_datetime) WHERE is_deleted = FALSE;
CREATE INDEX idx_biometric_emp_datetime ON biometric_logs(employee_id, log_datetime) WHERE is_deleted = FALSE;
CREATE INDEX idx_biometric_processed ON biometric_logs(is_processed) WHERE is_deleted = FALSE;

-- ============================================================================
-- 5. ATTENDANCE REGULARIZATION TABLE
-- Purpose: Attendance correction/regularization requests
-- ============================================================================
CREATE TABLE IF NOT EXISTS attendance_regularization (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Reference
    attendance_id UUID NOT NULL REFERENCES attendance(id),
    employee_id UUID NOT NULL REFERENCES employees(id),
    
    -- Requested Changes
    requested_check_in TIMESTAMP,
    requested_check_out TIMESTAMP,
    reason TEXT NOT NULL,
    supporting_documents TEXT, -- JSON array of URLs
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, APPROVED, REJECTED
    
    -- Approval
    approved_by VARCHAR(36),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_regularization_tenant ON attendance_regularization(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_regularization_attendance ON attendance_regularization(attendance_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_regularization_employee ON attendance_regularization(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_regularization_status ON attendance_regularization(status) WHERE is_deleted = FALSE;

-- ============================================================================
-- 6. LEAVE POLICIES TABLE
-- Purpose: Define leave types and entitlements
-- ============================================================================
CREATE TABLE IF NOT EXISTS leave_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Policy Details
    policy_code VARCHAR(50) NOT NULL UNIQUE,
    policy_name VARCHAR(200) NOT NULL,
    leave_type VARCHAR(50) NOT NULL, -- CASUAL_LEAVE, SICK_LEAVE, EARNED_LEAVE, etc.
    
    -- Entitlement
    annual_quota DECIMAL(5,2) NOT NULL,
    max_consecutive_days INTEGER,
    min_notice_days INTEGER DEFAULT 0,
    max_carry_forward DECIMAL(5,2) DEFAULT 0.0,
    
    -- Accrual Settings
    is_accrual_based BOOLEAN DEFAULT FALSE,
    accrual_frequency VARCHAR(20), -- MONTHLY, QUARTERLY, YEARLY
    accrual_rate DECIMAL(5,2),
    
    -- Applicability
    applicable_after_days INTEGER DEFAULT 0,
    applicable_gender VARCHAR(20), -- MALE, FEMALE, ALL
    
    -- Restrictions
    allow_half_day BOOLEAN DEFAULT TRUE,
    allow_negative_balance BOOLEAN DEFAULT FALSE,
    require_document BOOLEAN DEFAULT FALSE,
    require_document_after_days INTEGER,
    
    -- Weekend/Holiday Treatment
    include_weekends BOOLEAN DEFAULT FALSE,
    include_holidays BOOLEAN DEFAULT FALSE,
    
    -- Encashment
    is_encashable BOOLEAN DEFAULT FALSE,
    encashment_min_balance DECIMAL(5,2),
    encashment_percentage DECIMAL(5,2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE,
    effective_to DATE,
    
    -- Description
    description TEXT,
    rules TEXT, -- JSON: Additional rules and conditions
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_policy_per_tenant UNIQUE (tenant_id, policy_code)
);

CREATE INDEX idx_policies_tenant ON leave_policies(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_policies_type ON leave_policies(leave_type) WHERE is_deleted = FALSE;
CREATE INDEX idx_policies_active ON leave_policies(is_active) WHERE is_deleted = FALSE;

-- ============================================================================
-- 7. EMPLOYEE LEAVE BALANCE TABLE
-- Purpose: Track leave balance for each employee
-- ============================================================================
CREATE TABLE IF NOT EXISTS employee_leave_balance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Employee and Leave Type
    employee_id UUID NOT NULL REFERENCES employees(id),
    leave_policy_id UUID NOT NULL REFERENCES leave_policies(id),
    leave_type VARCHAR(50) NOT NULL,
    
    -- Balance for Financial Year
    financial_year VARCHAR(10) NOT NULL, -- e.g., "2026-27"
    
    -- Balance Details
    opening_balance DECIMAL(5,2) DEFAULT 0.0,
    accrued DECIMAL(5,2) DEFAULT 0.0,
    availed DECIMAL(5,2) DEFAULT 0.0,
    carry_forward DECIMAL(5,2) DEFAULT 0.0,
    encashed DECIMAL(5,2) DEFAULT 0.0,
    lapsed DECIMAL(5,2) DEFAULT 0.0,
    current_balance DECIMAL(5,2) DEFAULT 0.0,
    
    -- Pending Applications
    pending_approval DECIMAL(5,2) DEFAULT 0.0,
    
    -- Last Updated
    last_accrual_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_balance_per_emp_fy UNIQUE (tenant_id, employee_id, leave_type, financial_year)
);

CREATE INDEX idx_balance_tenant ON employee_leave_balance(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_balance_employee ON employee_leave_balance(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_balance_emp_fy ON employee_leave_balance(employee_id, financial_year) WHERE is_deleted = FALSE;
CREATE INDEX idx_balance_type ON employee_leave_balance(leave_type) WHERE is_deleted = FALSE;

-- ============================================================================
-- 8. LEAVE APPLICATIONS TABLE
-- Purpose: Employee leave requests
-- ============================================================================
CREATE TABLE IF NOT EXISTS leave_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Application Details
    application_code VARCHAR(50) NOT NULL UNIQUE,
    employee_id UUID NOT NULL REFERENCES employees(id),
    leave_policy_id UUID NOT NULL REFERENCES leave_policies(id),
    leave_type VARCHAR(50) NOT NULL,
    
    -- Leave Period
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    from_period VARCHAR(20) DEFAULT 'FULL_DAY', -- FULL_DAY, FIRST_HALF, SECOND_HALF
    to_period VARCHAR(20) DEFAULT 'FULL_DAY',
    total_days DECIMAL(5,2) NOT NULL,
    
    -- Reason and Documents
    reason TEXT NOT NULL,
    contact_during_leave VARCHAR(200),
    address_during_leave TEXT,
    supporting_documents TEXT, -- JSON array of URLs
    
    -- Status and Workflow
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT', -- DRAFT, PENDING, APPROVED, REJECTED, CANCELLED
    applied_date DATE,
    
    -- Approval Chain
    reporting_manager_id VARCHAR(36),
    reporting_manager_status VARCHAR(20),
    reporting_manager_remarks TEXT,
    reporting_manager_date TIMESTAMP,
    
    hr_approver_id VARCHAR(36),
    hr_approver_status VARCHAR(20),
    hr_approver_remarks TEXT,
    hr_approver_date TIMESTAMP,
    
    final_approver_id VARCHAR(36),
    final_approver_status VARCHAR(20),
    final_approver_remarks TEXT,
    final_approver_date TIMESTAMP,
    
    -- Rejection
    rejection_reason TEXT,
    
    -- Cancellation
    is_cancelled BOOLEAN DEFAULT FALSE,
    cancelled_by VARCHAR(36),
    cancellation_reason TEXT,
    cancelled_at TIMESTAMP,
    
    -- Balance Impact
    balance_before DECIMAL(5,2),
    balance_after DECIMAL(5,2),
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_app_per_tenant UNIQUE (tenant_id, application_code)
);

CREATE INDEX idx_leave_app_tenant ON leave_applications(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_leave_app_employee ON leave_applications(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_leave_app_status ON leave_applications(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_leave_app_emp_status ON leave_applications(employee_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_leave_app_dates ON leave_applications(from_date, to_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_leave_app_type ON leave_applications(leave_type) WHERE is_deleted = FALSE;

-- ============================================================================
-- 9. LEAVE ENCASHMENT TABLE
-- Purpose: Leave encashment requests
-- ============================================================================
CREATE TABLE IF NOT EXISTS leave_encashment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Employee and Leave Type
    employee_id UUID NOT NULL REFERENCES employees(id),
    leave_policy_id UUID NOT NULL REFERENCES leave_policies(id),
    leave_type VARCHAR(50) NOT NULL,
    
    -- Encashment Details
    encashment_code VARCHAR(50) NOT NULL UNIQUE,
    financial_year VARCHAR(10) NOT NULL,
    days_to_encash DECIMAL(5,2) NOT NULL,
    per_day_amount DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    
    -- Balance Before/After
    balance_before DECIMAL(5,2),
    balance_after DECIMAL(5,2),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    
    -- Approval
    approved_by VARCHAR(36),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Payment
    is_paid BOOLEAN DEFAULT FALSE,
    payment_date DATE,
    payment_reference VARCHAR(100),
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_encashment_per_tenant UNIQUE (tenant_id, encashment_code)
);

CREATE INDEX idx_encashment_tenant ON leave_encashment(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_encashment_employee ON leave_encashment(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_encashment_status ON leave_encashment(status) WHERE is_deleted = FALSE;

-- ============================================================================
-- COMMENTS & DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE shifts IS 'Work shift master data';
COMMENT ON TABLE employee_shifts IS 'Employee shift assignments';
COMMENT ON TABLE attendance IS 'Daily attendance records with check-in/out';
COMMENT ON TABLE biometric_logs IS 'Raw biometric device logs';
COMMENT ON TABLE attendance_regularization IS 'Attendance correction requests';
COMMENT ON TABLE leave_policies IS 'Leave policy master with rules';
COMMENT ON TABLE employee_leave_balance IS 'Employee leave balance tracking';
COMMENT ON TABLE leave_applications IS 'Leave application requests';
COMMENT ON TABLE leave_encashment IS 'Leave encashment requests';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Tables Created: 9
-- Indexes Created: 45
-- Purpose: Complete attendance and leave management system
-- ============================================================================
