"use client";

import { AppShell } from '../../../components/AppShell';
import { EventPageFrame, ReportCard } from '../eventComponents';

const reports = [
  ['Event Register', 'Complete accounting event list by module, type, reference, date, status, and queue.'],
  ['Event Failures', 'Validation errors, posting rule gaps, period failures, duplicate risks, and source integrity issues.'],
  ['Retry Report', 'Retry count, backoff windows, replay history, and manual intervention reasons.'],
  ['Dead Letter Queue', 'Failed events pending finance review with rule/data remediation status.'],
  ['Throughput Report', 'Daily and module-wise event volume, queue movement, and processing trends.'],
  ['Processing Time', 'Latency by module, event type, validation stage, queue, and posting stage.'],
  ['Module-wise Events', 'Loan, deposit, gold loan, treasury, forex, HRMS, procurement, asset, and CRM events.'],
  ['AI Prediction Report', 'Failure prediction, duplicate risk, unusual event patterns, and retry recommendations.'],
];

export default function EventReportsPage() {
  return (
    <AppShell>
      <EventPageFrame title="Event Reports" description="Standard reporting catalog for event intake, validation, queues, retries, dead letters, and AI diagnostics.">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {reports.map(([title, description]) => <ReportCard key={title} title={title} description={description} />)}
        </div>
      </EventPageFrame>
    </AppShell>
  );
}
