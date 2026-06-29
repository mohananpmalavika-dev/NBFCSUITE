"use client";

import { AppShell } from '../../../components/AppShell';
import { JournalPageFrame, ReportCard } from '../journalComponents';

const settings = [
  ['Numbering Rules', 'Configurable prefix, branch sequence, entity sequence, suffix, and restart-safe counters.'],
  ['Approval Policy', 'Threshold, role, delegation, escalation, and sequential or parallel approval routing.'],
  ['Maker-Checker Policy', 'Mandatory controls for manual journals, adjustments, write-offs, and intercompany entries.'],
  ['Currency Policy', 'FX rate source, approval workflow, rounding policy, and multi-book reporting behavior.'],
  ['Validation Policy', 'Double-entry, period, GL, dimension, budget, fraud, and tax checks that cannot be bypassed.'],
  ['Ledger Pattern', 'Journal as business representation feeding immutable ledger entries and GL views.'],
];

export default function JournalSettingsPage() {
  return (
    <AppShell>
      <JournalPageFrame title="Journal Settings" description="Enterprise controls for numbering, approvals, maker-checker, currencies, validation, and immutable ledger behavior.">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {settings.map(([title, description]) => <ReportCard key={title} title={title} description={description} />)}
        </div>
      </JournalPageFrame>
    </AppShell>
  );
}
