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

export interface PostingRuleLine {
  account_code: string;
  direction: 'debit' | 'credit' | string;
  description?: string | null;
  sequence?: number | null;
  amount_source?: string | null;
  percentage?: number | null;
  formula?: string | null;
  currency?: string | null;
  dimension_source?: Record<string, unknown> | null;
  transaction_currency_source?: string | null;
  exchange_rate_source?: string | null;
}

export interface PostingRuleCondition {
  field: string;
  operator: string;
  value?: unknown;
}

export interface PostingRule {
  id: string;
  tenant_id: string;
  source_module: string;
  source_event: string;
  rule_name?: string | null;
  rule_code?: string;
  accounting_event?: string;
  product?: string | null;
  scope?: string | Record<string, unknown> | null;
  priority: number;
  status?: string | null;
  version?: number | null;
  supersedes_rule_id?: string | null;
  effective_from?: string | null;
  effective_to?: string | null;
  requires_approval?: string | null;
  approval_status?: string | null;
  maker_by?: string | null;
  checker_by?: string | null;
  finance_head_by?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  dependency_rule_ids?: string[];
  rollback_strategy?: string | null;
  debit_account_code?: string | null;
  credit_account_code?: string | null;
  description?: string | null;
  is_active: string;
  lines: PostingRuleLine[];
  debit_lines?: PostingRuleLine[];
  credit_lines?: PostingRuleLine[];
  conditions: PostingRuleCondition[];
  dimensions?: Record<string, unknown>;
  validation_rules?: string[];
  workflow?: Record<string, unknown>;
  execution_summary?: {
    execution_count: number;
    success_count: number;
    failure_count: number;
    success_rate?: number;
    average_execution_time_ms: number;
  };
  ai?: {
    duplicate_risk?: string;
    conflict_detection?: string;
    recommendation?: string;
    predicted_failure?: string;
    health_score?: number;
    coverage?: string;
  };
  business_view?: Record<string, unknown>;
  accounting_view?: Record<string, unknown>;
  operations_view?: Record<string, unknown>;
  governance_view?: Record<string, unknown>;
  ai_view?: Record<string, unknown>;
  recent_executions?: Array<Record<string, unknown>>;
  created_at?: string | null;
  updated_at?: string | null;
  created_by?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface PostingRulePayload {
  tenant_id: string;
  source_module: string;
  source_event: string;
  rule_name?: string;
  priority?: number;
  status?: string;
  version?: number;
  effective_from?: string;
  effective_to?: string;
  requires_approval?: string;
  debit_account_code?: string;
  credit_account_code?: string;
  description?: string;
  lines?: PostingRuleLine[];
  conditions?: PostingRuleCondition[];
  created_by?: string;
  metadata?: Record<string, unknown>;
}

export interface PostingRuleDashboard {
  tenant_id: string;
  kpis: {
    posting_rules: number;
    active_rules: number;
    draft_rules: number;
    failed_rules: number;
    average_execution_time_ms: number;
    rule_coverage: number;
    unused_rules: number;
    ai_recommendations: number;
    rule_health: number;
  };
  charts: {
    rules_by_product: Array<{ label: string; value: number }>;
    execution_frequency: Array<{ label: string; value: number }>;
    rule_success_rate: Array<{ label: string; value: number }>;
    rules_by_status: Array<{ label: string; value: number }>;
  };
  summary: {
    status: string;
    message: string;
  };
}

export interface PostingRuleSimulationResponse {
  rule: PostingRule;
  is_balanced: boolean;
  total_debit: number;
  total_credit: number;
  lines: Array<Record<string, unknown>>;
  pipeline?: Record<string, unknown>;
  ai?: Record<string, unknown>;
}

export interface JournalLine {
  id?: string;
  sequence?: number | null;
  gl_account_id?: string | null;
  account_code?: string | null;
  account_name?: string | null;
  debit: number;
  credit: number;
  currency?: string | null;
  transaction_currency?: string | null;
  transaction_amount?: number | null;
  exchange_rate?: number | null;
  branch_id?: string | null;
  department_id?: string | null;
  cost_center?: string | null;
  profit_center?: string | null;
  project_id?: string | null;
  employee_id?: string | null;
  product_id?: string | null;
  business_unit_id?: string | null;
  description?: string | null;
}

export interface Journal {
  id: string;
  tenant_id: string;
  journal_no?: string | null;
  journal_number?: string | null;
  posting_date?: string | null;
  accounting_date?: string | null;
  entry_date?: string | null;
  business_date?: string | null;
  business_event?: string | null;
  journal_type?: string | null;
  voucher_type?: string | null;
  description: string;
  reference?: string | null;
  source_module?: string | null;
  source_event?: string | null;
  source_reference?: string | null;
  branch_id?: string | null;
  legal_entity?: string | null;
  business_unit?: string | null;
  financial_year?: string | null;
  period?: string | null;
  currency?: string | null;
  exchange_rate?: number | null;
  status: string;
  posting_status?: string | null;
  created_by?: string | null;
  approved_by?: string | null;
  approved_at?: string | null;
  reversal_of?: string | null;
  voucher_id?: string | null;
  template_id?: string | null;
  amount?: number | null;
  total_debit: number;
  total_credit: number;
  total_amount?: number | null;
  lines: JournalLine[];
  attachments?: Array<Record<string, unknown>>;
  approvals?: Array<Record<string, unknown>>;
  validation_result?: Record<string, unknown> | null;
  validation_summary?: {
    valid?: boolean;
    is_balanced: boolean;
    errors: string[];
    warnings: string[];
    checks: Array<Record<string, unknown>>;
  };
  approval_state?: Record<string, unknown>;
  posting_window?: Record<string, unknown>;
  business_view?: Record<string, unknown>;
  accounting_view?: Record<string, unknown>;
  financial_view?: Record<string, unknown>;
  compliance_view?: Record<string, unknown>;
  source_transaction?: Record<string, unknown> | null;
  timeline?: Array<Record<string, unknown>>;
  ai?: Record<string, unknown>;
  ai_view?: Record<string, unknown>;
  metadata?: Record<string, unknown> | null;
}

export interface JournalPayload {
  tenant_id: string;
  posting_date?: string;
  voucher_type?: string;
  source_module?: string;
  source_event?: string;
  source_reference?: string;
  description: string;
  reference?: string;
  currency?: string;
  exchange_rate?: number;
  branch_id?: string;
  financial_year?: string;
  template_id?: string;
  created_by?: string;
  metadata?: Record<string, unknown>;
  lines: JournalLine[];
  attachments?: Array<{ document_id?: string; file_name: string; uploaded_by?: string }>;
}

export interface JournalDashboard {
  tenant_id: string;
  kpis: {
    todays_journals: number;
    posted: number;
    draft: number;
    pending_approval: number;
    rejected: number;
    reversed: number;
    recurring: number;
    failed: number;
    processing_time_ms: number;
    journal_health: number;
    total_journals: number;
    total_amount: number;
  };
  charts: {
    journals_by_type: Array<{ label: string; value: number }>;
    posting_volume: Array<{ label: string; value: number }>;
    approval_status: Array<{ label: string; value: number }>;
    module_distribution: Array<{ label: string; value: number }>;
    daily_throughput: Array<{ label: string; value: number }>;
  };
  summary: {
    status: string;
    message: string;
  };
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
  getPostingRuleDashboard: (tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<PostingRuleDashboard>(`/api/v1/accounting/posting-rules/dashboard?${tenantParam(tenantId)}`),
  listPostingRules: (tenantId = DEFAULT_ACCOUNTING_TENANT, params = '') =>
    getJson<{ tenant_id: string; total: number; items: PostingRule[] }>(`/api/v1/accounting/posting-rules?${tenantParam(tenantId)}${params ? `&${params}` : ''}`),
  createPostingRule: (payload: PostingRulePayload) =>
    postJson<PostingRule>('/api/v1/accounting/posting-rules', payload),
  getPostingRule: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<PostingRule>(`/api/v1/accounting/posting-rules/${id}?${tenantParam(tenantId)}`),
  updatePostingRule: (id: string, tenantId: string, payload: Partial<PostingRulePayload>) =>
    putJson<PostingRule>(`/api/v1/accounting/posting-rules/${id}?${tenantParam(tenantId)}`, payload),
  simulatePostingRule: (id: string, tenantId: string, payload: { amount: number; source_reference?: string; currency?: string; branch_id?: string; event_data?: Record<string, unknown> }) =>
    postJson<PostingRuleSimulationResponse>(`/api/v1/accounting/posting-rules/${id}/simulate`, {
      tenant_id: tenantId,
      ...payload,
    }),
  publishPostingRule: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    postJson<PostingRule>(`/api/v1/accounting/posting-rules/${id}/publish`, { tenant_id: tenantId, performed_by: 'rule-console' }),
  getPostingRuleVersions: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<{ tenant_id: string; rule_id: string; items: PostingRule[] }>(`/api/v1/accounting/posting-rules/${id}/versions?${tenantParam(tenantId)}`),
  getJournalDashboard: (tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<JournalDashboard>(`/api/v1/accounting/journals/dashboard?${tenantParam(tenantId)}`),
  listJournals: (tenantId = DEFAULT_ACCOUNTING_TENANT, params = '') =>
    getJson<{ tenant_id: string; total: number; status_counts: Record<string, number>; items: Journal[] }>(`/api/v1/accounting/journals?${tenantParam(tenantId)}${params ? `&${params}` : ''}`),
  searchJournals: (tenantId = DEFAULT_ACCOUNTING_TENANT, params = '') =>
    getJson<{ tenant_id: string; query: string; total: number; items: Journal[] }>(`/api/v1/accounting/journals/search?${tenantParam(tenantId)}${params ? `&${params}` : ''}`),
  createJournal: (payload: JournalPayload) =>
    postJson<Journal>('/api/v1/accounting/journals', payload),
  getJournal: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT) =>
    getJson<Journal>(`/api/v1/accounting/journals/${id}?${tenantParam(tenantId)}`),
  updateJournal: (id: string, tenantId: string, payload: Partial<JournalPayload> & { performed_by?: string }) =>
    putJson<Journal>(`/api/v1/accounting/journals/${id}?${tenantParam(tenantId)}`, payload),
  approveJournal: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT, performedBy = 'journal-checker') =>
    postJson<Journal>(`/api/v1/accounting/journals/${id}/approve`, { tenant_id: tenantId, performed_by: performedBy, decision: 'approved' }),
  postJournal: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT, performedBy = 'finance-head') =>
    postJson<Journal>(`/api/v1/accounting/journals/${id}/post`, { tenant_id: tenantId, performed_by: performedBy }),
  reverseJournal: (id: string, tenantId = DEFAULT_ACCOUNTING_TENANT, remarks = 'Controlled reversal from journal console') =>
    postJson<{ journal: Journal; reversal: Journal }>(`/api/v1/accounting/journals/${id}/reverse`, { tenant_id: tenantId, performed_by: 'finance-head', remarks }),
};
