"use client";

import { AppShell } from '../../../components/AppShell';
import { CalendarPageFrame, ReportCard } from '../calendarComponents';

const reports = [
  ['Financial Calendar', 'Financial years, generated periods, business days, and assigned calendar scopes.'],
  ['Period Status', 'Open, future, soft close, hard close, archived, and reopen workflow states.'],
  ['Close Report', 'EOD, EOM, EOQ, and EOY execution summaries with checklist completion.'],
  ['Reopen Report', 'Period reopen requests, approvals, reasons, and audit trail.'],
  ['Holiday Calendar', 'National, state, branch, treasury, forex, payroll, and tax calendars.'],
  ['Posting Window', 'Accounting date and posting-allowed windows with late adjustment policy.'],
  ['Close SLA', 'Timeliness, bottlenecks, exceptions, and calendar health score.'],
  ['EOD Summary', 'Business-day lifecycle, trial balance status, and branch close certificate.'],
  ['EOM Summary', 'Accrual, depreciation, provisioning, reconciliation, and trial balance readiness.'],
  ['EOY Summary', 'Final close, profit transfer, opening balance, new year, and archive status.'],
];

export default function CalendarReportsPage() {
  return (
    <AppShell>
      <CalendarPageFrame
        title="Calendar Reports"
        description="Standard reporting catalog for financial calendar, period control, close operations, and compliance calendars."
      >
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {reports.map(([title, description]) => (
            <ReportCard key={title} title={title} description={description} />
          ))}
        </div>
      </CalendarPageFrame>
    </AppShell>
  );
}
