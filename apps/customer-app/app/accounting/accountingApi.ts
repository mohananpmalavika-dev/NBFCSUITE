export const ACCOUNTING_API_BASE = process.env.NEXT_PUBLIC_ACCOUNTING_API_URL ?? 'http://localhost:8008';
export const DEFAULT_ACCOUNTING_TENANT = process.env.NEXT_PUBLIC_ACCOUNTING_TENANT_ID ?? 'tenant-local-accounting';

export function accountingApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${ACCOUNTING_API_BASE}${normalizedPath}`;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(accountingApiUrl(path));
  if (!response.ok) {
    throw new Error(`Accounting API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(accountingApiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Accounting API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function putJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(accountingApiUrl(path), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Accounting API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function patchJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(accountingApiUrl(path), {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Accounting API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export interface GLAccount {
  id: string;
  tenant_id: string;
  gl_code: string;
  account_code: string;
  name: string;
  account_name: string;
  short_name?: string | null;
  account_type: string;
  category?: string | null;
  parent_account_id?: string | null;
  posting_allowed?: string | null;
  allow_manual_posting?: string | null;
  allow_auto_posting?: string | null;
  requires_approval?: string | null;
  freeze_status?: string | null;
  currency?: string | null;
  base_currency?: string | null;
  normal_balance?: string | null;
  opening_balance?: number | null;
  balance?: number | null;
  financial_year?: string | null;
  branch_id?: string | null;
  status?: string | null;
  child_count?: number;
  dimensions?: string[];
  reporting?: Record<string, unknown>;
  tax?: Record<string, unknown>;
  product?: Record<string, unknown>;
  workflow?: Record<string, unknown>;
  security?: Record<string, unknown>;
  ai?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface GLAccountPayload {
  tenant_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  parent_account_id?: string | null;
  category?: string | null;
  currency?: string | null;
  base_currency?: string | null;
  normal_balance?: string | null;
  posting_allowed?: string | null;
  allow_manual_posting?: string | null;
  allow_auto_posting?: string | null;
  requires_approval?: string | null;
  freeze_status?: string | null;
  status?: string | null;
  opening_balance?: number | null;
  financial_year?: string | null;
  metadata?: Record<string, unknown>;
}

export interface GLAccountListResponse {
  tenant_id: string;
  total: number;
  items: GLAccount[];
}

export interface GLTreeNode {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  category?: string | null;
  currency?: string | null;
  posting_allowed?: string | null;
  freeze_status?: string | null;
  status?: string | null;
  balance?: number | null;
  children: GLTreeNode[];
}

export interface GLTreeResponse {
  tenant_id: string;
  items: GLTreeNode[];
}

export interface GLDashboard {
  tenant_id: string;
  kpis: {
    total_accounts: number;
    active_accounts: number;
    control_accounts: number;
    posting_accounts: number;
    parent_accounts: number;
    inactive_accounts: number;
    pending_approvals: number;
    ai_health: number;
  };
  charts: {
    accounts_by_type: Array<{ label: string; value: number }>;
    accounts_by_category: Array<{ label: string; value: number }>;
    accounts_by_status: Array<{ label: string; value: number }>;
  };
  summary: {
    status: string;
    message: string;
  };
}

export interface GLUsageResponse {
  tenant_id: string;
  account: GLAccount;
  summary: {
    transaction_count: number;
    total_debit: number;
    total_credit: number;
    net_movement: number;
    last_activity?: string | null;
    ai_summary: string;
  };
  source_modules: Array<{ source_module: string; amount: number }>;
  recent_lines: Array<Record<string, unknown>>;
}

function tenantParam(tenantId = DEFAULT_ACCOUNTING_TENANT) {
  return `tenant_id=${encodeURIComponent(tenantId)}`;
}

export const accountingApi = {
  getDashboard: (tenantId = DEFAULT_ACCOUNTING_TENANT) => getJson<GLDashboard>(`/api/v1/gl/dashboard?${tenantParam(tenantId)}`),
  listAccounts: (tenantId = DEFAULT_ACCOUNTING_TENANT, params = '') =>
    getJson<GLAccountListResponse>(`/api/v1/gl/accounts?${tenantParam(tenantId)}${params ? `&${params}` : ''}`),
  getAccount: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<GLAccount>(`/api/v1/gl/accounts/${id}?${tenantParam(tenantId)}`),
  createAccount: (payload: GLAccountPayload) => postJson<GLAccount>('/api/v1/gl/accounts', payload),
  updateAccount: (id: string, tenantId: string, payload: Partial<GLAccountPayload>) =>
    putJson<GLAccount>(`/api/v1/gl/accounts/${id}?${tenantParam(tenantId)}`, payload),
  setAccountStatus: (id: string, tenantId: string, status: string) =>
    patchJson<GLAccount>(`/api/v1/gl/accounts/${id}/status`, { tenant_id: tenantId, status }),
  getTree: (tenantId = DEFAULT_ACCOUNTING_TENANT) => getJson<GLTreeResponse>(`/api/v1/gl/accounts/tree?${tenantParam(tenantId)}`),
  searchAccounts: (tenantId = DEFAULT_ACCOUNTING_TENANT, query = '') =>
    getJson<{ tenant_id: string; query: string; items: GLAccount[] }>(`/api/v1/gl/accounts/search?${tenantParam(tenantId)}&q=${encodeURIComponent(query)}`),
  getUsage: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<GLUsageResponse>(`/api/v1/gl/accounts/${id}/usage?${tenantParam(tenantId)}`),
  seedDefaults: (tenantId = DEFAULT_ACCOUNTING_TENANT, currency = 'INR', financialYear = '2026-27') =>
    postJson<{ tenant_id: string; created: string[]; created_count: number }>('/api/v1/gl/accounts/seed-defaults', {
      tenant_id: tenantId,
      currency,
      financial_year: financialYear,
    }),
};
