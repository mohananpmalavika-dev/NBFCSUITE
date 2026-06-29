"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { Journal } from '../../accountingApi';
import { EmptyState, JournalActionButton, JournalBadge, JournalPageFrame, JournalTable, LoadingBlock, formatAmount, formatDate } from '../journalComponents';

export default function JournalReversalsPage() {
  const [journals, setJournals] = useState<Journal[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listJournals(DEFAULT_ACCOUNTING_TENANT, 'status=posted,reversed&limit=100');
      setJournals(body.items);
      setMessage('');
    } catch {
      setJournals([]);
      setMessage('Unable to load reversal register.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function reverse(id: string) {
    setMessage('Reversing journal...');
    try {
      await accountingApi.reverseJournal(id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal reversed.');
    } catch {
      setMessage('Unable to reverse journal.');
    }
  }

  return (
    <AppShell>
      <JournalPageFrame title="Reversals" description="Control automatic, manual, scheduled, partial, and full reversal workflows with traceable reversal journals.">
        <div className="space-y-4">
          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}
          {loading ? (
            <LoadingBlock />
          ) : journals.length === 0 ? (
            <EmptyState message="No posted or reversed journals found." />
          ) : (
            <JournalTable columns={['Journal', 'Reference', 'Amount', 'Posting Date', 'Status', 'Reversal Of', 'Action']}>
              {journals.map((journal) => (
                <tr key={journal.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold"><Link href={`/accounting/journal-engine/journals/${journal.id}`} className="text-accent-primary underline">{journal.journal_number ?? journal.journal_no}</Link></td>
                  <td className="p-3 text-text-secondary">{journal.reference ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(journal.amount ?? journal.total_debit, journal.currency ?? 'INR')}</td>
                  <td className="p-3 text-text-secondary">{formatDate(journal.posting_date ?? journal.entry_date)}</td>
                  <td className="p-3"><JournalBadge value={journal.status} /></td>
                  <td className="p-3 text-text-secondary">{journal.reversal_of ?? '-'}</td>
                  <td className="p-3">{journal.status === 'posted' ? <JournalActionButton onClick={() => reverse(journal.id)}>Reverse</JournalActionButton> : null}</td>
                </tr>
              ))}
            </JournalTable>
          )}
        </div>
      </JournalPageFrame>
    </AppShell>
  );
}
