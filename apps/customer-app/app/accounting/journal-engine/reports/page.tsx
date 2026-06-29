"use client";

import { AppShell } from '../../../components/AppShell';
import { JournalPageFrame, ReportCard } from '../journalComponents';

const reports = [
  ['Journal Register', 'Complete journal listing by number, type, branch, source, status, amount, and posting date.'],
  ['Posted Journals', 'Immutable posted journals with voucher, GL, and audit references.'],
  ['Pending Journals', 'Draft, pending, approved, and rejected journals by age and owner.'],
  ['Reversal Register', 'Original journals, reversal journals, reversal reasons, and approvers.'],
  ['Adjustment Register', 'Manual adjustments, write-offs, high-value entries, and maker-checker evidence.'],
  ['Intercompany Register', 'Cross-entity receivable and payable entries with settlement state.'],
  ['Currency Register', 'Transaction, functional, and reporting currency impact with FX rates.'],
  ['Journal Health', 'Validation errors, reversal percentage, duplicate risk, latency, and audit exceptions.'],
];

export default function JournalReportsPage() {
  return (
    <AppShell>
      <JournalPageFrame title="Journal Reports" description="Standard reporting catalog for journal operations, controls, currency, reversals, approvals, and health.">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {reports.map(([title, description]) => <ReportCard key={title} title={title} description={description} />)}
        </div>
      </JournalPageFrame>
    </AppShell>
  );
}
