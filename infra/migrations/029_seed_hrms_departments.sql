-- Seed HRMS Departments for Phase 1 Organization Setup
-- Creates 16 core departments with hierarchy and cost/profit center mapping

INSERT INTO hr_departments (
  id, tenant_id, department_code, department_name, 
  parent_department_id, cost_center_code, profit_center_code, 
  annual_budget, status, created_at, updated_at
) VALUES
-- Core Business Departments
('dept-hr-001', 'default', 'HR', 'Human Resources', NULL, 'CC-HR-001', 'PC-ADMIN-001', 5000000.00, 'active', NOW(), NOW()),
('dept-fin-001', 'default', 'FIN', 'Finance', NULL, 'CC-FIN-001', 'PC-ADMIN-001', 8000000.00, 'active', NOW(), NOW()),
('dept-ops-001', 'default', 'OPS', 'Operations', NULL, 'CC-OPS-001', 'PC-OPS-001', 12000000.00, 'active', NOW(), NOW()),

-- Lending & Collections Departments
('dept-los-001', 'default', 'LOS', 'Loan Origination System', 'dept-ops-001', 'CC-LOS-001', 'PC-LENDING-001', 15000000.00, 'active', NOW(), NOW()),
('dept-gold-001', 'default', 'GOLD', 'Gold Loan', 'dept-ops-001', 'CC-GOLD-001', 'PC-LENDING-002', 10000000.00, 'active', NOW(), NOW()),
('dept-col-001', 'default', 'COL', 'Collections', 'dept-ops-001', 'CC-COL-001', 'PC-COLLECTIONS-001', 8000000.00, 'active', NOW(), NOW()),

-- Banking & Treasury Departments
('dept-dep-001', 'default', 'DEP', 'Deposits', 'dept-ops-001', 'CC-DEP-001', 'PC-DEPOSITS-001', 12000000.00, 'active', NOW(), NOW()),
('dept-treas-001', 'default', 'TREAS', 'Treasury & Forex', 'dept-fin-001', 'CC-TREAS-001', 'PC-TREASURY-001', 5000000.00, 'active', NOW(), NOW()),

-- Support & Compliance Departments
('dept-it-001', 'default', 'IT', 'Information Technology', NULL, 'CC-IT-001', 'PC-ADMIN-001', 20000000.00, 'active', NOW(), NOW()),
('dept-legal-001', 'default', 'LEGAL', 'Legal', 'dept-hr-001', 'CC-LEGAL-001', 'PC-ADMIN-001', 4000000.00, 'active', NOW(), NOW()),
('dept-audit-001', 'default', 'AUDIT', 'Audit & Assurance', 'dept-fin-001', 'CC-AUDIT-001', 'PC-ADMIN-001', 6000000.00, 'active', NOW(), NOW()),
('dept-risk-001', 'default', 'RISK', 'Risk Management', NULL, 'CC-RISK-001', 'PC-ADMIN-001', 7000000.00, 'active', NOW(), NOW()),
('dept-comp-001', 'default', 'COMP', 'Compliance', 'dept-risk-001', 'CC-COMP-001', 'PC-ADMIN-001', 5000000.00, 'active', NOW(), NOW()),

-- Business Development Departments
('dept-proc-001', 'default', 'PROC', 'Procurement', 'dept-ops-001', 'CC-PROC-001', 'PC-OPS-001', 6000000.00, 'active', NOW(), NOW()),
('dept-mkt-001', 'default', 'MKT', 'Marketing', NULL, 'CC-MKT-001', 'PC-REVENUE-001', 10000000.00, 'active', NOW(), NOW());

-- Add comments for clarity
COMMENT ON TABLE hr_departments IS 'HRMS Departments with organizational hierarchy, cost centers, and profit centers for Phase 1';
