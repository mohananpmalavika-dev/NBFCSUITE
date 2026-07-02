"use client";

import Link from 'next/link';
import { AppShell } from '../components/AppShell';

const modules = [
  { title: 'General Ledger', href: '/accounting/general-ledger', description: 'Enterprise ledger balances, entries, and posting visibility.' },
  { title: 'Journal Engine', href: '/accounting/journal-engine', description: 'Create, approve, post, and reverse journals with audit trails.' },
  { title: 'Chart of Accounts', href: '/accounting/chart-of-accounts', description: 'Manage the enterprise financial taxonomy for postings and tax mapping.' },
  { title: 'Tax Engine', href: '/accounting/tax-engine', description: 'GST, TDS, e-invoice, e-way bill, and compliance workflows for taxation operations.' },
  { title: 'Financial Close', href: '/accounting/financial-close', description: 'Close process orchestration, task management, consolidation and regulatory reporting.' },
];

export default function AccountingLandingPage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Accounting Workspace</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Enterprise accounting and tax operations</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Navigate to accounting modules for ledger management, journal processing, chart of accounts control, and tax engine compliance workflows.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {modules.map((module) => (
            <Link key={module.href} href={module.href} className="rounded-md border border-border-default bg-background-default p-6 text-sm transition hover:border-accent-primary">
              <div className="text-lg font-semibold text-text-primary">{module.title}</div>
              <div className="mt-2 text-text-secondary">{module.description}</div>
              <div className="mt-4 text-sm font-semibold text-accent-primary">Open module →</div>
            </Link>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
