"use client";

import { AppShell } from '../../components/AppShell';

export default function PlatformGlossaryPage() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Business Glossary</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Enterprise Glossary</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Capture business terms, definitions, synonyms, and semantic standards that govern finance and operations data.
          </p>
        </div>

        <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">
          Glossary management is scaffolded and will be wired to semantic governance and enterprise metadata.
        </div>
      </div>
    </AppShell>
  );
}
