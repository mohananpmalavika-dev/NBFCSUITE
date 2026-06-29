"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { AccountingEvent } from '../../accountingApi';
import { EmptyState, EventActionButton, EventBadge, EventPageFrame, EventTable, LoadingBlock, formatDate } from '../eventComponents';

export default function RetryQueuePage() {
  const [items, setItems] = useState<AccountingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const body = await accountingApi.getEventQueue(DEFAULT_ACCOUNTING_TENANT, 'retry_queue');
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

  async function replay(event: AccountingEvent) {
    setBusyId(event.id);
    try {
      await accountingApi.replayEvent(event.id, DEFAULT_ACCOUNTING_TENANT);
      await load();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <AppShell>
      <EventPageFrame title="Retry Queue" description="Review events scheduled for backoff retry and replay events after rule or data corrections.">
        {loading ? (
          <LoadingBlock />
        ) : items.length === 0 ? (
          <EmptyState message="No retry events are queued." />
        ) : (
          <EventTable columns={['Event', 'Module', 'Reference', 'Retry Count', 'Next Retry', 'Reason', 'Status', 'Action']}>
            {items.map((event) => (
              <tr key={event.id} className="border-t border-border-light hover:bg-gray-50">
                <td className="p-3 font-semibold"><Link href={`/accounting/event-engine/events/${event.id}`} className="text-accent-primary underline">{event.event_type}</Link></td>
                <td className="p-3 text-text-secondary">{event.source_module}</td>
                <td className="p-3 text-text-secondary">{event.reference_number ?? event.reference_id}</td>
                <td className="p-3 text-text-secondary">{event.retry_count}</td>
                <td className="p-3 text-text-secondary">{formatDate(event.next_retry_at)}</td>
                <td className="p-3 text-text-secondary">{event.dead_letter_reason ?? '-'}</td>
                <td className="p-3"><EventBadge value={event.queue_status} /></td>
                <td className="p-3"><EventActionButton onClick={() => replay(event)} disabled={busyId === event.id}>Replay</EventActionButton></td>
              </tr>
            ))}
          </EventTable>
        )}
      </EventPageFrame>
    </AppShell>
  );
}
