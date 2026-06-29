"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../accountingApi';
import type { AccountingEvent, EventDashboard } from '../accountingApi';
import { EmptyState, EventBadge, EventMetric, EventPageFrame, EventTable, LoadingBlock, formatAmount, formatDate } from './eventComponents';

export default function EventEngineDashboardPage() {
  const [dashboard, setDashboard] = useState<EventDashboard | null>(null);
  const [events, setEvents] = useState<AccountingEvent[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [dashboardBody, eventsBody] = await Promise.all([
        accountingApi.getEventDashboard(DEFAULT_ACCOUNTING_TENANT),
        accountingApi.listEvents(DEFAULT_ACCOUNTING_TENANT, 'limit=8'),
      ]);
      setDashboard(dashboardBody);
      setEvents(eventsBody.items);
    } catch {
      setDashboard(null);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <EventPageFrame
        title="Accounting Event Engine"
        description="Transform business transactions into standardized accounting events that can be validated, queued, retried, replayed, and monitored."
      >
        {loading ? (
          <LoadingBlock />
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm font-semibold text-text-primary">Tenant</div>
              <div className="text-sm text-text-secondary">{DEFAULT_ACCOUNTING_TENANT}</div>
              <div className="mt-2 text-sm text-text-secondary">{dashboard.summary.message}</div>
            </div>

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <EventMetric label="Today's Events" value={dashboard.kpis.todays_events} note="Created today" />
              <EventMetric label="Pending" value={dashboard.kpis.pending} note="Created, validated, or queued" />
              <EventMetric label="Failed" value={dashboard.kpis.failed} note="Validation or processing failures" />
              <EventMetric label="Health" value={`${dashboard.kpis.event_health}%`} note={dashboard.summary.status} />
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              <EventMetric label="Posted" value={dashboard.kpis.posted} note="Completed posting pipeline" />
              <EventMetric label="Avg Time" value={`${dashboard.kpis.average_processing_time_ms}ms`} note="Processing latency" />
              <EventMetric label="Retry Queue" value={dashboard.kpis.retry_queue} note="Backoff retries" />
              <EventMetric label="Dead Letter" value={dashboard.kpis.dead_letter_queue} note="Manual review queue" />
            </div>

            <EventTable columns={['Event', 'Module', 'Reference', 'Priority', 'Amount', 'Business Date', 'Queue', 'Status']}>
              {events.map((event) => (
                <tr key={event.id} className="border-t border-border-light hover:bg-gray-50">
                  <td className="p-3 font-semibold">
                    <Link href={`/accounting/event-engine/events/${event.id}`} className="text-accent-primary underline">
                      {event.event_type}
                    </Link>
                  </td>
                  <td className="p-3 text-text-secondary">{event.source_module}</td>
                  <td className="p-3 text-text-secondary">{event.reference_number ?? event.reference_id}</td>
                  <td className="p-3 text-text-secondary">{event.priority}</td>
                  <td className="p-3 text-text-secondary">{formatAmount(event.amount, event.currency)}</td>
                  <td className="p-3 text-text-secondary">{formatDate(event.business_date)}</td>
                  <td className="p-3"><EventBadge value={event.queue_status} /></td>
                  <td className="p-3"><EventBadge value={event.status} /></td>
                </tr>
              ))}
              {events.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-text-secondary">No accounting events found.</td>
                </tr>
              ) : null}
            </EventTable>
          </div>
        ) : (
          <EmptyState message="Accounting Event Engine API is unavailable. Check that the accounting service is running." />
        )}
      </EventPageFrame>
    </AppShell>
  );
}
