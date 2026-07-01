"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';

interface StatementLine { id: string; section?: string | null; label: string; account_code?: string | null; amount: number; line_type?: string | null; order_index: number; }
interface StatementRatio { id: string; ratio_name: string; value: number; interpretation?: string | null; }
interface StatementItem { id: string; tenant_id: string; statement_type: string; scope: string; book: string; period?: string | null; currency: string; status: string; generated_on: string; as_of?: string | null; lines: StatementLine[]; ratios: StatementRatio[]; }

export default function FinancialStatementsPage() {
  const [statements, setStatements] = useState<StatementItem[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const payload = await accountingApi.listFinancialStatements(DEFAULT_ACCOUNTING_TENANT);
      setStatements(payload.items ?? []);
    } catch {
      setStatements([]);
    } finally {
      setLoading(false);
    }
  }

  async function generate() {
    const generated = await accountingApi.generateFinancialStatement({
      tenant_id: DEFAULT_ACCOUNTING_TENANT,
      statement_type: 'balance_sheet',
      period: 'monthly',
      currency: 'INR',
    });
    setStatements((current) => [generated, ...current]);
  }

  useEffect(() => { void load(); }, []);

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Financial Statements</div>
              <h1 className="mt-2 text-2xl font-semibold text-text-primary">Balance sheet and P&L snapshots generated from the accounting core</h1>
              <p className="mt-2 max-w-3xl text-sm text-text-secondary">The statements are built from GL balances and trial-balance-ready data so finance users can review reporting views without duplicating ledger logic.</p>
            </div>
            <button onClick={() => void generate()} className="rounded-md bg-accent-primary px-3 py-2 text-sm font-medium text-white">Generate statement</button>
          </div>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Loading financial statements…</div>
        ) : (
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="mb-3 text-sm font-semibold text-text-primary">Recent statements</div>
            <div className="space-y-3">
              {statements.map((statement) => (
                <div key={statement.id} className="rounded-md border border-border-light bg-background-default p-3">
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <div className="text-sm font-semibold text-text-primary">{statement.statement_type}</div>
                      <div className="text-xs uppercase tracking-wide text-text-secondary">{statement.period ?? 'monthly'} • {statement.currency}</div>
                    </div>
                    <div className="text-sm text-text-secondary">{statement.status}</div>
                  </div>
                  <div className="mt-3 grid gap-3 md:grid-cols-2">
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Lines</div>
                      <div className="mt-2 space-y-1">
                        {statement.lines.slice(0, 4).map((line) => (
                          <div key={line.id} className="flex items-center justify-between text-sm text-text-secondary">
                            <span>{line.label}</span>
                            <span>{line.amount.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Ratios</div>
                      <div className="mt-2 space-y-1">
                        {statement.ratios.slice(0, 4).map((ratio) => (
                          <div key={ratio.id} className="flex items-center justify-between text-sm text-text-secondary">
                            <span>{ratio.ratio_name}</span>
                            <span>{ratio.value.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {statements.length === 0 ? <div className="text-sm text-text-secondary">No statements generated yet.</div> : null}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
