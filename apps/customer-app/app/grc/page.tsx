"use client";

import Link from 'next/link';
import { AppShell } from '../components/AppShell';

const grcModules = [
  { title: 'GRC Dashboard', href: '/grc/dashboard', description: 'Governance, compliance, audit, and issue visibility for enterprise assurance.' },
  { title: 'Policies', href: '/grc/policies', description: 'Manage policy lifecycle, versions, approval, and acknowledgements.' },
  { title: 'Compliance Obligations', href: '/grc/obligations', description: 'Track compliance obligations with deadlines, owners, and evidence.' },
];

export default function GrcLandingPage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise GRC</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Governance, Risk & Compliance platform</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Get started with the governance control tower, compliance obligations, policy lifecycle, and audit monitoring.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {grcModules.map((module) => (
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
