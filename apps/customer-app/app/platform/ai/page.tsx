"use client";

import Link from 'next/link';
import { AppShell } from '../../components/AppShell';

const aiModules = [
  { title: 'AI Dashboard', href: '/platform/ai/dashboard', description: 'AI platform status, usage, and model metrics.' },
  { title: 'Copilots', href: '/platform/ai/copilots', description: 'Manage module copilots and agent registrations.' },
  { title: 'Prompts', href: '/platform/ai/prompts', description: 'Prompt studio, versions, and templates.' },
];

export default function AiLanding() {
  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise AI</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">AI Platform (EAP-001)</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">A multi-model AI gateway, agent framework, RAG, and decision intelligence platform.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {aiModules.map((m) => (
            <Link key={m.href} href={m.href} className="rounded-md border border-border-default bg-background-default p-6 text-sm transition hover:border-accent-primary">
              <div className="text-lg font-semibold text-text-primary">{m.title}</div>
              <div className="mt-2 text-text-secondary">{m.description}</div>
              <div className="mt-4 text-sm font-semibold text-accent-primary">Open module →</div>
            </Link>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
