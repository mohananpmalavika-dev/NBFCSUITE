"use client";

import { AppShell } from '../../components/AppShell';

export default function PlatformLineagePage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Data Lineage</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Enterprise Data Lineage</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Visualize and manage how data flows across systems, integrations, and transformation processes.
          </p>
        </div>

        <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">
          Data Lineage is scaffolded and will be enriched with asset dependencies and transformation mappings.
        </div>
      </div>
    </AppShell>
  );
}
