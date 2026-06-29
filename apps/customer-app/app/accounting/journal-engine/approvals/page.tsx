"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { Journal } from '../../accountingApi';
import { EmptyState, JournalActionButton, JournalBadge, JournalPageFrame, JournalTable, LoadingBlock, formatAmount, formatDate } from '../journalComponents';

export default function JournalApprovalsPage() {
  const [journals, setJournals] = useState<Journal[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listJournals(DEFAULT_ACCOUNTING_TENANT, 'status=draft,pending,approved&limit=100');
      setJournals(body.items);
      setMessage('');
    } catch {
      setJournals([]);
      setMessage('Unable to load approval queue.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function approve(id: string) {
    setMessage('Approving journal...');
    try {
      await accountingApi.approveJournal(id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal approved.');
    } catch {
      setMessage('Approval failed.');
    }
  }

  async function post(id: string) {
    setMessage('Posting journal...');
    try {
      await accountingApi.postJournal(id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal posted.');
    } catch {
      setMessage('Posting failed.');
    }
  }

  return (
    <AppShell>
      <JournalPageFrame title="Approval Queue" description="Maker-checker controls for manual journals, adjustments, high-value entries, and intercompany postings.">
        <div className="space-y-4">
          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}
          {loading ? (
            <LoadingBlock />
          ) : journals.length === 0 ? (
            <EmptyState message="No journals are waiting for approval." />
          ) : (
            <JournalTable columns={['Journal', 'Type', 'Amount', 'Created By', 'Posting Date', 'Status', 'Action']}>
              {journals.map((journal) => (
                <tr key={journal.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold"><Link href={`/accounting/journal-engine/journals/${journal.id}`} className="text-accent-primary underline">{journal.journal_number ?? journal.journal_no}</Link></td>
                  <td className="p-3 text-text-secondary">{journal.journal_type ?? journal.voucher_type}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(journal.amount ?? journal.total_debit, journal.currency ?? 'INR')}</td>
                  <td className="p-3 text-text-secondary">{journal.created_by ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatDate(journal.posting_date ?? journal.entry_date)}</td>
                  <td className="p-3"><JournalBadge value={journal.status} /></td>
                  <td className="p-3">
                    {journal.status === 'approved' ? (
                      <JournalActionButton onClick={() => post(journal.id)}>Post</JournalActionButton>
                    ) : (
                      <JournalActionButton onClick={() => approve(journal.id)}>Approve</JournalActionButton>
                    )}
                  </td>
                </tr>
              ))}
            </JournalTable>
          )}
        </div>
      </JournalPageFrame>
    </AppShell>
  );
}
