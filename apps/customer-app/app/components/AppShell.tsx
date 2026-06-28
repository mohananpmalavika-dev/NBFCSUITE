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
  ShieldAlert,
  Layers,
  Activity,
  ClipboardList,
} from 'lucide-react';

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard },
  { label: 'Customers', icon: Users2 },
  { label: 'Lending', icon: DollarSign },
  { label: 'Deposits', icon: Banknote },
  { label: 'Gold Loans', icon: FileText },
  { label: 'Treasury', icon: ShieldAlert },
  { label: 'Accounting', icon: ClipboardList },
  { label: 'HRMS', icon: ShieldCheck },
  { label: 'CRM', icon: Activity },
  { label: 'Risk', icon: Compass },
  { label: 'Compliance', icon: Layers },
  { label: 'Reports', icon: ChartPie },
  { label: 'Administration', icon: Settings2 },
  { label: 'AI', icon: Sparkles },
];

const kpis = [
  { label: 'Products', value: '14' },
  { label: 'Personas', value: '7' },
  { label: 'Max Depth', value: '3 clicks' },
  { label: 'Breadcrumbs', value: '4 levels' },
];

const personas = [
  {
    title: 'Executive',
    items: ['Executive Dashboard', 'Business KPIs', 'Approvals', 'Alerts', 'AI Insights'],
  },
  {
    title: 'Branch Operations',
    items: ['Branch Dashboard', 'Today’s Business', 'Customers', 'Collections', 'Cash Position', 'Approvals'],
  },
  {
    title: 'Loan Officer',
    items: ['My Leads', 'Applications', 'Pending Documents', 'Disbursements', 'Tasks'],
  },
  {
    title: 'Gold Appraiser',
    items: ['Gold Valuation', 'Gold Packets', 'Renewals', 'Auction Queue', 'Today’s Customers'],
  },
  {
    title: 'HR Executive',
    items: ['Employees', 'Attendance', 'Leave', 'Recruitment', 'Payroll', 'Approvals'],
  },
  {
    title: 'Finance Officer',
    items: ['General Ledger', 'Vouchers', 'Bank Book', 'Cash Book', 'Reports'],
  },
  {
    title: 'Auditor',
    items: ['Audit Dashboard', 'Exceptions', 'Pending Reviews', 'Logs', 'Compliance'],
  },
];

const menuStructures = [
  {
    title: 'Customers',
    sections: ['Dashboard', 'Prospects', 'Customers', 'Customer 360', 'Relationships', 'Documents', 'KYC', 'Reports'],
  },
  {
    title: 'Lending',
    sections: ['Dashboard', 'Applications', 'Approvals', 'Disbursement', 'Repayments', 'Collections', 'Recovery', 'Reports'],
  },
  {
    title: 'Accounting',
    sections: ['Dashboard', 'Chart of Accounts', 'Journals', 'General Ledger', 'Sub Ledger', 'Cash Book', 'Bank Book', 'Reports'],
  },
  {
    title: 'HRMS',
    sections: ['Dashboard', 'Organization', 'Employees', 'Recruitment', 'Attendance', 'Leave', 'Payroll', 'Performance', 'Assets', 'Reports'],
  },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-sm">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">ARTH.OS</p>
              <p className="font-semibold text-slate-900">Enterprise Information Architecture</p>
            </div>
          </div>

          <div className="relative w-full max-w-2xl">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              aria-label="Search ARTH.OS"
              placeholder="Search ARTH.OS..."
              className="w-full rounded-2xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div className="flex items-center gap-3">
            <button className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50">
              <Sparkles className="h-4 w-4" />
              Ask FinDNA
            </button>
            <button className="rounded-2xl border border-slate-200 bg-white p-2 text-slate-600 transition hover:border-slate-300 hover:text-slate-900">
              <Bell className="h-5 w-5" />
            </button>
            <button className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50">
              Branch 1204
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6">
        <aside className="hidden w-72 shrink-0 flex-col gap-4 rounded-3xl border border-slate-200 bg-slate-950 p-4 text-slate-100 lg:flex">
          <div className="mb-4 flex items-center justify-between rounded-3xl bg-slate-900 px-4 py-3">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Product Hierarchy</p>
              <p className="font-semibold">Top-level products</p>
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
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>

          <div className="mt-auto rounded-3xl bg-slate-900 p-4 text-sm text-slate-400">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Navigation Rules</p>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              3-level navigation, 3-click maximum, 4 breadcrumb depth, and role-filtered menus.
            </p>
          </div>
        </aside>

        <main className="flex-1">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.26em] text-blue-600">EDS-002</p>
                <h1 className="mt-3 text-3xl font-semibold text-slate-950">Enterprise Information Architecture</h1>
                <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600">
                  The IA defines where every screen belongs before implementation. It creates a single source of truth for product hierarchy, persona home experiences, navigation model, and menu structure.
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

            <div className="mt-6 grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div className="grid gap-2 sm:grid-cols-[0.5fr_1fr] sm:items-center">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-700">Navigation Model</p>
                <p className="text-sm text-slate-600">Level 1 Product → Level 2 Module → Level 3 Screen. Example: HRMS → Employees → Employee Profile.</p>
              </div>
              <div className="grid gap-2 sm:grid-cols-[0.5fr_1fr] sm:items-center">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-700">Workspace Pattern</p>
                <p className="text-sm text-slate-600">Every module follows Dashboard → List → Detail → Create/Edit Wizard → Reports → Settings.</p>
              </div>
              <div className="grid gap-2 sm:grid-cols-[0.5fr_1fr] sm:items-center">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-700">Breadcrumb Standard</p>
                <p className="text-sm text-slate-600">Breadcrumbs are limited to 4 levels: Home → HRMS → Employees → Employee Profile.</p>
              </div>
              <div className="grid gap-2 sm:grid-cols-[0.5fr_1fr] sm:items-center">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-700">Screen Types</p>
                <p className="text-sm text-slate-600">Dashboard, List, Details, Wizard, Analytics, Settings.</p>
              </div>
            </div>
          </section>

          <section className="mt-6 grid gap-6">
            <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Personas</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-950">Role-driven home experiences</h2>
                </div>
                <div className="rounded-2xl bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700">Role-specific IA</div>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {personas.map((persona) => (
                  <div key={persona.title} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                    <p className="text-sm font-semibold text-slate-950">{persona.title}</p>
                    <ul className="mt-3 space-y-2 text-sm text-slate-600">
                      {persona.items.map((item) => (
                        <li key={item} className="flex items-center gap-2">
                          <span className="inline-flex h-2.5 w-2.5 rounded-full bg-blue-500" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </article>

            <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Menu Structure</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-950">Core product navigation</h2>
                </div>
                <div className="rounded-2xl bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">Top modules</div>
              </div>

              <div className="mt-6 grid gap-4 xl:grid-cols-2">
                {menuStructures.map((menu) => (
                  <div key={menu.title} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                    <p className="text-sm font-semibold text-slate-950">{menu.title}</p>
                    <div className="mt-3 space-y-2 text-sm text-slate-600">
                      {menu.sections.map((section) => (
                        <div key={section} className="flex items-center gap-2">
                          <span className="inline-flex h-2.5 w-2.5 rounded-full bg-slate-400" />
                          {section}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Navigation Rules</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-950">Enterprise IA guardrails</h2>
                </div>
                <div className="rounded-2xl bg-slate-50 px-3 py-2 text-sm font-semibold text-slate-700">Scale-ready</div>
              </div>

              <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-900">3 Clicks</p>
                  <p className="mt-2 text-sm text-slate-600">Common tasks should be reachable in no more than three clicks.</p>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-900">4 Breadcrumb Levels</p>
                  <p className="mt-2 text-sm text-slate-600">Depth is capped to preserve clarity and orientation.</p>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-900">Permission-based</p>
                  <p className="mt-2 text-sm text-slate-600">Users only see menus they can access.</p>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-900">Right Drawer</p>
                  <p className="mt-2 text-sm text-slate-600">Details open in context without leaving the list.</p>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-900">Screen Types</p>
                  <p className="mt-2 text-sm text-slate-600">Only six screen types are allowed to keep the UX consistent.</p>
                </div>
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-semibold text-slate-900">No Forms on Dashboards</p>
                  <p className="mt-2 text-sm text-slate-600">Dashboards are for insight, not entry.</p>
                </div>
              </div>
            </article>
          </section>
        </main>
      </div>
    </div>
  );
}
