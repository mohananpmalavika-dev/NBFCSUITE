'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  Banknote,
  Bell,
  Building2,
  ChartPie,
  CheckCircle2,
  ChevronRight,
  ClipboardList,
  Clock3,
  Command,
  Compass,
  DollarSign,
  FileText,
  HelpCircle,
  Home,
  LayoutDashboard,
  Layers,
  Menu,
  Palette,
  PanelRightOpen,
  Search,
  Settings2,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  UserCircle,
  Users2,
  X,
} from 'lucide-react';
import { buildCssVariables, themes, type ThemeName } from '../../lib/design-tokens';
import {
  AISummary,
  Alert,
  ApprovalCard,
  Button as EDSButton,
  Checkbox,
  Customer360Card,
  EnterpriseTable,
  LoanSummaryCard,
  MetricCard,
  RoleBadge,
  TextInput,
  Toggle,
  componentRegistry,
} from './eds';

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
  { label: 'Deposits', icon: Banknote },
  { label: 'Gold Loans', icon: FileText },
  { label: 'Treasury', icon: Compass },
  { label: 'Accounting', icon: ClipboardList },
  { label: 'HRMS', icon: ShieldCheck },
  { label: 'CRM', icon: Users2 },
  { label: 'Risk', icon: ShieldAlert },
  { label: 'Compliance', icon: Layers },
  { label: 'Reports', icon: ChartPie },
  { label: 'Administration', icon: Settings2 },
  { label: 'AI', icon: Sparkles },
];

const mobileTabs = [
  { label: 'Home', icon: Home },
  { label: 'Search', icon: Search },
  { label: 'Tasks', icon: ClipboardList },
  { label: 'Alerts', icon: Bell },
  { label: 'Profile', icon: UserCircle },
];

const breadcrumbs = ['Home', 'Workspace', 'Expenses', 'Approval'];

const kpis = [
  { label: 'Pending Approvals', value: '38', change: '+6 today' },
  { label: 'SLA Health', value: '94%', change: 'On track' },
  { label: 'Exceptions', value: '7', change: 'Needs review' },
  { label: 'Avg Turnaround', value: '2.4h', change: 'Fast lane' },
];

const favorites = ['Employee Directory', 'Customer 360', 'General Ledger'];
const recent = ['Expense Approval', 'Branch 1204', 'Policy Exceptions'];

const commandActions = [
  'Create Employee',
  'Open Customer 360',
  'Find Loan Application',
  'Review Expense Approval',
  'Open General Ledger',
  'Show HRMS Dashboard',
  'Ask FinDNA',
];

const approvals = [
  { employee: 'Asha Menon', amount: 'INR 18,420', status: 'Policy matched' },
  { employee: 'Rohan Iyer', amount: 'INR 7,900', status: 'Manager approved' },
  { employee: 'Neha Shah', amount: 'INR 24,600', status: 'Receipt pending' },
];

const registryRows = [
  { component: 'EnterpriseTable', layer: 'Data Display', status: 'Typed API' },
  { component: 'ApprovalCard', layer: 'Workflow', status: 'Action Ready' },
  { component: 'AISummary', layer: 'AI', status: 'FinDNA Ready' },
  { component: 'PermissionGuard', layer: 'Security', status: 'RBAC Ready' },
];

const registryColumns = [
  { key: 'component' as const, label: 'Component' },
  { key: 'layer' as const, label: 'Layer' },
  { key: 'status' as const, label: 'Contract' },
];

export function AppShell() {
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [themeName, setThemeName] = useState<ThemeName>('default');
  const [commandOpen, setCommandOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [autosaveEnabled, setAutosaveEnabled] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const activeTheme = useMemo(() => themes[themeName], [themeName]);
  const libraryLayerCount = useMemo(
    () => new Set(componentRegistry.map((component) => component.layer)).size,
    [],
  );
  const visibleCommands = useMemo(
    () =>
      commandActions.filter((action) =>
        action.toLowerCase().includes(searchQuery.trim().toLowerCase()),
      ),
    [searchQuery],
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeName);
    Object.assign(document.documentElement.style, buildCssVariables(activeTheme));
  }, [activeTheme, themeName]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setCommandOpen(true);
      }

      if (event.key === 'Escape') {
        setCommandOpen(false);
        setMobileMenuOpen(false);
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  function cycleTheme() {
    setThemeName((current) =>
      current === 'default' ? 'dark' : current === 'dark' ? 'high-contrast' : 'default',
    );
  }

  const sidebar = (
    <aside
      className="flex h-full shrink-0 flex-col border-r bg-background-sidebar text-text-inverse transition-all duration-normal ease-standard"
      style={{ width: sidebarExpanded ? 'var(--shell-sidebar-expanded)' : 'var(--shell-sidebar-collapsed)' }}
      onMouseEnter={() => setSidebarExpanded(true)}
      onMouseLeave={() => setSidebarExpanded(false)}
    >
      <div className="flex h-16 items-center gap-3 border-b border-border-default px-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-background-sidebarSubtle">
          <Sparkles className="h-5 w-5" />
        </div>
        {sidebarExpanded && (
          <div className="min-w-0">
            <p className="truncate text-xs font-semibold uppercase tracking-[0.18em] text-text-inverseMuted">
              ARTH.OS
            </p>
            <p className="truncate text-sm font-semibold">Global Navigation</p>
          </div>
        )}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4" aria-label="Global navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = item.label === 'HRMS';

          return (
            <a
              key={item.label}
              href="#"
              className="flex min-h-12 items-center gap-3 rounded-xl px-3 text-sm font-semibold text-text-inverse transition duration-normal ease-standard hover:bg-background-sidebarSubtle"
              style={isActive ? { backgroundColor: 'var(--background-sidebar-subtle)' } : undefined}
              title={sidebarExpanded ? undefined : item.label}
            >
              <Icon className="h-5 w-5 shrink-0 text-text-inverseMuted" />
              {sidebarExpanded && <span className="truncate">{item.label}</span>}
            </a>
          );
        })}
      </nav>

      {sidebarExpanded && (
        <div className="space-y-4 border-t border-border-default p-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-inverseMuted">
              Favorites
            </p>
            <div className="mt-3 space-y-2">
              {favorites.map((item) => (
                <a key={item} href="#" className="block truncate text-sm text-text-inverseMuted">
                  {item}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-text-inverseMuted">
              Recent
            </p>
            <div className="mt-3 space-y-2">
              {recent.map((item) => (
                <a key={item} href="#" className="block truncate text-sm text-text-inverseMuted">
                  {item}
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </aside>
  );

  return (
    <div className="flex min-h-screen flex-col bg-background-default text-text-primary">
      <header className="sticky top-0 z-header h-16 border-b border-border-default bg-background-header backdrop-blur-sm">
        <div className="flex h-full items-center gap-3 px-4 sm:px-6">
          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary lg:hidden"
            onClick={() => {
              setSidebarExpanded(true);
              setMobileMenuOpen(true);
            }}
            aria-label="Open navigation"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex min-w-0 items-center gap-3">
            <div className="hidden h-10 w-10 items-center justify-center rounded-xl bg-background-sidebar text-text-inverse sm:flex">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs font-semibold uppercase tracking-[0.18em] text-text-muted">
                ARTH.OS
              </p>
              <p className="truncate text-sm font-semibold text-text-primary">Enterprise Shell</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setCommandOpen(true)}
            className="ml-auto hidden h-10 min-w-0 flex-1 max-w-xl items-center gap-3 rounded-xl border border-border-default bg-background-elevated px-4 text-left text-sm text-text-muted shadow-xs md:flex"
            aria-label="Open global search"
          >
            <Search className="h-4 w-4 shrink-0" />
            <span className="truncate">Search customers, employees, loans, GL, reports...</span>
            <span className="ml-auto hidden items-center gap-1 rounded-md border border-border-default px-2 py-1 text-xs font-semibold lg:inline-flex">
              <Command className="h-3 w-3" /> K
            </span>
          </button>

          <div className="hidden items-center gap-2 md:flex">
            {topNavItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.label}
                  type="button"
                  className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary shadow-xs transition duration-normal ease-standard hover:border-border-focus"
                  aria-label={item.label}
                  title={item.label}
                >
                  <Icon className="h-5 w-5" />
                </button>
              );
            })}
          </div>

          <button
            type="button"
            onClick={cycleTheme}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary shadow-xs"
            aria-label="Cycle theme"
            title={`Theme: ${activeTheme.name}`}
          >
            <Palette className="h-5 w-5" />
          </button>

          <div className="hidden items-center gap-2 rounded-xl border border-border-default bg-background-surface px-3 py-2 text-sm text-text-secondary shadow-xs xl:flex">
            <span className="h-2.5 w-2.5 rounded-full bg-accent-success" />
            Branch 1204
          </div>
          <div className="hidden items-center gap-2 rounded-xl border border-border-default bg-background-surface px-3 py-2 text-sm text-text-secondary shadow-xs xl:flex">
            <Building2 className="h-4 w-4" />
            FinCorp
          </div>
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        <div className="hidden lg:block">{sidebar}</div>

        <main className="min-w-0 flex-1 overflow-y-auto pb-24 md:pb-0">
          <div className="border-b border-border-default bg-background-surface px-4 py-4 sm:px-6">
            <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-text-muted">
              {breadcrumbs.map((crumb, index) => (
                <span key={crumb} className="inline-flex items-center gap-2">
                  {index > 0 && <ChevronRight className="h-3 w-3" />}
                  {crumb}
                </span>
              ))}
            </div>
          </div>

          <section className="px-4 py-6 sm:px-6">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div className="max-w-3xl">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-primary">
                  EDS-001 to EDS-005
                </p>
                <h1 className="mt-3 text-3xl font-semibold text-text-primary">
                  Expense Approval Workspace
                </h1>
                <p className="mt-3 text-sm leading-7 text-text-secondary">
                  Dashboard-first workspace with global navigation, contextual drawer, command search,
                  runtime themes, and token-backed shell surfaces.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  className="rounded-full bg-accent-primary px-4 py-2 text-sm font-semibold shadow-sm"
                  style={{ color: 'var(--accent-on-primary)' }}
                >
                  New Approval
                </button>
                <button
                  type="button"
                  className="rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                >
                  Import
                </button>
                <button
                  type="button"
                  className="rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                >
                  Export
                </button>
                <button
                  type="button"
                  onClick={() => setDrawerOpen((open) => !open)}
                  className="inline-flex items-center gap-2 rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                >
                  <PanelRightOpen className="h-4 w-4" />
                  Context
                </button>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {kpis.map((kpi) => (
                <article
                  key={kpi.label}
                  className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm"
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-text-muted">
                    {kpi.label}
                  </p>
                  <p className="mt-3 text-2xl font-semibold text-text-primary">{kpi.value}</p>
                  <p className="mt-2 text-sm text-text-secondary">{kpi.change}</p>
                </article>
              ))}
            </div>

            <div className="mt-6 flex flex-col gap-3 border-y border-border-default bg-background-surface py-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-border-default bg-background-elevated px-4 py-3">
                <Search className="h-4 w-4 shrink-0 text-text-muted" />
                <input
                  type="search"
                  aria-label="Search approvals"
                  placeholder="Search approvals, employees, policies..."
                  className="min-w-0 flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
                />
              </div>
              <div className="flex flex-wrap gap-3">
                {['Department', 'Branch', 'Status', 'Save View'].map((filter) => (
                  <button
                    key={filter}
                    type="button"
                    className="rounded-full border border-border-default bg-background-surface px-4 py-2 text-sm font-semibold text-text-secondary shadow-xs"
                  >
                    {filter}
                  </button>
                ))}
              </div>
            </div>

            <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_var(--shell-right-drawer)]">
              <section className="min-w-0 rounded-xl border border-border-default bg-background-surface shadow-sm">
                <div className="flex items-center justify-between border-b border-border-default px-4 py-4">
                  <div>
                    <h2 className="text-lg font-semibold text-text-primary">Approval Queue</h2>
                    <p className="mt-1 text-sm text-text-secondary">List context stays visible while details open.</p>
                  </div>
                  <button
                    type="button"
                    className="rounded-full border border-border-default bg-background-elevated px-3 py-2 text-sm font-semibold text-text-secondary"
                  >
                    Bulk Action
                  </button>
                </div>

                <div className="divide-y divide-border-default">
                  {approvals.map((approval) => (
                    <button
                      key={approval.employee}
                      type="button"
                      onClick={() => setDrawerOpen(true)}
                      className="grid w-full gap-3 px-4 py-4 text-left transition duration-normal ease-standard hover:bg-background-elevated md:grid-cols-[1fr_auto_auto]"
                    >
                      <div>
                        <p className="font-semibold text-text-primary">{approval.employee}</p>
                        <p className="mt-1 text-sm text-text-secondary">{approval.status}</p>
                      </div>
                      <p className="font-semibold text-text-primary">{approval.amount}</p>
                      <span className="inline-flex items-center rounded-full bg-background-accent px-3 py-1 text-xs font-semibold text-accent-primary">
                        Review
                      </span>
                    </button>
                  ))}
                </div>
              </section>

              {drawerOpen && (
                <aside className="hidden resize-x overflow-auto rounded-xl border border-border-default bg-background-surface p-5 shadow-lg xl:block">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent-primary">
                        Right Context Panel
                      </p>
                      <h2 className="mt-2 text-lg font-semibold text-text-primary">Expense Summary</h2>
                    </div>
                    <button
                      type="button"
                      onClick={() => setDrawerOpen(false)}
                      className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-border-default text-text-secondary"
                      aria-label="Close context panel"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="mt-6 space-y-4">
                    <div className="rounded-xl bg-background-elevated p-4">
                      <p className="text-sm font-semibold text-text-primary">AI Summary</p>
                      <p className="mt-2 text-sm leading-6 text-text-secondary">
                        FinDNA found matching travel policy, manager approval, and one receipt that needs
                        attachment before final posting.
                      </p>
                    </div>
                    <div className="rounded-xl bg-background-elevated p-4">
                      <p className="text-sm font-semibold text-text-primary">Audit Trail</p>
                      <div className="mt-3 space-y-3 text-sm text-text-secondary">
                        <p>Submitted by Asha Menon</p>
                        <p>Reviewed by Branch Manager</p>
                        <p>Pending Finance approval</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      className="w-full rounded-full bg-accent-primary px-4 py-2 text-sm font-semibold"
                      style={{ color: 'var(--accent-on-primary)' }}
                    >
                      Approve Expense
                    </button>
                  </div>
                </aside>
              )}
            </div>

            <section className="mt-8 space-y-6 rounded-xl border border-border-default bg-background-surface p-5 shadow-sm">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent-primary">
                    EDS-006
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-text-primary">
                    Enterprise Component Library
                  </h2>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-text-secondary">
                    Reusable, theme-aware, accessible components now cover foundation, layout,
                    navigation, forms, data display, workflow, feedback, AI, banking, and security layers.
                  </p>
                </div>
                <RoleBadge role="Design System Maintainer" elevated />
              </div>

              <div className="grid gap-4 md:grid-cols-3">
                <MetricCard label="Component Contracts" value={`${componentRegistry.length}`} helper="Published from registry" />
                <MetricCard label="EDS Layers" value={`${libraryLayerCount}`} helper="Foundation to security" tone="success" />
                <MetricCard label="Theme Modes" value="3" helper="Light, dark, contrast" tone="warning" />
              </div>

              <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
                <div className="space-y-6">
                  <EnterpriseTable columns={registryColumns} rows={registryRows} />

                  <div className="grid gap-4 lg:grid-cols-2">
                    <div className="rounded-xl border border-border-default bg-background-elevated p-4">
                      <h3 className="text-lg font-semibold text-text-primary">Form Controls</h3>
                      <div className="mt-4 space-y-4">
                        <TextInput label="Employee Search" placeholder="Search by name or employee ID" helperText="Supports validation and localized helper copy." />
                        <Checkbox label="Require approval audit note" defaultChecked />
                        <Toggle
                          checked={autosaveEnabled}
                          label="Autosave draft"
                          onClick={() => setAutosaveEnabled((enabled) => !enabled)}
                        />
                      </div>
                    </div>

                    <div className="space-y-4">
                      <ApprovalCard
                        title="Travel Expense"
                        requester="Asha Menon | Branch 1204"
                        amount="INR 18,420"
                        onApprove={() => setDrawerOpen(true)}
                      >
                        Includes semantic status, requester metadata, and an auditable action surface.
                      </ApprovalCard>
                      <Alert title="Component contract ready" tone="success">
                        EDS components expose typed props, theme tokens, focus states, and semantic variants.
                      </Alert>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <AISummary
                    summary="FinDNA recommends approving the expense after receipt attachment. No duplicate claims were detected."
                    suggestions={['Request receipt', 'Approve after attachment', 'Add audit note']}
                  />
                  <Customer360Card
                    name="Nisha Rao"
                    customerId="CIF-104928"
                    risk="medium"
                    relationshipValue="INR 42.8L"
                  />
                  <LoanSummaryCard
                    accountNumber="LN-7721-001"
                    product="Vehicle Loan"
                    outstanding="INR 7.4L"
                    status="standard"
                  />
                  <div className="flex flex-wrap gap-3">
                    <EDSButton size="sm">Primary</EDSButton>
                    <EDSButton size="sm" variant="secondary">Secondary</EDSButton>
                  </div>
                </div>
              </div>
            </section>
          </section>
        </main>
      </div>

      <footer className="hidden h-8 items-center justify-between border-t border-border-default bg-background-surface px-6 text-xs text-text-secondary md:flex">
        <span>ARTH.OS v1.0 | Production | Branch 1204 | Connected</span>
        <span className="inline-flex items-center gap-2">
          <Clock3 className="h-3.5 w-3.5" />
          Theme: {activeTheme.name}
        </span>
      </footer>

      <nav className="fixed inset-x-0 bottom-0 z-sidebar grid h-[var(--shell-mobile-nav-height)] grid-cols-5 border-t border-border-default bg-background-surface md:hidden">
        {mobileTabs.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.label}
              type="button"
              className="flex flex-col items-center justify-center gap-1 text-xs font-semibold text-text-secondary"
              aria-label={item.label}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </button>
          );
        })}
      </nav>

      <button
        type="button"
        className="fixed bottom-24 right-6 z-ai inline-flex items-center gap-3 rounded-full bg-accent-primary px-5 py-3 text-sm font-semibold shadow-xl md:bottom-12"
        style={{ color: 'var(--accent-on-primary)' }}
      >
        <Sparkles className="h-5 w-5" />
        Ask FinDNA
      </button>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-drawer bg-background-header lg:hidden">
          <div className="absolute inset-y-0 left-0 shadow-xl">{sidebar}</div>
          <button
            type="button"
            className="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border-default bg-background-surface text-text-secondary"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      )}

      {commandOpen && (
        <div className="fixed inset-0 z-modal flex items-start justify-center bg-background-header px-4 py-20 backdrop-blur-sm">
          <div className="w-full max-w-2xl overflow-hidden rounded-xl border border-border-default bg-background-surface shadow-xl">
            <div className="flex items-center gap-3 border-b border-border-default px-4 py-4">
              <Search className="h-5 w-5 text-text-muted" />
              <input
                autoFocus
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search ARTH.OS or run a command"
                className="min-w-0 flex-1 bg-transparent text-sm text-text-primary outline-none placeholder:text-text-muted"
              />
              <button
                type="button"
                onClick={() => setCommandOpen(false)}
                className="rounded-md border border-border-default px-2 py-1 text-xs font-semibold text-text-secondary"
              >
                Esc
              </button>
            </div>
            <div className="max-h-80 overflow-y-auto p-2">
              {visibleCommands.map((action) => (
                <button
                  key={action}
                  type="button"
                  className="flex w-full items-center justify-between rounded-xl px-4 py-3 text-left text-sm font-semibold text-text-primary hover:bg-background-elevated"
                  onClick={() => setCommandOpen(false)}
                >
                  {action}
                  <ChevronRight className="h-4 w-4 text-text-muted" />
                </button>
              ))}
              {visibleCommands.length === 0 && (
                <p className="px-4 py-6 text-sm text-text-secondary">No matching commands found.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
