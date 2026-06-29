"use client";

import { AppShell } from '../../../components/AppShell';
import { EmptyState, FinancePageFrame, MetricTile } from '../financeComponents';

const reports = [
  'Cost Center Register',
  'Profit Center Register',
  'Budget Report',
  'Budget Variance',
  'Allocation Report',
  'Internal Order Report',
  'Financial Organization Health',
];

export default function FinanceReportsPage() {
  return (
    <AppShell>
      <FinancePageFrame
        title="Finance Reports"
        description="Report stubs for financial organization governance, allocation, budget control, and health monitoring."
      >
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {reports.map((report) => (
            <MetricTile key={report} label="Report" value={report} note="Report builder integration pending" />
          ))}
        </div>
        <EmptyState message="Report generation is not implemented in this MVP." />
      </FinancePageFrame>
    </AppShell>
  );
}
