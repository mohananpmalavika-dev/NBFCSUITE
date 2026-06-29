"use client";

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { Journal } from '../../accountingApi';
import { EmptyState, JournalActionButton, JournalBadge, JournalPageFrame, JournalTable, LoadingBlock, formatAmount } from '../journalComponents';

export default function JournalExplorerPage() {
  const [journals, setJournals] = useState<Journal[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [message, setMessage] = useState('');

  async function load() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('limit', '100');
      if (search) params.set('q', search);
      if (status) params.set('status', status);
      const body = await accountingApi.listJournals(DEFAULT_ACCOUNTING_TENANT, params.toString());
      setJournals(body.items);
      setMessage('');
    } catch {
      setJournals([]);
      setMessage('Unable to load journals.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const statusOptions = useMemo(() => ['draft', 'pending', 'approved', 'posted', 'reversed', 'cancelled', 'failed'], []);

  async function approve(id: string) {
    setMessage('Approving journal...');
    try {
      await accountingApi.approveJournal(id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal approved.');
    } catch {
      setMessage('Unable to approve journal.');
    }
  }

  async function post(id: string) {
    setMessage('Posting journal...');
    try {
      await accountingApi.postJournal(id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal posted.');
    } catch {
      setMessage('Unable to post journal.');
    }
  }

  return (
    <AppShell>
      <JournalPageFrame title="Journal Explorer" description="Search, filter, drill down, approve, post, reverse, export, and inspect all journal activity.">
        <div className="space-y-4">
          <div className="grid gap-3 rounded-md border border-border-default bg-background-surface p-4 md:grid-cols-[1fr_180px_auto]">
            <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search journal number, reference, narration" />
            <select className="h-10 rounded-md border border-border-default px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">All statuses</option>
              {statusOptions.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <button type="button" onClick={load} className="h-10 rounded-md bg-accent-primary px-4 text-sm font-semibold text-accent-onPrimary">Search</button>
          </div>
          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}
          {loading ? (
            <LoadingBlock />
          ) : journals.length === 0 ? (
            <EmptyState message="No journals matched the selected filters." />
          ) : (
            <JournalTable columns={['Journal Number', 'Type', 'Reference', 'Branch', 'Amount', 'Status', 'Created By', 'Actions']}>
              {journals.map((journal) => (
                <tr key={journal.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold"><Link href={`/accounting/journal-engine/journals/${journal.id}`} className="text-accent-primary underline">{journal.journal_number ?? journal.journal_no}</Link></td>
                  <td className="p-3 text-text-secondary">{journal.journal_type ?? journal.voucher_type}</td>
                  <td className="p-3 text-text-secondary">{journal.reference ?? journal.source_reference ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{journal.branch_id ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(journal.amount ?? journal.total_debit, journal.currency ?? 'INR')}</td>
                  <td className="p-3"><JournalBadge value={journal.status} /></td>
                  <td className="p-3 text-text-secondary">{journal.created_by ?? '-'}</td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      {journal.status === 'draft' || journal.status === 'pending' ? <JournalActionButton onClick={() => approve(journal.id)}>Approve</JournalActionButton> : null}
                      {journal.status === 'approved' ? <JournalActionButton onClick={() => post(journal.id)}>Post</JournalActionButton> : null}
                    </div>
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
