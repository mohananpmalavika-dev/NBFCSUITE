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

export interface FinancialYear {
  id: string;
  tenant_id: string;
  year_code: string;
  description?: string | null;
  start_date: string;
  end_date: string;
  calendar_type: string;
  status: string;
  calendars: string[];
  close_schedule: Record<string, unknown>;
  created_by?: string | null;
  activated_by?: string | null;
  created_at: string;
  updated_at: string;
}

export interface FinancialYearPayload {
  tenant_id: string;
  year_code: string;
  description?: string;
  start_date: string;
  end_date: string;
  calendar_type?: string;
  status?: string;
  calendars?: string[];
  close_schedule?: Record<string, unknown>;
  generate_periods?: string;
  performed_by?: string;
}

export interface AccountingPeriod {
  id: string;
  tenant_id: string;
  financial_year: string;
  period_name: string;
  period_start: string;
  period_end: string;
  branch_id?: string | null;
  status: string;
  state: string;
  locked_by?: string | null;
  unlocked_by?: string | null;
  approved_by?: string | null;
  unlock_requested_by?: string | null;
  lock_reason?: string | null;
  unlock_reason?: string | null;
  posting_window: {
    posting_allowed_from: string;
    posting_allowed_to: string;
    late_adjustments_allowed: boolean;
  };
  close_checklist: Array<{ key: string; label: string; status: string }>;
  ai: {
    close_readiness: number;
    delay_prediction: string;
    recommendation: string;
  };
  created_at: string;
  updated_at: string;
}

export interface CalendarDashboard {
  tenant_id: string;
  current_financial_year?: FinancialYear | null;
  kpis: {
    current_financial_year: string;
    open_periods: number;
    closed_periods: number;
    pending_eod: number;
    pending_eom: number;
    pending_eoy: number;
    late_journals: number;
    calendar_exceptions: number;
    calendar_health: number;
  };
  charts: {
    period_status: Array<{ label: string; value: number }>;
    close_progress: Array<{ label: string; value: number }>;
    closing_sla: Array<{ label: string; value: number }>;
  };
  summary: {
    status: string;
    message: string;
  };
}

export interface EodMonitor {
  tenant_id: string;
  branch_id?: string | null;
  business_day: {
    date: string;
    status: string;
    lifecycle: string[];
  };
  items: Array<Record<string, unknown>>;
}

export interface AccountingEvent {
  id: string;
  event_id: string;
  tenant_id: string;
  event_type: string;
  source_module: string;
  reference_id: string;
  reference_number?: string | null;
  business_date: string;
  currency: string;
  amount?: number | null;
  priority: string;
  status: string;
  queue_status: string;
  validation_status: string;
  validation_result?: {
    status: string;
    errors: string[];
    warnings: string[];
    checks: Array<{ key: string; label: string; status: string; detail?: string | null }>;
    normalized_source_module?: string;
    normalized_source_event?: string;
    posting_rule_id?: string | null;
    processing_time_ms?: number;
  } | null;
  dimensions: Record<string, unknown>;
  payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
  version: number;
  retry_count: number;
  next_retry_at?: string | null;
  dead_letter_reason?: string | null;
  posting_rule_id?: string | null;
  posting_execution_id?: string | null;
  journal_id?: string | null;
  processing_time_ms: number;
  created_by?: string | null;
  approved_by?: string | null;
  created_at: string;
  updated_at: string;
  posted_at?: string | null;
  business_view?: Record<string, unknown>;
  processing_view?: Record<string, unknown>;
  financial_view?: Record<string, unknown>;
  audit_view?: Record<string, unknown>;
  ai_view?: Record<string, unknown>;
}

export interface AccountingEventPayload {
  tenant_id: string;
  event_type: string;
  source_module: string;
  reference_id: string;
  reference_number?: string;
  business_date?: string;
  currency?: string;
  amount?: number;
  priority?: string;
  dimensions?: Record<string, unknown>;
  payload?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  created_by?: string;
}

export interface EventDashboard {
  tenant_id: string;
  kpis: {
    todays_events: number;
    pending: number;
    failed: number;
    posted: number;
    average_processing_time_ms: number;
    retry_queue: number;
    dead_letter_queue: number;
    event_health: number;
  };
  charts: {
    events_by_module: Array<{ label: string; value: number }>;
    events_by_status: Array<{ label: string; value: number }>;
    success_rate: Array<{ label: string; value: number }>;
    failure_analysis: Array<{ label: string; value: number }>;
  };
  monitoring: {
    queue_size: number;
    average_latency_ms: number;
    throughput: number;
    success_percent: number;
    error_percent: number;
    retry_count: number;
  };
  summary: {
    status: string;
    message: string;
  };
}

export interface EventListResponse {
  tenant_id: string;
  total: number;
  items: AccountingEvent[];
}

export interface EventQueueResponse {
  tenant_id: string;
  queue_status?: string | null;
  counts: Record<string, number>;
  items: AccountingEvent[];
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
  getCalendarDashboard: (tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<CalendarDashboard>(`/api/v1/accounting/calendar/dashboard?${tenantParam(tenantId)}`),
  listFinancialYears: (tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<{ tenant_id: string; items: FinancialYear[] }>(`/api/v1/accounting/calendar/years?${tenantParam(tenantId)}`),
  createFinancialYear: (payload: FinancialYearPayload) =>
    postJson<{ financial_year: FinancialYear; generated_periods: AccountingPeriod[]; generated_count: number }>('/api/v1/accounting/calendar/years', payload),
  listPeriods: (tenantId = DEFAULT_ACCOUNTING_TENANT, financialYear = '') =>
    getJson<{ tenant_id: string; items: AccountingPeriod[] }>(
      `/api/v1/accounting/calendar/periods?${tenantParam(tenantId)}${financialYear ? `&financial_year=${encodeURIComponent(financialYear)}` : ''}`,
    ),
  setPeriodState: (periodId: string, tenantId: string, action: 'open' | 'soft-close' | 'hard-close' | 'reopen', reason?: string) =>
    postJson<AccountingPeriod>(`/api/v1/accounting/calendar/periods/${periodId}/${action}`, {
      tenant_id: tenantId,
      performed_by: 'finance-console',
      reason,
    }),
  getEodMonitor: (tenantId = DEFAULT_ACCOUNTING_TENANT, branchId = '') =>
    getJson<EodMonitor>(`/api/v1/accounting/calendar/eod?${tenantParam(tenantId)}${branchId ? `&branch_id=${encodeURIComponent(branchId)}` : ''}`),
  executeEod: (tenantId = DEFAULT_ACCOUNTING_TENANT, businessDate = new Date().toISOString(), branchId = '') =>
    postJson<{ event: string; close: Record<string, unknown> }>('/api/v1/accounting/calendar/eod/execute', {
      tenant_id: tenantId,
      business_date: businessDate,
      branch_id: branchId || null,
      performed_by: 'finance-console',
    }),
  executeEom: (tenantId: string, periodId: string) =>
    postJson<{ event: string; period: AccountingPeriod; checklist: string[] }>('/api/v1/accounting/calendar/eom/execute', {
      tenant_id: tenantId,
      period_id: periodId,
      performed_by: 'finance-console',
    }),
  executeEoy: (tenantId: string, financialYear: string) =>
    postJson<{ event: string; financial_year: string; periods_archived: number; checklist: string[] }>('/api/v1/accounting/calendar/eoy/execute', {
      tenant_id: tenantId,
      financial_year: financialYear,
      performed_by: 'finance-console',
    }),
  getEventDashboard: (tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<EventDashboard>(`/api/v1/accounting/events/dashboard?${tenantParam(tenantId)}`),
  listEvents: (tenantId = DEFAULT_ACCOUNTING_TENANT, params = '') =>
    getJson<EventListResponse>(`/api/v1/accounting/events?${tenantParam(tenantId)}${params ? `&${params}` : ''}`),
  createEvent: (payload: AccountingEventPayload) =>
    postJson<AccountingEvent>('/api/v1/accounting/events', payload),
  getEvent: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<AccountingEvent>(`/api/v1/accounting/events/${id}?${tenantParam(tenantId)}`),
  validateEvent: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    postJson<AccountingEvent>(`/api/v1/accounting/events/${id}/validate`, { tenant_id: tenantId, performed_by: 'event-console' }),
  retryEvent: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT, reason = 'retry from console') =>
    postJson<AccountingEvent>(`/api/v1/accounting/events/${id}/retry`, { tenant_id: tenantId, performed_by: 'event-console', reason }),
  replayEvent: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT, reason = 'replay from console') =>
    postJson<AccountingEvent>(`/api/v1/accounting/events/${id}/replay`, { tenant_id: tenantId, performed_by: 'event-console', reason }),
  getEventQueue: (tenantId = DEFAULT_ACCOUNTING_TENANT, queueStatus = '') =>
    getJson<EventQueueResponse>(`/api/v1/accounting/events/queue?${tenantParam(tenantId)}${queueStatus ? `&queue_status=${encodeURIComponent(queueStatus)}` : ''}`),
};
