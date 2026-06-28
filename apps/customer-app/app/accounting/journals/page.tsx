'use client';

import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Ban, Eye, FileClock, Plus, RefreshCw, RotateCcw, Send, Upload } from 'lucide-react';
import { apiClient, type JournalStatus } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { JournalShell } from '@/components/accounting/journal-shell';
import { journalDate, journalError, money, StatusBadge, ValidationPanel } from '@/components/accounting/journal-ui';
import type { JournalAuditItem, JournalBatch, JournalDocument, JournalListResponse } from '@/components/accounting/journal-types';

const statuses: JournalStatus[] = ['draft', 'pending', 'approved', 'posted', 'reversed', 'cancelled'];

export default function JournalDashboardPage() {
  const { user, token, isLoading } = useAuth();
  const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || 'default';
  const [data, setData] = useState<JournalListResponse>({ items: [], total: 0, status_counts: {} });
  const [batches, setBatches] = useState<JournalBatch[]>([]);
  const [history, setHistory] = useState<JournalAuditItem[]>([]);
  const [status, setStatus] = useState<JournalStatus | 'all'>('all');
  const [selectedId, setSelectedId] = useState('');
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');

  const refresh = useCallback(async () => {
    if (!token || !tenantId) return;
    try {
      const [journalsResponse, batchesResponse, historyResponse] = await Promise.all([
        apiClient.getJournals(tenantId, status === 'all' ? undefined : { status }),
        apiClient.getJournalBatches(tenantId),
        apiClient.getJournalHistory(tenantId),
      ]);
      const nextData = journalsResponse.data as JournalListResponse;
      setData(nextData);
      setBatches(batchesResponse.data.items || []);
      setHistory(historyResponse.data.items || []);
      setSelectedId((current) => current && nextData.items.some((item) => item.id === current) ? current : nextData.items[0]?.id || '');
      setMessage('');
    } catch (error) {
      setMessage(journalError(error, 'Unable to load the journal dashboard.'));
    }
  }, [status, tenantId, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const selected = useMemo(
    () => data.items.find((item) => item.id === selectedId) || null,
    [data.items, selectedId],
  );

  async function runAction(name: string, action: () => Promise<unknown>, success: string) {
    setBusy(name);
    setMessage('');
    try {
      await action();
      setMessage(success);
      await refresh();
    } catch (error) {
      setMessage(journalError(error, 'Journal action failed.'));
    } finally {
      setBusy('');
    }
  }

  function journalActions(journal: JournalDocument) {
    if (journal.status === 'draft') {
      return (
        <>
          <button
            type="button"
            title="Submit for approval"
            disabled={Boolean(busy)}
            onClick={() => runAction(`submit-${journal.id}`, () => apiClient.submitJournal(journal.id, tenantId, user?.username), 'Journal submitted for checker approval.')}
            className="inline-flex h-8 items-center gap-1 rounded bg-slate-950 px-2 text-xs font-bold text-white disabled:opacity-50"
          >
            <Send className="h-3.5 w-3.5" /> Submit
          </button>
          <button
            type="button"
            title="Cancel draft"
            disabled={Boolean(busy)}
            onClick={() => window.confirm('Cancel this journal permanently?') && runAction(`cancel-${journal.id}`, () => apiClient.cancelJournal(journal.id, tenantId, user?.username, 'Cancelled from dashboard'), 'Journal cancelled.')}
            className="inline-flex h-8 items-center gap-1 rounded border border-rose-300 px-2 text-xs font-bold text-rose-700 disabled:opacity-50"
          >
            <Ban className="h-3.5 w-3.5" /> Cancel
          </button>
        </>
      );
    }
    if (journal.status === 'approved') {
      return (
        <button
          type="button"
          title="Post journal to GL"
          disabled={Boolean(busy)}
          onClick={() => runAction(`post-${journal.id}`, () => apiClient.postJournal(journal.id, tenantId, user?.username), 'Journal posted to voucher and ledger engines.')}
          className="inline-flex h-8 items-center gap-1 rounded bg-emerald-700 px-2 text-xs font-bold text-white disabled:opacity-50"
        >
          <Upload className="h-3.5 w-3.5" /> Post
        </button>
      );
    }
    if (journal.status === 'posted') {
      return (
        <button
          type="button"
          title="Create reversal journal"
          disabled={Boolean(busy)}
          onClick={() => window.confirm('Create and post a linked reversal journal?') && runAction(`reverse-${journal.id}`, () => apiClient.reverseJournal(journal.id, tenantId, user?.username, 'Reversed from dashboard'), 'Linked reversal journal posted.')}
          className="inline-flex h-8 items-center gap-1 rounded border border-violet-300 px-2 text-xs font-bold text-violet-700 disabled:opacity-50"
        >
          <RotateCcw className="h-3.5 w-3.5" /> Reverse
        </button>
      );
    }
    return null;
  }

  if (isLoading) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Loading Journal Engine...</main>;
  if (!user) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Please login to continue.</main>;

  return (
    <JournalShell
      title="Journal Dashboard"
      description="Monitor permanent accounting documents from draft through reversal."
      tenantId={tenantId}
      actions={(
        <Link href="/accounting/journals/new" className="inline-flex h-9 items-center gap-2 rounded bg-emerald-700 px-3 text-xs font-bold text-white hover:bg-emerald-800">
          <Plus className="h-4 w-4" /> New journal
        </Link>
      )}
    >
      {message ? <div className="mb-4 border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-900">{message}</div> : null}

      <section className="grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-7">
        <button
          type="button"
          onClick={() => setStatus('all')}
          className={`h-20 border px-3 text-left ${status === 'all' ? 'border-slate-950 bg-slate-950 text-white' : 'border-slate-200 bg-white'}`}
        >
          <p className="text-2xl font-black">{Object.values(data.status_counts).reduce((sum, value) => sum + Number(value || 0), 0)}</p>
          <p className={`text-xs font-bold uppercase ${status === 'all' ? 'text-slate-300' : 'text-slate-500'}`}>All journals</p>
        </button>
        {statuses.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setStatus(item)}
            className={`h-20 border px-3 text-left ${status === item ? 'border-slate-950 bg-slate-950 text-white' : 'border-slate-200 bg-white'}`}
          >
            <p className="text-2xl font-black">{data.status_counts[item] || 0}</p>
            <p className={`text-xs font-bold uppercase ${status === item ? 'text-slate-300' : 'text-slate-500'}`}>{item}</p>
          </button>
        ))}
      </section>

      <div className="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-4">
          <section className="border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <div>
                <h2 className="text-sm font-black uppercase text-slate-800">Journal register</h2>
                <p className="mt-0.5 text-xs font-semibold text-slate-500">{data.total} document{data.total === 1 ? '' : 's'} in this view</p>
              </div>
              <button type="button" title="Refresh journals" onClick={refresh} className="flex h-8 w-8 items-center justify-center rounded border border-slate-300 text-slate-600 hover:bg-slate-50">
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-sm">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-left text-[11px] font-black uppercase text-slate-500">
                    <th className="px-4 py-3">Journal</th>
                    <th className="px-4 py-3">Posting date</th>
                    <th className="px-4 py-3">Source</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 text-right">Amount</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((journal) => (
                    <tr key={journal.id} className={`border-b border-slate-100 ${selectedId === journal.id ? 'bg-blue-50/60' : 'hover:bg-slate-50'}`}>
                      <td className="px-4 py-3">
                        <p className="font-black text-slate-900">{journal.journal_no}</p>
                        <p className="mt-0.5 max-w-[300px] truncate text-xs font-semibold text-slate-500">{journal.description}</p>
                      </td>
                      <td className="px-4 py-3 font-semibold text-slate-600">{journalDate(journal.posting_date)}</td>
                      <td className="px-4 py-3">
                        <p className="font-bold capitalize text-slate-800">{journal.source_module || 'manual'}</p>
                        <p className="text-xs text-slate-500">{journal.reference || journal.source_reference || '-'}</p>
                      </td>
                      <td className="px-4 py-3"><StatusBadge status={journal.status} /></td>
                      <td className="px-4 py-3 text-right font-black">{money(journal.total_amount, journal.currency)}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button type="button" title="View journal detail" onClick={() => setSelectedId(journal.id)} className="flex h-8 w-8 items-center justify-center rounded border border-slate-300 text-slate-600">
                            <Eye className="h-4 w-4" />
                          </button>
                          {journalActions(journal)}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!data.items.length ? <p className="px-4 py-12 text-center text-sm font-semibold text-slate-500">No journals found for this status.</p> : null}
            </div>
          </section>

          {selected ? (
            <section className="border border-slate-200 bg-white">
              <div className="flex flex-col gap-3 border-b border-slate-200 px-4 py-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-black">{selected.journal_no}</h2>
                    <StatusBadge status={selected.status} />
                  </div>
                  <p className="mt-1 text-sm font-semibold text-slate-600">{selected.description}</p>
                  <p className="mt-1 text-xs text-slate-500">Period {selected.period || '-'} / Voucher {selected.voucher_id || 'not generated'}</p>
                </div>
                <div className="flex gap-2">{journalActions(selected)}</div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-sm">
                  <thead><tr className="border-b border-slate-200 bg-slate-50 text-left text-[11px] font-black uppercase text-slate-500"><th className="px-4 py-2">#</th><th className="px-4 py-2">Account</th><th className="px-4 py-2">Dimensions</th><th className="px-4 py-2 text-right">Debit</th><th className="px-4 py-2 text-right">Credit</th></tr></thead>
                  <tbody>
                    {selected.lines.map((line, index) => (
                      <tr key={line.id || index} className="border-b border-slate-100">
                        <td className="px-4 py-3 text-slate-500">{line.sequence || index + 1}</td>
                        <td className="px-4 py-3"><p className="font-bold">{line.account_code || line.gl_account_id}</p><p className="text-xs text-slate-500">{line.remarks || line.description || '-'}</p></td>
                        <td className="px-4 py-3 text-xs font-semibold text-slate-600">{[line.branch_id, line.department_id, line.cost_center, line.project_id].filter(Boolean).join(' / ') || '-'}</td>
                        <td className="px-4 py-3 text-right font-bold">{line.debit ? money(line.debit, selected.currency) : '-'}</td>
                        <td className="px-4 py-3 text-right font-bold">{line.credit ? money(line.credit, selected.currency) : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="grid border-t border-slate-200 lg:grid-cols-2">
                <div className="border-b border-slate-200 p-4 lg:border-b-0 lg:border-r">
                  <h3 className="text-xs font-black uppercase text-slate-500">Approval history</h3>
                  <div className="mt-3 space-y-3">
                    {selected.approvals.map((approval) => (
                      <div key={approval.id} className="flex items-start justify-between gap-3 text-xs">
                        <div><p className="font-bold capitalize text-slate-800">{approval.level}: {approval.decision}</p><p className="text-slate-500">{approval.approver} / {approval.remarks || 'No remarks'}</p></div>
                        <span className="shrink-0 text-slate-500">{journalDate(approval.approved_time, true)}</span>
                      </div>
                    ))}
                    {!selected.approvals.length ? <p className="text-xs font-semibold text-slate-500">No workflow decisions yet.</p> : null}
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="text-xs font-black uppercase text-slate-500">Attachments</h3>
                  <div className="mt-3 space-y-2">
                    {selected.attachments.map((attachment) => <p key={attachment.id} className="text-xs font-bold text-slate-700">{attachment.file_name}</p>)}
                    {!selected.attachments.length ? <p className="text-xs font-semibold text-slate-500">No supporting documents.</p> : null}
                  </div>
                </div>
              </div>
              <div className="border-t border-slate-200 p-4"><ValidationPanel result={selected.validation_result || null} compact /></div>
            </section>
          ) : null}
        </div>

        <aside className="space-y-4">
          <section className="border border-slate-200 bg-white">
            <div className="flex items-center gap-2 border-b border-slate-200 px-4 py-3">
              <FileClock className="h-4 w-4 text-slate-500" />
              <h2 className="text-sm font-black uppercase text-slate-800">Open batches</h2>
            </div>
            <div className="divide-y divide-slate-100">
              {batches.slice(0, 8).map((batch) => (
                <div key={batch.id} className="px-4 py-3">
                  <div className="flex items-center justify-between gap-3"><p className="text-sm font-black">{batch.batch_no}</p><span className="text-[11px] font-bold uppercase text-slate-500">{batch.status}</span></div>
                  <p className="mt-1 text-xs font-semibold text-slate-500">{batch.period} / {batch.journal_count} journals</p>
                  <p className="mt-1 text-xs font-black text-slate-700">{money(batch.total_amount)}</p>
                </div>
              ))}
              {!batches.length ? <p className="px-4 py-8 text-center text-xs font-semibold text-slate-500">No journal batches.</p> : null}
            </div>
          </section>

          <section className="border border-slate-200 bg-white">
            <div className="border-b border-slate-200 px-4 py-3"><h2 className="text-sm font-black uppercase text-slate-800">Audit trail</h2></div>
            <div className="max-h-[520px] divide-y divide-slate-100 overflow-y-auto">
              {history.slice(0, 20).map((item) => (
                <div key={item.id} className="px-4 py-3">
                  <p className="text-xs font-black uppercase text-slate-800">{item.action.replace(/_/g, ' ')}</p>
                  <p className="mt-1 truncate text-xs font-semibold text-slate-500">{item.entity_id}</p>
                  <p className="mt-1 text-[11px] text-slate-400">{item.performed_by || 'system'} / {journalDate(item.created_at, true)}</p>
                </div>
              ))}
              {!history.length ? <p className="px-4 py-8 text-center text-xs font-semibold text-slate-500">No journal activity yet.</p> : null}
            </div>
          </section>
        </aside>
      </div>
    </JournalShell>
  );
}
