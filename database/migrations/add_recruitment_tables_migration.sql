-- ============================================================================
-- HRMS Recruitment & Onboarding Module - Database Migration
-- Description: Job requisitions, applicant tracking, interviews, onboarding
-- Version: 1.0.0
-- Date: 2026-07-08
-- ============================================================================

-- ============================================================================
-- 1. JOB REQUISITIONS TABLE
-- Purpose: Track job opening requests and approval workflow
-- ============================================================================
CREATE TABLE IF NOT EXISTS job_requisitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    requisition_code VARCHAR(50) NOT NULL UNIQUE,
    
    -- Job Details
    title VARCHAR(200) NOT NULL,
    department_id UUID REFERENCES departments(id),
    designation_id UUID REFERENCES designations(id),
    number_of_positions INTEGER NOT NULL DEFAULT 1,
    employment_type VARCHAR(50) NOT NULL, -- FULL_TIME, PART_TIME, CONTRACT, INTERNSHIP
    work_location VARCHAR(200),
    reporting_to_employee_id UUID REFERENCES employees(id),
    
    -- Job Description
    job_description TEXT,
    responsibilities TEXT,
    required_qualifications TEXT,
    preferred_qualifications TEXT,
    required_experience_years DECIMAL(4,2),
    
    -- Compensation
    min_salary DECIMAL(15,2),
    max_salary DECIMAL(15,2),
    
    -- Priority & Timeline
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM', -- LOW, MEDIUM, HIGH, URGENT
    required_by_date DATE,
    justification TEXT,
    
    -- Replacement Details
    is_replacement BOOLEAN DEFAULT FALSE,
    replacement_for_employee_id UUID REFERENCES employees(id),
    
    -- Request Details
    requested_by_employee_id UUID REFERENCES employees(id),
    requested_date DATE NOT NULL,
    
    -- Approval Workflow
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT', -- DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, CLOSED
    approved_by_employee_id UUID REFERENCES employees(id),
    approved_date DATE,
    rejection_reason TEXT,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_requisition_per_tenant UNIQUE (tenant_id, requisition_code)
);

CREATE INDEX idx_requisitions_tenant ON job_requisitions(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_requisitions_status ON job_requisitions(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_requisitions_department ON job_requisitions(department_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_requisitions_requested_by ON job_requisitions(requested_by_employee_id) WHERE is_deleted = FALSE;

-- ============================================================================
-- 2. JOB POSTINGS TABLE
-- Purpose: Published job openings for internal and external candidates
-- ============================================================================
CREATE TABLE IF NOT EXISTS job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    posting_code VARCHAR(50) NOT NULL UNIQUE,
    requisition_id UUID NOT NULL REFERENCES job_requisitions(id),
    
    -- Posting Details
    title VARCHAR(200) NOT NULL,
    job_description TEXT NOT NULL,
    responsibilities TEXT,
    required_qualifications TEXT,
    preferred_qualifications TEXT,
    required_experience_years DECIMAL(4,2),
    employment_type VARCHAR(50) NOT NULL,
    work_location VARCHAR(200),
    
    -- Compensation (public-facing)
    salary_range VARCHAR(100), -- e.g., "5-8 LPA" or "Competitive"
    benefits TEXT,
    
    -- Publishing Details
    application_deadline DATE,
    posting_channels TEXT, -- JSON array: ["CAREER_SITE", "LINKEDIN", "NAUKRI"]
    external_job_board_urls TEXT, -- JSON object with URLs
    is_internal_only BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Status & Analytics
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT', -- DRAFT, PUBLISHED, UNPUBLISHED, CLOSED
    published_date DATE,
    closed_date DATE,
    view_count INTEGER DEFAULT 0,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_posting_per_tenant UNIQUE (tenant_id, posting_code)
);

CREATE INDEX idx_postings_tenant ON job_postings(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_postings_status ON job_postings(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_postings_requisition ON job_postings(requisition_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_postings_published ON job_postings(published_date) WHERE is_deleted = FALSE AND status = 'PUBLISHED';

-- ============================================================================
-- 3. JOB APPLICATIONS TABLE
-- Purpose: Applicant tracking system (ATS) for all job applications
-- ============================================================================
CREATE TABLE IF NOT EXISTS job_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    application_code VARCHAR(50) NOT NULL UNIQUE,
    posting_id UUID NOT NULL REFERENCES job_postings(id),
    
    -- Applicant Details
    applicant_name VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    current_location VARCHAR(200),
    
    -- Professional Details
    current_company VARCHAR(200),
    current_designation VARCHAR(200),
    total_experience_years DECIMAL(4,2),
    current_salary DECIMAL(15,2),
    expected_salary DECIMAL(15,2),
    notice_period_days INTEGER,
    
    -- Documents
    resume_url VARCHAR(500),
    cover_letter TEXT,
    portfolio_url VARCHAR(500),
    
    -- Application Details
    source VARCHAR(50) NOT NULL, -- CAREER_SITE, LINKEDIN, NAUKRI, REFERRAL, WALK_IN
    referrer_employee_id UUID REFERENCES employees(id),
    applied_date DATE NOT NULL,
    
    -- Screening & Assessment
    screening_score DECIMAL(5,2),
    screening_notes TEXT,
    assessment_results TEXT, -- JSON object
    
    -- Status & Workflow
    status VARCHAR(20) NOT NULL DEFAULT 'NEW', -- NEW, SCREENING, SHORTLISTED, INTERVIEW, OFFERED, HIRED, REJECTED
    current_stage VARCHAR(50), -- e.g., "Technical Round 1", "HR Round"
    rejection_reason TEXT,
    
    -- Tracking
    last_activity_date DATE,
    assigned_to_employee_id UUID REFERENCES employees(id),
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_application_per_tenant UNIQUE (tenant_id, application_code)
);

CREATE INDEX idx_applications_tenant ON job_applications(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_applications_posting ON job_applications(posting_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_applications_status ON job_applications(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_applications_email ON job_applications(email) WHERE is_deleted = FALSE;
CREATE INDEX idx_applications_assigned ON job_applications(assigned_to_employee_id) WHERE is_deleted = FALSE;

-- ============================================================================
-- 4. INTERVIEWS TABLE
-- Purpose: Interview scheduling and feedback management
-- ============================================================================
CREATE TABLE IF NOT EXISTS interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    interview_code VARCHAR(50) NOT NULL UNIQUE,
    application_id UUID NOT NULL REFERENCES job_applications(id),
    
    -- Interview Details
    interview_type VARCHAR(50) NOT NULL, -- SCREENING, TECHNICAL, HR, MANAGERIAL, FINAL
    round_number INTEGER NOT NULL DEFAULT 1,
    scheduled_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    duration_minutes INTEGER,
    
    -- Location/Mode
    interview_mode VARCHAR(20) NOT NULL, -- IN_PERSON, VIDEO, PHONE
    location VARCHAR(200),
    meeting_link VARCHAR(500),
    meeting_id VARCHAR(100),
    
    -- Interviewers
    interviewer_ids TEXT NOT NULL, -- JSON array of employee UUIDs
    panel_size INTEGER DEFAULT 1,
    
    -- Instructions
    instructions_for_candidate TEXT,
    instructions_for_interviewer TEXT,
    
    -- Status & Outcome
    status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED', -- SCHEDULED, COMPLETED, CANCELLED, NO_SHOW, RESCHEDULED
    cancellation_reason TEXT,
    reschedule_count INTEGER DEFAULT 0,
    
    -- Feedback
    feedback_notes TEXT,
    rating DECIMAL(3,2), -- 1.00 to 5.00
    recommendation VARCHAR(20), -- STRONG_HIRE, HIRE, MAYBE, NO_HIRE
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_interview_per_tenant UNIQUE (tenant_id, interview_code)
);

CREATE INDEX idx_interviews_tenant ON interviews(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_interviews_application ON interviews(application_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_interviews_date ON interviews(scheduled_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_interviews_status ON interviews(status) WHERE is_deleted = FALSE;

-- ============================================================================
-- 5. ONBOARDING TABLE
-- Purpose: Employee onboarding workflow and checklist tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS onboarding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    onboarding_code VARCHAR(50) NOT NULL UNIQUE,
    application_id UUID NOT NULL REFERENCES job_applications(id),
    employee_id UUID REFERENCES employees(id),
    
    -- Onboarding Details
    joining_date DATE NOT NULL,
    department_id UUID REFERENCES departments(id),
    designation_id UUID REFERENCES designations(id),
    reporting_to_employee_id UUID REFERENCES employees(id),
    work_location VARCHAR(200),
    
    -- Compensation
    offered_salary DECIMAL(15,2) NOT NULL,
    probation_period_months INTEGER DEFAULT 3,
    
    -- Onboarding Checklist (JSON)
    checklist_items TEXT, -- JSON array of checklist items with completion status
    
    -- Documents Required
    documents_required TEXT, -- JSON array: ["AADHAAR", "PAN", "EDUCATION_CERTIFICATES"]
    documents_submitted TEXT, -- JSON array of submitted documents with URLs
    
    -- Assets Assigned
    assets_assigned TEXT, -- JSON array: ["LAPTOP", "MOBILE", "ID_CARD"]
    
    -- Status & Progress
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    started_date DATE,
    completed_date DATE,
    
    -- Buddy/Mentor
    buddy_employee_id UUID REFERENCES employees(id),
    
    -- Notes
    notes TEXT,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_onboarding_per_tenant UNIQUE (tenant_id, onboarding_code)
);

CREATE INDEX idx_onboarding_tenant ON onboarding(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_onboarding_application ON onboarding(application_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_onboarding_employee ON onboarding(employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_onboarding_status ON onboarding(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_onboarding_joining_date ON onboarding(joining_date) WHERE is_deleted = FALSE;

-- ============================================================================
-- 6. BACKGROUND VERIFICATIONS TABLE
-- Purpose: Track background verification checks for candidates
-- ============================================================================
CREATE TABLE IF NOT EXISTS background_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    verification_code VARCHAR(50) NOT NULL UNIQUE,
    onboarding_id UUID NOT NULL REFERENCES onboarding(id),
    
    -- Verification Details
    verification_type VARCHAR(50) NOT NULL, -- EDUCATION, EMPLOYMENT, ADDRESS, CRIMINAL, CREDIT, REFERENCE
    verification_agency VARCHAR(200),
    agency_reference_id VARCHAR(100),
    
    -- Candidate Details
    candidate_name VARCHAR(200) NOT NULL,
    candidate_email VARCHAR(255),
    candidate_phone VARCHAR(20),
    
    -- Verification Specifics
    document_type VARCHAR(100), -- e.g., "Degree Certificate", "Experience Letter"
    document_url VARCHAR(500),
    verification_details TEXT, -- JSON object with specific details
    
    -- Status & Timeline
    status VARCHAR(20) NOT NULL DEFAULT 'INITIATED', -- INITIATED, IN_PROGRESS, COMPLETED, FAILED, ON_HOLD
    initiated_date DATE NOT NULL,
    completed_date DATE,
    
    -- Results
    is_verified BOOLEAN,
    verification_result VARCHAR(20), -- CLEAR, DISCREPANCY, MAJOR_DISCREPANCY, UNABLE_TO_VERIFY
    discrepancy_notes TEXT,
    verification_report_url VARCHAR(500),
    
    -- Additional Info
    notes TEXT,
    
    -- Audit Fields
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    CONSTRAINT unique_verification_per_tenant UNIQUE (tenant_id, verification_code)
);

CREATE INDEX idx_verifications_tenant ON background_verifications(tenant_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_verifications_onboarding ON background_verifications(onboarding_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_verifications_status ON background_verifications(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_verifications_type ON background_verifications(verification_type) WHERE is_deleted = FALSE;

-- ============================================================================
-- COMMENTS & DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE job_requisitions IS 'Job opening requests with approval workflow';
COMMENT ON TABLE job_postings IS 'Published job openings for candidates';
COMMENT ON TABLE job_applications IS 'Applicant tracking system (ATS) for all applications';
COMMENT ON TABLE interviews IS 'Interview scheduling and feedback management';
COMMENT ON TABLE onboarding IS 'Employee onboarding workflow and checklist';
COMMENT ON TABLE background_verifications IS 'Background verification checks for candidates';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Tables Created: 6
-- Indexes Created: 32
-- Purpose: Complete recruitment lifecycle from requisition to onboarding
-- ============================================================================
