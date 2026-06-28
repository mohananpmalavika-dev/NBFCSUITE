import { Bell, Globe2, LayoutDashboard, Search, Settings2, Sparkles, Users2, FileText, DollarSign, Banknote, ShieldCheck, ChartPie, ChevronRight } from 'lucide-react';

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard },
  { label: 'Customers', icon: Users2 },
  { label: 'Lending', icon: DollarSign },
  { label: 'Deposits', icon: Banknote },
  { label: 'Accounting', icon: FileText },
  { label: 'HRMS', icon: ShieldCheck },
  { label: 'Reports', icon: ChartPie },
  { label: 'Administration', icon: Settings2 },
];

const kpis = [
  { label: 'Active Users', value: '1,284' },
  { label: 'Open Applications', value: '72' },
  { label: 'Approval Rate', value: '91%' },
  { label: 'Pending Tasks', value: '14' },
];

const principles = [
  {
    title: 'Workspace Driven',
    description: 'Every module is organized by Workspace → Dashboard → Lists → Details → Wizard.',
  },
  {
    title: 'Dashboard First',
    description: 'Modules begin with KPIs, insights, and actions rather than data entry forms.',
  },
  {
    title: 'Contextual Navigation',
    description: 'Related workflow tabs live together in context rather than deep back-and-forth flows.',
  },
  {
    title: 'Progressive Disclosure',
    description: 'Show only the next step, not 100 fields at once.',
  },
  {
    title: 'Single Responsibility Screen',
    description: 'Each screen has one clear purpose, reducing complexity and cognitive load.',
  },
  {
    title: 'AI Everywhere',
    description: 'Contextual intelligence is available on every screen via Ask FinDNA.',
  },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-sm">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">ARTH.OS</p>
              <p className="font-semibold text-slate-900">Enterprise Design System</p>
            </div>
          </div>

          <div className="flex-1">
            <div className="relative max-w-xl">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                aria-label="Search ARTH.OS"
                placeholder="Search ARTH.OS..."
                className="w-full rounded-2xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>
          </div>

          <div className="hidden items-center gap-3 md:flex">
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
              <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Shell</p>
              <p className="font-semibold">Workspace</p>
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
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Favorites</p>
            <div className="mt-3 grid gap-3 text-slate-200">
              <span className="rounded-2xl bg-slate-800 px-3 py-2">Employee</span>
              <span className="rounded-2xl bg-slate-800 px-3 py-2">Customer</span>
              <span className="rounded-2xl bg-slate-800 px-3 py-2">Journal</span>
            </div>
          </div>
        </aside>

        <main className="flex-1">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.26em] text-blue-600">EDS-001</p>
                <h1 className="mt-3 text-3xl font-semibold text-slate-950">Enterprise Design Principles</h1>
                <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600">
                  Build every ARTH.OS experience around clarity, consistency, workspaces, and contextual intelligence. This is the foundation for every screen and module across the platform.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {kpis.map((kpi) => (
                  <div key={kpi.label} className="rounded-3xl border border-slate-200 bg-slate-50 p-4 shadow-sm">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{kpi.label}</p>
                    <p className="mt-3 text-2xl font-semibold text-slate-950">{kpi.value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-900">Workspace actions</p>
                <p className="text-sm text-slate-500">Primary and secondary actions live together in the workspace header.</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <button className="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700">+ New Employee</button>
                <button className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300">Export</button>
                <button className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300">Import</button>
              </div>
            </div>
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
            <div className="space-y-6">
              <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-slate-950">Design Principles in Action</h2>
                <p className="mt-3 text-sm leading-7 text-slate-600">
                  This implementation demonstrates the first EDS deliverable with a consistent shell, workspace-first structure, and enterprise-ready navigation patterns.
                </p>

                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  {principles.map((principle) => (
                    <div key={principle.title} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                      <p className="text-sm font-semibold text-slate-950">{principle.title}</p>
                      <p className="mt-2 text-sm text-slate-600">{principle.description}</p>
                    </div>
                  ))}
                </div>
              </article>

              <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-blue-600">Implementation</p>
                    <h3 className="mt-2 text-lg font-semibold text-slate-950">EDS-001 Status</h3>
                  </div>
                  <div className="rounded-2xl bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">Complete</div>
                </div>
                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm font-semibold text-slate-900">Enterprise first</p>
                    <p className="mt-2 text-sm text-slate-600">A shared shell and workspace pattern drives all modules.</p>
                  </div>
                  <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm font-semibold text-slate-900">No page overload</p>
                    <p className="mt-2 text-sm text-slate-600">Screens are focused, actionable, and aligned to one purpose.</p>
                  </div>
                  <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm font-semibold text-slate-900">Accessible</p>
                    <p className="mt-2 text-sm text-slate-600">Clear hierarchy, readable typography, and consistent spacing.</p>
                  </div>
                  <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm font-semibold text-slate-900">Role-ready</p>
                    <p className="mt-2 text-sm text-slate-600">Navigation and layout support enterprise personas and workflows.</p>
                  </div>
                </div>
              </article>
            </div>

            <aside className="space-y-6">
              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3 text-slate-900">
                  <Globe2 className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="text-sm font-semibold">Workspace Personalization</p>
                    <p className="mt-2 text-sm text-slate-600">Pin favorites, save views, and keep workspace settings per user.</p>
                  </div>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-slate-950 p-6 text-slate-100 shadow-sm">
                <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Navigation</p>
                <p className="mt-4 text-sm leading-7 text-slate-100">
                  EDS-001 enforces a three-click maximum, clear breadcrumb depth, and consistent page types for every module.
                </p>
                <div className="mt-5 space-y-3 text-sm text-slate-300">
                  <p>• Dashboard first</p>
                  <p>• Right drawer details</p>
                  <p>• No popup hell</p>
                  <p>• Global search everywhere</p>
                </div>
              </div>
            </aside>
          </section>
        </main>
      </div>
    </div>
  );
}
