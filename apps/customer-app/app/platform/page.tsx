"use client";

import Link from 'next/link';
import { AppShell } from '../components/AppShell';

const platformModules = [
  { title: 'EDP Dashboard', href: '/platform/dashboard', description: 'Data catalog, lineage, quality, glossary and governance health for enterprise data assets.' },
  { title: 'Data Catalog', href: '/platform/catalog', description: 'Browse and manage data assets, owners, domains, and enterprise metadata.' },
  { title: 'Data Lineage', href: '/platform/lineage', description: 'Trace how data flows, transforms, and integrates across the enterprise.' },
  { title: 'Data Quality', href: '/platform/quality', description: 'Monitor quality checks, data health, and remediation priorities.' },
  { title: 'Business Glossary', href: '/platform/glossary', description: 'Manage terms, definitions, and semantic consistency across the business.' },
  { title: 'Data Platform Reports', href: '/platform/reports', description: 'Run data platform reports for catalog coverage, lineage completeness, and quality trends.' },
];

export default function PlatformLandingPage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise Data Platform</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">EDP Data Platform</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            A central platform for enterprise data catalogs, lineage, quality, glossary, and reporting across core banking operations.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {platformModules.map((module) => (
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
