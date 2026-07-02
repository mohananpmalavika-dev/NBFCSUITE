"use client";

import Link from 'next/link';
import { AppShell } from '../components/AppShell';

const riskModules = [
  { title: 'Risk Dashboard', href: '/risk/dashboard', description: 'Enterprise risk score, incidents, and compliance issue monitoring.' },
];

export default function RiskLandingPage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise Governance</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Risk management and enterprise governance platform</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Start with the risk dashboard and expand into register, assessments, incidents, KRI, and reporting workflows.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {riskModules.map((module) => (
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
