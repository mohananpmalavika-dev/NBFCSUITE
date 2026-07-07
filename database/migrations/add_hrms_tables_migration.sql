-- HRMS (Human Resource Management System) Tables Migration
-- Created: July 8, 2026
-- Module: HRMS - Employee Management, Organization Structure, Department, Designation, Reporting Hierarchy

-- ============================================================================
-- 1. HRMS ORGANIZATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS hrms_organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Basic Information
    organization_code VARCHAR(20) NOT NULL,
    organization_name VARCHAR(200) NOT NULL,
    short_name VARCHAR(50),
    legal_name VARCHAR(200),
    
    -- Registration Details
    pan_number VARCHAR(10),
    tan_number VARCHAR(10),
    gstin VARCHAR(15),
    cin_number VARCHAR(21),
    
    -- Contact Information
    email VARCHAR(100),
    phone VARCHAR(20),
    website VARCHAR(200),
    
    -- Registered Address
    registered_address_line1 VARCHAR(200),
    registered_address_line2 VARCHAR(200),
    registered_city VARCHAR(100),
    registered_state VARCHAR(100),
    registered_pincode VARCHAR(10),
    registered_country VARCHAR(100) DEFAULT 'India',
    
    -- Status
    is_active BOOLEAN DEFAULT true NOT NULL,
    established_date DATE,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    
    CONSTRAINT uk_tenant_org_code UNIQUE (tenant_id, organization_code)
);

CREATE INDEX idx_hrms_org_tenant ON hrms_organizations(tenant_id);
CREATE INDEX idx_hrms_org_active ON hrms_organizations(tenant_id, is_active);

-- ============================================================================
-- 2. HRMS DEPARTMENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS hrms_departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Basic Information
    department_code VARCHAR(20) NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    department_type VARCHAR(50) NOT NULL DEFAULT 'other',
    description TEXT,
    
    -- Organization Link
    organization_id UUID NOT NULL,
    
    -- Hierarchy
    parent_department_id UUID,
    
    -- Head of Department (forward reference)
    hod_employee_id UUID,
    
    -- Contact Information
    email VARCHAR(100),
    phone VARCHAR(20),
    extension VARCHAR(10),
    
    -- Location
    location VARCHAR(100),
    floor VARCHAR(50),
    
    -- Cost Center
    cost_center_code VARCHAR(20),
    
    -- Status
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    
    CONSTRAINT uk_tenant_dept_code UNIQUE (tenant_id, department_code),
    CONSTRAINT fk_dept_organization FOREIGN KEY (organization_id) REFERENCES hrms_organizations(id) ON DELETE CASCADE,
    CONSTRAINT fk_dept_parent FOREIGN KEY (parent_department_id) REFERENCES hrms_departments(id) ON DELETE SET NULL
);

CREATE INDEX idx_hrms_dept_tenant ON hrms_departments(tenant_id);
CREATE INDEX idx_hrms_dept_org ON hrms_departments(organization_id);
CREATE INDEX idx_hrms_dept_parent ON hrms_departments(parent_department_id);
CREATE INDEX idx_hrms_dept_active ON hrms_departments(tenant_id, is_active);

-- ============================================================================
-- 3. HRMS DESIGNATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS hrms_designations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Basic Information
    designation_code VARCHAR(20) NOT NULL,
    designation_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Hierarchy Level
    level INTEGER,
    grade VARCHAR(10),
    
    -- Salary Range
    min_salary NUMERIC(15,2),
    max_salary NUMERIC(15,2),
    
    -- Requirements
    min_experience_years INTEGER,
    required_qualification VARCHAR(200),
    
    -- Status
    is_active BOOLEAN DEFAULT true NOT NULL,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    
    CONSTRAINT uk_tenant_desig_code UNIQUE (tenant_id, designation_code)
);

CREATE INDEX idx_hrms_desig_tenant ON hrms_designations(tenant_id);
CREATE INDEX idx_hrms_desig_level ON hrms_designations(level);
CREATE INDEX idx_hrms_desig_active ON hrms_designations(tenant_id, is_active);

-- ============================================================================
-- 4. HRMS EMPLOYEES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS hrms_employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- ========================================
    -- EMPLOYMENT INFORMATION
    -- ========================================
    
    -- Employee Identification
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    employee_id_display VARCHAR(50),
    
    -- User Account Link
    user_id UUID,
    
    -- Organization & Department
    organization_id UUID NOT NULL,
    department_id UUID,
    designation_id UUID,
    
    -- Reporting Hierarchy
    reporting_manager_id UUID,
    
    -- Employment Details
    employment_type VARCHAR(50) NOT NULL DEFAULT 'permanent',
    employment_status VARCHAR(50) NOT NULL DEFAULT 'active',
    
    -- Important Dates
    date_of_joining DATE NOT NULL,
    date_of_confirmation DATE,
    date_of_resignation DATE,
    date_of_relieving DATE,
    last_working_day DATE,
    
    -- Work Location
    work_location VARCHAR(100),
    branch_id UUID,
    
    -- Shift & Work Schedule
    shift_type VARCHAR(20),
    work_schedule VARCHAR(50),
    
    -- ========================================
    -- PERSONAL INFORMATION
    -- ========================================
    
    -- Name
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    full_name VARCHAR(300) NOT NULL,
    
    -- Basic Details
    date_of_birth DATE,
    age INTEGER,
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    marital_status VARCHAR(20),
    
    -- Family Details
    father_name VARCHAR(200),
    mother_name VARCHAR(200),
    spouse_name VARCHAR(200),
    number_of_children INTEGER DEFAULT 0,
    
    -- Contact Information
    personal_email VARCHAR(100),
    official_email VARCHAR(100),
    mobile VARCHAR(20) NOT NULL,
    alternate_mobile VARCHAR(20),
    emergency_contact_name VARCHAR(200),
    emergency_contact_number VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    
    -- ========================================
    -- ADDRESS INFORMATION
    -- ========================================
    
    -- Current Address
    current_address_line1 VARCHAR(200),
    current_address_line2 VARCHAR(200),
    current_city VARCHAR(100),
    current_state VARCHAR(100),
    current_pincode VARCHAR(10),
    current_country VARCHAR(100) DEFAULT 'India',
    
    -- Permanent Address
    permanent_address_line1 VARCHAR(200),
    permanent_address_line2 VARCHAR(200),
    permanent_city VARCHAR(100),
    permanent_state VARCHAR(100),
    permanent_pincode VARCHAR(10),
    permanent_country VARCHAR(100) DEFAULT 'India',
    
    -- Address Same Flag
    is_permanent_same_as_current BOOLEAN DEFAULT false,
    
    -- ========================================
    -- IDENTITY DOCUMENTS
    -- ========================================
    
    pan_number VARCHAR(10),
    aadhaar_number VARCHAR(12),
    passport_number VARCHAR(20),
    driving_license_number VARCHAR(20),
    voter_id_number VARCHAR(20),
    
    -- ========================================
    -- BANK & SALARY INFORMATION
    -- ========================================
    
    -- Salary Account
    salary_bank_name VARCHAR(100),
    salary_account_number VARCHAR(30),
    salary_ifsc_code VARCHAR(11),
    salary_account_holder_name VARCHAR(200),
    
    -- PF Account
    pf_number VARCHAR(30),
    uan_number VARCHAR(12),
    pf_join_date DATE,
    
    -- ESI Account
    esi_number VARCHAR(20),
    
    -- Salary Details (Current CTC)
    current_ctc NUMERIC(15,2),
    basic_salary NUMERIC(15,2),
    gross_salary NUMERIC(15,2),
    net_salary NUMERIC(15,2),
    
    -- ========================================
    -- EDUCATION & EXPERIENCE
    -- ========================================
    
    highest_qualification VARCHAR(100),
    specialization VARCHAR(100),
    university VARCHAR(200),
    year_of_passing INTEGER,
    
    total_experience_years INTEGER,
    previous_employer VARCHAR(200),
    previous_designation VARCHAR(100),
    
    -- ========================================
    -- DOCUMENTS & COMPLIANCE
    -- ========================================
    
    -- Photo & Signature
    photo_url VARCHAR(500),
    signature_url VARCHAR(500),
    
    -- Background Verification
    is_background_verified BOOLEAN DEFAULT false,
    background_verification_date DATE,
    background_verification_agency VARCHAR(200),
    
    -- Police Verification
    is_police_verified BOOLEAN DEFAULT false,
    police_verification_date DATE,
    
    -- Medical Examination
    is_medical_done BOOLEAN DEFAULT false,
    medical_examination_date DATE,
    is_medical_fit BOOLEAN DEFAULT true,
    
    -- ========================================
    -- STATUS & FLAGS
    -- ========================================
    
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_on_probation BOOLEAN DEFAULT false,
    probation_end_date DATE,
    
    -- Notice Period (in days)
    notice_period_days INTEGER DEFAULT 30,
    
    -- ========================================
    -- ADDITIONAL INFORMATION
    -- ========================================
    
    remarks TEXT,
    skills TEXT,
    certifications TEXT,
    languages_known TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    
    CONSTRAINT uk_tenant_emp_code UNIQUE (tenant_id, employee_code),
    CONSTRAINT fk_emp_organization FOREIGN KEY (organization_id) REFERENCES hrms_organizations(id) ON DELETE CASCADE,
    CONSTRAINT fk_emp_department FOREIGN KEY (department_id) REFERENCES hrms_departments(id) ON DELETE SET NULL,
    CONSTRAINT fk_emp_designation FOREIGN KEY (designation_id) REFERENCES hrms_designations(id) ON DELETE SET NULL,
    CONSTRAINT fk_emp_manager FOREIGN KEY (reporting_manager_id) REFERENCES hrms_employees(id) ON DELETE SET NULL,
    CONSTRAINT fk_emp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_hrms_emp_tenant ON hrms_employees(tenant_id);
CREATE INDEX idx_hrms_emp_code ON hrms_employees(employee_code);
CREATE INDEX idx_hrms_emp_full_name ON hrms_employees(full_name);
CREATE INDEX idx_hrms_emp_official_email ON hrms_employees(tenant_id, official_email);
CREATE INDEX idx_hrms_emp_mobile ON hrms_employees(tenant_id, mobile);
CREATE INDEX idx_hrms_emp_pan ON hrms_employees(tenant_id, pan_number);
CREATE INDEX idx_hrms_emp_status ON hrms_employees(tenant_id, employment_status, is_active);
CREATE INDEX idx_hrms_emp_dept ON hrms_employees(tenant_id, department_id, is_active);
CREATE INDEX idx_hrms_emp_manager ON hrms_employees(tenant_id, reporting_manager_id);

-- ============================================================================
-- 5. HRMS REPORTING HIERARCHY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS hrms_reporting_hierarchy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Employee & Manager
    employee_id UUID NOT NULL,
    manager_id UUID NOT NULL,
    
    -- Reporting Type
    reporting_type VARCHAR(20) NOT NULL DEFAULT 'direct',
    is_primary BOOLEAN DEFAULT true NOT NULL,
    
    -- Effective Period
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_current BOOLEAN DEFAULT true NOT NULL,
    
    -- Reason for Change
    change_reason VARCHAR(200),
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT false NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deleted_by UUID,
    
    CONSTRAINT fk_hierarchy_employee FOREIGN KEY (employee_id) REFERENCES hrms_employees(id) ON DELETE CASCADE,
    CONSTRAINT fk_hierarchy_manager FOREIGN KEY (manager_id) REFERENCES hrms_employees(id) ON DELETE CASCADE
);

CREATE INDEX idx_hrms_hierarchy_tenant ON hrms_reporting_hierarchy(tenant_id);
CREATE INDEX idx_hrms_hierarchy_emp_current ON hrms_reporting_hierarchy(tenant_id, employee_id, is_current);
CREATE INDEX idx_hrms_hierarchy_manager ON hrms_reporting_hierarchy(tenant_id, manager_id, is_current);

-- ============================================================================
-- 6. ADD FOREIGN KEY FOR HOD IN DEPARTMENTS (deferred constraint)
-- ============================================================================

ALTER TABLE hrms_departments 
ADD CONSTRAINT fk_dept_hod FOREIGN KEY (hod_employee_id) 
REFERENCES hrms_employees(id) ON DELETE SET NULL;

-- ============================================================================
-- 7. COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE hrms_organizations IS 'Organization/Company entities - parent organization management';
COMMENT ON TABLE hrms_departments IS 'Department master - hierarchical department structure';
COMMENT ON TABLE hrms_designations IS 'Designation/Job Title master - employee positions and grades';
COMMENT ON TABLE hrms_employees IS 'Employee master - comprehensive employee information';
COMMENT ON TABLE hrms_reporting_hierarchy IS 'Reporting relationships - current and historical reporting structure';

COMMENT ON COLUMN hrms_employees.employee_code IS 'Auto-generated unique employee code: EMP-YYYYMM-XXXX';
COMMENT ON COLUMN hrms_employees.employment_type IS 'permanent, contract, probation, intern, consultant';
COMMENT ON COLUMN hrms_employees.employment_status IS 'active, inactive, resigned, terminated, absconded, retired';
COMMENT ON COLUMN hrms_employees.is_on_probation IS 'Automatically set based on employment_type and confirmation status';
COMMENT ON COLUMN hrms_reporting_hierarchy.reporting_type IS 'direct, dotted, functional - supports matrix reporting';

-- ============================================================================
-- 8. GRANT PERMISSIONS (if needed)
-- ============================================================================

-- Grant permissions to application role (adjust as per your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO nbfc_app_role;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nbfc_app_role;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary:
-- ✓ 5 tables created (Organizations, Departments, Designations, Employees, Reporting Hierarchy)
-- ✓ All indexes created for performance
-- ✓ Foreign key constraints established
-- ✓ Multi-tenant support with tenant_id
-- ✓ Audit trail fields (created_by, updated_by, timestamps)
-- ✓ Soft delete support
-- ✓ Comprehensive employee data model
-- ✓ Hierarchical organization structure support
