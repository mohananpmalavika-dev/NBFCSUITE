'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Check, ClipboardCheck, RefreshCw, Upload, X } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { JournalShell } from '@/components/accounting/journal-shell';
import { journalDate, journalError, money, StatusBadge, ValidationPanel } from '@/components/accounting/journal-ui';
import type { JournalAuditItem, JournalDocument, JournalListResponse } from '@/components/accounting/journal-types';

export default function JournalApprovalQueuePage() {
  const { user, token, isLoading } = useAuth();
  const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || 'default';
  const [pending, setPending] = useState<JournalDocument[]>([]);
  const [approved, setApproved] = useState<JournalDocument[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [history, setHistory] = useState<JournalAuditItem[]>([]);
  const [remarks, setRemarks] = useState('');
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');

  const refresh = useCallback(async () => {
    if (!token || !tenantId) return;
    try {
      const [pendingResponse, approvedResponse, historyResponse] = await Promise.all([
        apiClient.getJournals(tenantId, { status: 'pending' }),
        apiClient.getJournals(tenantId, { status: 'approved' }),
        apiClient.getJournalHistory(tenantId),
      ]);
      const pendingItems = (pendingResponse.data as JournalListResponse).items;
      const approvedItems = (approvedResponse.data as JournalListResponse).items;
      const all = [...pendingItems, ...approvedItems];
      setPending(pendingItems);
      setApproved(approvedItems);
      setHistory(historyResponse.data.items || []);
      setSelectedId((current) => current && all.some((item) => item.id === current) ? current : all[0]?.id || '');
      setMessage('');
    } catch (error) {
      setMessage(journalError(error, 'Unable to load approval queue.'));
    }
  }, [tenantId, token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const selected = useMemo(
    () => [...pending, ...approved].find((journal) => journal.id === selectedId) || null,
    [approved, pending, selectedId],
  );
  const selectedHistory = useMemo(
    () => history.filter((item) => item.entity_id === selectedId),
    [history, selectedId],
  );

  async function decide(decision: 'approved' | 'rejected') {
    if (!selected) return;
    setBusy(decision);
    setMessage('');
    try {
      await apiClient.approveJournal(selected.id, tenantId, user?.username, decision, remarks || undefined);
      setRemarks('');
      setMessage(decision === 'approved' ? 'Checker approval recorded.' : 'Journal returned to draft with rejection history preserved.');
      await refresh();
    } catch (error) {
      setMessage(journalError(error, 'Unable to record approval decision.'));
    } finally {
      setBusy('');
    }
  }

  async function postSelected() {
    if (!selected) return;
    setBusy('post');
    setMessage('');
    try {
      await apiClient.postJournal(selected.id, tenantId, user?.username, remarks || undefined);
      setRemarks('');
      setMessage('Journal posted. Voucher and GL updates completed atomically.');
      await refresh();
    } catch (error) {
      setMessage(journalError(error, 'Unable to post approved journal.'));
    } finally {
      setBusy('');
    }
  }

  if (isLoading) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Loading approval queue...</main>;
  if (!user) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Please login to continue.</main>;

  return (
    <JournalShell
      title="Journal Approval Queue"
      description="Maker/checker review, approval history, and controlled release to the ledger."
      tenantId={tenantId}
      actions={<button type="button" title="Refresh approval queue" onClick={refresh} className="flex h-9 w-9 items-center justify-center rounded border border-slate-300 bg-white text-slate-600"><RefreshCw className="h-4 w-4" /></button>}
    >
      {message ? <div className="mb-4 border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-900">{message}</div> : null}
      <section className="mb-4 grid gap-3 sm:grid-cols-3">
        <div className="border border-amber-200 bg-amber-50 px-4 py-4"><p className="text-2xl font-black text-amber-900">{pending.length}</p><p className="text-xs font-bold uppercase text-amber-700">Awaiting checker</p></div>
        <div className="border border-blue-200 bg-blue-50 px-4 py-4"><p className="text-2xl font-black text-blue-900">{approved.length}</p><p className="text-xs font-bold uppercase text-blue-700">Approved to post</p></div>
        <div className="border border-slate-200 bg-white px-4 py-4"><p className="text-2xl font-black text-slate-900">{pending.length + approved.length}</p><p className="text-xs font-bold uppercase text-slate-500">Active workflow</p></div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[390px_minmax(0,1fr)]">
        <aside className="border border-slate-200 bg-white">
          <div className="flex items-center gap-2 border-b border-slate-200 px-4 py-3"><ClipboardCheck className="h-4 w-4 text-slate-500" /><h2 className="text-sm font-black uppercase text-slate-800">Review queue</h2></div>
          <div className="max-h-[760px] divide-y divide-slate-100 overflow-y-auto">
            {[...pending, ...approved].map((journal) => (
              <button key={journal.id} type="button" onClick={() => { setSelectedId(journal.id); setRemarks(''); }} className={`w-full px-4 py-4 text-left ${selectedId === journal.id ? 'bg-blue-50' : 'hover:bg-slate-50'}`}>
                <div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="truncate text-sm font-black text-slate-900">{journal.journal_no}</p><p className="mt-1 truncate text-xs font-semibold text-slate-500">{journal.description}</p></div><StatusBadge status={journal.status} /></div>
                <div className="mt-3 flex items-center justify-between text-xs"><span className="font-semibold text-slate-500">{journalDate(journal.posting_date)}</span><span className="font-black text-slate-800">{money(journal.total_amount, journal.currency)}</span></div>
                <p className="mt-2 text-[11px] font-semibold text-slate-400">Maker {journal.created_by || 'unassigned'}</p>
              </button>
            ))}
            {!pending.length && !approved.length ? <div className="px-6 py-16 text-center"><Check className="mx-auto h-8 w-8 text-emerald-600" /><p className="mt-3 text-sm font-black text-slate-800">Queue cleared</p><p className="mt-1 text-xs font-semibold text-slate-500">There are no journals waiting for approval or posting.</p></div> : null}
          </div>
        </aside>

        {selected ? (
          <div className="min-w-0 space-y-4">
            <section className="border border-slate-200 bg-white">
              <div className="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-start lg:justify-between">
                <div><div className="flex items-center gap-2"><h2 className="text-xl font-black">{selected.journal_no}</h2><StatusBadge status={selected.status} /></div><p className="mt-1 text-sm font-semibold text-slate-600">{selected.description}</p><p className="mt-1 text-xs text-slate-500">{selected.source_module || 'manual'} / {selected.reference || selected.source_reference || 'no reference'} / {selected.period}</p></div>
                <div className="text-left lg:text-right"><p className="text-xs font-bold uppercase text-slate-500">Journal amount</p><p className="mt-1 text-xl font-black">{money(selected.total_amount, selected.currency)}</p></div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-sm">
                  <thead><tr className="border-b border-slate-200 bg-slate-50 text-left text-[11px] font-black uppercase text-slate-500"><th className="px-4 py-3">Account</th><th className="px-4 py-3">Remarks</th><th className="px-4 py-3">Dimensions</th><th className="px-4 py-3 text-right">Debit</th><th className="px-4 py-3 text-right">Credit</th></tr></thead>
                  <tbody>{selected.lines.map((line, index) => <tr key={line.id || index} className="border-b border-slate-100"><td className="px-4 py-3 font-black">{line.account_code || line.gl_account_id}</td><td className="px-4 py-3 text-slate-600">{line.remarks || line.description || '-'}</td><td className="px-4 py-3 text-xs font-semibold text-slate-500">{[line.branch_id, line.department_id, line.cost_center, line.project_id].filter(Boolean).join(' / ') || '-'}</td><td className="px-4 py-3 text-right font-bold">{line.debit ? money(line.debit, selected.currency) : '-'}</td><td className="px-4 py-3 text-right font-bold">{line.credit ? money(line.credit, selected.currency) : '-'}</td></tr>)}</tbody>
                  <tfoot><tr className="bg-slate-950 font-black text-white"><td className="px-4 py-3" colSpan={3}>Control total</td><td className="px-4 py-3 text-right">{money(selected.total_debit, selected.currency)}</td><td className="px-4 py-3 text-right">{money(selected.total_credit, selected.currency)}</td></tr></tfoot>
                </table>
              </div>
            </section>

            <div className="grid gap-4 lg:grid-cols-2">
              <ValidationPanel result={selected.validation_result || null} compact />
              <section className="border border-slate-200 bg-white p-4">
                <h2 className="text-sm font-black uppercase text-slate-800">Decision</h2>
                <label className="mt-3 block"><span className="text-xs font-bold text-slate-600">Review remarks</span><textarea value={remarks} onChange={(event) => setRemarks(event.target.value)} rows={4} className="mt-1 w-full resize-none rounded border border-slate-300 px-3 py-2 text-sm" placeholder="Control checks, exceptions, or posting note" /></label>
                {selected.status === 'pending' ? (
                  <div className="mt-3 grid grid-cols-2 gap-2"><button type="button" disabled={Boolean(busy)} onClick={() => decide('rejected')} className="inline-flex h-10 items-center justify-center gap-2 rounded border border-rose-300 text-sm font-bold text-rose-700 disabled:opacity-50"><X className="h-4 w-4" /> Reject</button><button type="button" disabled={Boolean(busy)} onClick={() => decide('approved')} className="inline-flex h-10 items-center justify-center gap-2 rounded bg-blue-700 text-sm font-bold text-white disabled:opacity-50"><Check className="h-4 w-4" /> Approve</button></div>
                ) : (
                  <button type="button" disabled={Boolean(busy)} onClick={postSelected} className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded bg-emerald-700 text-sm font-bold text-white disabled:opacity-50"><Upload className="h-4 w-4" /> Post to voucher and GL</button>
                )}
                {selected.created_by === user.username && selected.status === 'pending' ? <p className="mt-3 text-xs font-semibold text-amber-800">Maker/checker control will prevent approval by the journal creator.</p> : null}
              </section>
            </div>

            <section className="grid border border-slate-200 bg-white lg:grid-cols-2">
              <div className="border-b border-slate-200 p-4 lg:border-b-0 lg:border-r"><h2 className="text-sm font-black uppercase text-slate-800">Approval history</h2><div className="mt-3 space-y-3">{selected.approvals.map((approval) => <div key={approval.id} className="flex items-start justify-between gap-3 text-xs"><div><p className="font-black capitalize text-slate-800">{approval.level} / {approval.decision}</p><p className="mt-0.5 text-slate-500">{approval.approver} / {approval.remarks || 'No remarks'}</p></div><span className="shrink-0 text-slate-400">{journalDate(approval.approved_time, true)}</span></div>)}{!selected.approvals.length ? <p className="text-xs font-semibold text-slate-500">No decisions recorded.</p> : null}</div></div>
              <div className="p-4"><h2 className="text-sm font-black uppercase text-slate-800">Audit trail</h2><div className="mt-3 space-y-3">{selectedHistory.map((item) => <div key={item.id} className="flex items-start justify-between gap-3 text-xs"><div><p className="font-black uppercase text-slate-800">{item.action.replace(/_/g, ' ')}</p><p className="mt-0.5 text-slate-500">{item.performed_by || 'system'}</p></div><span className="shrink-0 text-slate-400">{journalDate(item.created_at, true)}</span></div>)}</div></div>
            </section>
          </div>
        ) : (
          <section className="flex min-h-[520px] flex-col items-center justify-center border border-dashed border-slate-300 bg-white text-center"><ClipboardCheck className="h-9 w-9 text-slate-400" /><p className="mt-3 text-sm font-black text-slate-700">Select a journal to review</p></section>
        )}
      </div>
    </JournalShell>
  );
}
