"use client";

import Link from 'next/link';
import { BarChart3, FileText, FolderTree, ListTree, PlusCircle, Search, Settings2 } from 'lucide-react';
import type { ReactNode } from 'react';

const navItems = [
  { label: 'Dashboard', href: '/accounting/chart-of-accounts/dashboard', icon: BarChart3 },
  { label: 'Chart Explorer', href: '/accounting/chart-of-accounts/explorer', icon: FolderTree },
  { label: 'Account Directory', href: '/accounting/chart-of-accounts/directory', icon: ListTree },
  { label: 'Reports', href: '/accounting/chart-of-accounts/reports', icon: FileText },
];

export function CoaPageFrame({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 border-b border-border-default pb-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-muted">Accounting Core</p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">{title}</h1>
          <p className="mt-1 max-w-3xl text-sm text-text-secondary">{description}</p>
        </div>
        <Link
          href="/accounting/chart-of-accounts/directory"
          className="inline-flex h-10 items-center gap-2 rounded-md border border-border-default bg-background-surface px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent"
        >
          <Search className="h-4 w-4" />
          Find Account
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

export function MetricTile({ label, value, note }: { label: string; value: string | number; note: string }) {
  return (
    <div className="rounded-md border border-border-default bg-background-surface p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-text-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-text-primary">{value}</p>
      <p className="mt-1 text-sm text-text-secondary">{note}</p>
    </div>
  );
}

export function CoaTable({ columns, children }: { columns: string[]; children: ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-md border border-border-default bg-background-surface">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 text-left">
          <tr>
            {columns.map((column) => (
              <th key={column} className="p-3 font-semibold text-text-secondary">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

export function StatusBadge({ value }: { value?: string | null }) {
  const normalized = value ?? 'unknown';
  const tone =
    normalized === 'active' || normalized === 'published'
      ? 'bg-green-100 text-green-800'
      : normalized === 'draft' || normalized === 'finance_review' || normalized === 'cfo_review'
        ? 'bg-amber-100 text-amber-800'
        : normalized === 'inactive'
          ? 'bg-slate-100 text-slate-700'
          : 'bg-blue-100 text-blue-800';
  return <span className={`inline-flex rounded px-2 py-0.5 text-xs font-semibold ${tone}`}>{normalized}</span>;
}

export function BooleanBadge({ value }: { value?: string | null }) {
  const yes = ['true', '1', 'yes', 'active'].includes((value ?? '').toLowerCase());
  return (
    <span className={`inline-flex rounded px-2 py-0.5 text-xs font-semibold ${yes ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-700'}`}>
      {yes ? 'Allowed' : 'Blocked'}
    </span>
  );
}

export function LoadingBlock() {
  return <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Loading...</div>;
}

export function EmptyState({ message, actionHref }: { message: string; actionHref?: string }) {
  return (
    <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <span>{message}</span>
        {actionHref ? (
          <Link href={actionHref} className="inline-flex h-9 items-center gap-2 rounded-md bg-accent-primary px-3 text-sm font-semibold text-accent-onPrimary">
            <PlusCircle className="h-4 w-4" />
            Create Account
          </Link>
        ) : null}
      </div>
    </div>
  );
}

export function formatAmount(value?: number | null, currency = 'INR') {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

export function ReportStub({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-md border border-border-default bg-background-surface p-4">
      <div className="flex items-start gap-3">
        <Settings2 className="mt-0.5 h-4 w-4 text-text-muted" />
        <div>
          <div className="font-semibold text-text-primary">{title}</div>
          <div className="mt-1 text-sm text-text-secondary">{description}</div>
        </div>
      </div>
    </div>
  );
}
