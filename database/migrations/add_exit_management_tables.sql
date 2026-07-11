-- ============================================================================
-- Exit Management System - Database Migration Script
-- ============================================================================
-- Description: Creates all tables, enums, indexes, and triggers for Exit Management
-- Version: 1.0
-- Date: 2024
-- ============================================================================

-- Start transaction
BEGIN;

-- ============================================================================
-- CREATE ENUMS
-- ============================================================================

-- Resignation Type
CREATE TYPE resignationtype AS ENUM (
    'voluntary',
    'involuntary',
    'retirement',
    'absconding',
    'end_of_contract',
    'mutual_consent'
);

-- Resignation Status
CREATE TYPE resignationstatus AS ENUM (
    'submitted',
    'under_review',
    'approved',
    'rejected',
    'withdrawn',
    'completed',
    'cancelled'
);

-- Clearance Status
CREATE TYPE clearancestatus AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'not_applicable',
    'waived'
);

-- Settlement Status
CREATE TYPE settlementstatus AS ENUM (
    'pending',
    'calculated',
    'approved',
    'processing',
    'paid',
    'on_hold',
    'rejected'
);

-- Settlement Component Type
CREATE TYPE settlementcomponenttype AS ENUM (
    'salary',
    'leave_encashment',
    'notice_pay',
    'bonus',
    'gratuity',
    'reimbursement',
    'recovery',
    'other'
);

-- Exit Document Type
CREATE TYPE exitdocumenttype AS ENUM (
    'resignation_letter',
    'acceptance_letter',
    'experience_letter',
    'relieving_letter',
    'service_certificate',
    'noc',
    'clearance_form',
    'fnf_statement',
    'form_16',
    'pf_withdrawal',
    'gratuity_form',
    'other'
);

-- ============================================================================
-- CREATE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Resignations Table
-- ----------------------------------------------------------------------------
CREATE TABLE exit_resignations (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tenant
    tenant_id UUID NOT NULL,
    
    -- Basic Information
    resignation_code VARCHAR(50) NOT NULL,
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    
    -- Resignation Details
    resignation_type resignationtype NOT NULL DEFAULT 'voluntary',
    resignation_date DATE NOT NULL,
    last_working_date DATE NOT NULL,
    actual_last_working_date DATE,
    
    -- Notice Period
    notice_period_days INTEGER NOT NULL DEFAULT 30,
    notice_period_served INTEGER,
    is_notice_period_waived BOOLEAN DEFAULT FALSE,
    notice_waiver_reason TEXT,
    
    -- Reason for Leaving
    reason_category VARCHAR(100),
    reason_details TEXT NOT NULL,
    feedback TEXT,
    
    -- Status and Workflow
    status resignationstatus NOT NULL DEFAULT 'submitted',
    
    -- Reporting Manager Review
    reporting_manager_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    manager_reviewed_date TIMESTAMP,
    manager_comments TEXT,
    manager_recommendation VARCHAR(50),
    
    -- HR Review
    hr_reviewer_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    hr_reviewed_date TIMESTAMP,
    hr_comments TEXT,
    
    -- Approval
    approved_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    approved_date TIMESTAMP,
    approval_comments TEXT,
    
    -- Rejection/Withdrawal
    rejected_date TIMESTAMP,
    rejection_reason TEXT,
    withdrawn_date TIMESTAMP,
    withdrawal_reason TEXT,
    
    -- Counter Offer
    counter_offer_made BOOLEAN DEFAULT FALSE,
    counter_offer_details TEXT,
    counter_offer_accepted BOOLEAN,
    
    -- Exit Interview
    exit_interview_scheduled BOOLEAN DEFAULT FALSE,
    exit_interview_date TIMESTAMP,
    exit_interview_conducted_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    exit_interview_notes TEXT,
    
    -- Handover
    handover_completed BOOLEAN DEFAULT FALSE,
    handover_to_employee_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    handover_notes TEXT,
    handover_document_path VARCHAR(500),
    
    -- Additional Info
    re_employment_eligible BOOLEAN DEFAULT TRUE,
    blacklist_flag BOOLEAN DEFAULT FALSE,
    blacklist_reason TEXT,
    
    -- Attachments
    resignation_letter_path VARCHAR(500),
    supporting_documents TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID
);

-- ----------------------------------------------------------------------------
-- Exit Clearances Table
-- ----------------------------------------------------------------------------
CREATE TABLE exit_clearances (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tenant
    tenant_id UUID NOT NULL,
    
    -- Basic Information
    resignation_id UUID NOT NULL REFERENCES exit_resignations(id) ON DELETE CASCADE,
    
    -- Clearance Details
    clearance_from VARCHAR(100) NOT NULL,
    clearance_type VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Status
    status clearancestatus NOT NULL DEFAULT 'pending',
    
    -- Assigned To
    assigned_to_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    assigned_date TIMESTAMP,
    
    -- Clearance Items/Checklist
    checklist_items TEXT,
    pending_items TEXT,
    
    -- Completion
    cleared_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    cleared_date TIMESTAMP,
    clearance_remarks TEXT,
    
    -- Attachments
    supporting_documents TEXT,
    
    -- Dependencies
    is_mandatory BOOLEAN DEFAULT TRUE,
    depends_on_clearance_id UUID REFERENCES exit_clearances(id) ON DELETE SET NULL,
    
    -- Escalation
    due_date DATE,
    is_overdue BOOLEAN DEFAULT FALSE,
    escalated BOOLEAN DEFAULT FALSE,
    escalation_level INTEGER DEFAULT 0,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID
);

-- ----------------------------------------------------------------------------
-- Exit Settlements Table (Full & Final Settlement)
-- ----------------------------------------------------------------------------
CREATE TABLE exit_settlements (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tenant
    tenant_id UUID NOT NULL,
    
    -- Basic Information
    settlement_code VARCHAR(50) NOT NULL,
    resignation_id UUID NOT NULL UNIQUE REFERENCES exit_resignations(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    
    -- Settlement Period
    settlement_from_date DATE NOT NULL,
    settlement_to_date DATE NOT NULL,
    
    -- Status
    status settlementstatus NOT NULL DEFAULT 'pending',
    
    -- Calculation Details
    -- Salary Components
    basic_salary_days INTEGER,
    basic_salary_amount NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Leave Encashment
    total_leave_balance NUMERIC(10, 2) DEFAULT 0.00,
    encashable_leaves NUMERIC(10, 2) DEFAULT 0.00,
    leave_encashment_amount NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Notice Period
    notice_period_shortfall_days INTEGER DEFAULT 0,
    notice_pay_recovery NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Gratuity
    years_of_service NUMERIC(5, 2),
    gratuity_eligible BOOLEAN DEFAULT FALSE,
    gratuity_amount NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Bonus/Incentives
    bonus_amount NUMERIC(15, 2) DEFAULT 0.00,
    incentive_amount NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Reimbursements
    pending_reimbursement_amount NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Recoveries/Deductions
    loan_recovery NUMERIC(15, 2) DEFAULT 0.00,
    advance_recovery NUMERIC(15, 2) DEFAULT 0.00,
    asset_loss_recovery NUMERIC(15, 2) DEFAULT 0.00,
    other_recovery NUMERIC(15, 2) DEFAULT 0.00,
    recovery_remarks TEXT,
    
    -- Totals
    gross_payable NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    total_deductions NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    net_payable NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    
    -- Tax
    tds_amount NUMERIC(15, 2) DEFAULT 0.00,
    professional_tax NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Calculated By
    calculated_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    calculated_date TIMESTAMP,
    calculation_remarks TEXT,
    
    -- Approval
    approved_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    approved_date TIMESTAMP,
    approval_remarks TEXT,
    
    -- Finance Processing
    finance_processor_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    finance_processed_date TIMESTAMP,
    finance_remarks TEXT,
    
    -- Payment Details
    payment_date DATE,
    payment_mode VARCHAR(50),
    payment_reference VARCHAR(100),
    bank_account_number VARCHAR(50),
    bank_name VARCHAR(200),
    bank_ifsc_code VARCHAR(20),
    
    -- Hold/Rejection
    hold_reason TEXT,
    hold_until_date DATE,
    rejected_date TIMESTAMP,
    rejection_reason TEXT,
    
    -- Attachments
    fnf_statement_path VARCHAR(500),
    supporting_documents TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID
);

-- ----------------------------------------------------------------------------
-- Settlement Components Table
-- ----------------------------------------------------------------------------
CREATE TABLE exit_settlement_components (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tenant
    tenant_id UUID NOT NULL,
    
    -- Basic Information
    settlement_id UUID NOT NULL REFERENCES exit_settlements(id) ON DELETE CASCADE,
    
    -- Component Details
    component_type settlementcomponenttype NOT NULL,
    component_name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Amount
    amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    is_deduction BOOLEAN DEFAULT FALSE,
    
    -- Calculation Details
    calculation_basis TEXT,
    quantity NUMERIC(10, 2),
    rate NUMERIC(15, 2),
    
    -- Tax
    is_taxable BOOLEAN DEFAULT TRUE,
    tax_amount NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Remarks
    remarks TEXT,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID
);

-- ----------------------------------------------------------------------------
-- Exit Documents Table
-- ----------------------------------------------------------------------------
CREATE TABLE exit_documents (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Tenant
    tenant_id UUID NOT NULL,
    
    -- Basic Information
    document_code VARCHAR(50) NOT NULL,
    resignation_id UUID NOT NULL REFERENCES exit_resignations(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES hrms_employees(id) ON DELETE CASCADE,
    
    -- Document Details
    document_type exitdocumenttype NOT NULL,
    document_name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Template
    template_name VARCHAR(200),
    template_version VARCHAR(20),
    
    -- Content
    document_content TEXT,
    document_path VARCHAR(500),
    document_url VARCHAR(500),
    
    -- Status
    is_generated BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    is_issued BOOLEAN DEFAULT FALSE,
    
    -- Generation
    generated_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    generated_date TIMESTAMP,
    
    -- Approval
    approved_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    approved_date TIMESTAMP,
    approval_remarks TEXT,
    
    -- Issuance
    issued_by_id UUID REFERENCES hrms_employees(id) ON DELETE SET NULL,
    issued_date TIMESTAMP,
    issue_remarks TEXT,
    
    -- Document Metadata
    document_number VARCHAR(100),
    issue_place VARCHAR(200),
    validity_date DATE,
    
    -- Digital Signature
    is_digitally_signed BOOLEAN DEFAULT FALSE,
    digital_signature_info TEXT,
    
    -- Delivery
    delivery_mode VARCHAR(50),
    delivered_date TIMESTAMP,
    recipient_email VARCHAR(100),
    recipient_address TEXT,
    tracking_number VARCHAR(100),
    
    -- Employee Acknowledgment
    acknowledged_by_employee BOOLEAN DEFAULT FALSE,
    acknowledgment_date TIMESTAMP,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID
);

-- ============================================================================
-- CREATE INDEXES
-- ============================================================================

-- Resignations Indexes
CREATE UNIQUE INDEX idx_tenant_resignation_code ON exit_resignations(tenant_id, resignation_code) WHERE is_deleted = FALSE;
CREATE INDEX idx_tenant_resignation_emp ON exit_resignations(tenant_id, employee_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_resignation_dates ON exit_resignations(tenant_id, resignation_date, last_working_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_resignation_manager ON exit_resignations(tenant_id, reporting_manager_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_resignation_status ON exit_resignations(tenant_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_resignation_type ON exit_resignations(tenant_id, resignation_type) WHERE is_deleted = FALSE;

-- Clearances Indexes
CREATE INDEX idx_tenant_clearance_resignation ON exit_clearances(tenant_id, resignation_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_clearance_status ON exit_clearances(tenant_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_clearance_assigned ON exit_clearances(tenant_id, assigned_to_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_clearance_from ON exit_clearances(tenant_id, clearance_from) WHERE is_deleted = FALSE;
CREATE INDEX idx_clearance_overdue ON exit_clearances(tenant_id, is_overdue) WHERE is_deleted = FALSE AND is_overdue = TRUE;

-- Settlements Indexes
CREATE UNIQUE INDEX idx_tenant_settlement_code ON exit_settlements(tenant_id, settlement_code) WHERE is_deleted = FALSE;
CREATE INDEX idx_tenant_settlement_emp ON exit_settlements(tenant_id, employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_settlement_status ON exit_settlements(tenant_id, status) WHERE is_deleted = FALSE;
CREATE INDEX idx_settlement_payment ON exit_settlements(tenant_id, payment_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_settlement_resignation ON exit_settlements(tenant_id, resignation_id) WHERE is_deleted = FALSE;

-- Settlement Components Indexes
CREATE INDEX idx_tenant_settlement_comp ON exit_settlement_components(tenant_id, settlement_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_settlement_comp_type ON exit_settlement_components(tenant_id, component_type) WHERE is_deleted = FALSE;

-- Exit Documents Indexes
CREATE UNIQUE INDEX idx_tenant_exit_doc_code ON exit_documents(tenant_id, document_code) WHERE is_deleted = FALSE;
CREATE INDEX idx_tenant_exit_doc_resignation ON exit_documents(tenant_id, resignation_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_exit_doc_type ON exit_documents(tenant_id, document_type) WHERE is_deleted = FALSE;
CREATE INDEX idx_exit_doc_employee ON exit_documents(tenant_id, employee_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_exit_doc_status ON exit_documents(tenant_id, is_generated, is_approved, is_issued) WHERE is_deleted = FALSE;

-- ============================================================================
-- CREATE TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Resignations trigger
CREATE OR REPLACE FUNCTION update_exit_resignations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_exit_resignations_updated_at
    BEFORE UPDATE ON exit_resignations
    FOR EACH ROW
    EXECUTE FUNCTION update_exit_resignations_updated_at();

-- Clearances trigger
CREATE OR REPLACE FUNCTION update_exit_clearances_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_exit_clearances_updated_at
    BEFORE UPDATE ON exit_clearances
    FOR EACH ROW
    EXECUTE FUNCTION update_exit_clearances_updated_at();

-- Settlements trigger
CREATE OR REPLACE FUNCTION update_exit_settlements_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_exit_settlements_updated_at
    BEFORE UPDATE ON exit_settlements
    FOR EACH ROW
    EXECUTE FUNCTION update_exit_settlements_updated_at();

-- Settlement Components trigger
CREATE OR REPLACE FUNCTION update_exit_settlement_components_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_exit_settlement_components_updated_at
    BEFORE UPDATE ON exit_settlement_components
    FOR EACH ROW
    EXECUTE FUNCTION update_exit_settlement_components_updated_at();

-- Exit Documents trigger
CREATE OR REPLACE FUNCTION update_exit_documents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_exit_documents_updated_at
    BEFORE UPDATE ON exit_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_exit_documents_updated_at();

-- ============================================================================
-- CREATE HELPER FUNCTIONS
-- ============================================================================

-- Function to calculate settlement net payable
CREATE OR REPLACE FUNCTION calculate_settlement_net_payable(p_settlement_id UUID)
RETURNS NUMERIC(15, 2) AS $$
DECLARE
    v_gross_payable NUMERIC(15, 2) := 0;
    v_total_deductions NUMERIC(15, 2) := 0;
    v_net_payable NUMERIC(15, 2) := 0;
BEGIN
    -- Calculate gross payable (non-deduction components)
    SELECT COALESCE(SUM(amount), 0)
    INTO v_gross_payable
    FROM exit_settlement_components
    WHERE settlement_id = p_settlement_id
    AND is_deduction = FALSE
    AND is_deleted = FALSE;
    
    -- Calculate total deductions (deduction components)
    SELECT COALESCE(SUM(amount), 0)
    INTO v_total_deductions
    FROM exit_settlement_components
    WHERE settlement_id = p_settlement_id
    AND is_deduction = TRUE
    AND is_deleted = FALSE;
    
    -- Calculate net payable
    v_net_payable := v_gross_payable - v_total_deductions;
    
    -- Update settlement record
    UPDATE exit_settlements
    SET gross_payable = v_gross_payable,
        total_deductions = v_total_deductions,
        net_payable = v_net_payable,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_settlement_id;
    
    RETURN v_net_payable;
END;
$$ LANGUAGE plpgsql;

-- Function to check if all clearances are completed
CREATE OR REPLACE FUNCTION check_all_clearances_completed(p_resignation_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_pending_count INTEGER := 0;
BEGIN
    SELECT COUNT(*)
    INTO v_pending_count
    FROM exit_clearances
    WHERE resignation_id = p_resignation_id
    AND is_mandatory = TRUE
    AND status NOT IN ('completed', 'not_applicable', 'waived')
    AND is_deleted = FALSE;
    
    RETURN v_pending_count = 0;
END;
$$ LANGUAGE plpgsql;

-- Function to update clearance overdue status
CREATE OR REPLACE FUNCTION update_clearance_overdue_status()
RETURNS void AS $$
BEGIN
    UPDATE exit_clearances
    SET is_overdue = TRUE
    WHERE due_date < CURRENT_DATE
    AND status NOT IN ('completed', 'not_applicable', 'waived')
    AND is_deleted = FALSE
    AND is_overdue = FALSE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INSERT DEFAULT DATA
-- ============================================================================

-- Insert default clearance types (these can be customized per organization)
-- This is optional and can be populated through application logic

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant appropriate permissions (adjust based on your role structure)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO hrms_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO hrms_user;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE exit_resignations IS 'Employee resignation and exit requests with complete workflow';
COMMENT ON TABLE exit_clearances IS 'Departmental clearances required before employee exit';
COMMENT ON TABLE exit_settlements IS 'Full and Final settlement calculations and payments';
COMMENT ON TABLE exit_settlement_components IS 'Detailed breakdown of settlement components';
COMMENT ON TABLE exit_documents IS 'Exit-related documents like experience letters, relieving letters, etc.';

COMMENT ON TYPE resignationtype IS 'Type of resignation - voluntary, involuntary, retirement, etc.';
COMMENT ON TYPE resignationstatus IS 'Status of resignation workflow';
COMMENT ON TYPE clearancestatus IS 'Status of clearance process';
COMMENT ON TYPE settlementstatus IS 'Status of settlement process';
COMMENT ON TYPE settlementcomponenttype IS 'Type of settlement component - salary, leave, recovery, etc.';
COMMENT ON TYPE exitdocumenttype IS 'Type of exit document - experience letter, relieving letter, etc.';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify all tables were created
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'exit_resignations',
        'exit_clearances',
        'exit_settlements',
        'exit_settlement_components',
        'exit_documents'
    );
    
    RAISE NOTICE 'Created % Exit Management tables', table_count;
    
    IF table_count <> 5 THEN
        RAISE EXCEPTION 'Expected 5 tables but found %', table_count;
    END IF;
END $$;

-- Verify all enums were created
DO $$
DECLARE
    enum_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO enum_count
    FROM pg_type
    WHERE typname IN (
        'resignationtype',
        'resignationstatus',
        'clearancestatus',
        'settlementstatus',
        'settlementcomponenttype',
        'exitdocumenttype'
    );
    
    RAISE NOTICE 'Created % Exit Management enums', enum_count;
    
    IF enum_count <> 6 THEN
        RAISE EXCEPTION 'Expected 6 enums but found %', enum_count;
    END IF;
END $$;

-- Commit transaction
COMMIT;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Display success message
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Exit Management System Migration Completed Successfully!';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - 6 Enums';
    RAISE NOTICE '  - 5 Tables';
    RAISE NOTICE '  - 20+ Indexes';
    RAISE NOTICE '  - 5 Update Triggers';
    RAISE NOTICE '  - 3 Helper Functions';
    RAISE NOTICE '============================================================================';
END $$;
