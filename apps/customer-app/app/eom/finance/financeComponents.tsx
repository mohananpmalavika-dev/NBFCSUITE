"use client";

import Link from 'next/link';
import { BarChart3, Boxes, ClipboardList, FileText, FolderTree, Landmark, LineChart, ReceiptText } from 'lucide-react';
import type { ReactNode } from 'react';

const financeNavItems = [
  { label: 'Dashboard', href: '/eom/finance/dashboard', icon: BarChart3 },
  { label: 'Explorer', href: '/eom/finance/explorer', icon: FolderTree },
  { label: 'Cost Centers', href: '/eom/finance/cost-centers', icon: Boxes },
  { label: 'Profit Centers', href: '/eom/finance/profit-centers', icon: Landmark },
  { label: 'Budgets', href: '/eom/finance/budgets', icon: ReceiptText },
  { label: 'Internal Orders', href: '/eom/finance/internal-orders', icon: ClipboardList },
  { label: 'Reports', href: '/eom/finance/reports', icon: FileText },
];

export function FinancePageFrame({
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
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-muted">Financial Organization</p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">{title}</h1>
          <p className="mt-1 max-w-3xl text-sm text-text-secondary">{description}</p>
        </div>
        <Link
          href="/eom/finance/dashboard"
          className="inline-flex h-10 items-center gap-2 rounded-md border border-border-default bg-background-surface px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent"
        >
          <LineChart className="h-4 w-4" />
          Finance Home
        </Link>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {financeNavItems.map((item) => {
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

export function StatusBadge({ value }: { value?: string | null }) {
  const normalized = value ?? 'unknown';
  const tone =
    normalized === 'active' || normalized === 'open'
      ? 'bg-green-100 text-green-800'
      : normalized === 'draft' || normalized === 'original'
        ? 'bg-gray-100 text-gray-700'
        : normalized === 'closed' || normalized === 'archived' || normalized === 'inactive'
          ? 'bg-slate-100 text-slate-700'
          : 'bg-blue-100 text-blue-800';

  return <span className={`inline-flex rounded px-2 py-0.5 text-xs font-semibold ${tone}`}>{normalized}</span>;
}

export function LoadingBlock() {
  return <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">Loading...</div>;
}

export function EmptyState({ message }: { message: string }) {
  return <div className="rounded-md border border-border-default bg-background-surface p-6 text-sm text-text-secondary">{message}</div>;
}

export function FinanceTable({
  columns,
  children,
}: {
  columns: string[];
  children: ReactNode;
}) {
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

export function formatMoney(value?: number | null, currency = 'INR') {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}
