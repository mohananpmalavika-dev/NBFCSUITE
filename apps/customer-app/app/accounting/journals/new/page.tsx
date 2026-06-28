'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FilePlus2, Paperclip, Plus, Save, Send, Trash2, WandSparkles } from 'lucide-react';
import { apiClient, type AccountingPostingLine, type JournalDocumentPayload } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { JournalShell } from '@/components/accounting/journal-shell';
import { journalError, money, ValidationPanel } from '@/components/accounting/journal-ui';
import type { GlAccountOption, JournalBatch, JournalDocument, JournalTemplate, JournalValidation } from '@/components/accounting/journal-types';

interface EditorLine extends AccountingPostingLine {
  rowId: string;
}

function emptyLine(direction: 'debit' | 'credit'): EditorLine {
  return {
    rowId: crypto.randomUUID(),
    gl_account_id: '',
    debit: direction === 'debit' ? 0 : 0,
    credit: direction === 'credit' ? 0 : 0,
    currency: 'INR',
    branch_id: '',
    department_id: '',
    cost_center: '',
    profit_center: '',
    project_id: '',
    employee_id: '',
    product_id: '',
    business_unit_id: '',
    description: '',
  };
}

export default function JournalEntryPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || 'default';
  const [accounts, setAccounts] = useState<GlAccountOption[]>([]);
  const [templates, setTemplates] = useState<JournalTemplate[]>([]);
  const [batches, setBatches] = useState<JournalBatch[]>([]);
  const [lines, setLines] = useState<EditorLine[]>([emptyLine('debit'), emptyLine('credit')]);
  const [attachments, setAttachments] = useState<File[]>([]);
  const [validation, setValidation] = useState<JournalValidation | null>(null);
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({
    description: '',
    posting_date: new Date().toISOString().slice(0, 10),
    voucher_type: 'journal',
    source_module: 'manual',
    source_event: 'manual_journal',
    source_reference: '',
    reference: '',
    currency: 'INR',
    exchange_rate: '1',
    branch_id: '',
    financial_year: '2026-27',
    batch_id: '',
    template_id: '',
    tax_code: '',
  });

  const loadOptions = useCallback(async () => {
    if (!token || !tenantId) return;
    try {
      const [accountsResponse, templatesResponse, batchesResponse] = await Promise.all([
        apiClient.getGlAccounts(tenantId),
        apiClient.getJournalTemplates(tenantId),
        apiClient.getJournalBatches(tenantId),
      ]);
      setAccounts((accountsResponse.data || []).filter((account: GlAccountOption) => account.status !== 'inactive' && String(account.posting_allowed || 'true') !== 'false'));
      setTemplates(templatesResponse.data.items || []);
      setBatches((batchesResponse.data.items || []).filter((batch: JournalBatch) => !['posted', 'closed', 'cancelled'].includes(batch.status)));
    } catch (error) {
      setMessage(journalError(error, 'Unable to load journal setup data.'));
    }
  }, [tenantId, token]);

  useEffect(() => {
    loadOptions();
  }, [loadOptions]);

  const totals = useMemo(() => lines.reduce(
    (result, line) => ({ debit: result.debit + Number(line.debit || 0), credit: result.credit + Number(line.credit || 0) }),
    { debit: 0, credit: 0 },
  ), [lines]);

  function updateLine(rowId: string, patch: Partial<EditorLine>) {
    setLines((current) => current.map((line) => line.rowId === rowId ? { ...line, ...patch } : line));
    setValidation(null);
  }

  function applyTemplate(templateId: string) {
    const template = templates.find((item) => item.id === templateId);
    setForm((current) => ({ ...current, template_id: templateId, currency: template?.currency || current.currency }));
    if (!template) return;
    setLines(template.lines.map((line) => ({
      ...emptyLine(line.direction),
      gl_account_id: accounts.find((account) => account.account_code === line.account_code)?.id || '',
      description: line.description || '',
    })));
    setValidation(null);
  }

  function payload(): JournalDocumentPayload {
    return {
      tenant_id: tenantId,
      batch_id: form.batch_id || undefined,
      posting_date: `${form.posting_date}T00:00:00`,
      voucher_type: form.voucher_type,
      source_module: form.source_module,
      source_event: form.source_event,
      source_reference: form.source_reference || undefined,
      description: form.description,
      reference: form.reference || undefined,
      currency: form.currency,
      exchange_rate: Number(form.exchange_rate || 1),
      branch_id: form.branch_id || undefined,
      financial_year: form.financial_year || undefined,
      template_id: form.template_id || undefined,
      created_by: user?.username,
      metadata: form.tax_code ? { tax_code: form.tax_code } : undefined,
      lines: lines.map(({ rowId: _rowId, ...line }) => ({
        ...line,
        gl_account_id: line.gl_account_id || undefined,
        debit: Number(line.debit || 0),
        credit: Number(line.credit || 0),
        branch_id: line.branch_id || form.branch_id || undefined,
      })),
      attachments: attachments.map((file) => ({ file_name: file.name, document_id: `${file.name}-${file.lastModified}`, uploaded_by: user?.username })),
    };
  }

  async function validate() {
    setBusy('validate');
    setMessage('');
    try {
      const document = payload();
      const response = await apiClient.validateJournal({
        tenant_id: document.tenant_id,
        posting_date: document.posting_date,
        source_module: document.source_module,
        source_event: document.source_event,
        source_reference: document.source_reference,
        branch_id: document.branch_id,
        financial_year: document.financial_year,
        currency: document.currency,
        exchange_rate: document.exchange_rate,
        metadata: document.metadata,
        lines: document.lines,
      });
      setValidation(response.data);
      setMessage(response.data.valid ? 'Journal passed all posting controls.' : 'Journal requires correction before submission.');
      return response.data as JournalValidation;
    } catch (error) {
      setMessage(journalError(error, 'Unable to validate journal.'));
      return null;
    } finally {
      setBusy('');
    }
  }

  async function save(submit: boolean) {
    if (!form.description.trim()) {
      setMessage('Description is required.');
      return;
    }
    setBusy(submit ? 'save-submit' : 'save');
    setMessage('');
    try {
      const response = await apiClient.createJournal(payload());
      const journal = response.data as JournalDocument;
      if (submit) {
        await apiClient.submitJournal(journal.id, tenantId, user?.username, 'Submitted from journal entry screen');
      }
      router.push('/accounting/journals');
    } catch (error) {
      setMessage(journalError(error, 'Unable to create journal.'));
    } finally {
      setBusy('');
    }
  }

  async function createBatch() {
    setBusy('batch');
    try {
      const response = await apiClient.createJournalBatch({
        tenant_id: tenantId,
        posting_date: `${form.posting_date}T00:00:00`,
        financial_year: form.financial_year,
        created_by: user?.username,
      });
      setBatches((current) => [response.data, ...current]);
      setForm((current) => ({ ...current, batch_id: response.data.id }));
      setMessage(`Batch ${response.data.batch_no} opened.`);
    } catch (error) {
      setMessage(journalError(error, 'Unable to create batch.'));
    } finally {
      setBusy('');
    }
  }

  if (isLoading) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Loading journal entry...</main>;
  if (!user) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Please login to continue.</main>;

  return (
    <JournalShell
      title="Journal Entry"
      description="Create a balanced accounting document using manual lines or a controlled template."
      tenantId={tenantId}
      actions={(
        <>
          <button type="button" disabled={Boolean(busy)} onClick={() => save(false)} className="inline-flex h-9 items-center gap-2 rounded border border-slate-300 bg-white px-3 text-xs font-bold text-slate-700 disabled:opacity-50"><Save className="h-4 w-4" /> Save draft</button>
          <button type="button" disabled={Boolean(busy) || validation?.valid === false} onClick={() => save(true)} className="inline-flex h-9 items-center gap-2 rounded bg-emerald-700 px-3 text-xs font-bold text-white disabled:opacity-50"><Send className="h-4 w-4" /> Save & submit</button>
        </>
      )}
    >
      {message ? <div className="mb-4 border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-900">{message}</div> : null}
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="min-w-0 space-y-4">
          <section className="border border-slate-200 bg-white">
            <div className="border-b border-slate-200 px-4 py-3"><h2 className="text-sm font-black uppercase text-slate-800">Document header</h2></div>
            <div className="grid gap-4 p-4 md:grid-cols-2 xl:grid-cols-4">
              <label className="md:col-span-2 xl:col-span-4"><span className="text-xs font-bold text-slate-600">Description</span><input value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" placeholder="Purpose of this journal" /></label>
              <label><span className="text-xs font-bold text-slate-600">Posting date</span><input type="date" value={form.posting_date} onChange={(event) => setForm({ ...form, posting_date: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
              <label><span className="text-xs font-bold text-slate-600">Financial year</span><input value={form.financial_year} onChange={(event) => setForm({ ...form, financial_year: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
              <label><span className="text-xs font-bold text-slate-600">Voucher type</span><select value={form.voucher_type} onChange={(event) => setForm({ ...form, voucher_type: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 bg-white px-3 text-sm"><option value="journal">Journal</option><option value="accrual">Accrual</option><option value="adjustment">Adjustment</option><option value="provision">Provision</option></select></label>
              <label><span className="text-xs font-bold text-slate-600">Reference</span><input value={form.reference} onChange={(event) => setForm({ ...form, reference: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" placeholder="External reference" /></label>
              <label><span className="text-xs font-bold text-slate-600">Source module</span><input value={form.source_module} onChange={(event) => setForm({ ...form, source_module: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
              <label><span className="text-xs font-bold text-slate-600">Source event</span><input value={form.source_event} onChange={(event) => setForm({ ...form, source_event: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
              <label><span className="text-xs font-bold text-slate-600">Branch</span><input value={form.branch_id} onChange={(event) => setForm({ ...form, branch_id: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" placeholder="Optional branch code" /></label>
              <label><span className="text-xs font-bold text-slate-600">Tax code</span><input value={form.tax_code} onChange={(event) => setForm({ ...form, tax_code: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" placeholder="Optional" /></label>
              <label><span className="text-xs font-bold text-slate-600">Currency</span><input maxLength={3} value={form.currency} onChange={(event) => setForm({ ...form, currency: event.target.value.toUpperCase() })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
              <label><span className="text-xs font-bold text-slate-600">Exchange rate</span><input type="number" min="0" step="0.0001" value={form.exchange_rate} onChange={(event) => setForm({ ...form, exchange_rate: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
            </div>
          </section>

          <section className="border border-slate-200 bg-white">
            <div className="flex flex-col gap-3 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
              <div><h2 className="text-sm font-black uppercase text-slate-800">Journal lines</h2><p className="mt-0.5 text-xs font-semibold text-slate-500">Each line carries its own operating dimensions.</p></div>
              <button type="button" onClick={() => setLines((current) => [...current, emptyLine('debit')])} className="inline-flex h-8 items-center gap-1 rounded border border-slate-300 px-2 text-xs font-bold text-slate-700"><Plus className="h-3.5 w-3.5" /> Add line</button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[1220px] text-sm">
                <thead><tr className="border-b border-slate-200 bg-slate-50 text-left text-[11px] font-black uppercase text-slate-500"><th className="px-3 py-2">#</th><th className="px-3 py-2">GL Account</th><th className="px-3 py-2">Debit</th><th className="px-3 py-2">Credit</th><th className="px-3 py-2">Department</th><th className="px-3 py-2">Cost centre</th><th className="px-3 py-2">Profit centre</th><th className="px-3 py-2">Project</th><th className="px-3 py-2">Remarks</th><th className="px-3 py-2"></th></tr></thead>
                <tbody>
                  {lines.map((line, index) => (
                    <tr key={line.rowId} className="border-b border-slate-100 align-top">
                      <td className="px-3 py-3 font-bold text-slate-500">{index + 1}</td>
                      <td className="px-3 py-2"><select value={line.gl_account_id} onChange={(event) => updateLine(line.rowId, { gl_account_id: event.target.value })} className="h-9 w-64 rounded border border-slate-300 bg-white px-2 text-xs"><option value="">Select account</option>{accounts.map((account) => <option key={account.id} value={account.id}>{account.account_code} - {account.account_name}</option>)}</select></td>
                      <td className="px-3 py-2"><input type="number" min="0" step="0.01" value={line.debit || ''} onChange={(event) => updateLine(line.rowId, { debit: Number(event.target.value), credit: event.target.value ? 0 : line.credit })} className="h-9 w-28 rounded border border-slate-300 px-2 text-right text-xs" /></td>
                      <td className="px-3 py-2"><input type="number" min="0" step="0.01" value={line.credit || ''} onChange={(event) => updateLine(line.rowId, { credit: Number(event.target.value), debit: event.target.value ? 0 : line.debit })} className="h-9 w-28 rounded border border-slate-300 px-2 text-right text-xs" /></td>
                      <td className="px-3 py-2"><input value={line.department_id || ''} onChange={(event) => updateLine(line.rowId, { department_id: event.target.value })} className="h-9 w-28 rounded border border-slate-300 px-2 text-xs" /></td>
                      <td className="px-3 py-2"><input value={line.cost_center || ''} onChange={(event) => updateLine(line.rowId, { cost_center: event.target.value })} className="h-9 w-28 rounded border border-slate-300 px-2 text-xs" /></td>
                      <td className="px-3 py-2"><input value={line.profit_center || ''} onChange={(event) => updateLine(line.rowId, { profit_center: event.target.value })} className="h-9 w-28 rounded border border-slate-300 px-2 text-xs" /></td>
                      <td className="px-3 py-2"><input value={line.project_id || ''} onChange={(event) => updateLine(line.rowId, { project_id: event.target.value })} className="h-9 w-28 rounded border border-slate-300 px-2 text-xs" /></td>
                      <td className="px-3 py-2"><input value={line.description || ''} onChange={(event) => updateLine(line.rowId, { description: event.target.value })} className="h-9 w-44 rounded border border-slate-300 px-2 text-xs" /></td>
                      <td className="px-3 py-2"><button type="button" title="Remove line" disabled={lines.length <= 2} onClick={() => setLines((current) => current.filter((item) => item.rowId !== line.rowId))} className="flex h-9 w-9 items-center justify-center rounded text-rose-600 hover:bg-rose-50 disabled:text-slate-300"><Trash2 className="h-4 w-4" /></button></td>
                    </tr>
                  ))}
                </tbody>
                <tfoot><tr className={`font-black ${Math.abs(totals.debit - totals.credit) < 0.005 ? 'bg-emerald-50 text-emerald-900' : 'bg-rose-50 text-rose-900'}`}><td className="px-3 py-3" colSpan={2}>Totals</td><td className="px-3 py-3 text-right">{money(totals.debit, form.currency)}</td><td className="px-3 py-3 text-right">{money(totals.credit, form.currency)}</td><td colSpan={6} className="px-3 py-3 text-right">Variance {money(Math.abs(totals.debit - totals.credit), form.currency)}</td></tr></tfoot>
              </table>
            </div>
          </section>
        </div>

        <aside className="space-y-4">
          <section className="border border-slate-200 bg-white p-4">
            <div className="flex items-center gap-2"><WandSparkles className="h-4 w-4 text-blue-700" /><h2 className="text-sm font-black uppercase text-slate-800">Template</h2></div>
            <select value={form.template_id} onChange={(event) => applyTemplate(event.target.value)} className="mt-3 h-10 w-full rounded border border-slate-300 bg-white px-3 text-sm"><option value="">Manual journal</option>{templates.map((template) => <option key={template.id} value={template.id}>{template.template_name}</option>)}</select>
            <p className="mt-2 text-xs font-semibold text-slate-500">Selecting a template replaces current journal lines.</p>
          </section>

          <section className="border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between gap-2"><h2 className="text-sm font-black uppercase text-slate-800">Batch</h2><button type="button" title="Open journal batch" disabled={Boolean(busy)} onClick={createBatch} className="flex h-8 w-8 items-center justify-center rounded border border-slate-300"><FilePlus2 className="h-4 w-4" /></button></div>
            <select value={form.batch_id} onChange={(event) => setForm({ ...form, batch_id: event.target.value })} className="mt-3 h-10 w-full rounded border border-slate-300 bg-white px-3 text-sm"><option value="">No batch</option>{batches.map((batch) => <option key={batch.id} value={batch.id}>{batch.batch_no} / {batch.period}</option>)}</select>
          </section>

          <section className="border border-slate-200 bg-white p-4">
            <div className="flex items-center gap-2"><Paperclip className="h-4 w-4 text-slate-500" /><h2 className="text-sm font-black uppercase text-slate-800">Attachments</h2></div>
            <label className="mt-3 flex cursor-pointer items-center justify-center rounded border border-dashed border-slate-300 px-3 py-6 text-center text-xs font-bold text-slate-600 hover:bg-slate-50"><input type="file" multiple className="sr-only" onChange={(event) => setAttachments(Array.from(event.target.files || []))} />Choose supporting documents</label>
            <div className="mt-2 space-y-1">{attachments.map((file) => <p key={`${file.name}-${file.lastModified}`} className="truncate text-xs font-semibold text-slate-600">{file.name}</p>)}</div>
          </section>

          <button type="button" disabled={Boolean(busy)} onClick={validate} className="inline-flex h-10 w-full items-center justify-center gap-2 rounded bg-blue-700 px-4 text-sm font-bold text-white disabled:opacity-50"><WandSparkles className="h-4 w-4" /> Validate & explain</button>
          <ValidationPanel result={validation} compact />
        </aside>
      </div>
    </JournalShell>
  );
}

