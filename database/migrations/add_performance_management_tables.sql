-- ============================================================================
-- PERFORMANCE MANAGEMENT SYSTEM - DATABASE MIGRATION
-- ============================================================================
-- This migration adds complete Performance Management functionality including:
-- 1. Goal Setting (KRA/KPI)
-- 2. Appraisal Cycles
-- 3. Employee Appraisals
-- 4. 360-Degree Feedback
-- 5. Performance-based Increments
-- 6. Individual Development Plans (IDP)
-- ============================================================================

-- ============================================================================
-- ENUMS
-- ============================================================================

-- Goal Type
CREATE TYPE goal_type AS ENUM (
    'kra',              -- Key Result Area
    'kpi',              -- Key Performance Indicator
    'objective',
    'project'
);

-- Goal Status
CREATE TYPE goal_status AS ENUM (
    'draft',
    'submitted',
    'approved',
    'rejected',
    'in_progress',
    'completed',
    'cancelled'
);

-- Goal Priority
CREATE TYPE goal_priority AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Appraisal Cycle Status
CREATE TYPE appraisal_cycle_status AS ENUM (
    'draft',
    'active',
    'goal_setting',
    'self_assessment',
    'manager_review',
    'normalization',
    'hr_review',
    'completed',
    'closed',
    'cancelled'
);

-- Appraisal Status
CREATE TYPE appraisal_status AS ENUM (
    'not_started',
    'goal_setting_pending',
    'goal_setting_submitted',
    'goals_approved',
    'self_assessment_pending',
    'self_assessment_submitted',
    'manager_review_pending',
    'manager_review_submitted',
    'hr_review_pending',
    'completed',
    'cancelled'
);

-- Rating Scale
CREATE TYPE rating_scale AS ENUM (
    'outstanding',              -- 5
    'exceeds_expectations',     -- 4
    'meets_expectations',       -- 3
    'needs_improvement',        -- 2
    'unsatisfactory'            -- 1
);

-- Feedback Type
CREATE TYPE feedback_type AS ENUM (
    'self',
    'manager',
    'peer',
    'subordinate',
    'customer',
    'other'
);

-- Feedback Status
CREATE TYPE feedback_status AS ENUM (
    'pending',
    'submitted',
    'acknowledged'
);

-- Increment Type
CREATE TYPE increment_type AS ENUM (
    'annual',
    'promotion',
    'special',
    'performance_based',
    'market_correction'
);

-- IDP Status
CREATE TYPE idp_status AS ENUM (
    'draft',
    'submitted',
    'approved',
    'in_progress',
    'completed',
    'cancelled'
);

-- Development Activity Type
CREATE TYPE development_activity_type AS ENUM (
    'training',
    'certification',
    'workshop',
    'mentoring',
    'job_rotation',
    'self_learning',
    'conference',
    'project'
);

-- ============================================================================
-- TABLE: APPRAISAL CYCLES
-- ============================================================================

CREATE TABLE hrms_appraisal_cycles (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Cycle Identification
    cycle_code VARCHAR(50) NOT NULL,
    cycle_name VARCHAR(200) NOT NULL,
    cycle_description TEXT,
    
    -- Fiscal Year
    fiscal_year VARCHAR(20) NOT NULL,
    
    -- Timeline
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Phase Deadlines
    goal_setting_start DATE,
    goal_setting_end DATE,
    self_assessment_start DATE,
    self_assessment_end DATE,
    manager_review_start DATE,
    manager_review_end DATE,
    normalization_start DATE,
    normalization_end DATE,
    hr_review_start DATE,
    hr_review_end DATE,
    
    -- Status
    status appraisal_cycle_status NOT NULL DEFAULT 'draft',
    
    -- Configuration
    enable_360_feedback BOOLEAN DEFAULT FALSE,
    enable_self_assessment BOOLEAN DEFAULT TRUE,
    enable_goal_setting BOOLEAN DEFAULT TRUE,
    
    -- Statistics
    total_employees INTEGER DEFAULT 0,
    completed_appraisals INTEGER DEFAULT 0,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for Appraisal Cycles
CREATE UNIQUE INDEX idx_tenant_cycle_code ON hrms_appraisal_cycles(tenant_id, cycle_code);
CREATE INDEX idx_tenant_cycle_status ON hrms_appraisal_cycles(tenant_id, status);
CREATE INDEX idx_tenant_cycle_year ON hrms_appraisal_cycles(tenant_id, fiscal_year);
CREATE INDEX idx_cycle_dates ON hrms_appraisal_cycles(start_date, end_date);

-- Comments
COMMENT ON TABLE hrms_appraisal_cycles IS 'Annual or periodic performance appraisal cycles';
COMMENT ON COLUMN hrms_appraisal_cycles.cycle_code IS 'Unique code for the appraisal cycle (e.g., APR-2024-25)';
COMMENT ON COLUMN hrms_appraisal_cycles.fiscal_year IS 'Fiscal year (e.g., 2024-25)';

-- ============================================================================
-- TABLE: PERFORMANCE GOALS (KRA/KPI)
-- ============================================================================

CREATE TABLE hrms_performance_goals (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Goal Identification
    goal_code VARCHAR(50) NOT NULL,
    goal_title VARCHAR(200) NOT NULL,
    goal_description TEXT,
    
    -- Goal Type
    goal_type goal_type NOT NULL DEFAULT 'kpi',
    goal_priority goal_priority NOT NULL DEFAULT 'medium',
    
    -- Ownership
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    appraisal_cycle_id UUID NOT NULL REFERENCES hrms_appraisal_cycles(id) ON DELETE CASCADE,
    
    -- Measurement
    measurement_criteria TEXT,
    target_value VARCHAR(100),
    achieved_value VARCHAR(100),
    uom VARCHAR(50),
    weightage NUMERIC(5,2),
    
    -- Timeline
    start_date DATE NOT NULL,
    target_date DATE NOT NULL,
    completion_date DATE,
    
    -- Progress Tracking
    progress_percentage INTEGER DEFAULT 0,
    status goal_status NOT NULL DEFAULT 'draft',
    
    -- Approval
    submitted_date TIMESTAMP WITH TIME ZONE,
    approved_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    approved_date TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    
    -- Comments
    employee_comments TEXT,
    manager_comments TEXT,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_goal_progress CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    CONSTRAINT chk_goal_weightage CHECK (weightage >= 0 AND weightage <= 100),
    CONSTRAINT chk_goal_dates CHECK (target_date >= start_date)
);

-- Indexes for Performance Goals
CREATE INDEX idx_tenant_goal_emp ON hrms_performance_goals(tenant_id, employee_id, appraisal_cycle_id);
CREATE INDEX idx_tenant_goal_code ON hrms_performance_goals(tenant_id, goal_code);
CREATE INDEX idx_tenant_goal_status ON hrms_performance_goals(tenant_id, status);
CREATE INDEX idx_goal_dates ON hrms_performance_goals(start_date, target_date);

-- Comments
COMMENT ON TABLE hrms_performance_goals IS 'Employee performance goals (KRA/KPI) for appraisal cycles';
COMMENT ON COLUMN hrms_performance_goals.weightage IS 'Percentage weightage of this goal (0-100)';
COMMENT ON COLUMN hrms_performance_goals.uom IS 'Unit of Measurement for target/achieved values';

-- ============================================================================
-- TABLE: EMPLOYEE APPRAISALS
-- ============================================================================

CREATE TABLE hrms_employee_appraisals (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Identification
    appraisal_code VARCHAR(50) NOT NULL,
    
    -- Links
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    appraisal_cycle_id UUID NOT NULL REFERENCES hrms_appraisal_cycles(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    
    -- Status
    status appraisal_status NOT NULL DEFAULT 'not_started',
    
    -- Goal Setting
    goals_submitted_date TIMESTAMP WITH TIME ZONE,
    goals_approved_date TIMESTAMP WITH TIME ZONE,
    
    -- Self Assessment
    self_assessment_submitted_date TIMESTAMP WITH TIME ZONE,
    self_rating rating_scale,
    self_rating_numeric NUMERIC(3,2),
    self_comments TEXT,
    key_achievements TEXT,
    areas_of_improvement TEXT,
    
    -- Manager Review
    manager_review_submitted_date TIMESTAMP WITH TIME ZONE,
    manager_rating rating_scale,
    manager_rating_numeric NUMERIC(3,2),
    manager_comments TEXT,
    manager_strengths TEXT,
    manager_development_areas TEXT,
    
    -- HR Review
    hr_review_submitted_date TIMESTAMP WITH TIME ZONE,
    hr_comments TEXT,
    
    -- Final Rating
    final_rating rating_scale,
    final_rating_numeric NUMERIC(3,2),
    normalized_rating rating_scale,
    normalized_rating_numeric NUMERIC(3,2),
    
    -- Overall Goal Achievement
    overall_goal_achievement_percentage NUMERIC(5,2),
    
    -- Increment & Promotion
    recommended_increment_percentage NUMERIC(5,2),
    recommended_promotion BOOLEAN DEFAULT FALSE,
    recommended_promotion_designation_id UUID REFERENCES hrms_designations(id) ON DELETE SET NULL,
    
    -- Completion
    completed_date TIMESTAMP WITH TIME ZONE,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_appraisal_rating_range CHECK (
        self_rating_numeric IS NULL OR (self_rating_numeric >= 1.00 AND self_rating_numeric <= 5.00)
    ),
    CONSTRAINT chk_manager_rating_range CHECK (
        manager_rating_numeric IS NULL OR (manager_rating_numeric >= 1.00 AND manager_rating_numeric <= 5.00)
    ),
    CONSTRAINT chk_final_rating_range CHECK (
        final_rating_numeric IS NULL OR (final_rating_numeric >= 1.00 AND final_rating_numeric <= 5.00)
    )
);

-- Indexes for Employee Appraisals
CREATE UNIQUE INDEX idx_tenant_appraisal_emp_cycle ON hrms_employee_appraisals(tenant_id, employee_id, appraisal_cycle_id);
CREATE INDEX idx_tenant_appraisal_code ON hrms_employee_appraisals(tenant_id, appraisal_code);
CREATE INDEX idx_tenant_appraisal_status ON hrms_employee_appraisals(tenant_id, status);
CREATE INDEX idx_appraisal_reviewer ON hrms_employee_appraisals(reviewer_id);

-- Comments
COMMENT ON TABLE hrms_employee_appraisals IS 'Individual employee appraisal records for each cycle';
COMMENT ON COLUMN hrms_employee_appraisals.self_rating_numeric IS 'Numeric rating (1.00 to 5.00)';
COMMENT ON COLUMN hrms_employee_appraisals.normalized_rating IS 'Rating after normalization process';

-- ============================================================================
-- TABLE: FEEDBACK REQUESTS (360-Degree)
-- ============================================================================

CREATE TABLE hrms_feedback_requests (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Request Identification
    request_code VARCHAR(50) NOT NULL,
    
    -- Subject & Reviewer
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    appraisal_cycle_id UUID NOT NULL REFERENCES hrms_appraisal_cycles(id) ON DELETE CASCADE,
    
    -- Feedback Type
    feedback_type feedback_type NOT NULL,
    
    -- Request Details
    requested_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    
    -- Status
    status feedback_status NOT NULL DEFAULT 'pending',
    
    -- Reminders
    reminder_sent_count INTEGER DEFAULT 0,
    last_reminder_date TIMESTAMP WITH TIME ZONE,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for Feedback Requests
CREATE INDEX idx_tenant_feedback_req_emp ON hrms_feedback_requests(tenant_id, employee_id, appraisal_cycle_id);
CREATE INDEX idx_tenant_feedback_req_reviewer ON hrms_feedback_requests(tenant_id, reviewer_id, status);
CREATE INDEX idx_tenant_feedback_req_code ON hrms_feedback_requests(tenant_id, request_code);

-- Comments
COMMENT ON TABLE hrms_feedback_requests IS '360-degree feedback requests sent to stakeholders';
COMMENT ON COLUMN hrms_feedback_requests.employee_id IS 'Subject of the feedback';
COMMENT ON COLUMN hrms_feedback_requests.reviewer_id IS 'Person providing the feedback';

-- ============================================================================
-- TABLE: FEEDBACK RESPONSES (360-Degree)
-- ============================================================================

CREATE TABLE hrms_feedback_responses (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Response Link
    feedback_request_id UUID NOT NULL REFERENCES hrms_feedback_requests(id) ON DELETE CASCADE UNIQUE,
    employee_appraisal_id UUID REFERENCES hrms_employee_appraisals(id) ON DELETE CASCADE,
    
    -- Rating
    overall_rating rating_scale,
    overall_rating_numeric NUMERIC(3,2),
    
    -- Competency Ratings
    technical_skills_rating INTEGER,
    communication_skills_rating INTEGER,
    teamwork_rating INTEGER,
    leadership_rating INTEGER,
    problem_solving_rating INTEGER,
    
    -- Feedback Text
    strengths TEXT,
    areas_for_improvement TEXT,
    additional_comments TEXT,
    
    -- Submission
    submitted_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_date TIMESTAMP WITH TIME ZONE,
    
    -- Confidentiality
    is_anonymous BOOLEAN DEFAULT FALSE,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_competency_ratings CHECK (
        (technical_skills_rating IS NULL OR (technical_skills_rating >= 1 AND technical_skills_rating <= 5)) AND
        (communication_skills_rating IS NULL OR (communication_skills_rating >= 1 AND communication_skills_rating <= 5)) AND
        (teamwork_rating IS NULL OR (teamwork_rating >= 1 AND teamwork_rating <= 5)) AND
        (leadership_rating IS NULL OR (leadership_rating >= 1 AND leadership_rating <= 5)) AND
        (problem_solving_rating IS NULL OR (problem_solving_rating >= 1 AND problem_solving_rating <= 5))
    )
);

-- Indexes for Feedback Responses
CREATE UNIQUE INDEX idx_tenant_feedback_resp_request ON hrms_feedback_responses(tenant_id, feedback_request_id);
CREATE INDEX idx_tenant_feedback_resp_appraisal ON hrms_feedback_responses(tenant_id, employee_appraisal_id);

-- Comments
COMMENT ON TABLE hrms_feedback_responses IS '360-degree feedback responses submitted by reviewers';
COMMENT ON COLUMN hrms_feedback_responses.is_anonymous IS 'Whether feedback is shown anonymously to the subject';

-- ============================================================================
-- TABLE: PERFORMANCE INCREMENTS
-- ============================================================================

CREATE TABLE hrms_performance_increments (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Increment Identification
    increment_code VARCHAR(50) NOT NULL,
    
    -- Employee & Appraisal
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    employee_appraisal_id UUID REFERENCES hrms_employee_appraisals(id) ON DELETE SET NULL,
    appraisal_cycle_id UUID REFERENCES hrms_appraisal_cycles(id) ON DELETE SET NULL,
    
    -- Increment Type
    increment_type increment_type NOT NULL DEFAULT 'annual',
    
    -- Salary Details
    current_ctc NUMERIC(15,2) NOT NULL,
    increment_percentage NUMERIC(5,2) NOT NULL,
    increment_amount NUMERIC(15,2) NOT NULL,
    revised_ctc NUMERIC(15,2) NOT NULL,
    
    -- Effective Date
    effective_from DATE NOT NULL,
    
    -- Approval
    recommended_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    approved_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    approved_date TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_approved BOOLEAN DEFAULT FALSE,
    is_processed BOOLEAN DEFAULT FALSE,
    processed_date TIMESTAMP WITH TIME ZONE,
    
    -- Comments
    remarks TEXT,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_increment_amounts CHECK (
        current_ctc > 0 AND 
        increment_percentage >= 0 AND 
        increment_amount >= 0 AND 
        revised_ctc >= current_ctc
    )
);

-- Indexes for Performance Increments
CREATE INDEX idx_tenant_increment_emp ON hrms_performance_increments(tenant_id, employee_id);
CREATE INDEX idx_tenant_increment_code ON hrms_performance_increments(tenant_id, increment_code);
CREATE INDEX idx_tenant_increment_cycle ON hrms_performance_increments(tenant_id, appraisal_cycle_id);

-- Comments
COMMENT ON TABLE hrms_performance_increments IS 'Performance-based salary increments';
COMMENT ON COLUMN hrms_performance_increments.current_ctc IS 'Current Cost to Company';
COMMENT ON COLUMN hrms_performance_increments.revised_ctc IS 'Revised Cost to Company after increment';

-- ============================================================================
-- TABLE: INDIVIDUAL DEVELOPMENT PLANS (IDP)
-- ============================================================================

CREATE TABLE hrms_individual_development_plans (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- IDP Identification
    idp_code VARCHAR(50) NOT NULL,
    idp_title VARCHAR(200) NOT NULL,
    
    -- Employee & Period
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    appraisal_cycle_id UUID REFERENCES hrms_appraisal_cycles(id) ON DELETE SET NULL,
    
    -- Career Aspirations
    career_goal TEXT,
    target_role VARCHAR(200),
    target_designation_id UUID REFERENCES hrms_designations(id) ON DELETE SET NULL,
    
    -- Skill Gaps
    current_skills TEXT,
    required_skills TEXT,
    skill_gaps TEXT,
    
    -- Timeline
    plan_start_date DATE NOT NULL,
    plan_end_date DATE NOT NULL,
    
    -- Status
    status idp_status NOT NULL DEFAULT 'draft',
    
    -- Approval
    submitted_date TIMESTAMP WITH TIME ZONE,
    approved_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    approved_date TIMESTAMP WITH TIME ZONE,
    
    -- Progress
    overall_progress_percentage INTEGER DEFAULT 0,
    
    -- Comments
    employee_notes TEXT,
    manager_notes TEXT,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_idp_progress CHECK (overall_progress_percentage >= 0 AND overall_progress_percentage <= 100),
    CONSTRAINT chk_idp_dates CHECK (plan_end_date >= plan_start_date)
);

-- Indexes for IDPs
CREATE INDEX idx_tenant_idp_emp ON hrms_individual_development_plans(tenant_id, employee_id);
CREATE INDEX idx_tenant_idp_code ON hrms_individual_development_plans(tenant_id, idp_code);
CREATE INDEX idx_tenant_idp_status ON hrms_individual_development_plans(tenant_id, status);

-- Comments
COMMENT ON TABLE hrms_individual_development_plans IS 'Individual Development Plans for career growth';
COMMENT ON COLUMN hrms_individual_development_plans.skill_gaps IS 'Skills needed for target role (can be JSON)';

-- ============================================================================
-- TABLE: DEVELOPMENT ACTIVITIES
-- ============================================================================

CREATE TABLE hrms_development_activities (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Multi-tenancy
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Activity Identification
    activity_code VARCHAR(50) NOT NULL,
    activity_title VARCHAR(200) NOT NULL,
    activity_description TEXT,
    
    -- IDP Link
    idp_id UUID NOT NULL REFERENCES hrms_individual_development_plans(id) ON DELETE CASCADE,
    
    -- Activity Type
    activity_type development_activity_type NOT NULL,
    
    -- Details
    provider_name VARCHAR(200),
    course_name VARCHAR(200),
    duration_hours INTEGER,
    cost NUMERIC(15,2),
    
    -- Timeline
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    
    -- Status
    is_completed BOOLEAN DEFAULT FALSE,
    completion_percentage INTEGER DEFAULT 0,
    
    -- Outcome
    certification_obtained VARCHAR(200),
    certificate_url VARCHAR(500),
    learning_outcome TEXT,
    
    -- Comments
    employee_feedback TEXT,
    manager_feedback TEXT,
    
    -- Audit Fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT chk_activity_completion CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    CONSTRAINT chk_activity_dates CHECK (
        planned_end_date IS NULL OR planned_start_date IS NULL OR planned_end_date >= planned_start_date
    )
);

-- Indexes for Development Activities
CREATE INDEX idx_tenant_activity_idp ON hrms_development_activities(tenant_id, idp_id);
CREATE INDEX idx_tenant_activity_code ON hrms_development_activities(tenant_id, activity_code);

-- Comments
COMMENT ON TABLE hrms_development_activities IS 'Individual learning/development activities within IDPs';
COMMENT ON COLUMN hrms_development_activities.duration_hours IS 'Estimated duration in hours';

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_appraisal_cycles_updated_at BEFORE UPDATE ON hrms_appraisal_cycles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performance_goals_updated_at BEFORE UPDATE ON hrms_performance_goals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_appraisals_updated_at BEFORE UPDATE ON hrms_employee_appraisals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_requests_updated_at BEFORE UPDATE ON hrms_feedback_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_responses_updated_at BEFORE UPDATE ON hrms_feedback_responses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performance_increments_updated_at BEFORE UPDATE ON hrms_performance_increments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_individual_development_plans_updated_at BEFORE UPDATE ON hrms_individual_development_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_development_activities_updated_at BEFORE UPDATE ON hrms_development_activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================================

-- Note: Sample data should be inserted after ensuring tenant and employee records exist
-- This section can be uncommented and customized based on actual tenant/employee IDs

-- ============================================================================
-- ROLLBACK SCRIPT (For reference)
-- ============================================================================

/*
-- To rollback this migration:

DROP TABLE IF EXISTS hrms_development_activities CASCADE;
DROP TABLE IF EXISTS hrms_individual_development_plans CASCADE;
DROP TABLE IF EXISTS hrms_performance_increments CASCADE;
DROP TABLE IF EXISTS hrms_feedback_responses CASCADE;
DROP TABLE IF EXISTS hrms_feedback_requests CASCADE;
DROP TABLE IF EXISTS hrms_employee_appraisals CASCADE;
DROP TABLE IF EXISTS hrms_performance_goals CASCADE;
DROP TABLE IF EXISTS hrms_appraisal_cycles CASCADE;

DROP TYPE IF EXISTS development_activity_type CASCADE;
DROP TYPE IF EXISTS idp_status CASCADE;
DROP TYPE IF EXISTS increment_type CASCADE;
DROP TYPE IF EXISTS feedback_status CASCADE;
DROP TYPE IF EXISTS feedback_type CASCADE;
DROP TYPE IF EXISTS rating_scale CASCADE;
DROP TYPE IF EXISTS appraisal_status CASCADE;
DROP TYPE IF EXISTS appraisal_cycle_status CASCADE;
DROP TYPE IF EXISTS goal_priority CASCADE;
DROP TYPE IF EXISTS goal_status CASCADE;
DROP TYPE IF EXISTS goal_type CASCADE;
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
