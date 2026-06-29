"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../../accountingApi';
import type { Journal } from '../../../accountingApi';
import { EmptyState, JournalActionButton, JournalBadge, JournalMetric, JournalPageFrame, JournalTable, LoadingBlock, formatAmount, formatDate } from '../../journalComponents';

function textValue(value: unknown, fallback = '-') {
  if (value === null || value === undefined || value === '') return fallback;
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export default function Journal360Page() {
  const params = useParams<{ id: string }>();
  const [journal, setJournal] = useState<Journal | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  async function load() {
    if (!params.id) return;
    setLoading(true);
    try {
      const body = await accountingApi.getJournal(params.id, DEFAULT_ACCOUNTING_TENANT);
      setJournal(body);
      setMessage('');
    } catch {
      setJournal(null);
      setMessage('Journal 360 is unavailable.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [params.id]);

  async function approve() {
    if (!journal) return;
    setMessage('Approving journal...');
    try {
      await accountingApi.approveJournal(journal.id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal approved.');
    } catch {
      setMessage('Unable to approve journal.');
    }
  }

  async function post() {
    if (!journal) return;
    setMessage('Posting journal...');
    try {
      await accountingApi.postJournal(journal.id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal posted.');
    } catch {
      setMessage('Unable to post journal.');
    }
  }

  async function reverse() {
    if (!journal) return;
    setMessage('Reversing journal...');
    try {
      await accountingApi.reverseJournal(journal.id, DEFAULT_ACCOUNTING_TENANT);
      await load();
      setMessage('Journal reversed.');
    } catch {
      setMessage('Unable to reverse journal.');
    }
  }

  return (
    <AppShell>
      <JournalPageFrame title="Journal 360" description="Digital journal twin with header, lines, source transaction, approvals, dimensions, attachments, timeline, audit, and AI insights.">
        {loading ? (
          <LoadingBlock />
        ) : journal ? (
          <div className="space-y-6">
            <div className="flex flex-col gap-3 rounded-md border border-border-default bg-background-surface p-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-xl font-semibold text-text-primary">{journal.journal_number ?? journal.journal_no}</h2>
                  <JournalBadge value={journal.status} />
                </div>
                <p className="mt-1 text-sm text-text-secondary">{journal.description}</p>
                <p className="mt-1 text-sm text-text-secondary">{journal.source_module ?? 'manual'}.{journal.business_event ?? journal.source_event ?? 'manual_journal'} | {journal.reference ?? journal.source_reference ?? '-'}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Link href="/accounting/journal-engine/explorer" className="inline-flex h-9 items-center rounded-md border border-border-default px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent">Explorer</Link>
                {journal.status === 'draft' || journal.status === 'pending' ? <JournalActionButton onClick={approve}>Approve</JournalActionButton> : null}
                {journal.status === 'approved' ? <JournalActionButton onClick={post}>Post</JournalActionButton> : null}
                {journal.status === 'posted' ? <JournalActionButton onClick={reverse}>Reverse</JournalActionButton> : null}
              </div>
            </div>

            {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <JournalMetric label="Amount" value={formatAmount(journal.amount ?? journal.total_debit, journal.currency ?? 'INR')} note="Debit-side journal total" />
              <JournalMetric label="Balance" value={journal.validation_summary?.is_balanced ? 'Balanced' : 'Review'} note={`${journal.total_debit} debit / ${journal.total_credit} credit`} />
              <JournalMetric label="Currency" value={journal.currency ?? 'INR'} note={`FX ${journal.exchange_rate ?? 1}`} />
              <JournalMetric label="AI Risk" value={textValue(journal.ai?.anomaly_score, '0')} note={textValue(journal.ai?.duplicate_risk, 'low')} />
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">Header</h3>
                <div className="mt-3 grid gap-2 text-sm text-text-secondary md:grid-cols-2">
                  <div>Posting date: {formatDate(journal.posting_date ?? journal.entry_date)}</div>
                  <div>Accounting date: {formatDate(journal.accounting_date ?? journal.business_date)}</div>
                  <div>Branch: {journal.branch_id ?? '-'}</div>
                  <div>Period: {journal.period ?? '-'}</div>
                  <div>Legal entity: {journal.legal_entity ?? '-'}</div>
                  <div>Business unit: {journal.business_unit ?? '-'}</div>
                </div>
              </section>

              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">Business View</h3>
                <div className="mt-3 grid gap-2 text-sm text-text-secondary md:grid-cols-2">
                  <div>Source: {textValue(journal.business_view?.source_transaction ?? journal.source_reference)}</div>
                  <div>Module: {textValue(journal.business_view?.source_module ?? journal.source_module)}</div>
                  <div>Customer: {textValue(journal.business_view?.customer)}</div>
                  <div>Product: {textValue(journal.business_view?.product)}</div>
                </div>
              </section>
            </div>

            <JournalTable columns={['Seq', 'GL Account', 'Debit', 'Credit', 'Currency', 'Branch', 'Cost Center', 'Description']}>
              {journal.lines.map((line, index) => (
                <tr key={line.id ?? index} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold text-text-primary">{line.sequence ?? index + 1}</td>
                  <td className="p-3 text-text-secondary">{line.account_code ?? line.gl_account_id} {line.account_name ? `- ${line.account_name}` : ''}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(line.debit, line.currency ?? journal.currency ?? 'INR')}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(line.credit, line.currency ?? journal.currency ?? 'INR')}</td>
                  <td className="p-3 text-text-secondary">{line.currency ?? journal.currency ?? 'INR'}</td>
                  <td className="p-3 text-text-secondary">{line.branch_id ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{line.cost_center ?? '-'}</td>
                  <td className="p-3 text-text-secondary">{line.description ?? '-'}</td>
                </tr>
              ))}
            </JournalTable>

            <div className="grid gap-4 xl:grid-cols-3">
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">Approvals</h3>
                <div className="mt-3 space-y-2 text-sm text-text-secondary">
                  {(journal.approvals ?? []).length === 0 ? <div>No approvals recorded.</div> : null}
                  {(journal.approvals ?? []).map((approval, index) => <div key={index}>{textValue(approval.level)}: {textValue(approval.decision)} by {textValue(approval.approver)}</div>)}
                </div>
              </section>
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">Attachments</h3>
                <div className="mt-3 space-y-2 text-sm text-text-secondary">
                  {(journal.attachments ?? []).length === 0 ? <div>No attachments.</div> : null}
                  {(journal.attachments ?? []).map((attachment, index) => <div key={index}>{textValue(attachment.file_name)} ({textValue(attachment.document_id)})</div>)}
                </div>
              </section>
              <section className="rounded-md border border-border-default bg-background-surface p-4">
                <h3 className="font-semibold text-text-primary">AI View</h3>
                <div className="mt-3 space-y-2 text-sm text-text-secondary">
                  <div>Duplicate risk: {textValue(journal.ai?.duplicate_risk, 'low')}</div>
                  <div>Anomaly score: {textValue(journal.ai?.anomaly_score, '0')}</div>
                  <div>Explanation: {textValue(journal.ai?.explanation)}</div>
                </div>
              </section>
            </div>
          </div>
        ) : (
          <EmptyState message={message || 'Journal was not found.'} />
        )}
      </JournalPageFrame>
    </AppShell>
  );
}
