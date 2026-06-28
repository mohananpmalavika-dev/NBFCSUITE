'use client';

import { apiClient, type AccountingQuickActionPayload } from '@/lib/api';
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
    journal_entries: number;
    subledger_entries: number;
    automation_rate: number;
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

const actions: Array<{ key: ActionType; label: string; source: string }> = [
  { key: 'loan_disbursed', label: 'Loan disbursed', source: 'Loans' },
  { key: 'customer_paid_emi', label: 'Customer paid EMI', source: 'Loans' },
  { key: 'deposit_received', label: 'Deposit received', source: 'Deposits' },
  { key: 'expense_paid', label: 'Expense paid', source: 'Expenses' },
  { key: 'salary_paid', label: 'Salary paid', source: 'HRMS' },
  { key: 'interest_accrued', label: 'Interest accrued', source: 'Loans' },
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
      const response = await apiClient.getAccounting360Dashboard(tenantId);
      const data = response.data as Dashboard360;
      setDashboard(data);
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
