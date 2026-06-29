"use client";

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { AccountingEvent, AccountingEventPayload } from '../../accountingApi';
import { EmptyState, EventActionButton, EventBadge, EventPageFrame, EventTable, LoadingBlock, formatAmount, formatDate } from '../eventComponents';

const initialForm = {
  event_type: 'LOAN_DISBURSED',
  source_module: 'Loan',
  reference_id: '',
  reference_number: '',
  amount: '250000',
  currency: 'INR',
  priority: 'normal',
};

export default function EventExplorerPage() {
  const [items, setItems] = useState<AccountingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [module, setModule] = useState('');
  const [status, setStatus] = useState('');
  const [form, setForm] = useState(initialForm);
  const [creating, setCreating] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const params = useMemo(() => {
    const parts = ['limit=100'];
    if (query.trim()) parts.push(`q=${encodeURIComponent(query.trim())}`);
    if (module) parts.push(`source_module=${encodeURIComponent(module)}`);
    if (status) parts.push(`status=${encodeURIComponent(status)}`);
    return parts.join('&');
  }, [query, module, status]);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listEvents(DEFAULT_ACCOUNTING_TENANT, params);
      setItems(body.items);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [params]);

  function update(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function createEvent() {
    setCreating(true);
    setMessage(null);
    try {
      const payload: AccountingEventPayload = {
        tenant_id: DEFAULT_ACCOUNTING_TENANT,
        event_type: form.event_type.trim(),
        source_module: form.source_module.trim(),
        reference_id: form.reference_id.trim(),
        reference_number: form.reference_number.trim() || undefined,
        business_date: new Date().toISOString(),
        currency: form.currency || 'INR',
        amount: Number(form.amount || 0),
        priority: form.priority,
        dimensions: { branch_id: 'branch-001', product_id: 'gold-loan', currency: form.currency || 'INR' },
        payload: { amount: Number(form.amount || 0), currency: form.currency || 'INR' },
        created_by: 'event-console',
      };
      const created = await accountingApi.createEvent(payload);
      setMessage(`Created event ${created.event_type}`);
      setForm(initialForm);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Create failed');
    } finally {
      setCreating(false);
    }
  }

  async function action(event: AccountingEvent, type: 'validate' | 'retry' | 'replay') {
    setBusyId(event.id);
    setMessage(null);
    try {
      const result =
        type === 'validate'
          ? await accountingApi.validateEvent(event.id, DEFAULT_ACCOUNTING_TENANT)
          : type === 'retry'
            ? await accountingApi.retryEvent(event.id, DEFAULT_ACCOUNTING_TENANT)
            : await accountingApi.replayEvent(event.id, DEFAULT_ACCOUNTING_TENANT);
      setMessage(`${result.event_type} ${type} -> ${result.status}`);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : `${type} failed`);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <AppShell>
      <EventPageFrame title="Event Explorer" description="Search, filter, create, validate, retry, and replay accounting events from source modules.">
        <div className="space-y-4">
          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="grid gap-3 md:grid-cols-[minmax(220px,1fr)_180px_180px]">
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Search</span>
                <input className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Event type, module, reference" />
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Module</span>
                <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={module} onChange={(event) => setModule(event.target.value)}>
                  <option value="">All modules</option>
                  {['Loan', 'Deposit', 'Gold Loan', 'Treasury', 'Forex', 'HRMS', 'Procurement', 'Assets', 'CRM'].map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              <label className="block space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Status</span>
                <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
                  <option value="">All statuses</option>
                  {['created', 'queued', 'failed', 'posted', 'completed'].map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
            </div>
          </div>

          <div className="rounded-md border border-border-default bg-background-surface p-4">
            <div className="grid gap-3 md:grid-cols-4">
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.event_type} onChange={(event) => update('event_type', event.target.value)} placeholder="Event type" />
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.source_module} onChange={(event) => update('source_module', event.target.value)} placeholder="Source module" />
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.reference_id} onChange={(event) => update('reference_id', event.target.value)} placeholder="Reference ID" />
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.reference_number} onChange={(event) => update('reference_number', event.target.value)} placeholder="Reference number" />
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.amount} onChange={(event) => update('amount', event.target.value)} placeholder="Amount" />
              <input className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.currency} onChange={(event) => update('currency', event.target.value)} placeholder="Currency" />
              <select className="h-10 rounded-md border border-border-default px-3 text-sm" value={form.priority} onChange={(event) => update('priority', event.target.value)}>
                <option value="normal">normal</option>
                <option value="high">high</option>
                <option value="urgent">urgent</option>
              </select>
              <button type="button" onClick={createEvent} disabled={creating || !form.reference_id.trim()} className="h-10 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary disabled:opacity-60">
                {creating ? 'Creating...' : 'Create Event'}
              </button>
            </div>
          </div>

          {message ? <div className="rounded-md border border-border-default bg-background-surface p-3 text-sm text-text-secondary">{message}</div> : null}

          {loading ? (
            <LoadingBlock />
          ) : items.length === 0 ? (
            <EmptyState message="No accounting events matched the current filters." />
          ) : (
            <EventTable columns={['Event', 'Module', 'Reference', 'Priority', 'Amount', 'Date', 'Queue', 'Status', 'Actions']}>
              {items.map((event) => (
                <tr key={event.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold"><Link href={`/accounting/event-engine/events/${event.id}`} className="text-accent-primary underline">{event.event_type}</Link></td>
                  <td className="p-3 text-text-secondary">{event.source_module}</td>
                  <td className="p-3 text-text-secondary">{event.reference_number ?? event.reference_id}</td>
                  <td className="p-3 text-text-secondary">{event.priority}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(event.amount, event.currency)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(event.business_date)}</td>
                  <td className="p-3"><EventBadge value={event.queue_status} /></td>
                  <td className="p-3"><EventBadge value={event.status} /></td>
                  <td className="p-3">
                    <div className="flex flex-wrap gap-2">
                      <EventActionButton onClick={() => action(event, 'validate')} disabled={busyId === event.id}>Validate</EventActionButton>
                      <EventActionButton onClick={() => action(event, 'retry')} disabled={busyId === event.id}>Retry</EventActionButton>
                      <EventActionButton onClick={() => action(event, 'replay')} disabled={busyId === event.id}>Replay</EventActionButton>
                    </div>
                  </td>
                </tr>
              ))}
            </EventTable>
          )}
        </div>
      </EventPageFrame>
    </AppShell>
  );
}
