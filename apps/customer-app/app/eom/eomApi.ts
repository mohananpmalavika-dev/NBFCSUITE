export const EOM_API_BASE = process.env.NEXT_PUBLIC_EOM_API_URL ?? 'http://localhost:8002';

export function eomApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${EOM_API_BASE}${normalizedPath}`;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(eomApiUrl(path));
  if (!response.ok) {
    throw new Error(`EOM API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, payload: unknown, headers?: Record<string, string>): Promise<T> {
  const response = await fetch(eomApiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`EOM API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function putJson<T>(path: string, payload: unknown, headers?: Record<string, string>): Promise<T> {
  const response = await fetch(eomApiUrl(path), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`EOM API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function patchJson<T>(path: string, payload: unknown, headers?: Record<string, string>): Promise<T> {
  const response = await fetch(eomApiUrl(path), {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...(headers ?? {}) },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`EOM API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export type FinanceStatus = 'draft' | 'active' | 'inactive';
export type InternalOrderStatus = 'draft' | 'approved' | 'open' | 'active' | 'closed' | 'archived';
export type BudgetStatus = 'original' | 'revised' | 'forecast' | 'actual';

export interface FinanceListResponse<T> {
  total: number;
  items: T[];
}

export interface CostCenter {
  id: string;
  enterprise_id?: string | null;
  code: string;
  name: string;
  category?: string | null;
  status: FinanceStatus;
  description?: string | null;
  parent_cost_center_id?: string | null;
  budget_owner?: string | null;
  currency?: string | null;
  gl_mapping?: string | null;
  department_id?: string | null;
}

export type CostCenterPayload = Omit<CostCenter, 'id'>;

export interface ProfitCenter {
  id: string;
  enterprise_id?: string | null;
  code: string;
  name: string;
  category?: string | null;
  status: FinanceStatus;
  description?: string | null;
  parent_profit_center_id?: string | null;
  responsibility_owner?: string | null;
  currency?: string | null;
  gl_mapping?: string | null;
  branch_id?: string | null;
}

export type ProfitCenterPayload = Omit<ProfitCenter, 'id'>;

export interface Budget {
  id: string;
  enterprise_id?: string | null;
  budget_center_id?: string | null;
  cost_center_id?: string | null;
  profit_center_id?: string | null;
  year: number;
  status: BudgetStatus;
  original_total?: number | null;
  revised_total?: number | null;
  committed_total?: number | null;
  actual_total?: number | null;
  forecast_total?: number | null;
  currency?: string | null;
}

export type BudgetPayload = Omit<Budget, 'id'>;

export interface InternalOrder {
  id: string;
  enterprise_id?: string | null;
  code: string;
  name: string;
  description?: string | null;
  status: InternalOrderStatus;
  cost_center_id?: string | null;
  profit_center_id?: string | null;
  budget_center_id?: string | null;
  responsibility_center_id?: string | null;
  investment_center_id?: string | null;
}

export type InternalOrderPayload = Omit<InternalOrder, 'id'>;

export interface FinanceDashboard {
  kpis: {
    cost_centers: number;
    profit_centers: number;
    budgets: number;
    internal_orders: number;
    health_score: number;
    health_rating: string;
  };
  summary: {
    status: string;
  };
}

export interface Enterprise {
  id: string;
  code: string;
  name: string;
  display_name?: string | null;
  short_name?: string | null;
  status: string;
  currency_code?: string | null;
  timezone?: string | null;
  language?: string | null;
  fiscal_year_start?: string | null;
  description?: string | null;
}

export interface EnterpriseProfile {
  enterprise: Enterprise;
  branding: Record<string, string | null>;
  legal: Record<string, string | null>;
  finance: Record<string, string | null>;
  localization: Record<string, string | null>;
  contact: Record<string, string | null>;
  compliance: Record<string, string | boolean | null>;
  integrations: Array<{ integration_type: string; provider?: string | null; status: string }>;
  documents: Array<{ document_type: string; name: string; status: string; ocr_metadata?: string | null }>;
  settings: Array<{ setting_group: string; setting_key: string; setting_value?: string | null; inherited: boolean }>;
}

export interface EnterpriseProfileResponse extends EnterpriseProfile {
  health?: {
    score: number;
    status: string;
    passed?: string[];
    missing?: string[];
  };
}

export const enterpriseApi = {
  getEnterprise: (id: string) => getJson<Enterprise>(`/eom/enterprises/${id}`),
  getEnterpriseProfile: (id: string) => getJson<EnterpriseProfile>(`/eom/enterprises/${id}/profile`),
  patchEnterprise: (id: string, payload: Partial<Enterprise>) => patchJson<Enterprise>(`/eom/enterprises/${id}`, payload, { 'X-User-Roles': 'enterprise.admin' }),
  updateEnterpriseProfile: (id: string, payload: EnterpriseProfile) => putJson<EnterpriseProfileResponse>(`/eom/enterprises/${id}/profile`, payload, { 'X-User-Roles': 'enterprise.admin' }),
};

export const financeApi = {
  getDashboard: () => getJson<FinanceDashboard>('/api/v1/finance/dashboard'),
  listCostCenters: () => getJson<FinanceListResponse<CostCenter>>('/api/v1/finance/cost-centers'),
  getCostCenter: (id: string) => getJson<CostCenter>(`/api/v1/finance/cost-centers/${id}`),
  createCostCenter: (payload: CostCenterPayload) => postJson<CostCenter>('/api/v1/finance/cost-centers', payload),
  updateCostCenter: (id: string, payload: Partial<CostCenterPayload>) => putJson<CostCenter>(`/api/v1/finance/cost-centers/${id}`, payload),
  setCostCenterStatus: (id: string, status: FinanceStatus) => patchJson<{ id: string; status: FinanceStatus }>(`/api/v1/finance/cost-centers/${id}/status`, { status }),

  listProfitCenters: () => getJson<FinanceListResponse<ProfitCenter>>('/api/v1/finance/profit-centers'),
  getProfitCenter: (id: string) => getJson<ProfitCenter>(`/api/v1/finance/profit-centers/${id}`),
  createProfitCenter: (payload: ProfitCenterPayload) => postJson<ProfitCenter>('/api/v1/finance/profit-centers', payload),
  updateProfitCenter: (id: string, payload: Partial<ProfitCenterPayload>) => putJson<ProfitCenter>(`/api/v1/finance/profit-centers/${id}`, payload),
  setProfitCenterStatus: (id: string, status: FinanceStatus) => patchJson<{ id: string; status: FinanceStatus }>(`/api/v1/finance/profit-centers/${id}/status`, { status }),

  listBudgets: () => getJson<FinanceListResponse<Budget>>('/api/v1/finance/budgets'),
  getBudget: (id: string) => getJson<Budget>(`/api/v1/finance/budgets/${id}`),
  createBudget: (payload: BudgetPayload) => postJson<Budget>('/api/v1/finance/budgets', payload),
  updateBudget: (id: string, payload: Partial<BudgetPayload>) => putJson<Budget>(`/api/v1/finance/budgets/${id}`, payload),

  listInternalOrders: () => getJson<FinanceListResponse<InternalOrder>>('/api/v1/finance/internal-orders'),
  getInternalOrder: (id: string) => getJson<InternalOrder>(`/api/v1/finance/internal-orders/${id}`),
  createInternalOrder: (payload: InternalOrderPayload) => postJson<InternalOrder>('/api/v1/finance/internal-orders', payload),
  updateInternalOrder: (id: string, payload: Partial<InternalOrderPayload>) => putJson<InternalOrder>(`/api/v1/finance/internal-orders/${id}`, payload),
  setInternalOrderStatus: (id: string, status: InternalOrderStatus) => patchJson<{ id: string; status: InternalOrderStatus }>(`/api/v1/finance/internal-orders/${id}/status`, { status }),

  listAllocations: () => getJson<FinanceListResponse<unknown>>('/api/v1/finance/allocations'),
  executeAllocation: (payload: unknown) => postJson<{ executed: boolean; message: string; payload: unknown }>('/api/v1/finance/allocations', payload),
};
