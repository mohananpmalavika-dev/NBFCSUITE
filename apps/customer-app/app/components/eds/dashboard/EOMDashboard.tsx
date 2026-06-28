"use client";

import Link from 'next/link';
import {
  Building2,
  FileText,
  GitBranch,
  Map,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
  Users2,
} from 'lucide-react';
import { AISummary } from '../ai/AISummary';
import { MetricCard } from '../data-display/MetricCard';
import { Badge } from '../foundation/Badge';
import { DashboardLayout } from './DashboardLayout';
import { KPIWidget } from './KPIWidget';

interface EOMHierarchyNode {
  id: string;
  code: string;
  name: string;
  type: string;
  status: string;
  children?: EOMHierarchyNode[];
}

interface EOMDashboardData {
  summary?: Record<string, number>;
  recent_enterprises?: Array<{
    id: string;
    enterprise_name: string;
    enterprise_code: string;
    status: string;
  }>;
  workspace?: Array<{ label: string; description: string }>;
  operating_views?: string[];
  reports?: string[];
  hierarchy?: { items: EOMHierarchyNode[] };
}

const defaultWorkspace = [
  { label: 'Dashboard', description: 'Executive operational view' },
  { label: 'Enterprise list', description: 'Root entity administration' },
  { label: 'Hierarchy explorer', description: 'Tree-based organization drill-down' },
  { label: 'Organization chart', description: 'Reporting and position structure' },
  { label: 'Branch network', description: 'Geographic footprint and operations' },
  { label: 'Reports', description: 'Standard organization reports' },
];

const defaultOperatingViews = [
  'Operational view',
  'Financial view',
  'People view',
  'Risk view',
  'Performance view',
  'Document view',
  'AI insights',
];

const defaultReports = [
  'Branch list',
  'Branch hierarchy',
  'Department list',
  'Cost center report',
  'Profit center report',
  'Position vacancy',
  'Reporting structure',
  'Employee distribution',
  'Branch performance',
  'Organization tree',
];

const roadmap = [
  'EOM-001 Enterprise',
  'EOM-002 Brand',
  'EOM-003 Legal entity',
  'EOM-004 Business unit',
  'EOM-005 Geography',
  'EOM-006 Zone / Region / Area / Cluster',
  'EOM-007 Branch management',
  'EOM-008 Department management',
  'EOM-015 Organization explorer and org chart',
];

function normalizeCount(value: unknown) {
  return typeof value === 'number' ? value : 0;
}

function TreeNode({ node, depth = 0 }: { node: EOMHierarchyNode; depth?: number }) {
  return (
    <li>
      <div
        className="flex items-start gap-3 rounded-xl border border-border-default bg-background-surface p-3"
        style={{ marginLeft: depth ? `${Math.min(depth * 16, 48)}px` : undefined }}
      >
        <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-background-accent text-accent-primary">
          <GitBranch className="h-4 w-4" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-semibold text-text-primary">{node.name}</p>
            <Badge tone="neutral" className="text-xs">{node.type}</Badge>
            <Badge tone={node.status === 'active' ? 'success' : 'warning'} className="text-xs">{node.status}</Badge>
          </div>
          <p className="mt-1 text-sm text-text-secondary">{node.code}</p>
        </div>
      </div>
      {node.children?.length ? (
        <ol className="mt-2 space-y-2">
          {node.children.map((child) => (
            <TreeNode key={child.id} node={child} depth={depth + 1} />
          ))}
        </ol>
      ) : null}
    </li>
  );
}

export default function EOMDashboard({ data }: { data?: EOMDashboardData | null }) {
  const summary = data?.summary ?? {};
  const workspace = data?.workspace?.length ? data.workspace : defaultWorkspace;
  const operatingViews = data?.operating_views?.length ? data.operating_views : defaultOperatingViews;
  const reports = data?.reports?.length ? data.reports : defaultReports;
  const hierarchyItems = data?.hierarchy?.items ?? [];

  const kpis = [
    { label: 'Enterprises', value: normalizeCount(summary.enterprises), icon: <Building2 className="h-5 w-5" /> },
    { label: 'Brands', value: normalizeCount(summary.brands), icon: <Sparkles className="h-5 w-5" /> },
    { label: 'Legal Entities', value: normalizeCount(summary.legal_entities), icon: <ShieldCheck className="h-5 w-5" /> },
    { label: 'Business Units', value: normalizeCount(summary.business_units), icon: <Network className="h-5 w-5" /> },
    { label: 'Geography Nodes', value: normalizeCount(summary.geography_nodes), icon: <Map className="h-5 w-5" /> },
    { label: 'Open Approvals', value: normalizeCount(summary.open_approvals), icon: <FileText className="h-5 w-5" /> },
  ];

  return (
    <DashboardLayout
      title="Enterprise Organization Management"
      description="Digital enterprise twin for organization, geography, financial mapping, approval structure, reporting, and AI-assisted operating insight."
      persona="executive"
      actions={[
        { label: 'New Enterprise', icon: <Building2 className="h-4 w-4" /> },
        { label: 'Open Explorer', icon: <GitBranch className="h-4 w-4" /> },
      ]}
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        {kpis.map((kpi) => (
          <KPIWidget
            key={kpi.label}
            title={kpi.label}
            value={String(kpi.value)}
            trend={kpi.value > 0 ? 'up' : 'down'}
            change={kpi.value > 0 ? 'Live from EOM service' : 'Ready for setup'}
          />
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <section className="space-y-4 rounded-xl border border-border-default bg-background-elevated p-4">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-text-primary">Organization Explorer</h3>
              <p className="mt-1 text-sm text-text-secondary">
                Enterprise to brand, legal entity, business unit, geography, branch, department, position, and employee.
              </p>
            </div>
            <div className="flex items-center gap-2 rounded-xl border border-border-default bg-background-surface px-3 py-2 text-sm text-text-muted">
              <Search className="h-4 w-4" />
              <span>Search hierarchy</span>
            </div>
          </div>

          {hierarchyItems.length > 0 ? (
            <ol className="space-y-2">
              {hierarchyItems.map((node) => (
                <TreeNode key={node.id} node={node} />
              ))}
            </ol>
          ) : (
            <div className="rounded-xl border border-border-default bg-background-surface p-4">
              <p className="font-semibold text-text-primary">Hierarchy ready for data</p>
              <p className="mt-2 text-sm leading-6 text-text-secondary">
                Create enterprise, legal entity, business unit, and geography records to populate the explorer.
              </p>
            </div>
          )}
        </section>

        <aside className="space-y-4">
          <AISummary
            summary="EOM is the shared operating model for customers, branches, departments, employees, finance mappings, approvals, risk, and reporting."
            suggestions={[
              'Show vacant positions',
              'Find duplicate branches',
              'Recommend reporting changes',
            ]}
          />
          <section className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-text-primary">Recent Enterprises</h3>
            <div className="mt-3 space-y-2">
              {(data?.recent_enterprises ?? []).length > 0 ? (
                data?.recent_enterprises?.map((enterprise) => (
                  <div key={enterprise.id} className="rounded-xl bg-background-elevated p-3">
                    <p className="font-semibold text-text-primary">{enterprise.enterprise_name}</p>
                    <p className="mt-1 text-sm text-text-secondary">{enterprise.enterprise_code}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-text-secondary">No enterprises created yet.</p>
              )}
            </div>
          </section>
        </aside>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
          <h3 className="text-lg font-semibold text-text-primary">Workspace</h3>
          <div className="mt-4 space-y-3">
            {workspace.map((item) => (
              <div key={item.label} className="rounded-xl bg-background-elevated p-3">
                <p className="font-semibold text-text-primary">{item.label}</p>
                <p className="mt-1 text-sm text-text-secondary">{item.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
          <h3 className="text-lg font-semibold text-text-primary">Digital Twin Views</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {operatingViews.map((view) => (
              <Badge key={view} tone="accent">{view}</Badge>
            ))}
          </div>
          <div className="mt-4 grid gap-3">
            <MetricCard label="Permission roles" value="6" helper="Enterprise, zone, region, area, branch, department" icon={<Users2 className="h-5 w-5" />} />
            <MetricCard label="Workflow paths" value="2" helper="Branch and department creation examples" tone="warning" />
          </div>
        </section>

        <section className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
          <h3 className="text-lg font-semibold text-text-primary">Reports</h3>
          <div className="mt-4 grid gap-2">
            {reports.slice(0, 7).map((report) => (
              <div key={report} className="flex items-center justify-between rounded-xl bg-background-elevated px-3 py-2 text-sm">
                <span className="font-semibold text-text-primary">{report}</span>
                <FileText className="h-4 w-4 text-text-muted" />
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="rounded-xl border border-border-default bg-background-surface p-4 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-text-primary">Implementation Roadmap</h3>
            <p className="mt-1 text-sm text-text-secondary">
              EP-001 breaks the enterprise operating model into staged implementation packages.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link
              href="/eom/enterprises/new"
              className="inline-flex items-center justify-center rounded-full bg-accent-primary px-3 py-2 text-sm font-semibold"
              style={{ color: 'var(--accent-on-primary)' }}
            >
              Create enterprise
            </Link>
            <Link
              href="/eom/geography/new"
              className="inline-flex items-center justify-center rounded-full border border-border-default bg-background-surface px-3 py-2 text-sm font-semibold text-text-secondary"
            >
              Add geography
            </Link>
          </div>
        </div>
        <div className="mt-4 grid gap-2 md:grid-cols-3">
          {roadmap.map((item, index) => (
            <div key={item} className="rounded-xl border border-border-default bg-background-elevated p-3">
              <p className="text-xs font-semibold text-text-muted">Package {index + 1}</p>
              <p className="mt-1 text-sm font-semibold text-text-primary">{item}</p>
            </div>
          ))}
        </div>
      </section>
    </DashboardLayout>
  );
}
