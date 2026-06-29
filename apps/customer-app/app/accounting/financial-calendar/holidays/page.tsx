"use client";

import { AppShell } from '../../../components/AppShell';
import { CalendarPageFrame, CalendarTable, ReportCard } from '../calendarComponents';

const holidayScopes = [
  ['National Holidays', 'India-wide banking holidays and statutory closures', 'Corporate, Branch'],
  ['State Holidays', 'Regional holidays that affect branch posting windows', 'Branch, Treasury'],
  ['Treasury Calendar', 'Market, settlement, currency, and bank holidays', 'Treasury, Forex'],
  ['Tax Calendar', 'GST, TDS, TCS, RBI, ROC, and income tax due dates', 'Tax, Compliance'],
  ['Payroll Calendar', 'Payroll processing periods, salary cutoffs, and accrual dates', 'Payroll'],
];

export default function HolidayCalendarPage() {
  return (
    <AppShell>
      <CalendarPageFrame
        title="Holiday Calendar"
        description="Coordinate national, state, branch, treasury, forex, payroll, and tax calendars for posting control."
      >
        <div className="space-y-4">
          <CalendarTable columns={['Calendar', 'Purpose', 'Applies To']}>
            {holidayScopes.map(([calendar, purpose, appliesTo]) => (
              <tr key={calendar} className="border-t border-border-light hover:bg-gray-50">
                <td className="p-3 font-semibold text-text-primary">{calendar}</td>
                <td className="p-3 text-text-secondary">{purpose}</td>
                <td className="p-3 text-text-secondary">{appliesTo}</td>
              </tr>
            ))}
          </CalendarTable>

          <div className="grid gap-3 md:grid-cols-2">
            <ReportCard title="Weekend Rules" description="Configure Saturday, Sunday, alternate Saturday, and branch-specific non-business days." />
            <ReportCard title="Settlement Exceptions" description="Track treasury and forex settlement holidays separately from branch business days." />
            <ReportCard title="Regulatory Deadlines" description="Maintain GST, TDS, RBI, ROC, and audit checkpoints as calendar obligations." />
            <ReportCard title="Posting Impact" description="Use calendar exceptions to block or defer accounting events before journal generation." />
          </div>
        </div>
      </CalendarPageFrame>
    </AppShell>
  );
}
