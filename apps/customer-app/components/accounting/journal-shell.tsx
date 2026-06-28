'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ArrowLeft, BookOpenText, ClipboardCheck, FlaskConical, LayoutDashboard, Plus } from 'lucide-react';
import type { ReactNode } from 'react';

const navItems = [
  { href: '/accounting/journals', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/accounting/journals/new', label: 'Journal Entry', icon: Plus },
  { href: '/accounting/journals/simulator', label: 'Simulator', icon: FlaskConical },
  { href: '/accounting/journals/approvals', label: 'Approvals', icon: ClipboardCheck },
];

export function JournalShell({
  title,
  description,
  tenantId,
  actions,
  children,
}: {
  title: string;
  description: string;
  tenantId: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  const pathname = usePathname();

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1500px] flex-col gap-4 px-4 py-4 sm:px-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex min-w-0 items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded bg-slate-950 text-white">
                <BookOpenText className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <h1 className="text-2xl font-bold tracking-normal">{title}</h1>
                <p className="mt-1 text-sm font-medium text-slate-500">{description}</p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="h-9 rounded border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold text-slate-600">Tenant {tenantId}</span>
              {actions}
              <Link href="/accounting" className="inline-flex h-9 items-center gap-2 rounded border border-slate-300 bg-white px-3 text-xs font-bold text-slate-700 hover:bg-slate-50">
                <ArrowLeft className="h-4 w-4" /> Accounting 360
              </Link>
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto border-t border-slate-100 pt-3" aria-label="Journal Engine">
            {navItems.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex h-9 shrink-0 items-center gap-2 rounded px-3 text-xs font-bold ${active ? 'bg-slate-950 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
                >
                  <Icon className="h-4 w-4" /> {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>
      <div className="mx-auto max-w-[1500px] px-4 py-5 sm:px-6">{children}</div>
    </main>
  );
}

