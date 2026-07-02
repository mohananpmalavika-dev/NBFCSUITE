"use client";

import { AppShell } from '../../components/AppShell';

export default function PlatformCatalogPage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Data Catalog</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Enterprise Data Catalog</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Browse data assets, domains, owners, and metadata definitions in the enterprise data catalog.
          </p>
        </div>

        <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">
          Data Catalog is scaffolded and ready to connect with the EDP data asset registry.
        </div>
      </div>
    </AppShell>
  );
}
