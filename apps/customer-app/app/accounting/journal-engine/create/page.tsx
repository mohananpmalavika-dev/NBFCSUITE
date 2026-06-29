"use client";

import { useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import { JournalPageFrame } from '../journalComponents';

const initialForm = {
  description: 'Manual journal adjustment',
  reference: 'JV-REF-001',
  voucher_type: 'manual_journal',
  posting_date: '2026-06-28T00:00:00',
  branch_id: 'BR-001',
  debit_account_code: '5100_OPERATING_EXPENSE',
  credit_account_code: '1120_BANK',
  amount: '1000',
};

export default function DraftJournalPage() {
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [createdId, setCreatedId] = useState('');

  function update(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submit() {
    setSaving(true);
    setMessage('Creating journal...');
    try {
      const amount = Number(form.amount);
      const journal = await accountingApi.createJournal({
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        posting_date: form.posting_date,
        voucher_type: form.voucher_type,
        source_module: 'manual',
        source_event: 'manual_journal',
        description: form.description,
        reference: form.reference,
        branch_id: form.branch_id,
        created_by: 'journal-maker',
        lines: [
          { account_code: form.debit_account_code, debit: amount, credit: 0, branch_id: form.branch_id, description: 'Debit line' },
          { account_code: form.credit_account_code, debit: 0, credit: amount, branch_id: form.branch_id, description: 'Credit line' },
        ],
      });
      setCreatedId(journal.id);
      setMessage(`Journal ${journal.journal_number ?? journal.journal_no} created as ${journal.status}.`);
    } catch {
      setMessage('Unable to create journal. Confirm the GL accounts exist and are postable.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <JournalPageFrame title="Draft Journals" description="Create manual, adjustment, accrual, intercompany, and foreign-currency journal drafts with validation at creation time.">
        <div className="space-y-4">
          <div className="grid gap-3 rounded-md border border-border-default bg-background-surface p-4 md:grid-cols-3">
            <input className="h-10 rounded-md border border-border-default px-3 text-sm md:col-span-2" value={form.description} onChange={(event) => update('description', event.target.value)} placeholder="Description" />
            <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.reference} onChange={(event) => update('reference', event.target.value)} placeholder="Reference" />
            <select className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.voucher_type} onChange={(event) => update('voucher_type', event.target.value)}>
              <option value="manual_journal">Manual Journal</option>
              <option value="adjustment">Adjustment Journal</option>
              <option value="accrual">Accrual Journal</option>
              <option value="intercompany">Intercompany Journal</option>
            </select>
            <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.posting_date} onChange={(event) => update('posting_date', event.target.value)} placeholder="Posting date" />
            <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.branch_id} onChange={(event) => update('branch_id', event.target.value)} placeholder="Branch" />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="mb-3 text-sm font-semibold text-text-primary">Debit Line</div>
              <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.debit_account_code} onChange={(event) => update('debit_account_code', event.target.value)} placeholder="Debit GL account" />
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="mb-3 text-sm font-semibold text-text-primary">Credit Line</div>
              <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={form.credit_account_code} onChange={(event) => update('credit_account_code', event.target.value)} placeholder="Credit GL account" />
            </div>
          </div>

          <div className="flex items-center justify-between rounded-md border border-border-default bg-background-surface p-4">
            <input className="h-10 w-48 rounded-md border border-border-default px-3 text-sm" value={form.amount} onChange={(event) => update('amount', event.target.value)} placeholder="Amount" />
            <button type="button" onClick={submit} disabled={saving} className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60">{saving ? 'Creating...' : 'Create Journal'}</button>
          </div>

          {message ? (
            <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">
              {message}
              {createdId ? <Link href={`/accounting/journal-engine/journals/${createdId}`} className="ml-2 font-semibold text-accent-primary underline">Open 360</Link> : null}
            </div>
          ) : null}
        </div>
      </JournalPageFrame>
    </AppShell>
  );
}
