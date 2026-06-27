'use client';

import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { useCallback, useEffect, useMemo, useState } from 'react';

type TabKey = 'coa' | 'posting' | 'vouchers' | 'statements' | 'dayend';

interface GlAccount {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  parent_account_id?: string | null;
  category?: string | null;
  currency?: string | null;
  branch_id?: string | null;
  branch_specific?: string | null;
  posting_allowed?: string | null;
  status?: string | null;
  financial_year?: string | null;
  balance: number;
}

interface CoaCategorySummary {
  category: string;
  count: number;
  posting_allowed: number;
  control_accounts: number;
  balance: number;
}

interface CoaSummary {
  total_accounts: number;
  posting_accounts: number;
  control_accounts: number;
  categories: CoaCategorySummary[];
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

interface TrialBalanceRow {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  debit: number;
  credit: number;
}

interface Voucher {
  id: string;
  voucher_number: string;
  voucher_type: string;
  description: string;
  reference?: string | null;
  status: string;
  posted_journal_entry_id?: string | null;
}

interface LedgerRow {
  gl_account_id: string;
  gl_number?: string | null;
  account_code?: string | null;
  account_name?: string | null;
  branch?: string | null;
  branch_id?: string | null;
  currency: string;
  financial_year: string;
  opening_balance: number;
  debit: number;
  credit: number;
  balance: number;
  closing_balance: number;
}

interface Dashboard {
  chart_of_accounts: number;
  posting_rules: number;
  journal_entries: number;
  subledger_entries: number;
  pending_vouchers: number;
  trial_balance: {
    total_debit: number;
    total_credit: number;
    is_balanced: boolean;
  };
}

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'coa', label: 'COA' },
  { key: 'posting', label: 'Posting Engine' },
  { key: 'vouchers', label: 'Vouchers' },
  { key: 'statements', label: 'Statements' },
  { key: 'dayend', label: 'Day End' },
];

function money(value: number | undefined) {
  return Number(value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function errorText(error: unknown, fallback: string) {
  const candidate = error as { response?: { data?: { detail?: string } } };
  return candidate?.response?.data?.detail || fallback;
}

function accountLabel(account: GlAccount) {
  return `${account.account_code} - ${account.account_name}`;
}

function CoaTreeRows({ nodes, depth = 0 }: { nodes: CoaTreeNode[]; depth?: number }) {
  return (
    <>
      {nodes.map((node) => (
        <div key={node.id}>
          <div
            className="grid grid-cols-[1fr_auto_auto] gap-3 border-b border-slate-100 py-2 text-sm"
            style={{ paddingLeft: `${depth * 16}px` }}
          >
            <div>
              <p className="font-medium text-slate-900">{node.account_code} - {node.account_name}</p>
              <p className="text-xs text-slate-500">{node.category || node.account_type}</p>
            </div>
            <span className="text-xs text-slate-500">{node.posting_allowed === 'false' ? 'Control' : 'Posting'}</span>
            <span className="text-right text-slate-700">{money(node.balance)}</span>
          </div>
          {node.children.length > 0 && <CoaTreeRows nodes={node.children} depth={depth + 1} />}
        </div>
      ))}
    </>
  );
}

export default function AccountingPage() {
  const { user, token, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabKey>('coa');
  const [message, setMessage] = useState('');
  const [busyAction, setBusyAction] = useState('');
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [accounts, setAccounts] = useState<GlAccount[]>([]);
  const [coaSummary, setCoaSummary] = useState<CoaSummary | null>(null);
  const [coaTree, setCoaTree] = useState<CoaTreeNode[]>([]);
  const [trialRows, setTrialRows] = useState<TrialBalanceRow[]>([]);
  const [ledgerRows, setLedgerRows] = useState<LedgerRow[]>([]);
  const [vouchers, setVouchers] = useState<Voucher[]>([]);
  const [dayEndRows, setDayEndRows] = useState<Array<{ id: string; business_date: string; status: string; is_balanced: string }>>([]);

  const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || 'default';

  const [accountForm, setAccountForm] = useState({
    account_code: '',
    account_name: '',
    account_type: 'asset',
    parent_account_id: '',
    category: 'Assets',
    currency: 'INR',
    branch_id: '',
    branch_specific: 'false',
    posting_allowed: 'true',
    status: 'active',
    financial_year: '2026-27',
  });
  const [ruleForm, setRuleForm] = useState({
    source_module: 'loans',
    source_event: 'disbursement',
    debit_account_code: '',
    credit_account_code: '',
    description: '',
  });
  const [postingForm, setPostingForm] = useState({
    source_module: 'manual',
    source_event: 'adjustment',
    source_reference: '',
    description: '',
    debit_account_id: '',
    credit_account_id: '',
    amount: '0',
    branch_id: '',
  });
  const [voucherForm, setVoucherForm] = useState({
    voucher_type: 'journal',
    description: '',
    reference: '',
    debit_account_id: '',
    credit_account_id: '',
    amount: '0',
    branch_id: '',
  });
  const [dayEndForm, setDayEndForm] = useState({
    business_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
  });

  const selectableAccounts = useMemo(
    () => accounts.filter((account) => String(account.posting_allowed || 'true').toLowerCase() !== 'false'),
    [accounts],
  );

  const refresh = useCallback(async () => {
    if (!token || !tenantId) return;
    try {
      const [dashboardRes, accountsRes, trialRes, ledgerRes, vouchersRes, dayEndRes] = await Promise.all([
        apiClient.getAccountingDashboard(tenantId),
        apiClient.getGlAccounts(tenantId),
        apiClient.getTrialBalance(tenantId),
        apiClient.getGlLedger(tenantId),
        apiClient.getVouchers(tenantId),
        apiClient.getDayEndCloses(tenantId),
      ]);
      setDashboard(dashboardRes.data);
      setAccounts(accountsRes.data || []);
      const [summaryRes, hierarchyRes] = await Promise.all([
        apiClient.getGlAccountSummary(tenantId),
        apiClient.getGlAccountHierarchy(tenantId),
      ]);
      setCoaSummary(summaryRes.data || null);
      setCoaTree(hierarchyRes.data.items || []);
      setTrialRows(trialRes.data.rows || []);
      setLedgerRows(ledgerRes.data.items || []);
      setVouchers(vouchersRes.data.items || []);
      setDayEndRows(dayEndRes.data || []);
    } catch (error) {
      setMessage(errorText(error, 'Unable to load accounting workspace.'));
    }
  }, [tenantId, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function runAction(name: string, action: () => Promise<unknown>, success: string) {
    setBusyAction(name);
    setMessage('');
    try {
      await action();
      setMessage(success);
      await refresh();
    } catch (error) {
      setMessage(errorText(error, `${success} failed.`));
    } finally {
      setBusyAction('');
    }
  }

  const amount = Number(postingForm.amount || 0);
  const voucherAmount = Number(voucherForm.amount || 0);
  const canPost = postingForm.debit_account_id && postingForm.credit_account_id && amount > 0;
  const canCreateVoucher = voucherForm.debit_account_id && voucherForm.credit_account_id && voucherAmount > 0 && voucherForm.description;

  if (isLoading || !token) {
    return <div className="p-8 text-center">Loading accounting data...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
            <div>
              <p className="text-xs font-semibold uppercase text-blue-700">Enterprise Accounting Suite</p>
              <h1 className="mt-1 text-3xl font-bold text-slate-950">Accounting & General Ledger</h1>
              <p className="mt-2 max-w-3xl text-sm text-slate-600">
                Central posting engine, chart of accounts, vouchers, sub-ledger visibility, financial statements,
                and day-end controls for the tenant ledger.
              </p>
            </div>
            <button
              type="button"
              onClick={refresh}
              className="h-10 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-800 hover:border-blue-400"
            >
              Refresh
            </button>
          </div>
        </section>

        {message && (
          <div className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">{message}</div>
        )}

        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
          {[
            ['COA', dashboard?.chart_of_accounts],
            ['Posting Rules', dashboard?.posting_rules],
            ['Journals', dashboard?.journal_entries],
            ['Sub Ledger', dashboard?.subledger_entries],
            ['Pending Vouchers', dashboard?.pending_vouchers],
            ['Balanced', dashboard?.trial_balance?.is_balanced ? 'Yes' : 'No'],
          ].map(([label, value]) => (
            <div key={String(label)} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
              <dd className="mt-2 text-2xl font-bold text-slate-950">{value ?? 0}</dd>
            </div>
          ))}
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`h-9 rounded-md px-3 text-sm font-semibold ${
                  activeTab === tab.key ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'coa' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'account',
                    async () => {
                      await apiClient.createGlAccount({
                        tenant_id: tenantId,
                        ...accountForm,
                        parent_account_id: accountForm.parent_account_id || undefined,
                        branch_id: accountForm.branch_id || undefined,
                      });
                      setAccountForm({ ...accountForm, account_code: '', account_name: '', parent_account_id: '', branch_id: '' });
                    },
                    'GL account created.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Chart of Accounts</h2>
                <button
                  type="button"
                  disabled={!!busyAction}
                  onClick={() =>
                    runAction(
                      'seed-coa',
                      () => apiClient.seedDefaultGlAccounts({ tenant_id: tenantId, currency: accountForm.currency, financial_year: accountForm.financial_year }),
                      'Default NBFC COA seeded.',
                    )
                  }
                  className="h-10 rounded-md border border-blue-300 bg-blue-50 px-4 text-sm font-semibold text-blue-800 disabled:opacity-50"
                >
                  {busyAction === 'seed-coa' ? 'Seeding...' : 'Seed NBFC COA'}
                </button>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="GL Code" value={accountForm.account_code} onChange={(e) => setAccountForm({ ...accountForm, account_code: e.target.value })} />
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="GL Name" value={accountForm.account_name} onChange={(e) => setAccountForm({ ...accountForm, account_name: e.target.value })} />
                <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={accountForm.parent_account_id} onChange={(e) => setAccountForm({ ...accountForm, parent_account_id: e.target.value })}>
                  <option value="">No parent GL</option>
                  {accounts.map((account) => (
                    <option key={account.id} value={account.id}>{accountLabel(account)}</option>
                  ))}
                </select>
                <div className="grid gap-3 sm:grid-cols-2">
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={accountForm.account_type} onChange={(e) => setAccountForm({ ...accountForm, account_type: e.target.value, category: e.target.options[e.target.selectedIndex].text })}>
                    <option value="asset">Assets</option>
                    <option value="liability">Liabilities</option>
                    <option value="revenue">Income</option>
                    <option value="expense">Expenses</option>
                    <option value="equity">Capital</option>
                    <option value="off_balance">Off Balance Sheet</option>
                    <option value="memo">Memo Accounts</option>
                  </select>
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={accountForm.posting_allowed} onChange={(e) => setAccountForm({ ...accountForm, posting_allowed: e.target.value })}>
                    <option value="true">Posting Allowed</option>
                    <option value="false">Control Only</option>
                  </select>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Currency" value={accountForm.currency} onChange={(e) => setAccountForm({ ...accountForm, currency: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Optional Branch ID" value={accountForm.branch_id} onChange={(e) => setAccountForm({ ...accountForm, branch_id: e.target.value })} />
                </div>
                <button disabled={!!busyAction || !accountForm.account_code || !accountForm.account_name} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'account' ? 'Saving...' : 'Create GL Account'}
                </button>
              </form>

              <div className="space-y-5">
                <div className="grid gap-3 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Total GLs</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{coaSummary?.total_accounts || 0}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Posting</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{coaSummary?.posting_accounts || 0}</dd>
                  </div>
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <dt className="text-xs font-semibold uppercase text-slate-500">Control</dt>
                    <dd className="mt-1 text-2xl font-bold text-slate-950">{coaSummary?.control_accounts || 0}</dd>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[620px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Category</th>
                        <th className="px-3 py-2 text-right">Accounts</th>
                        <th className="px-3 py-2 text-right">Posting</th>
                        <th className="px-3 py-2 text-right">Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(coaSummary?.categories || []).map((row) => (
                        <tr key={row.category} className="border-b border-slate-100">
                          <td className="px-3 py-2 font-medium text-slate-900">{row.category}</td>
                          <td className="px-3 py-2 text-right text-slate-700">{row.count}</td>
                          <td className="px-3 py-2 text-right text-slate-700">{row.posting_allowed}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div>
                  <h3 className="text-base font-semibold text-slate-950">COA Hierarchy</h3>
                  <div className="mt-3 max-h-[420px] overflow-auto rounded-lg border border-slate-200 px-3">
                    {coaTree.length === 0 ? (
                      <p className="py-4 text-sm text-slate-600">No chart of accounts hierarchy available.</p>
                    ) : (
                      <CoaTreeRows nodes={coaTree} />
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'posting' && (
            <div className="mt-5 grid gap-6 lg:grid-cols-2">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'rule',
                    async () => {
                      await apiClient.createPostingRule({ tenant_id: tenantId, ...ruleForm });
                      setRuleForm({ ...ruleForm, description: '' });
                    },
                    'Posting rule created.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Posting Rule</h2>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={ruleForm.source_module} onChange={(e) => setRuleForm({ ...ruleForm, source_module: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={ruleForm.source_event} onChange={(e) => setRuleForm({ ...ruleForm, source_event: e.target.value })} />
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Debit GL Code" value={ruleForm.debit_account_code} onChange={(e) => setRuleForm({ ...ruleForm, debit_account_code: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Credit GL Code" value={ruleForm.credit_account_code} onChange={(e) => setRuleForm({ ...ruleForm, credit_account_code: e.target.value })} />
                </div>
                <button disabled={!!busyAction || !ruleForm.debit_account_code || !ruleForm.credit_account_code} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'rule' ? 'Saving...' : 'Create Posting Rule'}
                </button>
              </form>

              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'posting',
                    async () => {
                      await apiClient.postAccountingEngine({
                        tenant_id: tenantId,
                        source_module: postingForm.source_module,
                        source_event: postingForm.source_event,
                        source_reference: postingForm.source_reference || `MAN-${Date.now()}`,
                        description: postingForm.description,
                        branch_id: postingForm.branch_id || undefined,
                        lines: [
                          { gl_account_id: postingForm.debit_account_id, debit: amount, credit: 0, branch_id: postingForm.branch_id || undefined },
                          { gl_account_id: postingForm.credit_account_id, debit: 0, credit: amount, branch_id: postingForm.branch_id || undefined },
                        ],
                      });
                      setPostingForm({ ...postingForm, source_reference: '', description: '', amount: '0' });
                    },
                    'Transaction posted.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Transaction Engine</h2>
                <div className="grid gap-3 sm:grid-cols-2">
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.source_module} onChange={(e) => setPostingForm({ ...postingForm, source_module: e.target.value })} />
                  <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.source_event} onChange={(e) => setPostingForm({ ...postingForm, source_event: e.target.value })} />
                </div>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Reference" value={postingForm.source_reference} onChange={(e) => setPostingForm({ ...postingForm, source_reference: e.target.value })} />
                <div className="grid gap-3 sm:grid-cols-2">
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.debit_account_id} onChange={(e) => setPostingForm({ ...postingForm, debit_account_id: e.target.value })}>
                    <option value="">Debit account</option>
                    {selectableAccounts.map((account) => <option key={account.id} value={account.id}>{accountLabel(account)}</option>)}
                  </select>
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={postingForm.credit_account_id} onChange={(e) => setPostingForm({ ...postingForm, credit_account_id: e.target.value })}>
                    <option value="">Credit account</option>
                    {selectableAccounts.map((account) => <option key={account.id} value={account.id}>{accountLabel(account)}</option>)}
                  </select>
                </div>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" type="number" value={postingForm.amount} onChange={(e) => setPostingForm({ ...postingForm, amount: e.target.value })} />
                <button disabled={!!busyAction || !canPost} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'posting' ? 'Posting...' : 'Validate & Post'}
                </button>
              </form>
            </div>
          )}

          {activeTab === 'vouchers' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'voucher',
                    async () => {
                      await apiClient.createVoucher({
                        tenant_id: tenantId,
                        voucher_type: voucherForm.voucher_type,
                        description: voucherForm.description,
                        reference: voucherForm.reference,
                        branch_id: voucherForm.branch_id || undefined,
                        created_by: user?.username || 'system',
                        lines: [
                          { gl_account_id: voucherForm.debit_account_id, debit: voucherAmount, credit: 0 },
                          { gl_account_id: voucherForm.credit_account_id, debit: 0, credit: voucherAmount },
                        ],
                      });
                      setVoucherForm({ ...voucherForm, description: '', reference: '', amount: '0' });
                    },
                    'Voucher created.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Voucher Workflow</h2>
                <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={voucherForm.voucher_type} onChange={(e) => setVoucherForm({ ...voucherForm, voucher_type: e.target.value })}>
                  <option value="journal">Journal Voucher</option>
                  <option value="receipt">Receipt Voucher</option>
                  <option value="payment">Payment Voucher</option>
                  <option value="contra">Contra Voucher</option>
                  <option value="credit_note">Credit Note</option>
                  <option value="debit_note">Debit Note</option>
                </select>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Description" value={voucherForm.description} onChange={(e) => setVoucherForm({ ...voucherForm, description: e.target.value })} />
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Reference" value={voucherForm.reference} onChange={(e) => setVoucherForm({ ...voucherForm, reference: e.target.value })} />
                <div className="grid gap-3 sm:grid-cols-2">
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={voucherForm.debit_account_id} onChange={(e) => setVoucherForm({ ...voucherForm, debit_account_id: e.target.value })}>
                    <option value="">Debit account</option>
                    {selectableAccounts.map((account) => <option key={account.id} value={account.id}>{accountLabel(account)}</option>)}
                  </select>
                  <select className="h-10 rounded-md border border-slate-300 px-3 text-sm" value={voucherForm.credit_account_id} onChange={(e) => setVoucherForm({ ...voucherForm, credit_account_id: e.target.value })}>
                    <option value="">Credit account</option>
                    {selectableAccounts.map((account) => <option key={account.id} value={account.id}>{accountLabel(account)}</option>)}
                  </select>
                </div>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" type="number" value={voucherForm.amount} onChange={(e) => setVoucherForm({ ...voucherForm, amount: e.target.value })} />
                <button disabled={!!busyAction || !canCreateVoucher} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'voucher' ? 'Saving...' : 'Create Voucher'}
                </button>
              </form>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[720px] text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-slate-500">
                      <th className="px-3 py-2">Voucher</th>
                      <th className="px-3 py-2">Type</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {vouchers.map((voucher) => (
                      <tr key={voucher.id} className="border-b border-slate-100">
                        <td className="px-3 py-2">
                          <p className="font-medium text-slate-900">{voucher.voucher_number}</p>
                          <p className="text-slate-500">{voucher.description}</p>
                        </td>
                        <td className="px-3 py-2 text-slate-700">{voucher.voucher_type}</td>
                        <td className="px-3 py-2 text-slate-700">{voucher.status}</td>
                        <td className="px-3 py-2">
                          <div className="flex flex-wrap gap-2">
                            {voucher.status === 'draft' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('verify', () => apiClient.verifyVoucher(voucher.id, tenantId, user?.username), 'Voucher verified.')}>Verify</button>}
                            {voucher.status === 'verified' && <button className="rounded-md bg-slate-100 px-3 py-1 font-semibold text-slate-700" onClick={() => runAction('approve', () => apiClient.approveVoucher(voucher.id, tenantId, user?.username), 'Voucher approved.')}>Approve</button>}
                            {voucher.status === 'approved' && <button className="rounded-md bg-blue-600 px-3 py-1 font-semibold text-white" onClick={() => runAction('post-voucher', () => apiClient.postVoucher(voucher.id, tenantId, user?.username), 'Voucher posted.')}>Post</button>}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'statements' && (
            <div className="mt-5 grid gap-6 xl:grid-cols-2">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">Trial Balance</h2>
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full min-w-[620px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">Code</th>
                        <th className="px-3 py-2">Name</th>
                        <th className="px-3 py-2 text-right">Debit</th>
                        <th className="px-3 py-2 text-right">Credit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trialRows.map((row) => (
                        <tr key={row.account_id} className="border-b border-slate-100">
                          <td className="px-3 py-2 font-medium text-slate-900">{row.account_code}</td>
                          <td className="px-3 py-2 text-slate-700">{row.account_name}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.debit)}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.credit)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-slate-950">General Ledger Book</h2>
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full min-w-[900px] text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-left text-slate-500">
                        <th className="px-3 py-2">GL Number</th>
                        <th className="px-3 py-2">Branch</th>
                        <th className="px-3 py-2">Currency</th>
                        <th className="px-3 py-2 text-right">Opening</th>
                        <th className="px-3 py-2 text-right">Debit</th>
                        <th className="px-3 py-2 text-right">Credit</th>
                        <th className="px-3 py-2 text-right">Balance</th>
                        <th className="px-3 py-2 text-right">Closing</th>
                        <th className="px-3 py-2">FY</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ledgerRows.map((row) => (
                        <tr key={`${row.gl_account_id}-${row.financial_year}-${row.branch_id || 'all'}`} className="border-b border-slate-100">
                          <td className="px-3 py-2 text-slate-900">
                            <p className="font-medium">{row.gl_number || row.account_code}</p>
                            <p className="text-xs text-slate-500">{row.account_name}</p>
                          </td>
                          <td className="px-3 py-2 text-slate-700">{row.branch || row.branch_id || 'All'}</td>
                          <td className="px-3 py-2 text-slate-700">{row.currency}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.opening_balance)}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.debit)}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.credit)}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.balance)}</td>
                          <td className="px-3 py-2 text-right text-slate-900">{money(row.closing_balance)}</td>
                          <td className="px-3 py-2 text-slate-700">{row.financial_year}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'dayend' && (
            <div className="mt-5 grid gap-6 lg:grid-cols-[0.7fr_1.3fr]">
              <form
                className="grid gap-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction(
                    'dayend',
                    async () => {
                      await apiClient.closeDayEnd({
                        tenant_id: tenantId,
                        business_date: `${dayEndForm.business_date}T23:59:59`,
                        branch_id: dayEndForm.branch_id || undefined,
                        closed_by: user?.username || 'system',
                      });
                    },
                    'Day end closed.',
                  );
                }}
              >
                <h2 className="text-lg font-semibold text-slate-950">Close Business Date</h2>
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" type="date" value={dayEndForm.business_date} onChange={(e) => setDayEndForm({ ...dayEndForm, business_date: e.target.value })} />
                <input className="h-10 rounded-md border border-slate-300 px-3 text-sm" placeholder="Optional branch id" value={dayEndForm.branch_id} onChange={(e) => setDayEndForm({ ...dayEndForm, branch_id: e.target.value })} />
                <button disabled={!!busyAction || !dayEndForm.business_date} className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50">
                  {busyAction === 'dayend' ? 'Closing...' : 'Run EOD Close'}
                </button>
              </form>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[520px] text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-slate-500">
                      <th className="px-3 py-2">Business Date</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Balanced</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dayEndRows.map((row) => (
                      <tr key={row.id} className="border-b border-slate-100">
                        <td className="px-3 py-2 text-slate-900">{new Date(row.business_date).toLocaleDateString()}</td>
                        <td className="px-3 py-2 text-slate-700">{row.status}</td>
                        <td className="px-3 py-2 text-slate-700">{row.is_balanced}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
