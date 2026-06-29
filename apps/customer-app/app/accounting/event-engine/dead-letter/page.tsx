"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { AccountingEvent } from '../../accountingApi';
import { EmptyState, EventActionButton, EventBadge, EventPageFrame, EventTable, LoadingBlock, formatDate } from '../eventComponents';

export default function DeadLetterPage() {
  const [items, setItems] = useState<AccountingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.getEventQueue(DEFAULT_ACCOUNTING_TENANT, 'dead_letter_queue');
      setItems(body.items);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function retry(event: AccountingEvent) {
    setBusyId(event.id);
    try {
      await accountingApi.retryEvent(event.id, DEFAULT_ACCOUNTING_TENANT, 'manual review completed');
      await load();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <AppShell>
      <EventPageFrame title="Dead Letter Queue" description="Investigate failed events, correct source data or posting rules, then return events to retry.">
        {loading ? (
          <LoadingBlock />
        ) : items.length === 0 ? (
          <EmptyState message="No dead-letter events require review." />
        ) : (
          <EventTable columns={['Event', 'Module', 'Reference', 'Date', 'Failure', 'Validation', 'Queue', 'Action']}>
            {items.map((event) => (
              <tr key={event.id} className="border-t border-border-light hover:bg-gray-50">
                <td className="p-3 font-semibold"><Link href={`/accounting/event-engine/events/${event.id}`} className="text-accent-primary underline">{event.event_type}</Link></td>
                <td className="p-3 text-text-secondary">{event.source_module}</td>
                <td className="p-3 text-text-secondary">{event.reference_number ?? event.reference_id}</td>
                <td className="p-3 text-text-secondary">{formatDate(event.business_date)}</td>
                <td className="max-w-md p-3 text-text-secondary">{event.dead_letter_reason ?? '-'}</td>
                <td className="p-3"><EventBadge value={event.validation_status} /></td>
                <td className="p-3"><EventBadge value={event.queue_status} /></td>
                <td className="p-3"><EventActionButton onClick={() => retry(event)} disabled={busyId === event.id}>Retry</EventActionButton></td>
              </tr>
            ))}
          </EventTable>
        )}
      </EventPageFrame>
    </AppShell>
  );
}
