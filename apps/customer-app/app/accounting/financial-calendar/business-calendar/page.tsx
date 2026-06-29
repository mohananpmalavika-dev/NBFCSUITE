"use client";

import { AppShell } from '../../../components/AppShell';
import { CalendarMetric, CalendarPageFrame, CalendarTable, ReportCard } from '../calendarComponents';

const sessions = [
  ['Open', 'Start business day and enable transaction sessions', 'Operations'],
  ['Transactions', 'Accept teller, lending, deposit, treasury, and journal activity', 'Branch, Digital'],
  ['Validation', 'Check pending transactions, balancing, exceptions, and approvals', 'Operations, Finance'],
  ['EOD', 'Run close checklist, accounting postings, reconciliation, and certificates', 'Finance'],
  ['Closed', 'Lock business day and preserve audit trail', 'Compliance'],
];

export default function BusinessCalendarPage() {
  return (
    <AppShell>
      <CalendarPageFrame
        title="Business Calendar"
        description="Model business days, sessions, posting windows, branch calendars, and close lifecycle controls."
      >
        <div className="space-y-4">
          <div className="grid gap-3 md:grid-cols-4">
            <CalendarMetric label="Hierarchy" value="FY > Q > M > W > Day" note="Enterprise calendar structure" />
            <CalendarMetric label="Posting Window" value="T+35" note="Configurable late adjustment window" />
            <CalendarMetric label="Business Session" value="5 stages" note="Open to closed lifecycle" />
            <CalendarMetric label="Calendar Types" value="6" note="Corporate, payroll, treasury, forex, tax, audit" />
          </div>

          <CalendarTable columns={['Stage', 'Control', 'Owner']}>
            {sessions.map(([stage, control, owner]) => (
              <tr key={stage} className="border-t border-border-light hover:bg-gray-50">
                <td className="p-3 font-semibold text-text-primary">{stage}</td>
                <td className="p-3 text-text-secondary">{control}</td>
                <td className="p-3 text-text-secondary">{owner}</td>
              </tr>
            ))}
          </CalendarTable>

          <div className="grid gap-3 md:grid-cols-2">
            <ReportCard title="Branch Calendar" description="Branch-specific business days inherit enterprise rules and override regional holidays where approved." />
            <ReportCard title="Posting Guardrails" description="Journal posting validates period state and blocks future, hard-closed, archived, or locked periods." />
          </div>
        </div>
      </CalendarPageFrame>
    </AppShell>
  );
}
