'use client';

import { useEffect, useMemo, useState } from 'react';
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
  Palette,
  ShieldAlert as ShieldAlertIcon,
} from 'lucide-react';
import { buildCssVariables, themes, type ThemeName } from '../../lib/design-tokens';

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

export function AppShell() {
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [themeName, setThemeName] = useState<ThemeName>('default');

  const activeTheme = useMemo(() => themes[themeName], [themeName]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeName);
    Object.assign(document.documentElement.style, buildCssVariables(activeTheme));
  }, [activeTheme, themeName]);

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--background-default)', color: 'var(--text-primary)' }}>
      <header className="sticky top-0 z-30 border-b backdrop-blur-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-header)' }}>
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl text-white shadow-sm" style={{ backgroundColor: 'var(--background-sidebar)' }}>
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs uppercase tracking-[0.24em]" style={{ color: 'var(--text-muted)' }}>ARTH.OS</p>
              <p className="truncate font-semibold" style={{ color: 'var(--text-primary)' }}>Enterprise Navigation System</p>
            </div>
          </div>

          <div className="flex flex-1 items-center gap-4 sm:gap-3">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                aria-label="Search ARTH.OS"
                placeholder="Search ARTH.OS..."
                className="w-full rounded-2xl border py-2.5 pl-10 pr-4 text-sm shadow-sm outline-none transition"
                style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-elevated)', color: 'var(--text-primary)' }}
              />
            </div>
            <div className="hidden items-center gap-2 sm:flex">
              {topNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.label}
                    className="flex items-center gap-2 rounded-2xl border px-3 py-2 text-sm font-medium shadow-sm transition"
                    style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)', color: 'var(--text-secondary)' }}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setThemeName((current) => (current === 'default' ? 'dark' : current === 'dark' ? 'high-contrast' : 'default'))}
              className="rounded-2xl border p-2 shadow-sm transition"
              style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)', color: 'var(--text-secondary)' }}
              aria-label="Cycle theme"
            >
              <Palette className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2 rounded-2xl border px-3 py-2 text-sm shadow-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)', color: 'var(--text-secondary)' }}>
              <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
              Branch 1204
            </div>
            <div className="rounded-2xl border px-3 py-2 text-sm font-medium shadow-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)', color: 'var(--text-secondary)' }}>Tenant: FinCorp</div>
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6">
        <aside
          className={`hidden shrink-0 flex-col gap-4 rounded-3xl border p-4 lg:flex ${
            sidebarExpanded ? 'w-72' : 'w-20'
          }`}
          style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-sidebar)', color: 'var(--text-inverse)' }}
          onMouseEnter={() => setSidebarExpanded(true)}
          onMouseLeave={() => setSidebarExpanded(false)}
        >
          <div className="mb-4 flex items-center justify-between rounded-3xl px-4 py-3" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}>
            <div>
              <p className="text-xs uppercase tracking-[0.24em]" style={{ color: 'rgba(255,255,255,0.65)' }}>Global Navigation</p>
              <p className="font-semibold">Persistent Sidebar</p>
            </div>
            <ChevronRight className="h-4 w-4" style={{ color: 'rgba(255,255,255,0.65)' }} />
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.label}
                  href="#"
                  className="flex items-center gap-3 rounded-3xl px-4 py-3 text-sm font-semibold transition"
                  style={{ color: 'var(--text-inverse)' }}
                >
                  <Icon className="h-5 w-5" style={{ color: 'rgba(255,255,255,0.7)' }} />
                  <span className={`${sidebarExpanded ? 'block' : 'hidden'}`}>{item.label}</span>
                </a>
              );
            })}
          </nav>

          <div className="mt-auto rounded-3xl p-4 text-sm" style={{ backgroundColor: 'rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.72)' }}>
            <p className="text-xs uppercase tracking-[0.24em]" style={{ color: 'rgba(255,255,255,0.58)' }}>Compressed Behavior</p>
            <p className="mt-3 text-sm leading-6" style={{ color: 'rgba(255,255,255,0.84)' }}>
              Hover expands the sidebar. When collapsed, only icons remain to preserve space.
            </p>
          </div>
        </aside>

        <main className="flex-1">
          <section className="rounded-3xl border p-6 shadow-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)' }}>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.26em]" style={{ color: 'var(--accent-primary)' }}>EDS-005</p>
                <h1 className="mt-3 text-3xl font-semibold" style={{ color: 'var(--text-primary)' }}>Design Tokens & Theme System</h1>
                <p className="mt-4 max-w-2xl text-sm leading-7" style={{ color: 'var(--text-secondary)' }}>
                  Semantic tokens now drive surfaces, borders, text, and interactive states across the enterprise shell.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {kpis.map((kpi) => (
                  <div key={kpi.label} className="rounded-3xl border p-4 shadow-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-elevated)' }}>
                    <p className="text-xs uppercase tracking-[0.24em]" style={{ color: 'var(--text-muted)' }}>{kpi.label}</p>
                    <p className="mt-3 text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>{kpi.value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 rounded-3xl border p-5" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-elevated)' }}>
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em]" style={{ color: 'var(--text-secondary)' }}>Theme Controls</p>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Themes switch at runtime without changing component logic.</p>
                </div>
                <div className="rounded-2xl px-3 py-2 text-sm font-semibold" style={{ backgroundColor: 'var(--background-accent)', color: 'var(--accent-primary)' }}>Token-driven</div>
              </div>

              <div className="mt-6 rounded-3xl p-5 shadow-sm" style={{ backgroundColor: 'var(--background-surface)', border: '1px solid var(--border-default)' }}>
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.24em]" style={{ color: 'var(--text-muted)' }}>
                      {breadcrumbs.map((crumb, index) => (
                        <span key={crumb} className="inline-flex items-center gap-2">
                          {index > 0 && <ChevronRight className="h-3 w-3" style={{ color: 'var(--text-muted)' }} />}
                          {crumb}
                        </span>
                      ))}
                    </div>
                    <h2 className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>Approval Workspace</h2>
                    <p className="max-w-2xl text-sm" style={{ color: 'var(--text-secondary)' }}>Review and approve employee expenses, with access to tasks, approvals, and help in context.</p>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <button className="rounded-full px-4 py-2 text-sm font-semibold text-white transition" style={{ backgroundColor: 'var(--accent-primary)' }}>+ New Approval</button>
                    <button className="rounded-full border px-4 py-2 text-sm font-semibold transition" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)', color: 'var(--text-secondary)' }}>Import</button>
                    <button className="rounded-full border px-4 py-2 text-sm font-semibold transition" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)', color: 'var(--text-secondary)' }}>Export</button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <article className="rounded-3xl border p-6 shadow-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)' }}>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em]" style={{ color: 'var(--accent-primary)' }}>Theme Surface</p>
                  <h2 className="mt-2 text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>Semantic Tokens</h2>
                </div>
                <div className="rounded-2xl px-3 py-2 text-sm font-semibold" style={{ backgroundColor: 'var(--background-accent)', color: 'var(--accent-primary)' }}>Light / Dark / High Contrast</div>
              </div>
              <div className="mt-6 grid gap-4 lg:grid-cols-2">
                <div className="rounded-3xl border p-5" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-elevated)' }}>
                  <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Background Tokens</p>
                  <p className="mt-3 text-sm" style={{ color: 'var(--text-secondary)' }}>Default, surface, elevated, header, sidebar, and accent surfaces inherit semantic tokens.</p>
                </div>
                <div className="rounded-3xl border p-5" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-elevated)' }}>
                  <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Text & Border Tokens</p>
                  <p className="mt-3 text-sm" style={{ color: 'var(--text-secondary)' }}>Primary, secondary, muted, inverse, border focus, and state colors all come from the same token map.</p>
                </div>
              </div>
            </article>

            <aside className="rounded-3xl border p-6 text-slate-100 shadow-sm" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-sidebar)' }}>
              <p className="text-sm uppercase tracking-[0.24em]" style={{ color: 'rgba(255,255,255,0.65)' }}>Theme Preview</p>
              <h2 className="mt-3 text-xl font-semibold text-white">Runtime switching</h2>
              <p className="mt-2 text-sm" style={{ color: 'rgba(255,255,255,0.72)' }}>The active theme updates the whole shell without altering component structure or business logic.</p>
              <div className="mt-6 space-y-4">
                <div className="rounded-3xl p-4" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}>
                  <p className="text-sm font-semibold text-white">Current theme</p>
                  <p className="mt-2 text-sm" style={{ color: 'rgba(255,255,255,0.72)' }}>{activeTheme.name}</p>
                </div>
                <div className="rounded-3xl p-4" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}>
                  <p className="text-sm font-semibold text-white">Token coverage</p>
                  <p className="mt-2 text-sm" style={{ color: 'rgba(255,255,255,0.72)' }}>Backgrounds, text, borders, surfaces, and action colors are all tokenized.</p>
                </div>
              </div>
            </aside>
          </section>
        </main>
      </div>

      <footer className="border-t px-4 py-3 text-sm sm:px-6" style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--background-surface)', color: 'var(--text-secondary)' }}>
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
          <span>EDS-005 token system active • runtime theming enabled • tenant themes ready</span>
          <div className="flex flex-wrap items-center gap-3">
            <span>Theme: {activeTheme.name}</span>
            <span className="rounded-full px-3 py-1" style={{ backgroundColor: 'var(--background-accent)', color: 'var(--accent-primary)' }}>Online</span>
          </div>
        </div>
      </footer>

      <button className="fixed bottom-6 right-6 z-50 inline-flex items-center gap-3 rounded-full px-5 py-3 text-sm font-semibold text-white shadow-2xl transition" style={{ backgroundColor: 'var(--accent-primary)' }}>
        <Sparkles className="h-5 w-5" />
        Ask FinDNA
      </button>
    </div>
  );
}
