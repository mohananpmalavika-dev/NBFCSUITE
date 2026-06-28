'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, FlaskConical, Play, Plus, Trash2 } from 'lucide-react';
import { apiClient, type AccountingPostingLine } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { JournalShell } from '@/components/accounting/journal-shell';
import { journalError, money, ValidationPanel } from '@/components/accounting/journal-ui';
import type { GlAccountOption, JournalDocument, JournalTemplate, JournalValidation } from '@/components/accounting/journal-types';

interface SimulationResult extends JournalValidation {
  description: string;
  template?: JournalTemplate | null;
  lines: Array<AccountingPostingLine & { sequence: number }>;
}

interface SimulatorLine extends AccountingPostingLine {
  rowId: string;
}

function simulatorLine(direction: 'debit' | 'credit'): SimulatorLine {
  return { rowId: crypto.randomUUID(), gl_account_id: '', debit: direction === 'debit' ? 100000 : 0, credit: direction === 'credit' ? 100000 : 0, currency: 'INR', description: '' };
}

export default function JournalSimulatorPage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();
  const tenantId = user?.tenant_id || user?.branch_id || user?.organization_id || user?.id || 'default';
  const [mode, setMode] = useState<'template' | 'manual'>('template');
  const [templates, setTemplates] = useState<JournalTemplate[]>([]);
  const [accounts, setAccounts] = useState<GlAccountOption[]>([]);
  const [lines, setLines] = useState<SimulatorLine[]>([simulatorLine('debit'), simulatorLine('credit')]);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({
    template_id: '',
    amount: '100000',
    description: 'Journal simulation',
    posting_date: new Date().toISOString().slice(0, 10),
    branch_id: '',
    currency: 'INR',
  });

  const loadOptions = useCallback(async () => {
    if (!token || !tenantId) return;
    try {
      const [templatesResponse, accountsResponse] = await Promise.all([
        apiClient.getJournalTemplates(tenantId),
        apiClient.getGlAccounts(tenantId),
      ]);
      const nextTemplates = templatesResponse.data.items || [];
      setTemplates(nextTemplates);
      setAccounts((accountsResponse.data || []).filter((account: GlAccountOption) => account.status !== 'inactive' && String(account.posting_allowed || 'true') !== 'false'));
      setForm((current) => ({ ...current, template_id: current.template_id || nextTemplates[0]?.id || '' }));
    } catch (error) {
      setMessage(journalError(error, 'Unable to load simulator setup.'));
    }
  }, [tenantId, token]);

  useEffect(() => {
    loadOptions();
  }, [loadOptions]);

  const totals = useMemo(() => lines.reduce((sum, line) => ({
    debit: sum.debit + Number(line.debit || 0),
    credit: sum.credit + Number(line.credit || 0),
  }), { debit: 0, credit: 0 }), [lines]);

  function updateLine(rowId: string, patch: Partial<SimulatorLine>) {
    setLines((current) => current.map((line) => line.rowId === rowId ? { ...line, ...patch } : line));
    setResult(null);
  }

  async function simulate() {
    setBusy('simulate');
    setMessage('');
    try {
      const response = await apiClient.simulateJournal({
        tenant_id: tenantId,
        posting_date: `${form.posting_date}T00:00:00`,
        branch_id: form.branch_id || undefined,
        currency: form.currency,
        source_module: 'manual',
        source_event: 'manual_journal',
        description: form.description,
        ...(mode === 'template'
          ? { template_id: form.template_id, amount: Number(form.amount || 0) }
          : { lines: lines.map(({ rowId: _rowId, ...line }) => ({ ...line, debit: Number(line.debit || 0), credit: Number(line.credit || 0) })) }),
      });
      setResult(response.data);
      setMessage(response.data.valid ? 'Simulation passed. No ledger data was changed.' : 'Simulation found posting issues. No ledger data was changed.');
    } catch (error) {
      setMessage(journalError(error, 'Unable to run journal simulation.'));
    } finally {
      setBusy('');
    }
  }

  async function createDraft() {
    if (!result?.valid) return;
    setBusy('draft');
    setMessage('');
    try {
      const response = await apiClient.createJournal({
        tenant_id: tenantId,
        posting_date: `${form.posting_date}T00:00:00`,
        description: form.description || result.description,
        branch_id: form.branch_id || undefined,
        currency: form.currency,
        template_id: mode === 'template' ? form.template_id : undefined,
        source_module: 'manual',
        source_event: 'manual_journal',
        created_by: user?.username,
        lines: result.lines.map((line) => ({
          gl_account_id: line.gl_account_id,
          account_code: line.account_code,
          debit: Number(line.debit || 0),
          credit: Number(line.credit || 0),
          currency: line.currency || form.currency,
          description: line.description,
          branch_id: form.branch_id || undefined,
        })),
      });
      const journal = response.data as JournalDocument;
      router.push(`/accounting/journals?selected=${journal.id}`);
    } catch (error) {
      setMessage(journalError(error, 'Unable to create draft from simulation.'));
    } finally {
      setBusy('');
    }
  }

  if (isLoading) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Loading simulator...</main>;
  if (!user) return <main className="min-h-screen bg-slate-100 p-6 text-slate-600">Please login to continue.</main>;

  return (
    <JournalShell
      title="Journal Simulator"
      description="Preview validation, GL balances, and trial-balance impact without writing accounting data."
      tenantId={tenantId}
      actions={result?.valid ? <button type="button" disabled={Boolean(busy)} onClick={createDraft} className="inline-flex h-9 items-center gap-2 rounded bg-emerald-700 px-3 text-xs font-bold text-white disabled:opacity-50">Create draft <ArrowRight className="h-4 w-4" /></button> : undefined}
    >
      {message ? <div className="mb-4 border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-900">{message}</div> : null}
      <div className="grid gap-4 xl:grid-cols-[420px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <section className="border border-slate-200 bg-white p-4">
            <div className="grid grid-cols-2 rounded border border-slate-300 bg-slate-50 p-1">
              <button type="button" onClick={() => { setMode('template'); setResult(null); }} className={`h-9 rounded text-xs font-bold ${mode === 'template' ? 'bg-slate-950 text-white' : 'text-slate-600'}`}>Template</button>
              <button type="button" onClick={() => { setMode('manual'); setResult(null); }} className={`h-9 rounded text-xs font-bold ${mode === 'manual' ? 'bg-slate-950 text-white' : 'text-slate-600'}`}>Manual lines</button>
            </div>
            <div className="mt-4 space-y-3">
              {mode === 'template' ? (
                <>
                  <label className="block"><span className="text-xs font-bold text-slate-600">Journal template</span><select value={form.template_id} onChange={(event) => { setForm({ ...form, template_id: event.target.value }); setResult(null); }} className="mt-1 h-10 w-full rounded border border-slate-300 bg-white px-3 text-sm">{templates.map((template) => <option key={template.id} value={template.id}>{template.template_name}</option>)}</select></label>
                  <label className="block"><span className="text-xs font-bold text-slate-600">Transaction amount</span><input type="number" min="0" step="0.01" value={form.amount} onChange={(event) => { setForm({ ...form, amount: event.target.value }); setResult(null); }} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
                </>
              ) : null}
              <label className="block"><span className="text-xs font-bold text-slate-600">Description</span><input value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" /></label>
              <div className="grid grid-cols-2 gap-3">
                <label><span className="text-xs font-bold text-slate-600">Posting date</span><input type="date" value={form.posting_date} onChange={(event) => { setForm({ ...form, posting_date: event.target.value }); setResult(null); }} className="mt-1 h-10 w-full rounded border border-slate-300 px-2 text-sm" /></label>
                <label><span className="text-xs font-bold text-slate-600">Currency</span><input maxLength={3} value={form.currency} onChange={(event) => { setForm({ ...form, currency: event.target.value.toUpperCase() }); setResult(null); }} className="mt-1 h-10 w-full rounded border border-slate-300 px-2 text-sm" /></label>
              </div>
              <label className="block"><span className="text-xs font-bold text-slate-600">Branch</span><input value={form.branch_id} onChange={(event) => { setForm({ ...form, branch_id: event.target.value }); setResult(null); }} className="mt-1 h-10 w-full rounded border border-slate-300 px-3 text-sm" placeholder="Optional branch code" /></label>
            </div>
          </section>

          {mode === 'manual' ? (
            <section className="border border-slate-200 bg-white">
              <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3"><h2 className="text-sm font-black uppercase text-slate-800">Preview lines</h2><button type="button" title="Add simulator line" onClick={() => setLines((current) => [...current, simulatorLine('debit')])} className="flex h-8 w-8 items-center justify-center rounded border border-slate-300"><Plus className="h-4 w-4" /></button></div>
              <div className="divide-y divide-slate-100">
                {lines.map((line, index) => (
                  <div key={line.rowId} className="space-y-2 p-4">
                    <div className="flex items-center justify-between"><span className="text-xs font-black text-slate-500">LINE {index + 1}</span><button type="button" title="Remove simulator line" disabled={lines.length <= 2} onClick={() => setLines((current) => current.filter((item) => item.rowId !== line.rowId))} className="text-rose-600 disabled:text-slate-300"><Trash2 className="h-4 w-4" /></button></div>
                    <select value={line.gl_account_id} onChange={(event) => updateLine(line.rowId, { gl_account_id: event.target.value })} className="h-9 w-full rounded border border-slate-300 bg-white px-2 text-xs"><option value="">Select GL account</option>{accounts.map((account) => <option key={account.id} value={account.id}>{account.account_code} - {account.account_name}</option>)}</select>
                    <div className="grid grid-cols-2 gap-2"><input type="number" min="0" value={line.debit || ''} onChange={(event) => updateLine(line.rowId, { debit: Number(event.target.value), credit: event.target.value ? 0 : line.credit })} className="h-9 rounded border border-slate-300 px-2 text-right text-xs" placeholder="Debit" /><input type="number" min="0" value={line.credit || ''} onChange={(event) => updateLine(line.rowId, { credit: Number(event.target.value), debit: event.target.value ? 0 : line.debit })} className="h-9 rounded border border-slate-300 px-2 text-right text-xs" placeholder="Credit" /></div>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-2 border-t border-slate-200 bg-slate-50 px-4 py-3 text-xs font-black"><span>Debit {money(totals.debit, form.currency)}</span><span className="text-right">Credit {money(totals.credit, form.currency)}</span></div>
            </section>
          ) : null}

          <button type="button" disabled={Boolean(busy) || (mode === 'template' && !form.template_id)} onClick={simulate} className="inline-flex h-11 w-full items-center justify-center gap-2 rounded bg-blue-700 px-4 text-sm font-bold text-white disabled:opacity-50"><Play className="h-4 w-4" /> Run simulation</button>
        </aside>

        <div className="min-w-0 space-y-4">
          <ValidationPanel result={result} />
          {result ? (
            <>
              <section className="border border-slate-200 bg-white">
                <div className="flex items-center gap-2 border-b border-slate-200 px-4 py-3"><FlaskConical className="h-4 w-4 text-blue-700" /><h2 className="text-sm font-black uppercase text-slate-800">GL impact</h2></div>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[760px] text-sm">
                    <thead><tr className="border-b border-slate-200 bg-slate-50 text-left text-[11px] font-black uppercase text-slate-500"><th className="px-4 py-3">Account</th><th className="px-4 py-3 text-right">Debit</th><th className="px-4 py-3 text-right">Credit</th><th className="px-4 py-3 text-right">Current</th><th className="px-4 py-3 text-right">Projected</th></tr></thead>
                    <tbody>{result.impact.gl_accounts.map((account) => <tr key={`${account.account_id}-${account.debit}-${account.credit}`} className="border-b border-slate-100"><td className="px-4 py-3"><p className="font-black">{account.account_name}</p><p className="text-xs text-slate-500">{account.account_code}</p></td><td className="px-4 py-3 text-right font-bold">{account.debit ? money(account.debit, form.currency) : '-'}</td><td className="px-4 py-3 text-right font-bold">{account.credit ? money(account.credit, form.currency) : '-'}</td><td className="px-4 py-3 text-right text-slate-600">{money(account.current_balance, form.currency)}</td><td className="px-4 py-3 text-right font-black">{money(account.projected_balance, form.currency)}</td></tr>)}</tbody>
                  </table>
                </div>
              </section>
              <section className={`grid gap-4 border p-4 sm:grid-cols-3 ${result.impact.trial_balance.remains_balanced ? 'border-emerald-200 bg-emerald-50' : 'border-rose-200 bg-rose-50'}`}>
                <div><p className="text-xs font-bold uppercase text-slate-500">Trial balance debit</p><p className="mt-1 text-xl font-black">{money(result.impact.trial_balance.debit_change, form.currency)}</p></div>
                <div><p className="text-xs font-bold uppercase text-slate-500">Trial balance credit</p><p className="mt-1 text-xl font-black">{money(result.impact.trial_balance.credit_change, form.currency)}</p></div>
                <div><p className="text-xs font-bold uppercase text-slate-500">After simulation</p><p className={`mt-1 text-xl font-black ${result.impact.trial_balance.remains_balanced ? 'text-emerald-800' : 'text-rose-800'}`}>{result.impact.trial_balance.remains_balanced ? 'Balanced' : 'Variance'}</p></div>
              </section>
            </>
          ) : (
            <section className="flex min-h-[420px] flex-col items-center justify-center border border-dashed border-slate-300 bg-white px-6 text-center"><FlaskConical className="h-9 w-9 text-slate-400" /><h2 className="mt-4 text-lg font-black text-slate-800">No accounting data will be written</h2><p className="mt-2 max-w-md text-sm font-semibold text-slate-500">Choose a template or enter manual lines, then run the simulator to inspect every posting control and projected balance.</p></section>
          )}
        </div>
      </div>
    </JournalShell>
  );
}

