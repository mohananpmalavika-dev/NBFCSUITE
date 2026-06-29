"use client";

import { AppShell } from '../../../components/AppShell';
import { ReportCard, RulePageFrame } from '../ruleComponents';

const reports = [
  ['Posting Rule Register', 'Complete rule catalog by code, event, module, product, status, version, and effective date.'],
  ['Rule Coverage', 'Accounting events covered by published rules, default maps, and missing configurations.'],
  ['Unused Rules', 'Published or draft rules with no execution logs or no recent simulation activity.'],
  ['Rule Performance', 'Execution frequency, success rate, failure rate, latency, and rollback indicators.'],
  ['Version Comparison', 'Compare debit/credit lines, formulas, conditions, dimensions, and approval history between versions.'],
  ['Simulation Report', 'Simulation inputs, generated journal lines, balance status, and accounting impact.'],
  ['GL Mapping Report', 'Debit and credit account mappings by event, product, legal entity, branch, and currency.'],
  ['Rule Audit Report', 'Create, update, approval, publish, retire, and version change logs.'],
];

export default function PostingRuleReportsPage() {
  return (
    <AppShell>
      <RulePageFrame title="Posting Rule Reports" description="Standard reporting catalog for rule governance, coverage, versions, simulations, and execution performance.">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {reports.map(([title, description]) => <ReportCard key={title} title={title} description={description} />)}
        </div>
      </RulePageFrame>
    </AppShell>
  );
}
