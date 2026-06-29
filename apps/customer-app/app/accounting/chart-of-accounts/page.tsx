"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type { GLAccount, GLDashboard } from '../accountingApi';
import { BooleanBadge, CoaPageFrame, CoaTable, EmptyState, LoadingBlock, MetricTile, StatusBadge, formatAmount } from './coaComponents';

export default function ChartOfAccountsDashboardPage() {
  const [dashboard, setDashboard] = useState<GLDashboard | null>(null);
  const [accounts, setAccounts] = useState<GLAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const [dashboardBody, listBody] = await Promise.all([
        accountingApi.getDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listAccounts(DEFAULT_ACCOUNTING_TENANT, 'limit=8'),
      ]);
      setDashboard(dashboardBody);
      setAccounts(listBody.items);
    } catch {
      setDashboard(null);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function seedDefaults() {
    setSeeding(true);
    try {
      await accountingApi.seedDefaults(DEFAULT_ACCOUNTING_TENANT);
      await load();
    } finally {
      setSeeding(false);
    }
  }

  return (
    <AppShell>
      <CoaPageFrame
        title="Chart of Accounts"
        description="Manage the enterprise financial taxonomy for posting, reporting, dimensions, tax mapping, and GL account governance."
      >
        {loading ? (
          <LoadingBlock />
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="flex flex-col gap-3 rounded-md border border-border-default bg-background-surface p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="text-sm font-semibold text-text-primary">Tenant</div>
                <div className="text-sm text-text-secondary">{DEFAULT_ACCOUNTING_TENANT}</div>
              </div>
              <button
                type="button"
                onClick={seedDefaults}
                disabled={seeding}
                className="inline-flex h-10 items-center justify-center rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60"
              >
                {seeding ? 'Seeding...' : 'Seed NBFC COA'}
              </button>
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <MetricTile label="Total Accounts" value={dashboard.kpis.total_accounts} note="Configured GL nodes" />
              <MetricTile label="Posting Accounts" value={dashboard.kpis.posting_accounts} note="Accounts open for posting" />
              <MetricTile label="Control Accounts" value={dashboard.kpis.control_accounts} note="Parent or restricted accounts" />
              <MetricTile label="AI Health" value={`${dashboard.kpis.ai_health}%`} note={dashboard.summary.status} />
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <MetricTile label="Active" value={dashboard.kpis.active_accounts} note="Operational accounts" />
              <MetricTile label="Parents" value={dashboard.kpis.parent_accounts} note="Hierarchy control nodes" />
              <MetricTile label="Pending Approvals" value={dashboard.kpis.pending_approvals} note="Workflow queue" />
            </div>

            <CoaTable columns={['GL Code', 'Account Name', 'Type', 'Category', 'Posting', 'Currency', 'Balance', 'Status']}>
              {accounts.map((account) => (
                <tr key={account.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold">
                    <Link href={`/accounting/chart-of-accounts/accounts/${account.id}`} className="text-accent-primary underline">
                      {account.gl_code}
                    </Link>
                  </td>
                  <td className="p-3">{account.name}</td>
                  <td className="p-3 text-text-secondary">{account.account_type}</td>
                  <td className="p-3 text-text-secondary">{account.category ?? '-'}</td>
                  <td className="p-3"><BooleanBadge value={account.posting_allowed} /></td>
                  <td className="p-3 text-text-secondary">{account.currency ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(account.balance, account.currency ?? 'INR')}</td>
                  <td className="p-3"><StatusBadge value={account.status} /></td>
                </tr>
              ))}
              {accounts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-text-secondary">No GL accounts found.</td>
                </tr>
              ) : null}
            </CoaTable>
          </div>
        ) : (
          <EmptyState message="Chart of Accounts API is unavailable. Check that the accounting service is running." />
        )}
      </CoaPageFrame>
    </AppShell>
  );
}
