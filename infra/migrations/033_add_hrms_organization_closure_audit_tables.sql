-- Migration 033: Add HRMS organization closure and audit tables
-- Created: 2026-06-28

CREATE TABLE IF NOT EXISTS organization_unit_closure (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    ancestor_id VARCHAR(36) NOT NULL,
    descendant_id VARCHAR(36) NOT NULL,
    depth INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_organization_unit_closure UNIQUE (tenant_id, ancestor_id, descendant_id)
);

CREATE INDEX IF NOT EXISTS idx_organization_unit_closure_tenant_id ON organization_unit_closure(tenant_id);
CREATE INDEX IF NOT EXISTS idx_organization_unit_closure_ancestor_id ON organization_unit_closure(ancestor_id);
CREATE INDEX IF NOT EXISTS idx_organization_unit_closure_descendant_id ON organization_unit_closure(descendant_id);
CREATE INDEX IF NOT EXISTS idx_organization_unit_closure_depth ON organization_unit_closure(depth);

CREATE TABLE IF NOT EXISTS organization_unit_audit (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL,
    organization_unit_id VARCHAR(36) NOT NULL,
    action VARCHAR(50) NOT NULL,
    changed_by VARCHAR(36),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSON
);

CREATE INDEX IF NOT EXISTS idx_organization_unit_audit_tenant_id ON organization_unit_audit(tenant_id);
CREATE INDEX IF NOT EXISTS idx_organization_unit_audit_organization_unit_id ON organization_unit_audit(organization_unit_id);
CREATE INDEX IF NOT EXISTS idx_organization_unit_audit_action ON organization_unit_audit(action);
