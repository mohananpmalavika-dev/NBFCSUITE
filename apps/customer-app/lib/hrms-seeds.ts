// HRMS Department Seed Data - Phase 1
// Used for pre-populating 16 core departments with hierarchy

export const DEPARTMENT_SEEDS = [
  // Core Business Departments
  {
    department_code: 'HR',
    department_name: 'Human Resources',
    parent_department_id: null,
    cost_center_code: 'CC-HR-001',
    profit_center_code: 'PC-ADMIN-001',
    annual_budget: 5000000,
  },
  {
    department_code: 'FIN',
    department_name: 'Finance',
    parent_department_id: null,
    cost_center_code: 'CC-FIN-001',
    profit_center_code: 'PC-ADMIN-001',
    annual_budget: 8000000,
  },
  {
    department_code: 'OPS',
    department_name: 'Operations',
    parent_department_id: null,
    cost_center_code: 'CC-OPS-001',
    profit_center_code: 'PC-OPS-001',
    annual_budget: 12000000,
  },

  // Lending & Collections (under OPS)
  {
    department_code: 'LOS',
    department_name: 'Loan Origination System',
    parent_department_id: 'OPS',
    cost_center_code: 'CC-LOS-001',
    profit_center_code: 'PC-LENDING-001',
    annual_budget: 15000000,
  },
  {
    department_code: 'GOLD',
    department_name: 'Gold Loan',
    parent_department_id: 'OPS',
    cost_center_code: 'CC-GOLD-001',
    profit_center_code: 'PC-LENDING-002',
    annual_budget: 10000000,
  },
  {
    department_code: 'COL',
    department_name: 'Collections',
    parent_department_id: 'OPS',
    cost_center_code: 'CC-COL-001',
    profit_center_code: 'PC-COLLECTIONS-001',
    annual_budget: 8000000,
  },

  // Banking & Treasury
  {
    department_code: 'DEP',
    department_name: 'Deposits',
    parent_department_id: 'OPS',
    cost_center_code: 'CC-DEP-001',
    profit_center_code: 'PC-DEPOSITS-001',
    annual_budget: 12000000,
  },
  {
    department_code: 'TREAS',
    department_name: 'Treasury & Forex',
    parent_department_id: 'FIN',
    cost_center_code: 'CC-TREAS-001',
    profit_center_code: 'PC-TREASURY-001',
    annual_budget: 5000000,
  },

  // Support & Compliance
  {
    department_code: 'IT',
    department_name: 'Information Technology',
    parent_department_id: null,
    cost_center_code: 'CC-IT-001',
    profit_center_code: 'PC-ADMIN-001',
    annual_budget: 20000000,
  },
  {
    department_code: 'LEGAL',
    department_name: 'Legal',
    parent_department_id: 'HR',
    cost_center_code: 'CC-LEGAL-001',
    profit_center_code: 'PC-ADMIN-001',
    annual_budget: 4000000,
  },
  {
    department_code: 'AUDIT',
    department_name: 'Audit & Assurance',
    parent_department_id: 'FIN',
    cost_center_code: 'CC-AUDIT-001',
    profit_center_code: 'PC-ADMIN-001',
    annual_budget: 6000000,
  },
  {
    department_code: 'RISK',
    department_name: 'Risk Management',
    parent_department_id: null,
    cost_center_code: 'CC-RISK-001',
    profit_center_code: 'PC-ADMIN-001',
    annual_budget: 7000000,
  },
  {
    department_code: 'COMP',
    department_name: 'Compliance',
    parent_department_id: 'RISK',
    cost_center_code: 'CC-COMP-001',
    profit_center_code: 'PC-ADMIN-001',
    annual_budget: 5000000,
  },

  // Business Development
  {
    department_code: 'PROC',
    department_name: 'Procurement',
    parent_department_id: 'OPS',
    cost_center_code: 'CC-PROC-001',
    profit_center_code: 'PC-OPS-001',
    annual_budget: 6000000,
  },
  {
    department_code: 'MKT',
    department_name: 'Marketing',
    parent_department_id: null,
    cost_center_code: 'CC-MKT-001',
    profit_center_code: 'PC-REVENUE-001',
    annual_budget: 10000000,
  },
];

export function getDepartmentParentName(parentCode: string | null): string {
  if (!parentCode) return 'Root';
  const parent = DEPARTMENT_SEEDS.find((d) => d.department_code === parentCode);
  return parent?.department_name || 'Unknown';
}

export function getDepartmentLevel(code: string, visited = new Set<string>()): number {
  if (visited.has(code)) return 0;
  visited.add(code);

  const dept = DEPARTMENT_SEEDS.find((d) => d.department_code === code);
  if (!dept || !dept.parent_department_id) return 0;
  return 1 + getDepartmentLevel(dept.parent_department_id, visited);
}

export function getDepartmentHierarchy(departments: Array<{ department_code: string; parent_department_id?: string | null }>) {
  const byCode = new Map(departments.map((d) => [d.department_code, d]));
  const roots: typeof departments = [];
  const children = new Map<string, typeof departments>();

  for (const dept of departments) {
    if (!dept.parent_department_id) {
      roots.push(dept);
    } else {
      const parentCode = typeof dept.parent_department_id === 'string' ? dept.parent_department_id : null;
      if (parentCode && !children.has(parentCode)) {
        children.set(parentCode, []);
      }
      if (parentCode) {
        children.get(parentCode)!.push(dept);
      }
    }
  }

  return { roots, children, byCode };
}
