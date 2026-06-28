'use client';

import {
  apiClient,
  type AccountingQuickActionPayload,
  type PostingRuleConditionPayload,
  type PostingRuleLinePayload,
  type PostingRulePayload,
} from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useCallback, useEffect, useMemo, useState } from 'react';

type ActionType = 'loan_disbursed' | 'customer_paid_emi' | 'deposit_received' | 'expense_paid' | 'salary_paid' | 'interest_accrued';

interface Metric {
  key: string;
  label: string;
  amount: number;
  tone: string;
}

interface CoaTreeNode {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  category?: string | null;
  posting_allowed?: string | null;
  status?: string | null;
  balance: number;
  children: CoaTreeNode[];
}

interface AccountSearchItem {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  category?: string | null;
  posting_allowed?: string | null;
  balance: number;
}

interface Voucher {
  id: string;
  voucher_number: string;
  voucher_type: string;
  voucher_date: string;
  description: string;
  status: string;
  amount?: number | null;
  payee_name?: string | null;
  payer_name?: string | null;
  customer_name?: string | null;
}

interface JournalItem {
  id: string;
  entry_date: string;
  description: string;
  reference?: string | null;
  source_module?: string | null;
  source_event?: string | null;
  status: string;
}

interface Dashboard360 {
  metrics: Metric[];
  trial_balance: {
    total_debit: number;
    total_credit: number;
    is_balanced: boolean;
  };
  posting_health: {
    posting_rules: number;
    active_rules?: number;
    pending_rule_approvals?: number;
    journal_entries: number;
    subledger_entries: number;
    automation_rate: number;
  };
  period_controls?: {
    periods: number;
    open: number;
    locked: number;
    pending_unlock: number;
    latest?: AccountingPeriod | null;
  };
  voucher_workflow: Record<string, number>;
  gl_tree: CoaTreeNode[];
  top_accounts: AccountSearchItem[];
  source_modules: Array<{ source_module: string; entries: number; amount: number }>;
  recent_vouchers: Voucher[];
  recent_journals: JournalItem[];
  ai_summary: string;
}

interface GlDetail {
  account: AccountSearchItem & {
    currency?: string | null;
    base_currency?: string | null;
    freeze_status?: string | null;
    allow_manual_posting?: string | null;
    allow_auto_posting?: string | null;
    exchange_gain_loss_account_code?: string | null;
    revaluation_account_code?: string | null;
    status?: string | null;
  };
  summary: {
    total_debit: number;
    total_credit: number;
    balance: number;
    transaction_count: number;
    ai_summary: string;
    risk: string;
  };
  branch_wise: Array<{ branch: string; amount: number }>;
  source_modules: Array<{ source_module: string; entries: number; amount: number }>;
  monthly_trend: Array<{ month: string; amount: number }>;
  children: CoaTreeNode[];
  recent_entries: Array<{
    journal_entry_id: string;
    entry_date?: string | null;
    description?: string | null;
    reference?: string | null;
    source_module?: string | null;
    debit: number;
    credit: number;
    branch_id?: string | null;
  }>;
}

interface PostingRule {
  id: string;
  source_module: string;
  source_event: string;
  rule_name?: string | null;
  priority: number;
  status?: string | null;
  version?: number | null;
  supersedes_rule_id?: string | null;
  approval_status?: string | null;
  maker_by?: string | null;
  checker_by?: string | null;
  finance_head_by?: string | null;
  dependency_rule_ids?: string[];
  description?: string | null;
  lines: Array<PostingRuleLinePayload & { direction: 'debit' | 'credit' }>;
  conditions: PostingRuleConditionPayload[];
}

interface AccountingPeriod {
  id: string;
  financial_year: string;
  period_name: string;
  period_start: string;
  period_end: string;
  status: string;
  locked_by?: string | null;
  unlock_requested_by?: string | null;
}

interface RuleSimulation {
  is_balanced: boolean;
  total_debit: number;
  total_credit: number;
  lines: Array<{
    account_code: string;
    account_name: string;
    direction: string;
    debit: number;
    credit: number;
    description?: string | null;
  }>;
}

const actions: Array<{ key: ActionType; label: string; source: string }> = [
  { key: 'loan_disbursed', label: 'Loan disbursed', source: 'Loans' },
  { key: 'customer_paid_emi', label: 'Customer paid EMI', source: 'Loans' },
  { key: 'deposit_received', label: 'Deposit received', source: 'Deposits' },
  { key: 'expense_paid', label: 'Expense paid', source: 'Expenses' },
  { key: 'salary_paid', label: 'Salary paid', source: 'HRMS' },
  { key: 'interest_accrued', label: 'Interest accrued', source: 'Loans' },
];

const defaultRuleLines: Array<PostingRuleLinePayload & { direction: 'debit' | 'credit' }> = [
  { account_code: '1200_LOAN_RECEIVABLE', direction: 'debit', amount_source: 'amount', description: 'Generated debit' },
  { account_code: '1120_BANK', direction: 'credit', amount_source: 'amount', description: 'Generated credit' },
];

function money(value: number | undefined | null) {
  return `INR ${Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
}

function shortDate(value?: string | null) {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}

function errorText(error: unknown, fallback: string) {
  const candidate = error as { response?: { data?: { detail?: string } } };
  return candidate?.response?.data?.detail || fallback;
}

function metricTone(tone: string) {
  if (tone === 'emerald') return 'border-emerald-200 bg-emerald-50 text-emerald-900';
  if (tone === 'amber') return 'border-amber-200 bg-amber-50 text-amber-950';
  if (tone === 'rose') return 'border-rose-200 bg-rose-50 text-rose-900';
  if (tone === 'blue') return 'border-blue-200 bg-blue-50 text-blue-950';
  return 'border-slate-200 bg-white text-slate-950';
}

function flattenTree(nodes: CoaTreeNode[]): AccountSearchItem[] {
  return nodes.flatMap((node) => [
    {
      id: node.id,
      account_code: node.account_code,
      account_name: node.account_name,
      account_type: node.account_type,
      category: node.category,
      posting_allowed: node.posting_allowed,
      balance: node.balance,
    },
    ...flattenTree(node.children || []),
  ]);
}

function AccountTree({
  nodes,
  selectedId,
  onSelect,
  depth = 0,
}: {
  nodes: CoaTreeNode[];
  selectedId?: string;
  onSelect: (accountId: string) => void;
  depth?: number;
}) {
  return (
    <div className="space-y-1">
      {nodes.map((node) => (
        <div key={node.id}>
          <button
            type="button"
            onClick={() => onSelect(node.id)}
            className={`grid w-full grid-cols-[1fr_auto] items-center gap-3 rounded-md px-2 py-2 text-left transition ${
              selectedId === node.id ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
            }`}
            style={{ paddingLeft: `${8 + depth * 14}px` }}
          >
            <span className="min-w-0">
              <span className="block truncate text-[13px] font-semibold">{node.account_name}</span>
              <span className={`block truncate text-[11px] ${selectedId === node.id ? 'text-slate-300' : 'text-slate-500'}`}>
                {node.account_code} / {node.category || node.account_type}
              </span>
            </span>
            <span className={`text-[11px] ${selectedId === node.id ? 'text-slate-200' : 'text-slate-500'}`}>
              {node.children?.length ? node.children.length : String(node.posting_allowed || 'true').toLowerCase() === 'false' ? 'C' : 'P'}
            </span>
          </button>
          {node.children?.length > 0 && <AccountTree nodes={node.children} selectedId={selectedId} onSelect={onSelect} depth={depth + 1} />}
        </div>
      ))}
    </div>
  );
}

export default function AccountingPage() {
  const { user, token, isLoading } = useAuth();
  const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || 'default';
  const [dashboard, setDashboard] = useState<Dashboard360 | null>(null);
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [glDetail, setGlDetail] = useState<GlDetail | null>(null);
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState<AccountSearchItem[]>([]);
  const [message, setMessage] = useState('');
  const [busyAction, setBusyAction] = useState('');
  const [quickForm, setQuickForm] = useState({
    action_type: 'loan_disbursed' as ActionType,
    amount: '',
    party_name: '',
    description: '',
    source_reference: '',
    branch_id: '',
  });
  const [postingRules, setPostingRules] = useState<PostingRule[]>([]);
  const [accountingPeriods, setAccountingPeriods] = useState<AccountingPeriod[]>([]);
  const [ruleSimulation, setRuleSimulation] = useState<RuleSimulation | null>(null);
  const [periodForm, setPeriodForm] = useState({
    financial_year: '2026-27',
    period_name: 'July 2026',
    period_start: '2026-07-01',
    period_end: '2026-07-31',
    reason: 'Month close',
  });
  const [ruleForm, setRuleForm] = useState({
    rule_name: 'Loan disbursement rule',
    source_module: 'loans',
    source_event: 'disbursement',
    priority: '10',
    status: 'draft',
    dependency_rule_ids: '',
    description: 'Debit customer receivable and credit bank on disbursement',
    condition_field: 'amount',
    condition_operator: 'gt',
    condition_value: '0',
    simulation_amount: '500000',
    simulation_json: '{ "amount": 500000, "product": "gold_loan", "branch_id": "Kollam" }',
    lines: defaultRuleLines,
  });

  const allAccounts = useMemo(() => flattenTree(dashboard?.gl_tree || []), [dashboard]);
  const visibleAccounts = search ? searchResults : allAccounts.slice(0, 20);

  const loadGlDetail = useCallback(async (accountId: string) => {
    if (!token || !tenantId || !accountId) return;
    try {
      const response = await apiClient.getAccounting360Gl(tenantId, accountId);
      setGlDetail(response.data);
    } catch (error) {
      setMessage(errorText(error, 'Unable to load GL 360 view.'));
    }
  }, [tenantId, token]);

  const refresh = useCallback(async () => {
    if (!token || !tenantId) return;
    try {
      const [response, rulesResponse, periodsResponse] = await Promise.all([
        apiClient.getAccounting360Dashboard(tenantId),
        apiClient.getPostingRules(tenantId),
        apiClient.getAccountingPeriods(tenantId),
      ]);
      const data = response.data as Dashboard360;
      setDashboard(data);
      setPostingRules(rulesResponse.data || []);
      setAccountingPeriods(periodsResponse.data || []);
      setMessage('');
      const firstAccountId = selectedAccountId || data.top_accounts[0]?.id || flattenTree(data.gl_tree)[0]?.id || '';
      if (firstAccountId) {
        setSelectedAccountId(firstAccountId);
        await loadGlDetail(firstAccountId);
      }
    } catch (error) {
      setMessage(errorText(error, 'Unable to load Accounting 360.'));
    }
  }, [loadGlDetail, selectedAccountId, tenantId, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!token || !tenantId || !search.trim()) {
      setSearchResults([]);
      return;
    }
    const handle = window.setTimeout(async () => {
      try {
        const response = await apiClient.searchAccounting360(tenantId, search);
        setSearchResults(response.data.items || []);
      } catch {
        setSearchResults([]);
      }
    }, 250);
    return () => window.clearTimeout(handle);
  }, [search, tenantId, token]);

  async function runAction(name: string, action: () => Promise<unknown>, success: string) {
    setBusyAction(name);
    setMessage('');
    try {
      await action();
      setMessage(success);
      await refresh();
    } catch (error) {
      setMessage(errorText(error, 'Action failed.'));
    } finally {
      setBusyAction('');
    }
  }

  function selectAccount(accountId: string) {
    setSelectedAccountId(accountId);
    loadGlDetail(accountId);
  }

  function parseSimulationData() {
    try {
      const parsed = JSON.parse(ruleForm.simulation_json || '{}');
      return typeof parsed === 'object' && parsed ? parsed as Record<string, unknown> : {};
    } catch {
      throw new Error('Simulation JSON is invalid.');
    }
  }

  function updateRuleLine(index: number, patch: Partial<PostingRuleLinePayload & { direction: 'debit' | 'credit' }>) {
    setRuleForm({
      ...ruleForm,
      lines: ruleForm.lines.map((line, lineIndex) => lineIndex === index ? { ...line, ...patch } : line),
    });
  }

  function rulePayload(status = ruleForm.status): PostingRulePayload {
    const conditionValue = Number.isNaN(Number(ruleForm.condition_value)) ? ruleForm.condition_value : Number(ruleForm.condition_value);
    return {
      tenant_id: tenantId,
      rule_name: ruleForm.rule_name,
      source_module: ruleForm.source_module,
      source_event: ruleForm.source_event,
      priority: Number(ruleForm.priority || 100),
      status,
      requires_approval: 'true',
      dependency_rule_ids: ruleForm.dependency_rule_ids.split(',').map((item) => item.trim()).filter(Boolean),
      rollback_strategy: 'reverse_journal',
      description: ruleForm.description,
      created_by: user?.username,
      conditions: ruleForm.condition_field ? [{
        field: ruleForm.condition_field,
        operator: ruleForm.condition_operator,
        value: conditionValue,
      }] : [],
      lines: ruleForm.lines.map((line, index) => ({
        ...line,
        sequence: index + 1,
        percentage: line.percentage ? Number(line.percentage) : undefined,
      })),
    };
  }

  async function simulateRule() {
    setBusyAction('simulate-rule');
    setMessage('');
    try {
      await apiClient.validatePostingRule(rulePayload());
      const eventData = parseSimulationData();
      const response = await apiClient.simulatePostingRule({
        tenant_id: tenantId,
        source_module: ruleForm.source_module,
        source_event: ruleForm.source_event,
        amount: Number(ruleForm.simulation_amount || eventData.amount || 0),
        event_data: eventData,
      });
      setRuleSimulation(response.data);
      setMessage('Posting rule simulated successfully.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : errorText(error, 'Unable to simulate rule.'));
    } finally {
      setBusyAction('');
    }
  }

  function createPeriod() {
    return apiClient.createAccountingPeriod({
      tenant_id: tenantId,
      financial_year: periodForm.financial_year,
      period_name: periodForm.period_name,
      period_start: `${periodForm.period_start}T00:00:00`,
      period_end: `${periodForm.period_end}T23:59:59`,
      performed_by: user?.username,
    });
  }

  function ruleStageLabel(rule: PostingRule) {
    if (rule.status === 'active') return 'Published';
    if (rule.approval_status === 'finance_head_approved') return 'Ready to publish';
    if (rule.approval_status === 'checker_approved') return 'Finance approval';
    if (rule.approval_status === 'maker_submitted') return 'Checker approval';
    return 'Draft';
  }

  const latestPeriod = accountingPeriods[0] || dashboard?.period_controls?.latest || null;
  const canPostQuickAction = Number(quickForm.amount || 0) > 0;

  if (isLoading) {
    return <main className="min-h-screen bg-slate-100 p-6 text-slate-700">Loading Accounting 360...</main>;
  }

  if (!user) {
    return <main className="min-h-screen bg-slate-100 p-6 text-slate-700">Please login to continue.</main>;
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <div className="grid min-h-screen lg:grid-cols-[84px_1fr]">
        <aside className="hidden border-r border-slate-800 bg-slate-950 px-3 py-5 text-white lg:block">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded bg-emerald-400 text-sm font-black text-slate-950">A</div>
          <nav className="mt-8 grid gap-3 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            {['360', 'COA', 'GL', 'Rules', 'EOD'].map((item) => (
              <span key={item} className={`rounded px-2 py-2 text-center ${item === '360' ? 'bg-white text-slate-950' : 'bg-slate-900'}`}>
                {item}
              </span>
            ))}
          </nav>
        </aside>

        <section className="min-w-0">
          <header className="border-b border-slate-200 bg-white px-4 py-4 sm:px-6">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <h1 className="text-2xl font-bold tracking-normal text-slate-950">Accounting 360</h1>
                <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
                  <span className="rounded border border-slate-200 px-2 py-1">Tenant {tenantId}</span>
                  <span className={`rounded px-2 py-1 ${dashboard?.trial_balance.is_balanced ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>
                    Trial Balance {dashboard?.trial_balance.is_balanced ? 'Balanced' : 'Variance'}
                  </span>
                  <span className="rounded bg-slate-100 px-2 py-1">Automation {dashboard?.posting_health.automation_rate || 0}%</span>
                </div>
              </div>

              <form
                className="grid gap-2 rounded-md border border-slate-200 bg-slate-50 p-2 xl:w-[760px] xl:grid-cols-[1.1fr_0.8fr_0.7fr_0.7fr_auto]"
                onSubmit={(event) => {
                  event.preventDefault();
                  const payload: AccountingQuickActionPayload = {
                    tenant_id: tenantId,
                    action_type: quickForm.action_type,
                    amount: Number(quickForm.amount),
                    party_name: quickForm.party_name || undefined,
                    description: quickForm.description || undefined,
                    source_reference: quickForm.source_reference || undefined,
                    branch_id: quickForm.branch_id || undefined,
                    performed_by: user.username,
                  };
                  runAction('quick-action', () => apiClient.postAccounting360QuickAction(payload), 'Entry posted automatically.');
                }}
              >
                <select
                  className="h-10 rounded border border-slate-300 bg-white px-3 text-sm font-medium text-slate-800"
                  value={quickForm.action_type}
                  onChange={(event) => setQuickForm({ ...quickForm, action_type: event.target.value as ActionType })}
                >
                  {actions.map((action) => (
                    <option key={action.key} value={action.key}>{action.label}</option>
                  ))}
                </select>
                <input
                  className="h-10 rounded border border-slate-300 px-3 text-sm"
                  placeholder="Amount"
                  type="number"
                  value={quickForm.amount}
                  onChange={(event) => setQuickForm({ ...quickForm, amount: event.target.value })}
                />
                <input
                  className="h-10 rounded border border-slate-300 px-3 text-sm"
                  placeholder="Customer / vendor"
                  value={quickForm.party_name}
                  onChange={(event) => setQuickForm({ ...quickForm, party_name: event.target.value })}
                />
                <input
                  className="h-10 rounded border border-slate-300 px-3 text-sm"
                  placeholder="Reference"
                  value={quickForm.source_reference}
                  onChange={(event) => setQuickForm({ ...quickForm, source_reference: event.target.value })}
                />
                <button
                  disabled={!!busyAction || !canPostQuickAction}
                  className="h-10 rounded bg-slate-950 px-4 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busyAction === 'quick-action' ? 'Posting' : 'Post'}
                </button>
              </form>
            </div>
          </header>

          <div className="grid gap-4 p-4 sm:p-6">
            {message && <div className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700">{message}</div>}

            <div className="grid gap-3 md:grid-cols-5">
              {(dashboard?.metrics || []).map((metric) => (
                <div key={metric.key} className={`rounded-md border px-4 py-3 ${metricTone(metric.tone)}`}>
                  <p className="text-xs font-bold uppercase tracking-wide opacity-70">{metric.label}</p>
                  <p className="mt-2 text-xl font-black tracking-normal">{money(metric.amount)}</p>
                </div>
              ))}
            </div>

            {!dashboard?.gl_tree.length && (
              <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm font-bold text-amber-950">Chart of Accounts is empty</p>
                    <p className="text-sm text-amber-900">Seed the NBFC account structure to start using Accounting 360.</p>
                  </div>
                  <button
                    className="h-10 rounded bg-amber-900 px-4 text-sm font-bold text-white"
                    disabled={!!busyAction}
                    onClick={() => runAction('seed', () => apiClient.seedDefaultGlAccounts({ tenant_id: tenantId, currency: 'INR', financial_year: '2026-27' }), 'Default NBFC chart of accounts created.')}
                  >
                    Seed COA
                  </button>
                </div>
              </div>
            )}

            <section className="rounded-md border border-slate-200 bg-white p-4">
              <div className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
                <div>
                  <h2 className="text-sm font-black uppercase tracking-wide text-slate-800">Period Controls</h2>
                  <p className="mt-1 text-sm font-semibold text-slate-500">Lock closed months and route unlocks through approval.</p>
                  <div className="mt-3 grid grid-cols-4 gap-2 text-center text-xs font-bold text-slate-600">
                    <div className="rounded border border-slate-200 px-2 py-2">
                      <p className="text-lg font-black text-slate-950">{dashboard?.period_controls?.periods || accountingPeriods.length}</p>
                      <p>Periods</p>
                    </div>
                    <div className="rounded border border-slate-200 px-2 py-2">
                      <p className="text-lg font-black text-emerald-700">{dashboard?.period_controls?.open || accountingPeriods.filter((period) => period.status === 'open').length}</p>
                      <p>Open</p>
                    </div>
                    <div className="rounded border border-slate-200 px-2 py-2">
                      <p className="text-lg font-black text-rose-700">{dashboard?.period_controls?.locked || accountingPeriods.filter((period) => period.status === 'locked').length}</p>
                      <p>Locked</p>
                    </div>
                    <div className="rounded border border-slate-200 px-2 py-2">
                      <p className="text-lg font-black text-amber-700">{dashboard?.period_controls?.pending_unlock || accountingPeriods.filter((period) => period.status === 'pending_unlock').length}</p>
                      <p>Pending</p>
                    </div>
                  </div>
                </div>
                <div className="grid gap-3">
                  <div className="grid gap-2 md:grid-cols-5">
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="FY" value={periodForm.financial_year} onChange={(event) => setPeriodForm({ ...periodForm, financial_year: event.target.value })} />
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="Period" value={periodForm.period_name} onChange={(event) => setPeriodForm({ ...periodForm, period_name: event.target.value })} />
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" type="date" value={periodForm.period_start} onChange={(event) => setPeriodForm({ ...periodForm, period_start: event.target.value })} />
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" type="date" value={periodForm.period_end} onChange={(event) => setPeriodForm({ ...periodForm, period_end: event.target.value })} />
                    <button className="h-10 rounded bg-slate-950 px-3 text-sm font-bold text-white disabled:opacity-50" disabled={!!busyAction} onClick={() => runAction('create-period', createPeriod, 'Accounting period created.')}>Create</button>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 rounded border border-slate-200 px-3 py-2 text-sm">
                    <span className="font-bold text-slate-900">{latestPeriod ? `${latestPeriod.period_name} / ${latestPeriod.status}` : 'No period configured'}</span>
                    <input className="h-9 min-w-44 rounded border border-slate-300 px-3 text-sm" placeholder="Reason" value={periodForm.reason} onChange={(event) => setPeriodForm({ ...periodForm, reason: event.target.value })} />
                    {latestPeriod && latestPeriod.status === 'open' && (
                      <button className="h-9 rounded bg-rose-700 px-3 text-xs font-bold text-white" onClick={() => runAction(`lock-period-${latestPeriod.id}`, () => apiClient.lockAccountingPeriod(latestPeriod.id, tenantId, user.username, periodForm.reason), 'Accounting period locked.')}>Lock</button>
                    )}
                    {latestPeriod && latestPeriod.status === 'locked' && (
                      <button className="h-9 rounded bg-amber-600 px-3 text-xs font-bold text-white" onClick={() => runAction(`unlock-request-${latestPeriod.id}`, () => apiClient.requestUnlockAccountingPeriod(latestPeriod.id, tenantId, user.username, periodForm.reason), 'Unlock request submitted.')}>Request Unlock</button>
                    )}
                    {latestPeriod && latestPeriod.status === 'pending_unlock' && (
                      <button className="h-9 rounded bg-emerald-700 px-3 text-xs font-bold text-white" onClick={() => runAction(`unlock-approve-${latestPeriod.id}`, () => apiClient.approveUnlockAccountingPeriod(latestPeriod.id, tenantId, user.username), 'Unlock approved.')}>Approve Unlock</button>
                    )}
                  </div>
                </div>
              </div>
            </section>

            <section className="rounded-md border border-slate-200 bg-white p-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <h2 className="text-sm font-black uppercase tracking-wide text-slate-800">Posting Rule Builder</h2>
                  <p className="mt-1 text-sm font-semibold text-slate-500">Configure module events once; journals and GL entries are generated from rules.</p>
                </div>
                <div className="grid grid-cols-4 gap-2 text-center text-xs font-bold text-slate-600 sm:w-[460px]">
                  <div className="rounded border border-slate-200 px-2 py-2">
                    <p className="text-lg font-black text-slate-950">{postingRules.length}</p>
                    <p>Rules</p>
                  </div>
                  <div className="rounded border border-slate-200 px-2 py-2">
                    <p className="text-lg font-black text-emerald-700">{postingRules.filter((rule) => rule.status === 'active').length}</p>
                    <p>Active</p>
                  </div>
                  <div className="rounded border border-slate-200 px-2 py-2">
                    <p className="text-lg font-black text-amber-700">{postingRules.filter((rule) => rule.status === 'draft').length}</p>
                    <p>Draft</p>
                  </div>
                  <div className="rounded border border-slate-200 px-2 py-2">
                    <p className="text-lg font-black text-blue-700">{postingRules.filter((rule) => rule.status === 'pending_approval').length}</p>
                    <p>Pending</p>
                  </div>
                </div>
              </div>

              <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
                <form
                  className="grid gap-3"
                  onSubmit={(event) => {
                    event.preventDefault();
                    runAction('create-rule', () => apiClient.createPostingRule(rulePayload()), 'Posting rule created.');
                  }}
                >
                  <div className="grid gap-3 md:grid-cols-5">
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm md:col-span-2" placeholder="Rule name" value={ruleForm.rule_name} onChange={(event) => setRuleForm({ ...ruleForm, rule_name: event.target.value })} />
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="Module" value={ruleForm.source_module} onChange={(event) => setRuleForm({ ...ruleForm, source_module: event.target.value })} />
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="Event" value={ruleForm.source_event} onChange={(event) => setRuleForm({ ...ruleForm, source_event: event.target.value })} />
                    <select className="h-10 rounded border border-slate-300 bg-white px-3 text-sm" value={ruleForm.status} onChange={(event) => setRuleForm({ ...ruleForm, status: event.target.value })}>
                      <option value="draft">Draft</option>
                      <option value="active">Active</option>
                      <option value="frozen">Frozen</option>
                    </select>
                  </div>

                  <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="Dependency rule IDs, comma separated" value={ruleForm.dependency_rule_ids} onChange={(event) => setRuleForm({ ...ruleForm, dependency_rule_ids: event.target.value })} />

                  <div className="grid gap-3 md:grid-cols-[1fr_150px_1fr]">
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="Condition field" value={ruleForm.condition_field} onChange={(event) => setRuleForm({ ...ruleForm, condition_field: event.target.value })} />
                    <select className="h-10 rounded border border-slate-300 bg-white px-3 text-sm" value={ruleForm.condition_operator} onChange={(event) => setRuleForm({ ...ruleForm, condition_operator: event.target.value })}>
                      <option value="gt">Greater than</option>
                      <option value="gte">Greater or equal</option>
                      <option value="eq">Equals</option>
                      <option value="contains">Contains</option>
                    </select>
                    <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="Condition value" value={ruleForm.condition_value} onChange={(event) => setRuleForm({ ...ruleForm, condition_value: event.target.value })} />
                  </div>

                  <div className="rounded border border-slate-200">
                    <div className="grid grid-cols-[1fr_110px_1fr_1fr_auto] gap-2 border-b border-slate-200 bg-slate-50 px-3 py-2 text-xs font-black uppercase tracking-wide text-slate-500">
                      <span>Account</span>
                      <span>Side</span>
                      <span>Amount Source</span>
                      <span>Formula</span>
                      <span>Action</span>
                    </div>
                    <div className="grid gap-2 p-3">
                      {ruleForm.lines.map((line, index) => (
                        <div key={index} className="grid gap-2 md:grid-cols-[1fr_110px_1fr_1fr_auto]">
                          <select className="h-10 rounded border border-slate-300 bg-white px-3 text-sm" value={line.account_code} onChange={(event) => updateRuleLine(index, { account_code: event.target.value })}>
                            {allAccounts.filter((account) => String(account.posting_allowed || 'true').toLowerCase() !== 'false').map((account) => (
                              <option key={account.id} value={account.account_code}>{account.account_code} - {account.account_name}</option>
                            ))}
                          </select>
                          <select className="h-10 rounded border border-slate-300 bg-white px-3 text-sm" value={line.direction} onChange={(event) => updateRuleLine(index, { direction: event.target.value as 'debit' | 'credit' })}>
                            <option value="debit">Debit</option>
                            <option value="credit">Credit</option>
                          </select>
                          <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="amount / principal" value={line.amount_source || ''} onChange={(event) => updateRuleLine(index, { amount_source: event.target.value, formula: event.target.value ? undefined : line.formula })} />
                          <input className="h-10 rounded border border-slate-300 px-3 text-sm" placeholder="interest + penalty" value={line.formula || ''} onChange={(event) => updateRuleLine(index, { formula: event.target.value, amount_source: event.target.value ? undefined : line.amount_source })} />
                          <button
                            type="button"
                            disabled={ruleForm.lines.length <= 2}
                            className="h-10 rounded border border-slate-300 px-3 text-sm font-bold text-slate-700 disabled:opacity-40"
                            onClick={() => setRuleForm({ ...ruleForm, lines: ruleForm.lines.filter((_, lineIndex) => lineIndex !== index) })}
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  <textarea className="min-h-20 rounded border border-slate-300 px-3 py-2 text-sm" placeholder="Simulation JSON" value={ruleForm.simulation_json} onChange={(event) => setRuleForm({ ...ruleForm, simulation_json: event.target.value })} />

                  <div className="flex flex-wrap gap-2">
                    <button type="button" className="h-10 rounded border border-slate-300 px-4 text-sm font-bold text-slate-700" onClick={() => setRuleForm({ ...ruleForm, lines: [...ruleForm.lines, { account_code: allAccounts[0]?.account_code || '1000_CASH', direction: 'credit', amount_source: 'amount', description: 'Generated line' }] })}>
                      Add Line
                    </button>
                    <button type="button" disabled={!!busyAction} className="h-10 rounded bg-blue-700 px-4 text-sm font-bold text-white disabled:opacity-50" onClick={simulateRule}>
                      {busyAction === 'simulate-rule' ? 'Simulating' : 'Simulate'}
                    </button>
                    <button disabled={!!busyAction || ruleForm.lines.length < 2} className="h-10 rounded bg-slate-950 px-4 text-sm font-bold text-white disabled:opacity-50">
                      {busyAction === 'create-rule' ? 'Saving' : 'Create Rule'}
                    </button>
                  </div>
                </form>

                <div className="grid content-start gap-4">
                  <div className="rounded border border-slate-200 p-3">
                    <h3 className="text-xs font-black uppercase tracking-wide text-slate-500">Simulation</h3>
                    {ruleSimulation ? (
                      <div className="mt-3 space-y-2 text-sm">
                        <div className={`rounded px-3 py-2 text-center font-black ${ruleSimulation.is_balanced ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>
                          {ruleSimulation.is_balanced ? 'Balanced' : 'Not balanced'} / Debit {money(ruleSimulation.total_debit)} / Credit {money(ruleSimulation.total_credit)}
                        </div>
                        {ruleSimulation.lines.map((line, index) => (
                          <div key={`${line.account_code}-${index}`} className="grid grid-cols-[1fr_auto] gap-3 border-b border-slate-100 pb-2">
                            <span>
                              <span className="block font-bold text-slate-900">{line.account_name}</span>
                              <span className="text-xs text-slate-500">{line.account_code} / {line.direction}</span>
                            </span>
                            <span className="font-black">{money(line.debit || line.credit)}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-3 text-sm font-semibold text-slate-500">Run a simulation to preview generated accounting entries before publishing.</p>
                    )}
                  </div>

                  <div className="rounded border border-slate-200 p-3">
                    <h3 className="text-xs font-black uppercase tracking-wide text-slate-500">Rule Register</h3>
                    <div className="mt-3 max-h-72 space-y-2 overflow-y-auto">
                      {postingRules.slice(0, 8).map((rule) => (
                        <div key={rule.id} className="rounded border border-slate-200 px-3 py-2">
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                              <p className="truncate text-sm font-black text-slate-900">{rule.rule_name || `${rule.source_module}.${rule.source_event}`}</p>
                              <p className="text-xs font-semibold text-slate-500">{rule.source_module} / {rule.source_event} / v{rule.version || 1} / {ruleStageLabel(rule)}</p>
                            </div>
                            <span className={`rounded px-2 py-1 text-[11px] font-black ${rule.status === 'active' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-900'}`}>{rule.status || 'draft'}</span>
                          </div>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {rule.status !== 'active' && (!rule.approval_status || rule.approval_status === 'draft') && (
                              <button className="rounded bg-blue-700 px-3 py-1 text-xs font-bold text-white" onClick={() => runAction(`submit-${rule.id}`, () => apiClient.submitPostingRule(rule.id, tenantId, user.username), 'Posting rule submitted.')}>Submit</button>
                            )}
                            {rule.approval_status === 'maker_submitted' && (
                              <button className="rounded bg-indigo-700 px-3 py-1 text-xs font-bold text-white" onClick={() => runAction(`checker-${rule.id}`, () => apiClient.approvePostingRule(rule.id, tenantId, 'checker', user.username), 'Checker approval recorded.')}>Checker</button>
                            )}
                            {rule.approval_status === 'checker_approved' && (
                              <button className="rounded bg-violet-700 px-3 py-1 text-xs font-bold text-white" onClick={() => runAction(`finance-${rule.id}`, () => apiClient.approvePostingRule(rule.id, tenantId, 'finance_head', user.username), 'Finance head approval recorded.')}>Finance Head</button>
                            )}
                            {rule.approval_status === 'finance_head_approved' && (
                              <button className="rounded bg-emerald-700 px-3 py-1 text-xs font-bold text-white" onClick={() => runAction(`publish-${rule.id}`, () => apiClient.publishPostingRule(rule.id, tenantId, user.username), 'Posting rule published.')}>Publish</button>
                            )}
                            {rule.status === 'active' && (
                              <button className="rounded border border-slate-300 px-3 py-1 text-xs font-bold text-slate-700" onClick={() => runAction(`version-${rule.id}`, () => apiClient.createPostingRuleVersion(rule.id, { tenant_id: tenantId, performed_by: user.username }), 'New rule version drafted.')}>New Version</button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <div className="grid gap-4 xl:grid-cols-[340px_minmax(0,1fr)_360px]">
              <section className="rounded-md border border-slate-200 bg-white">
                <div className="border-b border-slate-200 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <h2 className="text-sm font-black uppercase tracking-wide text-slate-800">GL Explorer</h2>
                    <span className="text-xs font-semibold text-slate-500">{allAccounts.length} accounts</span>
                  </div>
                  <input
                    className="mt-3 h-10 w-full rounded border border-slate-300 px-3 text-sm"
                    placeholder="Search account"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                  />
                </div>
                <div className="max-h-[680px] overflow-y-auto p-2">
                  {search ? (
                    <div className="space-y-1">
                      {visibleAccounts.map((account) => (
                        <button
                          key={account.id}
                          className={`grid w-full grid-cols-[1fr_auto] gap-3 rounded-md px-2 py-2 text-left ${selectedAccountId === account.id ? 'bg-slate-900 text-white' : 'hover:bg-slate-100'}`}
                          onClick={() => selectAccount(account.id)}
                        >
                          <span className="min-w-0">
                            <span className="block truncate text-[13px] font-semibold">{account.account_name}</span>
                            <span className={`block truncate text-[11px] ${selectedAccountId === account.id ? 'text-slate-300' : 'text-slate-500'}`}>{account.account_code}</span>
                          </span>
                          <span className="text-[11px]">{money(account.balance)}</span>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <AccountTree nodes={dashboard?.gl_tree || []} selectedId={selectedAccountId} onSelect={selectAccount} />
                  )}
                </div>
              </section>

              <section className="grid min-w-0 gap-4">
                <div className="rounded-md border border-slate-200 bg-white p-4">
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div className="min-w-0">
                      <p className="text-xs font-black uppercase tracking-wide text-slate-500">GL 360</p>
                      <h2 className="mt-1 truncate text-2xl font-black text-slate-950">{glDetail?.account.account_name || 'Select a GL'}</h2>
                      <p className="mt-1 text-sm font-semibold text-slate-500">
                        {glDetail?.account.account_code || '-'} / {glDetail?.account.category || glDetail?.account.account_type || '-'}
                      </p>
                    </div>
                    <div className={`rounded-md px-3 py-2 text-sm font-black ${glDetail?.summary.risk === 'Review' ? 'bg-amber-100 text-amber-900' : 'bg-emerald-100 text-emerald-800'}`}>
                      Risk {glDetail?.summary.risk || '-'}
                    </div>
                  </div>

                  <div className="mt-4 grid gap-3 sm:grid-cols-4">
                    <div className="rounded border border-slate-200 px-3 py-3">
                      <p className="text-xs font-bold text-slate-500">Balance</p>
                      <p className="mt-1 text-lg font-black">{money(glDetail?.summary.balance)}</p>
                    </div>
                    <div className="rounded border border-slate-200 px-3 py-3">
                      <p className="text-xs font-bold text-slate-500">Debit</p>
                      <p className="mt-1 text-lg font-black">{money(glDetail?.summary.total_debit)}</p>
                    </div>
                    <div className="rounded border border-slate-200 px-3 py-3">
                      <p className="text-xs font-bold text-slate-500">Credit</p>
                      <p className="mt-1 text-lg font-black">{money(glDetail?.summary.total_credit)}</p>
                    </div>
                    <div className="rounded border border-slate-200 px-3 py-3">
                      <p className="text-xs font-bold text-slate-500">Entries</p>
                      <p className="mt-1 text-lg font-black">{glDetail?.summary.transaction_count || 0}</p>
                    </div>
                  </div>

                  <div className="mt-4 grid gap-3 rounded border border-slate-200 bg-slate-50 p-3 text-xs font-bold text-slate-600 md:grid-cols-3">
                    <div>
                      <p className="uppercase tracking-wide text-slate-400">Currency</p>
                      <p className="mt-1 text-sm text-slate-950">{glDetail?.account.currency || 'INR'} / Base {glDetail?.account.base_currency || glDetail?.account.currency || 'INR'}</p>
                    </div>
                    <div>
                      <p className="uppercase tracking-wide text-slate-400">Freeze</p>
                      <p className={`mt-1 text-sm ${glDetail?.account.freeze_status && glDetail.account.freeze_status !== 'open' ? 'text-rose-700' : 'text-emerald-700'}`}>{glDetail?.account.freeze_status || 'open'}</p>
                    </div>
                    <div>
                      <p className="uppercase tracking-wide text-slate-400">Posting Modes</p>
                      <p className="mt-1 text-sm text-slate-950">Manual {glDetail?.account.allow_manual_posting || 'true'} / Auto {glDetail?.account.allow_auto_posting || 'true'}</p>
                    </div>
                    <div className="md:col-span-3">
                      <p className="uppercase tracking-wide text-slate-400">Revaluation</p>
                      <p className="mt-1 text-sm text-slate-950">Gain/Loss {glDetail?.account.exchange_gain_loss_account_code || '-'} / Revaluation {glDetail?.account.revaluation_account_code || '-'}</p>
                    </div>
                  </div>

                  <div className="mt-4 rounded-md bg-slate-950 px-4 py-3 text-sm font-semibold text-white">
                    AI Finance Copilot: {glDetail?.summary.ai_summary || dashboard?.ai_summary || 'No movement yet.'}
                  </div>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-md border border-slate-200 bg-white p-4">
                    <h3 className="text-sm font-black uppercase tracking-wide text-slate-800">Branch Wise</h3>
                    <div className="mt-3 space-y-2">
                      {(glDetail?.branch_wise || []).slice(0, 6).map((row) => (
                        <div key={row.branch} className="grid grid-cols-[1fr_auto] items-center gap-3 border-b border-slate-100 pb-2 text-sm">
                          <span className="font-semibold text-slate-700">{row.branch}</span>
                          <span className="font-black">{money(row.amount)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-md border border-slate-200 bg-white p-4">
                    <h3 className="text-sm font-black uppercase tracking-wide text-slate-800">Source Modules</h3>
                    <div className="mt-3 space-y-2">
                      {(glDetail?.source_modules || dashboard?.source_modules || []).slice(0, 6).map((row) => (
                        <div key={row.source_module} className="grid grid-cols-[1fr_auto] items-center gap-3 border-b border-slate-100 pb-2 text-sm">
                          <span className="font-semibold capitalize text-slate-700">{row.source_module}</span>
                          <span className="font-black">{money(row.amount)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rounded-md border border-slate-200 bg-white p-4">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-sm font-black uppercase tracking-wide text-slate-800">Universal Transaction Timeline</h3>
                    <span className="text-xs font-semibold text-slate-500">Voucher / Journal / Ledger</span>
                  </div>
                  <div className="mt-3 overflow-x-auto">
                    <table className="w-full min-w-[720px] text-sm">
                      <thead>
                        <tr className="border-b border-slate-200 text-left text-xs font-black uppercase tracking-wide text-slate-500">
                          <th className="px-3 py-2">Date</th>
                          <th className="px-3 py-2">Narration</th>
                          <th className="px-3 py-2">Module</th>
                          <th className="px-3 py-2 text-right">Debit</th>
                          <th className="px-3 py-2 text-right">Credit</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(glDetail?.recent_entries || []).map((entry) => (
                          <tr key={`${entry.journal_entry_id}-${entry.debit}-${entry.credit}`} className="border-b border-slate-100">
                            <td className="px-3 py-2 text-slate-600">{shortDate(entry.entry_date)}</td>
                            <td className="px-3 py-2">
                              <p className="font-semibold text-slate-900">{entry.description || entry.reference || entry.journal_entry_id}</p>
                              <p className="text-xs text-slate-500">{entry.reference || entry.journal_entry_id}</p>
                            </td>
                            <td className="px-3 py-2 capitalize text-slate-600">{entry.source_module || 'manual'}</td>
                            <td className="px-3 py-2 text-right font-semibold">{money(entry.debit)}</td>
                            <td className="px-3 py-2 text-right font-semibold">{money(entry.credit)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </section>

              <aside className="grid content-start gap-4">
                <section className="rounded-md border border-slate-200 bg-white p-4">
                  <h2 className="text-sm font-black uppercase tracking-wide text-slate-800">Auto Posting</h2>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                    <div className="rounded border border-slate-200 px-2 py-3">
                      <p className="text-lg font-black">{dashboard?.posting_health.posting_rules || 0}</p>
                      <p className="text-[11px] font-semibold text-slate-500">Rules</p>
                    </div>
                    <div className="rounded border border-slate-200 px-2 py-3">
                      <p className="text-lg font-black">{dashboard?.posting_health.journal_entries || 0}</p>
                      <p className="text-[11px] font-semibold text-slate-500">Journals</p>
                    </div>
                    <div className="rounded border border-slate-200 px-2 py-3">
                      <p className="text-lg font-black">{dashboard?.posting_health.subledger_entries || 0}</p>
                      <p className="text-[11px] font-semibold text-slate-500">Sub</p>
                    </div>
                  </div>
                </section>

                <section className="rounded-md border border-slate-200 bg-white p-4">
                  <h2 className="text-sm font-black uppercase tracking-wide text-slate-800">Vouchers</h2>
                  <div className="mt-3 grid grid-cols-5 gap-1 text-center text-xs font-bold">
                    {['draft', 'verified', 'approved', 'posted', 'reversed'].map((status) => (
                      <div key={status} className="rounded border border-slate-200 py-2">
                        <p className="text-slate-950">{dashboard?.voucher_workflow[status] || 0}</p>
                        <p className="capitalize text-slate-500">{status.slice(0, 4)}</p>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 space-y-3">
                    {(dashboard?.recent_vouchers || []).map((voucher) => (
                      <div key={voucher.id} className="border-b border-slate-100 pb-3">
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-black text-slate-900">{voucher.voucher_number}</p>
                            <p className="truncate text-xs font-semibold text-slate-500">{voucher.description}</p>
                          </div>
                          <span className="rounded bg-slate-100 px-2 py-1 text-[11px] font-bold capitalize text-slate-700">{voucher.status}</span>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {voucher.status === 'draft' && (
                            <button className="rounded bg-slate-900 px-3 py-1 text-xs font-bold text-white" onClick={() => runAction(`verify-${voucher.id}`, () => apiClient.verifyVoucher(voucher.id, tenantId, user.username), 'Voucher verified.')}>Verify</button>
                          )}
                          {voucher.status === 'verified' && (
                            <button className="rounded bg-slate-900 px-3 py-1 text-xs font-bold text-white" onClick={() => runAction(`approve-${voucher.id}`, () => apiClient.approveVoucher(voucher.id, tenantId, user.username), 'Voucher approved.')}>Approve</button>
                          )}
                          {voucher.status === 'approved' && (
                            <button className="rounded bg-emerald-700 px-3 py-1 text-xs font-bold text-white" onClick={() => runAction(`post-${voucher.id}`, () => apiClient.postVoucher(voucher.id, tenantId, user.username), 'Voucher posted.')}>Post</button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="rounded-md border border-slate-200 bg-white p-4">
                  <h2 className="text-sm font-black uppercase tracking-wide text-slate-800">Trial Balance</h2>
                  <div className="mt-3 space-y-2 text-sm">
                    <div className="flex justify-between gap-3">
                      <span className="font-semibold text-slate-500">Debit</span>
                      <span className="font-black">{money(dashboard?.trial_balance.total_debit)}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                      <span className="font-semibold text-slate-500">Credit</span>
                      <span className="font-black">{money(dashboard?.trial_balance.total_credit)}</span>
                    </div>
                    <div className={`rounded px-3 py-2 text-center text-sm font-black ${dashboard?.trial_balance.is_balanced ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>
                      {dashboard?.trial_balance.is_balanced ? 'Balanced' : 'Variance'}
                    </div>
                  </div>
                </section>

                <section className="rounded-md border border-slate-200 bg-white p-4">
                  <h2 className="text-sm font-black uppercase tracking-wide text-slate-800">Recent Journals</h2>
                  <div className="mt-3 space-y-3">
                    {(dashboard?.recent_journals || []).slice(0, 6).map((journal) => (
                      <div key={journal.id} className="border-b border-slate-100 pb-2">
                        <p className="truncate text-sm font-bold text-slate-900">{journal.description}</p>
                        <p className="text-xs font-semibold capitalize text-slate-500">
                          {shortDate(journal.entry_date)} / {journal.source_module || 'manual'} / {journal.status}
                        </p>
                      </div>
                    ))}
                  </div>
                </section>
              </aside>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
