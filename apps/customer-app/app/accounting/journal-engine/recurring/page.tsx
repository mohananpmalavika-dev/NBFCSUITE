"use client";

import { AppShell } from '../../../components/AppShell';
import { JournalPageFrame, ReportCard } from '../journalComponents';

const recurringControls = [
  ['Rent Accrual', 'Monthly schedule, holiday-aware preview, automatic reversal on first business day.'],
  ['Salary Provision', 'Monthly payroll accrual with branch and cost-center dimensions.'],
  ['Insurance Amortization', 'Monthly allocation from prepaid asset to operating expense.'],
  ['Quarterly Accruals', 'Quarterly close templates with validation and retry controls.'],
  ['Generation Monitor', 'Tracks generated, skipped, failed, and retried recurring journals.'],
  ['Reversal Schedule', 'Schedules auto-reversal and exposes maker-checker approval state.'],
];

export default function RecurringJournalsPage() {
  return (
    <AppShell>
      <JournalPageFrame title="Recurring Journals" description="Recurring journal templates, generation schedules, holiday-aware previews, retries, and reversal policies.">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {recurringControls.map(([title, description]) => <ReportCard key={title} title={title} description={description} />)}
        </div>
      </JournalPageFrame>
    </AppShell>
  );
}
