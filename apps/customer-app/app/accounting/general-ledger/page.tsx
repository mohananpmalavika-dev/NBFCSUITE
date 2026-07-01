"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type { GLAccount } from '../accountingApi';

interface LedgerDashboardPayload {
  tenant_id: string;
  kpis: {
    total_accounts: number;
    active_accounts: number;
    posted_entries: number;
    draft_entries: number;
    balance_rows: number;
    health_score: number;
  };
  charts: {
    accounts_by_currency: Array<{ label: string; value: number }>;
    entries_by_status: Array<{ label: string; value: number }>;
  };
  summary: { status: string; message: string };
}

interface LedgerBalanceItem {
  id: string;
  gl_account_id: string;
  account_code?: string | null;
  account_name?: string | null;
  branch_id?: string | null;
  currency?: string | null;
  financial_year?: string | null;
  opening_balance?: number | null;
  total_debit?: number | null;
  total_credit?: number | null;
  closing_balance?: number | null;
  updated_at?: string | null;
}

interface LedgerEntryItem {
  id: string;
  entry_date?: string | null;
  description?: string | null;
  reference?: string | null;
  source_module?: string | null;
  source_event?: string | null;
  posting_status?: string | null;
  branch_id?: string | null;
  financial_year?: string | null;
  business_date?: string | null;
  total_debit?: number | null;
  total_credit?: number | null;
  line_count?: number | null;
}

function formatAmount(value: number | null | undefined, currency = 'INR') {
  const numericValue = typeof value === 'number' ? value : 0;
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency, maximumFractionDigits: 2 }).format(numericValue);
}

export default function GeneralLedgerPage() {
  const [dashboard, setDashboard] = useState<LedgerDashboardPayload | null>(null);
  const [balances, setBalances] = useState<LedgerBalanceItem[]>([]);
  const [entries, setEntries] = useState<LedgerEntryItem[]>([]);
  const [accounts, setAccounts] = useState<GLAccount[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [dashboardBody, balancesBody, entriesBody, accountsBody] = await Promise.all([
        accountingApi.getDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.getGeneralLedgerBalances(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.getGeneralLedgerEntries(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listAccounts(DEFAULT_ACCOUNTING_TENANT, 'limit=6'),
      ]);
      setDashboard({
        tenant_id: dashboardBody.tenant_id,
        kpis: {
          total_accounts: dashboardBody.kpis.total_accounts,
          active_accounts: dashboardBody.kpis.active_accounts,
          posted_entries: dashboardBody.kpis.posting_accounts,
          draft_entries: dashboardBody.kpis.pending_approvals,
          balance_rows: 0,
          health_score: dashboardBody.kpis.ai_health,
        },
        charts: {
          accounts_by_currency: [],
          entries_by_status: [],
        },
        summary: dashboardBody.summary,
      });
      setBalances((balancesBody as { items?: LedgerBalanceItem[] }).items ?? []);
      setEntries((entriesBody as { items?: LedgerEntryItem[] }).items ?? []);
      setAccounts(accountsBody.items ?? []);
    } catch {
      setDashboard(null);
      setBalances([]);
      setEntries([]);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">General Ledger</div>
              <h1 className="mt-2 text-2xl font-semibold text-text-primary">Enterprise ledger activity, balances, and posting visibility</h1>
              <p className="mt-2 max-w-3xl text-sm text-text-secondary">
                Review balances, recent journal entries, and the GL population from a single workspace aligned with the existing accounting service.
              </p>
            </div>
            <div className="rounded-md border border-border-default bg-background-default px-3 py-2 text-sm text-text-secondary">
              Tenant {DEFAULT_ACCOUNTING_TENANT}
            </div>
          </div>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Loading ledger workspace…</div>
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">Accounts</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard.kpis.total_accounts}</div>
              </div>
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">Active Accounts</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard.kpis.active_accounts}</div>
              </div>
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">Posted Entries</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard.kpis.posted_entries}</div>
              </div>
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="text-sm text-text-secondary">Health</div>
                <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard.kpis.health_score}%</div>
              </div>
            </div>

            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="mb-3 text-sm font-semibold text-text-primary">GL Accounts in Scope</div>
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {accounts.map((account) => (
                  <div key={account.id} className="rounded-md border border-border-light bg-background-default p-3">
                    <div className="text-sm font-semibold text-text-primary">{account.account_code}</div>
                    <div className="mt-1 text-sm text-text-secondary">{account.account_name}</div>
                    <div className="mt-2 text-xs uppercase tracking-wide text-text-secondary">{account.account_type}</div>
                  </div>
                ))}
                {accounts.length === 0 ? <div className="text-sm text-text-secondary">No accounts surfaced yet.</div> : null}
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-3 flex items-center justify-between">
                  <div className="text-sm font-semibold text-text-primary">Ledger Balances</div>
                  <Link href="/accounting/journal-engine" className="text-sm text-accent-primary underline">Open journal engine</Link>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="bg-background-default text-left text-text-secondary">
                        <th className="p-2">Account</th>
                        <th className="p-2">Branch</th>
                        <th className="p-2">Currency</th>
                        <th className="p-2">Closing</th>
                      </tr>
                    </thead>
                    <tbody>
                      {balances.map((balance) => (
                        <tr key={balance.id} className="border-t border-border-light">
                          <td className="p-2">
                            <div className="font-medium text-text-primary">{balance.account_code ?? balance.gl_account_id}</div>
                            <div className="text-xs text-text-secondary">{balance.account_name ?? '—'}</div>
                          </td>
                          <td className="p-2 text-text-secondary">{balance.branch_id ?? 'all'}</td>
                          <td className="p-2 text-text-secondary">{balance.currency ?? 'INR'}</td>
                          <td className="p-2 text-text-primary">{formatAmount(balance.closing_balance ?? 0, balance.currency ?? 'INR')}</td>
                        </tr>
                      ))}
                      {balances.length === 0 ? <tr><td colSpan={4} className="p-3 text-center text-text-secondary">No balance rows found.</td></tr> : null}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-3 text-sm font-semibold text-text-primary">Recent Ledger Entries</div>
                <div className="space-y-3">
                  {entries.map((entry) => (
                    <div key={entry.id} className="rounded-md border border-border-light bg-background-default p-3">
                      <div className="flex items-center justify-between gap-2">
                        <div className="text-sm font-semibold text-text-primary">{entry.description ?? entry.reference ?? 'Journal entry'}</div>
                        <div className="text-xs uppercase tracking-wide text-text-secondary">{entry.posting_status ?? 'draft'}</div>
                      </div>
                      <div className="mt-2 text-sm text-text-secondary">{entry.source_module ?? 'manual'} • {entry.reference ?? '—'}</div>
                      <div className="mt-2 flex items-center justify-between text-sm text-text-secondary">
                        <span>{entry.branch_id ?? 'all'}</span>
                        <span>{formatAmount(entry.total_debit ?? 0, 'INR')}</span>
                      </div>
                    </div>
                  ))}
                  {entries.length === 0 ? <div className="text-sm text-text-secondary">No entries available.</div> : null}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Ledger API is unavailable. Check that the accounting service is running.</div>
        )}
      </div>
    </AppShell>
  );
}
