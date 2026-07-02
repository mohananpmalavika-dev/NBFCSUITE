"use client";

import { AppShell } from '../../components/AppShell';

export default function PlatformQualityPage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Data Quality</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Enterprise Data Quality</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Monitor the quality of business-critical data, capture checks, and track remediation actions.
          </p>
        </div>

        <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">
          Data Quality is scaffolded and will connect to quality checks, scorecards, and issue workflows.
        </div>
      </div>
    </AppShell>
  );
}
