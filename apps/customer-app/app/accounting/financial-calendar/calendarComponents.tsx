"use client";

import Link from 'next/link';
import { BarChart3, CalendarDays, CalendarRange, CheckCircle2, Clock3, FileText, Landmark, ListChecks, Settings2 } from 'lucide-react';
import type { ReactNode } from 'react';

const navItems = [
  { label: 'Dashboard', href: '/accounting/financial-calendar/dashboard', icon: BarChart3 },
  { label: 'Financial Years', href: '/accounting/financial-calendar/financial-years', icon: Landmark },
  { label: 'Accounting Periods', href: '/accounting/financial-calendar/periods', icon: CalendarDays },
  { label: 'Business Calendar', href: '/accounting/financial-calendar/business-calendar', icon: CalendarRange },
  { label: 'Close Monitor', href: '/accounting/financial-calendar/close-monitor', icon: ListChecks },
  { label: 'Holidays', href: '/accounting/financial-calendar/holidays', icon: Clock3 },
  { label: 'Reports', href: '/accounting/financial-calendar/reports', icon: FileText },
];

export function CalendarPageFrame({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 border-b border-border-default pb-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-muted">Accounting Calendar</p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">{title}</h1>
          <p className="mt-1 max-w-3xl text-sm text-text-secondary">{description}</p>
        </div>
        <Link
          href="/accounting/chart-of-accounts"
          className="inline-flex h-10 items-center gap-2 rounded-md border border-border-default bg-background-surface px-3 text-sm font-semibold text-text-secondary hover:bg-background-accent"
        >
          <CheckCircle2 className="h-4 w-4" />
          Chart of Accounts
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

export function CalendarMetric({ label, value, note }: { label: string; value: string | number; note: string }) {
  return (
    <div className="rounded-md border border-border-default bg-background-surface p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-text-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-text-primary">{value}</p>
      <p className="mt-1 text-sm text-text-secondary">{note}</p>
    </div>
  );
}

export function CalendarTable({ columns, children }: { columns: string[]; children: ReactNode }) {
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

export function PeriodBadge({ value }: { value?: string | null }) {
  const normalized = value ?? 'unknown';
  const tone =
    normalized === 'open'
      ? 'bg-green-100 text-green-800'
      : normalized === 'soft_close'
        ? 'bg-amber-100 text-amber-800'
        : normalized === 'hard_close' || normalized === 'archived' || normalized === 'locked'
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

export function ReportCard({ title, description }: { title: string; description: string }) {
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

export function formatDate(value?: string | null) {
  if (!value) return '-';
  return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value));
}
