"use client";

import { AppShell } from '../../../components/AppShell';
import { CoaPageFrame, ReportStub } from '../coaComponents';

const reports = [
  ['Chart of Accounts', 'Complete GL code register by type, category, posting control, and status.'],
  ['Account Hierarchy', 'Parent-child hierarchy with control account rollups.'],
  ['Posting Accounts', 'Accounts enabled for manual or automated journal posting.'],
  ['Control Accounts', 'Restricted accounts that must be posted through child ledgers.'],
  ['Unused Accounts', 'Accounts with no recent journal line activity.'],
  ['Product Mapping', 'Product-to-GL mapping coverage for loans, deposits, gold, treasury, and fees.'],
  ['Tax Mapping', 'GST, TDS, withholding, and corporate tax mapping coverage.'],
  ['Dimension Usage', 'Required dimension coverage for branch, cost center, product, customer, and currency.'],
  ['Account Health', 'Metadata completeness, usage, reconciliation, and duplicate-risk score.'],
];

export default function CoaReportsPage() {
  return (
    <AppShell>
      <CoaPageFrame
        title="COA Reports"
        description="Operational report stubs for chart governance, controls, mappings, and account health."
      >
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {reports.map(([title, description]) => (
            <ReportStub key={title} title={title} description={description} />
          ))}
        </div>
      </CoaPageFrame>
    </AppShell>
  );
}
