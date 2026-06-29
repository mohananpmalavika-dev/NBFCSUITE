"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { AccountingEvent } from '../../accountingApi';
import { EmptyState, EventActionButton, EventBadge, EventPageFrame, EventTable, LoadingBlock } from '../eventComponents';

export default function ValidationPage() {
  const [items, setItems] = useState<AccountingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.listEvents(DEFAULT_ACCOUNTING_TENANT, 'limit=100');
      setItems(body.items.filter((event) => event.validation_status !== 'passed'));
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function validate(event: AccountingEvent) {
    setBusyId(event.id);
    try {
      await accountingApi.validateEvent(event.id, DEFAULT_ACCOUNTING_TENANT);
      await load();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <AppShell>
      <EventPageFrame title="Validation" description="Run mandatory field, duplicate, accounting period, currency, dimension, and posting rule checks.">
        {loading ? (
          <LoadingBlock />
        ) : items.length === 0 ? (
          <EmptyState message="No events are waiting for validation." />
        ) : (
          <EventTable columns={['Event', 'Module', 'Reference', 'Validation', 'Errors', 'Warnings', 'Action']}>
            {items.map((event) => (
              <tr key={event.id} className="border-t border-border-light hover:bg-gray-50">
                <td className="p-3 font-semibold"><Link href={`/accounting/event-engine/events/${event.id}`} className="text-accent-primary underline">{event.event_type}</Link></td>
                <td className="p-3 text-text-secondary">{event.source_module}</td>
                <td className="p-3 text-text-secondary">{event.reference_number ?? event.reference_id}</td>
                <td className="p-3"><EventBadge value={event.validation_status} /></td>
                <td className="max-w-xs p-3 text-text-secondary">{event.validation_result?.errors?.join('; ') || '-'}</td>
                <td className="max-w-xs p-3 text-text-secondary">{event.validation_result?.warnings?.join('; ') || '-'}</td>
                <td className="p-3"><EventActionButton onClick={() => validate(event)} disabled={busyId === event.id}>Validate</EventActionButton></td>
              </tr>
            ))}
          </EventTable>
        )}
      </EventPageFrame>
    </AppShell>
  );
}
