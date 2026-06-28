'use client';

import { useState } from 'react';
import {
  Bell,
  Compass,
  LayoutDashboard,
  Search,
  Settings2,
  Sparkles,
  Users2,
  FileText,
  DollarSign,
  Banknote,
  ShieldCheck,
  ChartPie,
  ChevronRight,
  Layers,
  ClipboardList,
  HelpCircle,
  CheckCircle2,
  Command,
  ShieldAlert as ShieldAlertIcon,
} from 'lucide-react';

const topNavItems = [
  { label: 'AI Assistant', icon: Sparkles },
  { label: 'Notifications', icon: Bell },
  { label: 'Approvals', icon: CheckCircle2 },
  { label: 'Tasks', icon: ClipboardList },
  { label: 'Help', icon: HelpCircle },
];

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard },
  { label: 'Customers', icon: Users2 },
  { label: 'Lending', icon: DollarSign },
  { label: 'Accounting', icon: ClipboardList },
  { label: 'HRMS', icon: ShieldCheck },
  { label: 'Reports', icon: ChartPie },
  { label: 'Administration', icon: Settings2 },
  { label: 'AI', icon: Sparkles },
  { label: 'Risk', icon: Compass },
  { label: 'Compliance', icon: Layers },
  { label: 'Deposits', icon: Banknote },
  { label: 'Gold Loans', icon: FileText },
  { label: 'Treasury', icon: ShieldAlertIcon },
];

const kpis = [
  { label: 'Global Layers', value: '5' },
  { label: 'Sidebar Items', value: '13' },
  { label: 'Search Shortcut', value: 'Ctrl+K' },
  { label: 'Max Depth', value: '3 clicks' },
];

const breadcrumbs = ['Home', 'Expenses', 'Approval Workspace'];

const commandPaletteItems = [
  'Create Employee',
  'Employee Directory',
  'Payroll Summary',
  'General Ledger',
  'Create Customer',
  'Search Loans',
  'Dashboard Reports',
  'Approvals Queue',
];

const megaNavigation = [
  {
    title: 'Accounting',
    categories: [
      { label: 'Dashboard' },
      { label: 'Master', children: ['Chart of Accounts', 'Fiscal Year', 'Periods'] },
      { label: 'Transactions', children: ['Journal', 'Voucher', 'Cash', 'Bank'] },
      { label: 'Ledger', children: ['General Ledger', 'Sub Ledger'] },
      { label: 'Reports', children: ['Trial Balance', 'Balance Sheet', 'P&L'] },
    ],
  },
  {
    title: 'HRMS',
    categories: [
      { label: 'Dashboard' },
      { label: 'Organization', children: ['Departments', 'Designations', 'Grades', 'Positions'] },
      { label: 'Employees', children: ['Directory', 'Onboarding', 'Transfers', 'Exit'] },
      { label: 'Attendance' },
      { label: 'Leave' },
      { label: 'Payroll' },
      { label: 'Performance' },
    ],
  },
  {
    title: 'Customers',
    categories: [
      { label: 'Dashboard' },
      { label: 'Prospects' },
      { label: 'Directory' },
      { label: 'Customer 360' },
      { label: 'Relationships' },
      { label: 'KYC' },
      { label: 'Documents' },
      { label: 'Reports' },
    ],
  },
];

export function AppShell() {
  const [sidebarExpanded, setSidebarExpanded] = useState(true);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-sm">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs uppercase tracking-[0.24em] text-slate-500">ARTH.OS</p>
              <p className="truncate font-semibold text-slate-900">Enterprise Navigation System</p>
            </div>
          </div>

          <div className="flex flex-1 items-center gap-4 sm:gap-3">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                aria-label="Search ARTH.OS"
                placeholder="Search ARTH.OS..."
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>
            <div className="hidden items-center gap-2 sm:flex">
              {topNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.label}
                    className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50"
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm">
              <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
              Branch 1204
            </div>
            <div className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm">Tenant: FinCorp</div>
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6">
        <aside
          className={`hidden shrink-0 flex-col gap-4 rounded-3xl border border-slate-200 bg-slate-950 p-4 text-slate-100 lg:flex ${
            sidebarExpanded ? 'w-72' : 'w-20'
          }`}
          onMouseEnter={() => setSidebarExpanded(true)}
          onMouseLeave={() => setSidebarExpanded(false)}
        >
          <div className="mb-4 flex items-center justify-between rounded-3xl bg-slate-900 px-4 py-3">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Global Navigation</p>
              <p className="font-semibold">Persistent Sidebar</p>
            </div>
            <ChevronRight className="h-4 w-4 text-slate-400" />
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.label}
                  href="#"
                  className="flex items-center gap-3 rounded-3xl px-4 py-3 text-sm font-semibold text-slate-100 transition hover:bg-slate-800"
                >
                  <Icon className="h-5 w-5 text-slate-300" />
                  <span className={`${sidebarExpanded ? 'block' : 'hidden'}`}>{item.label}</span>
                </a>
              );
            })}
          </nav>

          <div className="mt-auto rounded-3xl bg-slate-900 p-4 text-sm text-slate-400">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Compressed Behavior</p>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Hover expands the sidebar. When collapsed, only icons remain to preserve space.
            </p>
          </div>
        </aside>

        <main className="flex-1">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.26em] text-blue-600">EDS-003</p>
                <h1 className="mt-3 text-3xl font-semibold text-slate-950">Enterprise Navigation System</h1>
                <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600">
                  A scalable navigation system with global navigation, workspace header, command palette, mega menus, and a universal search experience.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {kpis.map((kpi) => (
                  <div key={kpi.label} className="rounded-3xl border border-slate-200 bg-slate-50 p-4 shadow-sm">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{kpi.label}</p>
                    <p className="mt-3 text-2xl font-semibold text-slate-950">{kpi.value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-slate-700">Workspace Header</p>
                  <p className="text-sm text-slate-600">Breadcrumbs, workspace title, description, and actions appear at the top of every module.</p>
                </div>
                <div className="rounded-2xl bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">Shell pattern</div>
              </div>

              <div className="mt-6 rounded-3xl bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.24em] text-slate-500">
                      {breadcrumbs.map((crumb, index) => (
                        <span key={crumb} className="inline-flex items-center gap-2">
                          {index > 0 && <ChevronRight className="h-3 w-3 text-slate-400" />}
                          {crumb}
                        </span>
                      ))}
                    </div>
                    <h2 className="text-2xl font-semibold text-slate-950">Approval Workspace</h2>
                    <p className="max-w-2xl text-sm text-slate-600">Review and approve employee expenses, with access to tasks, approvals, and help in context.</p>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <button className="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">+ New Approval</button>
                    <button className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300">Import</button>
                    <button className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300">Export</button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Command Palette</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-950">Search Productivity</h2>
                </div>
                <div className="rounded-2xl bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">VS Code style</div>
              </div>

              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                    <Command className="h-4 w-4 text-blue-600" />
                    <span>Universal Search</span>
                  </div>
                  <p className="mt-3 text-sm text-slate-600">Global Search and command palette let users discover screens, reports, actions, and settings.</p>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-950">Shortcut</p>
                  <p className="mt-3 text-2xl font-semibold text-slate-900">Ctrl + K</p>
                  <p className="mt-3 text-sm text-slate-600">Search across customers, employees, loans, reports, and workflows.</p>
                </div>
              </div>

              <div className="mt-6 space-y-3">
                {commandPaletteItems.map((item) => (
                  <div key={item} className="rounded-3xl border border-slate-200 bg-slate-100 px-4 py-3 text-sm text-slate-700">
                    {item}
                  </div>
                ))}
              </div>
            </article>

            <aside className="space-y-6">
              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Top Navigation</p>
                <div className="mt-4 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
                  <div className="rounded-3xl bg-slate-50 p-4">Global Search</div>
                  <div className="rounded-3xl bg-slate-50 p-4">AI Assistant</div>
                  <div className="rounded-3xl bg-slate-50 p-4">Notifications</div>
                  <div className="rounded-3xl bg-slate-50 p-4">Approvals</div>
                  <div className="rounded-3xl bg-slate-50 p-4">Tasks</div>
                  <div className="rounded-3xl bg-slate-50 p-4">Help & Profile</div>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Search UI</p>
                <div className="mt-4 space-y-3 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">
                  <p className="font-semibold text-slate-900">Search ARTH.OS</p>
                  <p>Customers Loans Employees Screens Reports Actions</p>
                </div>
              </div>
            </aside>
          </section>

          <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Mega Navigation</p>
                <h2 className="mt-2 text-xl font-semibold text-slate-950">Scale for 1,000+ screens</h2>
                <p className="mt-2 text-sm text-slate-600">Mega menus group deep modules with categories and quick actions.</p>
              </div>
              <div className="rounded-2xl bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700">Module menus</div>
            </div>

            <div className="mt-6 grid gap-4 xl:grid-cols-3">
              {megaNavigation.map((nav) => (
                <div key={nav.title} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-950">{nav.title}</p>
                  <div className="mt-4 space-y-4 text-sm text-slate-600">
                    {nav.categories.map((category) => (
                      <div key={category.label}>
                        <p className="font-semibold text-slate-900">{category.label}</p>
                        {category.children ? (
                          <ul className="mt-2 space-y-2 pl-4 text-slate-600">
                            {category.children.map((child) => (
                              <li key={child} className="list-disc">{child}</li>
                            ))}
                          </ul>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
