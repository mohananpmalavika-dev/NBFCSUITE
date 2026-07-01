"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type { TrialBalanceItem, TrialBalanceLineItem } from '../accountingApi';

function formatAmount(value: number | null | undefined, currency = 'INR') {
  const numericValue = typeof value === 'number' ? value : 0;
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency, maximumFractionDigits: 2 }).format(numericValue);
}

export default function TrialBalancePage() {
  const [dashboard, setDashboard] = useState<{
    tenant_id: string;
    kpis: Record<string, number | string>;
    charts: Record<string, Array<{ label: string; value: number }>>;
    summary: { status: string; message: string };
  } | null>(null);
  const [balances, setBalances] = useState<TrialBalanceItem[]>([]);
  const [selected, setSelected] = useState<TrialBalanceItem | null>(null);
  const [lines, setLines] = useState<TrialBalanceLineItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const [dashboardBody, balancesBody] = await Promise.all([
        accountingApi.getTrialBalanceDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listTrialBalances(DEFAULT_ACCOUNTING_TENANT),
      ]);
      setDashboard(dashboardBody);
      setBalances(balancesBody.items ?? []);
      if (balancesBody.items?.[0]) {
        const firstBalance = balancesBody.items[0];
        setSelected(firstBalance);
        const linesBody = await accountingApi.getTrialBalanceLines(firstBalance.id, DEFAULT_ACCOUNTING_TENANT);
        setLines(linesBody.items ?? []);
      }
    } catch {
      setDashboard(null);
      setBalances([]);
      setSelected(null);
      setLines([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const generated = await accountingApi.generateTrialBalance({
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        scope: 'enterprise',
        book: 'primary',
        period: '2026-27',
        currency: 'INR',
      });
      setSelected(generated);
      const linesBody = await accountingApi.getTrialBalanceLines(generated.id, DEFAULT_ACCOUNTING_TENANT);
      setLines(linesBody.items ?? []);
      await load();
    } finally {
      setGenerating(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Trial Balance</div>
              <h1 className="mt-2 text-2xl font-semibold text-text-primary">Continuous trial balance generation and validation for the enterprise ledger</h1>
              <p className="mt-2 max-w-3xl text-sm text-text-secondary">
                Generate a fresh trial balance from the existing GL and journal engine, review balance lines, and inspect validation health in one workspace.
              </p>
            </div>
            <button
              type="button"
              onClick={() => { void handleGenerate(); }}
              className="rounded-md bg-accent-primary px-4 py-2 text-sm font-semibold text-white"
              disabled={generating}
            >
              {generating ? 'Generating…' : 'Generate Trial Balance'}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Loading trial balance workspace…</div>
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              {[
                ['trial_balances_generated', 'Generated'],
                ['balanced', 'Balanced'],
                ['unbalanced', 'Unbalanced'],
                ['ai_financial_score', 'AI Score'],
              ].map(([key, label]) => (
                <div key={key} className="rounded-md border border-border-default bg-background-surface p-4">
                  <div className="text-sm text-text-secondary">{label}</div>
                  <div className="mt-2 text-2xl font-semibold text-text-primary">{dashboard.kpis[key] ?? '—'}</div>
                </div>
              ))}
            </div>

            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="mb-3 text-sm font-semibold text-text-primary">Latest trial balance snapshot</div>
              {selected ? (
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="rounded-md border border-border-light bg-background-default p-3">
                    <div className="text-sm text-text-secondary">Status</div>
                    <div className="mt-1 text-lg font-semibold text-text-primary">{selected.status}</div>
                  </div>
                  <div className="rounded-md border border-border-light bg-background-default p-3">
                    <div className="text-sm text-text-secondary">Debit</div>
                    <div className="mt-1 text-lg font-semibold text-text-primary">{formatAmount(selected.total_debit)}</div>
                  </div>
                  <div className="rounded-md border border-border-light bg-background-default p-3">
                    <div className="text-sm text-text-secondary">Credit</div>
                    <div className="mt-1 text-lg font-semibold text-text-primary">{formatAmount(selected.total_credit)}</div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-text-secondary">No trial balance generated yet.</div>
              )}
            </div>

            <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-3 text-sm font-semibold text-text-primary">History</div>
                <div className="space-y-3">
                  {balances.map((balance) => (
                    <button
                      key={balance.id}
                      type="button"
                      onClick={async () => {
                        setSelected(balance);
                        const linesBody = await accountingApi.getTrialBalanceLines(balance.id, DEFAULT_ACCOUNTING_TENANT);
                        setLines(linesBody.items ?? []);
                      }}
                      className="w-full rounded-md border border-border-light bg-background-default p-3 text-left"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="text-sm font-semibold text-text-primary">{balance.period ?? 'enterprise'}</div>
                        <div className="text-xs uppercase tracking-wide text-text-secondary">{balance.status}</div>
                      </div>
                      <div className="mt-2 text-sm text-text-secondary">{balance.book} • {balance.scope}</div>
                      <div className="mt-2 text-sm text-text-secondary">{formatAmount(balance.total_debit)} / {formatAmount(balance.total_credit)}</div>
                    </button>
                  ))}
                  {balances.length === 0 ? <div className="text-sm text-text-secondary">No historical trial balances yet.</div> : null}
                </div>
              </div>

              <div className="rounded-md border border-border-default bg-background-surface p-4">
                <div className="mb-3 text-sm font-semibold text-text-primary">Balance lines</div>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="bg-background-default text-left text-text-secondary">
                        <th className="p-2">Account</th>
                        <th className="p-2">Opening</th>
                        <th className="p-2">Period</th>
                        <th className="p-2">Closing</th>
                      </tr>
                    </thead>
                    <tbody>
                      {lines.map((line) => (
                        <tr key={line.id} className="border-t border-border-light">
                          <td className="p-2">
                            <div className="font-medium text-text-primary">{line.account_code ?? '—'}</div>
                            <div className="text-xs text-text-secondary">{line.account_name ?? '—'}</div>
                          </td>
                          <td className="p-2 text-text-secondary">{formatAmount(line.opening_debit - line.opening_credit)}</td>
                          <td className="p-2 text-text-secondary">{formatAmount(line.period_debit - line.period_credit)}</td>
                          <td className="p-2 text-text-primary">{formatAmount(line.closing_debit - line.closing_credit)}</td>
                        </tr>
                      ))}
                      {lines.length === 0 ? <tr><td colSpan={4} className="p-3 text-center text-text-secondary">No balance lines yet.</td></tr> : null}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Trial Balance API is unavailable. Check that the accounting service is running.</div>
        )}
      </div>
    </AppShell>
  );
}
