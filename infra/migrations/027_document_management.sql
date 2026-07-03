-- ============================================================================
-- Phase 10: Document Management Migration
-- ============================================================================
-- Description: Comprehensive document management system with version control,
--              OCR, workflows, templates, compliance, and retention policies
-- Version: 1.0.0
-- Date: 2026-07-03
-- ============================================================================

-- ============================================================================
-- 1. DOCUMENT CATEGORIES TABLE
-- ============================================================================
CREATE TABLE gold_document_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_code VARCHAR(50) NOT NULL UNIQUE,
    category_name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_category_id UUID REFERENCES gold_document_categories(category_id),
    category_level INTEGER NOT NULL DEFAULT 1,
    is_system_category BOOLEAN NOT NULL DEFAULT FALSE,
    retention_period_days INTEGER,
    is_mandatory BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_extensions TEXT[], -- ['pdf', 'jpg', 'png']
    max_file_size_mb DECIMAL(10,2),
    requires_approval BOOLEAN NOT NULL DEFAULT FALSE,
    requires_ocr BOOLEAN NOT NULL DEFAULT FALSE,
    metadata_schema JSONB, -- Custom metadata fields definition
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_categories_code ON gold_document_categories(category_code);
CREATE INDEX idx_doc_categories_parent ON gold_document_categories(parent_category_id);
CREATE INDEX idx_doc_categories_active ON gold_document_categories(is_active);

-- ============================================================================
-- 2. DOCUMENTS TABLE
-- ============================================================================
CREATE TABLE gold_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_number VARCHAR(50) NOT NULL UNIQUE,
    document_name VARCHAR(300) NOT NULL,
    description TEXT,
    category_id UUID NOT NULL REFERENCES gold_document_categories(category_id),
    entity_type VARCHAR(50) NOT NULL, -- 'loan', 'customer', 'pledge', 'valuation', 'branch'
    entity_id UUID NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- 'application', 'kyc', 'pledge_receipt', 'valuation_report'
    file_name VARCHAR(300) NOT NULL,
    file_extension VARCHAR(20) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_path TEXT NOT NULL,
    storage_provider VARCHAR(50) NOT NULL DEFAULT 's3', -- 's3', 'azure', 'gcp', 'local'
    checksum VARCHAR(64) NOT NULL, -- SHA-256 hash
    current_version INTEGER NOT NULL DEFAULT 1,
    is_encrypted BOOLEAN NOT NULL DEFAULT TRUE,
    encryption_key_id VARCHAR(100),
    ocr_status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'not_required'
    ocr_text TEXT,
    ocr_confidence DECIMAL(5,2),
    ocr_processed_at TIMESTAMP,
    is_signed BOOLEAN NOT NULL DEFAULT FALSE,
    signature_status VARCHAR(20), -- 'pending', 'signed', 'rejected', 'expired'
    signed_by UUID,
    signed_at TIMESTAMP,
    signature_certificate TEXT,
    access_level VARCHAR(20) NOT NULL DEFAULT 'internal', -- 'public', 'internal', 'confidential', 'restricted'
    retention_until DATE,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    archived_at TIMESTAMP,
    archived_by UUID,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID,
    tags TEXT[], -- ['urgent', 'verified', 'pending_review']
    metadata JSONB, -- Custom metadata based on category schema
    remarks TEXT,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_number ON gold_documents(document_number);
CREATE INDEX idx_documents_category ON gold_documents(category_id);
CREATE INDEX idx_documents_entity ON gold_documents(entity_type, entity_id);
CREATE INDEX idx_documents_type ON gold_documents(document_type);
CREATE INDEX idx_documents_ocr_status ON gold_documents(ocr_status);
CREATE INDEX idx_documents_signature_status ON gold_documents(signature_status);
CREATE INDEX idx_documents_retention ON gold_documents(retention_until) WHERE NOT is_archived;
CREATE INDEX idx_documents_archived ON gold_documents(is_archived);
CREATE INDEX idx_documents_deleted ON gold_documents(is_deleted) WHERE is_deleted = FALSE;
CREATE INDEX idx_documents_created_at ON gold_documents(created_at);

-- ============================================================================
-- 3. DOCUMENT VERSIONS TABLE
-- ============================================================================
CREATE TABLE gold_document_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES gold_documents(document_id),
    version_number INTEGER NOT NULL,
    file_name VARCHAR(300) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    change_description TEXT,
    version_type VARCHAR(20) NOT NULL DEFAULT 'minor', -- 'major', 'minor', 'patch'
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    replaced_version_id UUID REFERENCES gold_document_versions(version_id),
    ocr_text TEXT,
    ocr_confidence DECIMAL(5,2),
    metadata JSONB,
    created_by UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, version_number)
);

CREATE INDEX idx_doc_versions_document ON gold_document_versions(document_id);
CREATE INDEX idx_doc_versions_current ON gold_document_versions(document_id, is_current) WHERE is_current = TRUE;
CREATE INDEX idx_doc_versions_created_at ON gold_document_versions(created_at);

-- ============================================================================
-- 4. DOCUMENT METADATA TABLE
-- ============================================================================
CREATE TABLE gold_document_metadata (
    metadata_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES gold_documents(document_id),
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value TEXT NOT NULL,
    value_type VARCHAR(20) NOT NULL, -- 'string', 'number', 'date', 'boolean', 'json'
    is_indexed BOOLEAN NOT NULL DEFAULT FALSE,
    is_searchable BOOLEAN NOT NULL DEFAULT TRUE,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, metadata_key)
);

CREATE INDEX idx_doc_metadata_document ON gold_document_metadata(document_id);
CREATE INDEX idx_doc_metadata_key ON gold_document_metadata(metadata_key);
CREATE INDEX idx_doc_metadata_searchable ON gold_document_metadata(metadata_key, metadata_value) WHERE is_searchable = TRUE;

-- ============================================================================
-- 5. DOCUMENT TEMPLATES TABLE
-- ============================================================================
CREATE TABLE gold_document_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_code VARCHAR(50) NOT NULL UNIQUE,
    template_name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id UUID NOT NULL REFERENCES gold_document_categories(category_id),
    template_type VARCHAR(50) NOT NULL, -- 'loan_agreement', 'receipt', 'notice', 'report'
    file_format VARCHAR(20) NOT NULL, -- 'docx', 'pdf', 'html'
    storage_path TEXT NOT NULL,
    template_variables JSONB, -- {fields: [{name, type, required, default}]}
    merge_rules JSONB, -- Rules for data merging
    is_system_template BOOLEAN NOT NULL DEFAULT FALSE,
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_templates_code ON gold_document_templates(template_code);
CREATE INDEX idx_doc_templates_category ON gold_document_templates(category_id);
CREATE INDEX idx_doc_templates_type ON gold_document_templates(template_type);
CREATE INDEX idx_doc_templates_active ON gold_document_templates(is_active);

-- ============================================================================
-- 6. DOCUMENT WORKFLOWS TABLE
-- ============================================================================
CREATE TABLE gold_document_workflows (
    workflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_code VARCHAR(50) NOT NULL UNIQUE,
    workflow_name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES gold_document_categories(category_id),
    workflow_type VARCHAR(50) NOT NULL, -- 'approval', 'review', 'verification', 'signature'
    workflow_steps JSONB NOT NULL, -- [{step, role, action, sequence, is_parallel}]
    trigger_conditions JSONB, -- Conditions to auto-trigger workflow
    escalation_rules JSONB, -- {delay_hours, escalate_to_role}
    sla_hours INTEGER,
    is_mandatory BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_workflows_code ON gold_document_workflows(workflow_code);
CREATE INDEX idx_doc_workflows_category ON gold_document_workflows(category_id);
CREATE INDEX idx_doc_workflows_type ON gold_document_workflows(workflow_type);
CREATE INDEX idx_doc_workflows_active ON gold_document_workflows(is_active);

-- ============================================================================
-- 7. DOCUMENT APPROVALS TABLE
-- ============================================================================
CREATE TABLE gold_document_approvals (
    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES gold_documents(document_id),
    workflow_id UUID NOT NULL REFERENCES gold_document_workflows(workflow_id),
    approval_number VARCHAR(50) NOT NULL UNIQUE,
    current_step INTEGER NOT NULL DEFAULT 1,
    total_steps INTEGER NOT NULL,
    approval_status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'in_progress', 'approved', 'rejected', 'cancelled'
    priority VARCHAR(20) NOT NULL DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    initiated_by UUID NOT NULL,
    initiated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_to UUID,
    assigned_at TIMESTAMP,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    approval_steps JSONB, -- [{step, status, approver, timestamp, comments}]
    rejection_reason TEXT,
    is_escalated BOOLEAN NOT NULL DEFAULT FALSE,
    escalated_at TIMESTAMP,
    escalated_to UUID,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_approvals_document ON gold_document_approvals(document_id);
CREATE INDEX idx_doc_approvals_workflow ON gold_document_approvals(workflow_id);
CREATE INDEX idx_doc_approvals_number ON gold_document_approvals(approval_number);
CREATE INDEX idx_doc_approvals_status ON gold_document_approvals(approval_status);
CREATE INDEX idx_doc_approvals_assigned ON gold_document_approvals(assigned_to) WHERE approval_status IN ('pending', 'in_progress');
CREATE INDEX idx_doc_approvals_due ON gold_document_approvals(due_date) WHERE approval_status IN ('pending', 'in_progress');
CREATE INDEX idx_doc_approvals_escalated ON gold_document_approvals(is_escalated) WHERE is_escalated = TRUE;

-- ============================================================================
-- 8. DOCUMENT TAGS TABLE
-- ============================================================================
CREATE TABLE gold_document_tags (
    tag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_name VARCHAR(100) NOT NULL UNIQUE,
    tag_category VARCHAR(50), -- 'status', 'priority', 'department', 'custom'
    tag_color VARCHAR(7), -- Hex color code
    description TEXT,
    usage_count INTEGER NOT NULL DEFAULT 0,
    is_system_tag BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_tags_name ON gold_document_tags(tag_name);
CREATE INDEX idx_doc_tags_category ON gold_document_tags(tag_category);
CREATE INDEX idx_doc_tags_active ON gold_document_tags(is_active);

-- Document-Tag mapping (many-to-many)
CREATE TABLE gold_document_tag_mappings (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES gold_documents(document_id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES gold_document_tags(tag_id) ON DELETE CASCADE,
    tagged_by UUID NOT NULL,
    tagged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, tag_id)
);

CREATE INDEX idx_doc_tag_mappings_document ON gold_document_tag_mappings(document_id);
CREATE INDEX idx_doc_tag_mappings_tag ON gold_document_tag_mappings(tag_id);

-- ============================================================================
-- 9. DOCUMENT ACCESS LOGS TABLE
-- ============================================================================
CREATE TABLE gold_document_access_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES gold_documents(document_id),
    action_type VARCHAR(50) NOT NULL, -- 'view', 'download', 'upload', 'update', 'delete', 'share', 'print'
    user_id UUID NOT NULL,
    user_role VARCHAR(50),
    ip_address VARCHAR(45),
    user_agent TEXT,
    access_location VARCHAR(100), -- Geographic location if available
    access_device VARCHAR(50), -- 'desktop', 'mobile', 'tablet'
    session_id VARCHAR(100),
    access_result VARCHAR(20) NOT NULL, -- 'success', 'denied', 'failed'
    denial_reason TEXT,
    file_version INTEGER,
    download_size_bytes BIGINT,
    access_duration_seconds INTEGER,
    metadata JSONB, -- Additional context
    accessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_access_logs_document ON gold_document_access_logs(document_id);
CREATE INDEX idx_doc_access_logs_user ON gold_document_access_logs(user_id);
CREATE INDEX idx_doc_access_logs_action ON gold_document_access_logs(action_type);
CREATE INDEX idx_doc_access_logs_result ON gold_document_access_logs(access_result);
CREATE INDEX idx_doc_access_logs_accessed_at ON gold_document_access_logs(accessed_at);

-- ============================================================================
-- 10. DOCUMENT RETENTION POLICIES TABLE
-- ============================================================================
CREATE TABLE gold_document_retention_policies (
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_code VARCHAR(50) NOT NULL UNIQUE,
    policy_name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES gold_document_categories(category_id),
    document_type VARCHAR(50),
    retention_period_days INTEGER NOT NULL,
    retention_trigger VARCHAR(50) NOT NULL, -- 'from_creation', 'from_loan_closure', 'from_last_access'
    archive_after_days INTEGER, -- Move to archive storage
    delete_after_retention BOOLEAN NOT NULL DEFAULT FALSE,
    requires_legal_hold BOOLEAN NOT NULL DEFAULT FALSE,
    compliance_regulation VARCHAR(100), -- 'RBI', 'GDPR', 'SOX', 'HIPAA'
    auto_apply BOOLEAN NOT NULL DEFAULT FALSE,
    priority INTEGER NOT NULL DEFAULT 0, -- Higher priority policies apply first
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    affected_documents_count INTEGER NOT NULL DEFAULT 0,
    last_executed_at TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_retention_code ON gold_document_retention_policies(policy_code);
CREATE INDEX idx_doc_retention_category ON gold_document_retention_policies(category_id);
CREATE INDEX idx_doc_retention_type ON gold_document_retention_policies(document_type);
CREATE INDEX idx_doc_retention_active ON gold_document_retention_policies(is_active);
CREATE INDEX idx_doc_retention_effective ON gold_document_retention_policies(effective_from, effective_to);

-- ============================================================================
-- 11. DOCUMENT SHARES TABLE
-- ============================================================================
CREATE TABLE gold_document_shares (
    share_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES gold_documents(document_id),
    share_token VARCHAR(100) NOT NULL UNIQUE,
    share_type VARCHAR(20) NOT NULL, -- 'internal', 'external', 'public'
    shared_with_user_id UUID,
    shared_with_email VARCHAR(255),
    permissions JSONB NOT NULL, -- {can_view, can_download, can_edit, can_share}
    access_count INTEGER NOT NULL DEFAULT 0,
    max_access_count INTEGER, -- Limit number of accesses
    expires_at TIMESTAMP,
    is_password_protected BOOLEAN NOT NULL DEFAULT FALSE,
    password_hash VARCHAR(255),
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMP,
    revoked_by UUID,
    revocation_reason TEXT,
    shared_by UUID NOT NULL,
    shared_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_shares_document ON gold_document_shares(document_id);
CREATE INDEX idx_doc_shares_token ON gold_document_shares(share_token);
CREATE INDEX idx_doc_shares_user ON gold_document_shares(shared_with_user_id);
CREATE INDEX idx_doc_shares_active ON gold_document_shares(is_revoked, expires_at);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Document Repository Overview
CREATE VIEW vw_gold_document_repository AS
SELECT 
    d.document_id,
    d.document_number,
    d.document_name,
    d.entity_type,
    d.entity_id,
    dc.category_name,
    d.file_name,
    d.file_extension,
    ROUND(d.file_size_bytes / 1024.0 / 1024.0, 2) as file_size_mb,
    d.current_version,
    d.ocr_status,
    d.is_signed,
    d.signature_status,
    d.access_level,
    d.retention_until,
    d.is_archived,
    d.tags,
    COALESCE(
        (SELECT COUNT(*) FROM gold_document_versions dv WHERE dv.document_id = d.document_id),
        0
    ) as total_versions,
    COALESCE(
        (SELECT COUNT(*) FROM gold_document_access_logs dal 
         WHERE dal.document_id = d.document_id AND dal.action_type = 'view'),
        0
    ) as view_count,
    COALESCE(
        (SELECT COUNT(*) FROM gold_document_access_logs dal 
         WHERE dal.document_id = d.document_id AND dal.action_type = 'download'),
        0
    ) as download_count,
    (SELECT approval_status FROM gold_document_approvals da 
     WHERE da.document_id = d.document_id 
     ORDER BY da.created_at DESC LIMIT 1) as latest_approval_status,
    d.created_by,
    d.created_at,
    d.updated_at
FROM gold_documents d
LEFT JOIN gold_document_categories dc ON d.category_id = dc.category_id
WHERE d.is_deleted = FALSE;

-- View: Pending Document Approvals
CREATE VIEW vw_gold_pending_document_approvals AS
SELECT 
    da.approval_id,
    da.approval_number,
    d.document_id,
    d.document_number,
    d.document_name,
    dc.category_name,
    w.workflow_name,
    da.current_step,
    da.total_steps,
    da.approval_status,
    da.priority,
    da.assigned_to,
    da.due_date,
    CASE 
        WHEN da.due_date < CURRENT_TIMESTAMP THEN 'overdue'
        WHEN da.due_date < CURRENT_TIMESTAMP + INTERVAL '1 day' THEN 'due_soon'
        ELSE 'on_track'
    END as urgency_status,
    da.is_escalated,
    da.initiated_by,
    da.initiated_at,
    da.created_at
FROM gold_document_approvals da
INNER JOIN gold_documents d ON da.document_id = d.document_id
INNER JOIN gold_document_categories dc ON d.category_id = dc.category_id
INNER JOIN gold_document_workflows w ON da.workflow_id = w.workflow_id
WHERE da.approval_status IN ('pending', 'in_progress')
AND d.is_deleted = FALSE;

-- View: Document Access Analytics
CREATE VIEW vw_gold_document_access_analytics AS
SELECT 
    d.document_id,
    d.document_number,
    d.document_name,
    dc.category_name,
    COUNT(dal.log_id) as total_accesses,
    COUNT(DISTINCT dal.user_id) as unique_users,
    COUNT(CASE WHEN dal.action_type = 'view' THEN 1 END) as view_count,
    COUNT(CASE WHEN dal.action_type = 'download' THEN 1 END) as download_count,
    COUNT(CASE WHEN dal.action_type = 'update' THEN 1 END) as update_count,
    COUNT(CASE WHEN dal.access_result = 'denied' THEN 1 END) as denied_count,
    MAX(dal.accessed_at) as last_accessed_at,
    SUM(COALESCE(dal.download_size_bytes, 0)) as total_downloaded_bytes
FROM gold_documents d
LEFT JOIN gold_document_categories dc ON d.category_id = dc.category_id
LEFT JOIN gold_document_access_logs dal ON d.document_id = dal.document_id
WHERE d.is_deleted = FALSE
GROUP BY d.document_id, d.document_number, d.document_name, dc.category_name;

-- View: Document Retention Status
CREATE VIEW vw_gold_document_retention_status AS
SELECT 
    d.document_id,
    d.document_number,
    d.document_name,
    dc.category_name,
    d.retention_until,
    CASE 
        WHEN d.is_archived THEN 'archived'
        WHEN d.retention_until IS NULL THEN 'no_policy'
        WHEN d.retention_until < CURRENT_DATE THEN 'expired'
        WHEN d.retention_until < CURRENT_DATE + INTERVAL '30 days' THEN 'expiring_soon'
        ELSE 'active'
    END as retention_status,
    CASE 
        WHEN d.retention_until IS NOT NULL THEN 
            d.retention_until - CURRENT_DATE
        ELSE NULL
    END as days_until_expiry,
    drp.policy_name,
    drp.retention_period_days,
    drp.delete_after_retention,
    d.created_at,
    d.is_archived,
    d.archived_at
FROM gold_documents d
LEFT JOIN gold_document_categories dc ON d.category_id = dc.category_id
LEFT JOIN gold_document_retention_policies drp ON d.category_id = drp.category_id
WHERE d.is_deleted = FALSE;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Update document version count
CREATE OR REPLACE FUNCTION update_document_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Update current version in documents table
    UPDATE gold_documents 
    SET current_version = NEW.version_number,
        updated_at = CURRENT_TIMESTAMP
    WHERE document_id = NEW.document_id;
    
    -- Mark previous version as not current
    UPDATE gold_document_versions
    SET is_current = FALSE
    WHERE document_id = NEW.document_id 
    AND version_id != NEW.version_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_document_version
AFTER INSERT ON gold_document_versions
FOR EACH ROW
EXECUTE FUNCTION update_document_version();

-- Trigger: Update tag usage count
CREATE OR REPLACE FUNCTION update_tag_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE gold_document_tags 
        SET usage_count = usage_count + 1
        WHERE tag_id = NEW.tag_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE gold_document_tags 
        SET usage_count = usage_count - 1
        WHERE tag_id = OLD.tag_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_tag_usage_count
AFTER INSERT OR DELETE ON gold_document_tag_mappings
FOR EACH ROW
EXECUTE FUNCTION update_tag_usage_count();

-- Trigger: Update template usage count
CREATE OR REPLACE FUNCTION update_template_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE gold_document_templates
    SET usage_count = usage_count + 1,
        last_used_at = CURRENT_TIMESTAMP
    WHERE template_id = NEW.template_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- This trigger would be called from application layer when template is used

-- Trigger: Auto-apply retention policy
CREATE OR REPLACE FUNCTION apply_retention_policy()
RETURNS TRIGGER AS $$
DECLARE
    v_policy RECORD;
BEGIN
    -- Find applicable retention policy
    SELECT * INTO v_policy
    FROM gold_document_retention_policies
    WHERE (category_id = NEW.category_id OR category_id IS NULL)
    AND (document_type = NEW.document_type OR document_type IS NULL)
    AND is_active = TRUE
    AND effective_from <= CURRENT_DATE
    AND (effective_to IS NULL OR effective_to >= CURRENT_DATE)
    AND auto_apply = TRUE
    ORDER BY priority DESC, category_id DESC NULLS LAST
    LIMIT 1;
    
    IF FOUND THEN
        NEW.retention_until := CASE v_policy.retention_trigger
            WHEN 'from_creation' THEN CURRENT_DATE + (v_policy.retention_period_days || ' days')::INTERVAL
            ELSE NULL -- Other triggers handled by application
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_apply_retention_policy
BEFORE INSERT ON gold_documents
FOR EACH ROW
EXECUTE FUNCTION apply_retention_policy();

-- Trigger: Update timestamps
CREATE OR REPLACE FUNCTION update_document_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_document_timestamp
BEFORE UPDATE ON gold_documents
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

CREATE TRIGGER trg_update_category_timestamp
BEFORE UPDATE ON gold_document_categories
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

CREATE TRIGGER trg_update_template_timestamp
BEFORE UPDATE ON gold_document_templates
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

CREATE TRIGGER trg_update_workflow_timestamp
BEFORE UPDATE ON gold_document_workflows
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

CREATE TRIGGER trg_update_approval_timestamp
BEFORE UPDATE ON gold_document_approvals
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

CREATE TRIGGER trg_update_tag_timestamp
BEFORE UPDATE ON gold_document_tags
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

CREATE TRIGGER trg_update_metadata_timestamp
BEFORE UPDATE ON gold_document_metadata
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

CREATE TRIGGER trg_update_policy_timestamp
BEFORE UPDATE ON gold_document_retention_policies
FOR EACH ROW
EXECUTE FUNCTION update_document_timestamp();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Document Categories
INSERT INTO gold_document_categories (category_code, category_name, description, parent_category_id, category_level, is_system_category, retention_period_days, is_mandatory, allowed_extensions, max_file_size_mb, requires_approval, requires_ocr, display_order, created_by) VALUES
('DOC_KYC', 'KYC Documents', 'Customer identification and verification documents', NULL, 1, TRUE, 2555, TRUE, ARRAY['pdf', 'jpg', 'jpeg', 'png'], 10, FALSE, TRUE, 1, '00000000-0000-0000-0000-000000000000'),
('DOC_LOAN', 'Loan Documents', 'Loan application and agreement documents', NULL, 1, TRUE, 2555, TRUE, ARRAY['pdf', 'docx'], 20, TRUE, TRUE, 2, '00000000-0000-0000-0000-000000000000'),
('DOC_PLEDGE', 'Pledge Documents', 'Gold pledge receipts and valuation reports', NULL, 1, TRUE, 2555, TRUE, ARRAY['pdf'], 15, TRUE, TRUE, 3, '00000000-0000-0000-0000-000000000000'),
('DOC_VALUATION', 'Valuation Reports', 'Gold valuation and assessment reports', NULL, 1, TRUE, 1825, TRUE, ARRAY['pdf', 'xlsx'], 10, TRUE, FALSE, 4, '00000000-0000-0000-0000-000000000000'),
('DOC_REPAYMENT', 'Repayment Documents', 'Repayment receipts and statements', NULL, 1, TRUE, 2555, FALSE, ARRAY['pdf'], 5, FALSE, FALSE, 5, '00000000-0000-0000-0000-000000000000'),
('DOC_COLLECTION', 'Collection Documents', 'Collection notices and legal documents', NULL, 1, TRUE, 3650, FALSE, ARRAY['pdf', 'docx'], 10, TRUE, TRUE, 6, '00000000-0000-0000-0000-000000000000'),
('DOC_AUDIT', 'Audit Documents', 'Internal and external audit reports', NULL, 1, TRUE, 2555, FALSE, ARRAY['pdf', 'xlsx'], 20, TRUE, FALSE, 7, '00000000-0000-0000-0000-000000000000'),
('DOC_COMPLIANCE', 'Compliance Documents', 'Regulatory and compliance reports', NULL, 1, TRUE, 3650, TRUE, ARRAY['pdf'], 15, TRUE, FALSE, 8, '00000000-0000-0000-0000-000000000000'),
('DOC_INSURANCE', 'Insurance Documents', 'Insurance policies and claims', NULL, 1, TRUE, 2555, FALSE, ARRAY['pdf'], 10, FALSE, TRUE, 9, '00000000-0000-0000-0000-000000000000'),
('DOC_GENERAL', 'General Documents', 'Miscellaneous documents', NULL, 1, FALSE, 1095, FALSE, ARRAY['pdf', 'docx', 'xlsx', 'jpg', 'png'], 10, FALSE, FALSE, 10, '00000000-0000-0000-0000-000000000000');

-- Document Tags
INSERT INTO gold_document_tags (tag_name, tag_category, tag_color, description, is_system_tag, created_by) VALUES
('urgent', 'priority', '#FF0000', 'Urgent documents requiring immediate attention', TRUE, '00000000-0000-0000-0000-000000000000'),
('verified', 'status', '#00FF00', 'Documents that have been verified', TRUE, '00000000-0000-0000-0000-000000000000'),
('pending_review', 'status', '#FFA500', 'Documents pending review', TRUE, '00000000-0000-0000-0000-000000000000'),
('confidential', 'security', '#800080', 'Confidential documents with restricted access', TRUE, '00000000-0000-0000-0000-000000000000'),
('archived', 'status', '#808080', 'Archived documents', TRUE, '00000000-0000-0000-0000-000000000000'),
('legal', 'department', '#0000FF', 'Legal department documents', FALSE, '00000000-0000-0000-0000-000000000000'),
('operations', 'department', '#00FFFF', 'Operations department documents', FALSE, '00000000-0000-0000-0000-000000000000'),
('finance', 'department', '#FFFF00', 'Finance department documents', FALSE, '00000000-0000-0000-0000-000000000000');

