"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { accountingApi, DEFAULT_ACCOUNTING_TENANT } from '../../accountingApi';
import type { EventDashboard } from '../../accountingApi';
import { EmptyState, EventMetric, EventPageFrame, EventTable, LoadingBlock } from '../eventComponents';

export default function EventMonitoringPage() {
  const [dashboard, setDashboard] = useState<EventDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setDashboard(await accountingApi.getEventDashboard(DEFAULT_ACCOUNTING_TENANT));
      } catch {
        setDashboard(null);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <AppShell>
      <EventPageFrame title="Event Monitoring" description="Track real-time queue size, latency, throughput, success rate, error rate, and retry volume.">
        {loading ? (
          <LoadingBlock />
        ) : dashboard ? (
          <div className="space-y-6">
            <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
              <EventMetric label="Queue Size" value={dashboard.monitoring.queue_size} note="Active processing backlog" />
              <EventMetric label="Avg Latency" value={`${dashboard.monitoring.average_latency_ms}ms`} note="Processing delay" />
              <EventMetric label="Throughput" value={dashboard.monitoring.throughput} note="Events today" />
              <EventMetric label="Success" value={`${dashboard.monitoring.success_percent}%`} note="Posted or completed" />
              <EventMetric label="Error" value={`${dashboard.monitoring.error_percent}%`} note="Failed share" />
              <EventMetric label="Retries" value={dashboard.monitoring.retry_count} note="Retry attempts" />
            </div>

            <EventTable columns={['Chart', 'Values']}>
              <tr className="border-t border-border-light">
                <td className="p-3 font-semibold text-text-primary">Events by Module</td>
                <td className="p-3 text-text-secondary">{dashboard.charts.events_by_module.map((item) => `${item.label}: ${item.value}`).join(', ') || '-'}</td>
              </tr>
              <tr className="border-t border-border-light">
                <td className="p-3 font-semibold text-text-primary">Events by Status</td>
                <td className="p-3 text-text-secondary">{dashboard.charts.events_by_status.map((item) => `${item.label}: ${item.value}`).join(', ') || '-'}</td>
              </tr>
              <tr className="border-t border-border-light">
                <td className="p-3 font-semibold text-text-primary">Failure Analysis</td>
                <td className="p-3 text-text-secondary">{dashboard.charts.failure_analysis.map((item) => `${item.label}: ${item.value}`).join(', ') || '-'}</td>
              </tr>
            </EventTable>
          </div>
        ) : (
          <EmptyState message="Event monitoring data is unavailable." />
        )}
      </EventPageFrame>
    </AppShell>
  );
}
