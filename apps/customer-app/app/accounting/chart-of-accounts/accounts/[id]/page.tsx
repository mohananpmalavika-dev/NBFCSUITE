"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../../accountingApi';
import type { GLUsageResponse } from '../../../accountingApi';
import { BooleanBadge, CoaPageFrame, CoaTable, EmptyState, LoadingBlock, MetricTile, StatusBadge, formatAmount } from '../../coaComponents';

export default function AccountProfilePage() {
  const params = useParams<{ id: string }>();
  const [usage, setUsage] = useState<GLUsageResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    async function load() {
      try {
        const body = await accountingApi.getUsage(params.id, DEFAULT_ACCOUNTING_TENANT);
        if (mounted) setUsage(body);
      } catch {
        if (mounted) setUsage(null);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [params?.id]);

  return (
    <AppShell>
      <CoaPageFrame
        title="Account Profile"
        description="Inspect GL Account 360 details including posting controls, dimensions, usage, reporting, and AI summary."
      >
        {loading ? (
          <LoadingBlock />
        ) : usage ? (
          <div className="space-y-6">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="text-sm font-semibold text-accent-primary">{usage.account.gl_code}</div>
                  <h2 className="mt-1 text-xl font-semibold">{usage.account.name}</h2>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <StatusBadge value={usage.account.status} />
                    <BooleanBadge value={usage.account.posting_allowed} />
                  </div>
                </div>
                <Link href="/accounting/chart-of-accounts/directory" className="text-sm font-semibold text-accent-primary underline">
                  Back to directory
                </Link>
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <MetricTile label="Balance" value={formatAmount(usage.account.balance, usage.account.currency ?? 'INR')} note={usage.account.currency ?? 'INR'} />
              <MetricTile label="Journal Lines" value={usage.summary.transaction_count} note="Recent usage sample" />
              <MetricTile label="Debit Movement" value={formatAmount(usage.summary.total_debit, usage.account.currency ?? 'INR')} note="Recent debits" />
              <MetricTile label="Credit Movement" value={formatAmount(usage.summary.total_credit, usage.account.currency ?? 'INR')} note="Recent credits" />
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold">Controls</h3>
                <div className="mt-3 grid gap-2 text-sm">
                  <div className="flex justify-between gap-4"><span className="text-text-secondary">Type</span><span>{usage.account.account_type}</span></div>
                  <div className="flex justify-between gap-4"><span className="text-text-secondary">Category</span><span>{usage.account.category ?? '-'}</span></div>
                  <div className="flex justify-between gap-4"><span className="text-text-secondary">Normal balance</span><span>{usage.account.normal_balance ?? '-'}</span></div>
                  <div className="flex justify-between gap-4"><span className="text-text-secondary">Manual posting</span><span>{usage.account.allow_manual_posting ?? '-'}</span></div>
                  <div className="flex justify-between gap-4"><span className="text-text-secondary">Auto posting</span><span>{usage.account.allow_auto_posting ?? '-'}</span></div>
                  <div className="flex justify-between gap-4"><span className="text-text-secondary">Freeze status</span><span>{usage.account.freeze_status ?? '-'}</span></div>
                </div>
              </section>
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold">AI Summary</h3>
                <p className="mt-3 text-sm text-text-secondary">{usage.summary.ai_summary}</p>
                <div className="mt-4 text-sm text-text-secondary">
                  Dimensions: {usage.account.dimensions && usage.account.dimensions.length > 0 ? usage.account.dimensions.join(', ') : 'Not configured'}
                </div>
              </section>
            </div>

            <CoaTable columns={['Journal', 'Date', 'Description', 'Debit', 'Credit', 'Branch', 'Cost Center']}>
              {usage.recent_lines.map((line, index) => (
                <tr key={`${line.journal_entry_id}-${index}`} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold">{String(line.journal_entry_id ?? '-')}</td>
                  <td className="p-3 text-text-secondary">{String(line.entry_date ?? '-')}</td>
                  <td className="p-3">{String(line.description ?? '-')}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(Number(line.debit ?? 0), usage.account.currency ?? 'INR')}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(Number(line.credit ?? 0), usage.account.currency ?? 'INR')}</td>
                  <td className="p-3 text-text-secondary">{String(line.branch_id ?? '-')}</td>
                  <td className="p-3 text-text-secondary">{String(line.cost_center ?? '-')}</td>
                </tr>
              ))}
              {usage.recent_lines.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-text-secondary">No recent journal lines found.</td>
                </tr>
              ) : null}
            </CoaTable>
          </div>
        ) : (
          <EmptyState message="Account profile is unavailable." />
        )}
      </CoaPageFrame>
    </AppShell>
  );
}
