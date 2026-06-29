"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { AccountingEvent, EventQueueResponse } from '../../accountingApi';
import { EmptyState, EventActionButton, EventBadge, EventMetric, EventPageFrame, EventTable, LoadingBlock, formatAmount, formatDate } from '../eventComponents';

export default function QueueMonitorPage() {
  const [queue, setQueue] = useState<EventQueueResponse | null>(null);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  async function load(queueStatus = filter) {
    setLoading(true);
    try {
      setQueue(await accountingApi.getEventQueue(DEFAULT_ACCOUNTING_TENANT, queueStatus));
    } catch {
      setQueue(null);
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

  function changeFilter(value: string) {
    setFilter(value);
    load(value);
  }

  return (
    <AppShell>
      <EventPageFrame title="Queue Monitor" description="Monitor priority, normal, retry, and dead-letter queues for accounting event processing.">
        {loading ? (
          <LoadingBlock />
        ) : queue ? (
          <div className="space-y-4">
            <div className="grid gap-3 md:grid-cols-4">
              <EventMetric label="Priority" value={queue.counts.priority_queue ?? 0} note="High urgency events" />
              <EventMetric label="Normal" value={queue.counts.normal_queue ?? 0} note="Standard processing" />
              <EventMetric label="Retry" value={queue.counts.retry_queue ?? 0} note="Backoff queue" />
              <EventMetric label="Dead Letter" value={queue.counts.dead_letter_queue ?? 0} note="Manual review" />
            </div>

            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <label className="block max-w-xs space-y-1">
                <span className="text-sm font-semibold text-text-secondary">Queue</span>
                <select className="h-10 w-full rounded-md border border-border-default px-3 text-sm" value={filter} onChange={(event) => changeFilter(event.target.value)}>
                  <option value="">All queues</option>
                  <option value="priority_queue">priority_queue</option>
                  <option value="normal_queue">normal_queue</option>
                  <option value="retry_queue">retry_queue</option>
                  <option value="dead_letter_queue">dead_letter_queue</option>
                </select>
              </label>
            </div>

            {queue.items.length === 0 ? (
              <EmptyState message="No events in this queue." />
            ) : (
              <EventTable columns={['Event', 'Module', 'Reference', 'Priority', 'Amount', 'Date', 'Queue', 'Validation', 'Action']}>
                {queue.items.map((event) => (
                  <tr key={event.id} className="border-t border-border-light hover:bg-gray-50">
                    <td className="p-3 font-semibold"><Link href={`/accounting/event-engine/events/${event.id}`} className="text-accent-primary underline">{event.event_type}</Link></td>
                    <td className="p-3 text-text-secondary">{event.source_module}</td>
                    <td className="p-3 text-text-secondary">{event.reference_number ?? event.reference_id}</td>
                    <td className="p-3 text-text-secondary">{event.priority}</td>
                    <td className="p-3 text-text-secondary">{formatAmount(event.amount, event.currency)}</td>
                    <td className="p-3 text-text-secondary">{formatDate(event.business_date)}</td>
                    <td className="p-3"><EventBadge value={event.queue_status} /></td>
                    <td className="p-3"><EventBadge value={event.validation_status} /></td>
                    <td className="p-3"><EventActionButton onClick={() => validate(event)} disabled={busyId === event.id}>Validate</EventActionButton></td>
                  </tr>
                ))}
              </EventTable>
            )}
          </div>
        ) : (
          <EmptyState message="Event queue API is unavailable." />
        )}
      </EventPageFrame>
    </AppShell>
  );
}
