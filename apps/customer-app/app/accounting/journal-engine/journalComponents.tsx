"use client";

import Link from 'next/link';
import { BarChart3, FileText, ListChecks, Repeat2, RotateCcw, Search, Settings2, SquarePen, Workflow } from 'lucide-react';
import type { ReactNode } from 'react';

const navItems = [
  { label: 'Dashboard', href: '/accounting/journal-engine/dashboard', icon: BarChart3 },
  { label: 'Journal Explorer', href: '/accounting/journal-engine/explorer', icon: Search },
  { label: 'Draft Journals', href: '/accounting/journal-engine/create', icon: SquarePen },
  { label: 'Approval Queue', href: '/accounting/journal-engine/approvals', icon: ListChecks },
  { label: 'Recurring Journals', href: '/accounting/journal-engine/recurring', icon: Repeat2 },
  { label: 'Reversals', href: '/accounting/journal-engine/reversals', icon: RotateCcw },
  { label: 'Reports', href: '/accounting/journal-engine/reports', icon: FileText },
  { label: 'Settings', href: '/accounting/journal-engine/settings', icon: Settings2 },
];

export function JournalPageFrame({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 border-b border-border-default pb-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-muted">Enterprise Journal Engine</p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">{title}</h1>
          <p className="mt-1 max-w-3xl text-sm text-text-secondary">{description}</p>
        </div>
        <Link
          href="/accounting/posting-rules"
          className="inline-flex h-10 items-center gap-2 rounded-md border border-border-default bg-background-surface px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent"
        >
          <Workflow className="h-4 w-4" />
          Posting Rules
        </Link>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className="inline-flex h-10 shrink-0 items-center gap-2 rounded-md border border-border-default bg-background-surface px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent"
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </div>

      {children}
    </div>
  );
}

export function JournalMetric({ label, value, note }: { label: string; value: string | number; note: string }) {
  return (
    <div className="rounded-md border border-border-default bg-background-surface p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-text-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-text-primary">{value}</p>
      <p className="mt-1 text-sm text-text-secondary">{note}</p>
    </div>
  );
}

export function JournalTable({ columns, children }: { columns: string[]; children: ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-md border border-border-default bg-background-surface">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 text-left">
          <tr>
            {columns.map((column) => (
              <th key={column} className="p-3 font-semibold text-text-secondary">{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

export function JournalBadge({ value }: { value?: string | null }) {
  const normalized = value ?? 'unknown';
  const tone =
    normalized === 'posted' || normalized === 'approved'
      ? 'bg-green-100 text-green-800'
      : normalized === 'draft' || normalized === 'pending'
        ? 'bg-amber-100 text-amber-800'
        : normalized === 'failed' || normalized === 'rejected' || normalized === 'cancelled'
          ? 'bg-red-100 text-red-800'
          : 'bg-blue-100 text-blue-800';
  return <span className={`inline-flex rounded px-2 py-0.5 text-xs font-semibold ${tone}`}>{normalized}</span>;
}

export function LoadingBlock() {
  return <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Loading...</div>;
}

export function EmptyState({ message }: { message: string }) {
  return <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">{message}</div>;
}

export function JournalActionButton({ children, onClick, disabled }: { children: ReactNode; onClick: () => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex h-8 items-center rounded-md border border-border-default px-2 text-xs font-semibold text-text-secondary hover:bg-background-accent disabled:opacity-60"
    >
      {children}
    </button>
  );
}

export function ReportCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-md border border-border-default bg-background-surface p-4">
      <div className="font-semibold text-text-primary">{title}</div>
      <div className="mt-1 text-sm text-text-secondary">{description}</div>
    </div>
  );
}

export function formatAmount(value?: number | null, currency = 'INR') {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency, maximumFractionDigits: 0 }).format(value);
}

export function formatDate(value?: string | null) {
  if (!value) return '-';
  return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value));
}
