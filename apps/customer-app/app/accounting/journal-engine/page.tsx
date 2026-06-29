"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type { Journal, JournalDashboard } from '../accountingApi';
import { EmptyState, JournalBadge, JournalMetric, JournalPageFrame, JournalTable, LoadingBlock, formatAmount, formatDate } from './journalComponents';

export default function JournalEngineDashboardPage() {
  const [dashboard, setDashboard] = useState<JournalDashboard | null>(null);
  const [journals, setJournals] = useState<Journal[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [dashboardBody, journalBody] = await Promise.all([
        accountingApi.getJournalDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listJournals(DEFAULT_ACCOUNTING_TENANT, 'limit=8'),
      ]);
      setDashboard(dashboardBody);
      setJournals(journalBody.items);
    } catch {
      setDashboard(null);
      setJournals([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <JournalPageFrame title="Journal Engine" description="Create, validate, approve, post, reverse, and audit balanced enterprise journals with complete traceability.">
        {loading ? (
          <LoadingBlock />
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm font-semibold text-text-primary">Tenant</div>
              <div className="text-sm text-text-secondary">{DEFAULT_ACCOUNTING_TENANT}</div>
              <div className="mt-2 text-sm text-text-secondary">{dashboard.summary.message}</div>
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <JournalMetric label="Today's Journals" value={dashboard.kpis.todays_journals} note="Created or posted today" />
              <JournalMetric label="Posted" value={dashboard.kpis.posted} note="Locked into the ledger" />
              <JournalMetric label="Pending Approval" value={dashboard.kpis.pending_approval} note="Maker-checker queue" />
              <JournalMetric label="Journal Health" value={`${dashboard.kpis.journal_health}%`} note={dashboard.summary.status} />
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              <JournalMetric label="Draft" value={dashboard.kpis.draft} note="Editable journals" />
              <JournalMetric label="Reversed" value={dashboard.kpis.reversed} note="Controlled reversal trail" />
              <JournalMetric label="Recurring" value={dashboard.kpis.recurring} note="Active templates" />
              <JournalMetric label="Total Amount" value={formatAmount(dashboard.kpis.total_amount)} note="Debit-side journal volume" />
            </div>

            <JournalTable columns={['Journal Number', 'Business Event', 'Type', 'Branch', 'Amount', 'Currency', 'Status', 'Posting Date']}>
              {journals.map((journal) => (
                <tr key={journal.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold"><Link href={`/accounting/journal-engine/journals/${journal.id}`} className="text-accent-primary underline">{journal.journal_number ?? journal.journal_no}</Link></td>
                  <td className="p-3 text-text-secondary">{journal.business_event ?? journal.source_event ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{journal.journal_type ?? journal.voucher_type ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{journal.branch_id ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(journal.amount ?? journal.total_debit, journal.currency ?? 'INR')}</td>
                  <td className="p-3 text-text-secondary">{journal.currency ?? 'INR'}</td>
                  <td className="p-3"><JournalBadge value={journal.status} /></td>
                  <td className="p-3 text-text-secondary">{formatDate(journal.posting_date ?? journal.entry_date)}</td>
                </tr>
              ))}
              {journals.length === 0 ? <tr><td colSpan={8} className="p-6 text-center text-text-secondary">No journals found.</td></tr> : null}
            </JournalTable>
          </div>
        ) : (
          <EmptyState message="Journal Engine API is unavailable. Check that the accounting service is running." />
        )}
      </JournalPageFrame>
    </AppShell>
  );
}
