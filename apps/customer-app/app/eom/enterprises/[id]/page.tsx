import React from 'react';
import Link from 'next/link';
import { AppShell } from '../../../components/AppShell';
import { eomApiUrl } from '../../eomApi';

type Profile = {
  enterprise: {
    id: string;
    code: string;
    name: string;
    display_name?: string | null;
    short_name?: string | null;
    status: string;
    currency_code?: string | null;
    timezone?: string | null;
    language?: string | null;
  };
  branding: Record<string, string | null>;
  legal: Record<string, string | null>;
  finance: Record<string, string | null>;
  localization: Record<string, string | null>;
  contact: Record<string, string | null>;
  compliance: Record<string, string | boolean | null>;
  integrations: Array<Record<string, string | null>>;
  documents: Array<Record<string, string | null>>;
};

type Dashboard = {
  health: {
    score: number;
    status: string;
    missing: string[];
  };
  indicators: Array<{ label: string; value: number | string }>;
  perspectives: Record<string, string[]>;
  reports: string[];
};

type AuditItem = {
  id: string;
  action: string;
  payload?: string | null;
  created_at?: string | null;
};

function ValueGrid({ title, data }: { title: string; data: Record<string, string | boolean | null | undefined> }) {
  const entries = Object.entries(data).filter(([, value]) => value !== null && value !== undefined && value !== '');

  return (
    <section className="rounded-md border border-border-default bg-background-surface p-4">
      <h3 className="text-lg font-semibold">{title}</h3>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        {entries.length > 0 ? entries.map(([key, value]) => (
          <div key={key}>
            <div className="text-xs uppercase text-text-secondary">{key.replace(/_/g, ' ')}</div>
            <div className="mt-1 text-sm font-medium">{String(value)}</div>
          </div>
        )) : (
          <div className="text-sm text-text-secondary">No values configured.</div>
        )}
      </div>
    </section>
  );
}

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(eomApiUrl(path), { cache: 'no-store' });
    if (!res.ok) {
      return null;
    }
    return await res.json();
  } catch {
    return null;
  }
}

export default async function EnterpriseDetailPage({ params }: { params: { id: string } }) {
  const id = params.id;
  const [profile, dashboard, auditBody, settingsBody] = await Promise.all([
    getJson<Profile>(`/eom/enterprises/${id}/profile`),
    getJson<Dashboard>(`/eom/enterprises/${id}/dashboard`),
    getJson<{ items: AuditItem[] }>(`/eom/enterprises/${id}/audit`),
    getJson<{ items: Array<Record<string, string | boolean>> }>(`/eom/enterprises/${id}/settings`),
  ]);
  const audit = auditBody?.items || [];
  const settings = settingsBody?.items || [];

  if (!profile) {
    return (
      <AppShell>
        <div className="space-y-3">
          <div className="rounded-md border border-border-default bg-background-surface p-4 text-sm text-text-secondary">Enterprise not found.</div>
          <Link className="btn" href="/eom/enterprises">Back to enterprises</Link>
        </div>
      </AppShell>
    );
  }

  const enterprise = profile.enterprise;
  const health = dashboard?.health;

  return (
    <AppShell>
      <div className="space-y-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <Link href="/eom/enterprises" className="text-sm font-medium text-primary-600">Back to Enterprise Master</Link>
            <h2 className="mt-2 text-2xl font-semibold">{enterprise.display_name || enterprise.name}</h2>
            <p className="mt-1 text-sm text-text-secondary">{enterprise.code} · {enterprise.status} · {enterprise.currency_code || 'Currency not set'}</p>
          </div>
          <div className="flex flex-col gap-3">
            <Link href={`/eom/enterprises/${enterprise.id}/edit`} className="btn btn-secondary w-full text-center sm:w-auto">
              Edit Enterprise Profile
            </Link>
            <div className="rounded-md border border-border-default bg-background-surface p-4 lg:min-w-72">
              <div className="text-sm text-text-secondary">Enterprise Health</div>
              <div className="mt-1 text-3xl font-semibold">{health?.score ?? 0}%</div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-background-muted">
                <div className="h-full bg-primary-500" style={{ width: `${health?.score ?? 0}%` }} />
              </div>
              <div className="mt-2 text-sm font-medium capitalize">{health?.status?.replace(/-/g, ' ') || 'setup required'}</div>
            </div>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {(dashboard?.indicators || []).map((indicator) => (
            <div key={indicator.label} className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">{indicator.label}</div>
              <div className="mt-1 text-xl font-semibold">{indicator.value}</div>
            </div>
          ))}
        </div>

        <section className="rounded-md border border-border-default bg-background-surface p-4">
          <h3 className="text-lg font-semibold">Digital Enterprise Twin</h3>
          <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
            {Object.entries(dashboard?.perspectives || {}).map(([name, items]) => (
              <div key={name} className="rounded-md border border-border-default p-3">
                <div className="font-medium capitalize">{name}</div>
                <div className="mt-2 space-y-1 text-sm text-text-secondary">
                  {items.map((item) => <div key={item}>{item}</div>)}
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="grid gap-4 xl:grid-cols-2">
          <ValueGrid title="Branding" data={profile.branding} />
          <ValueGrid title="Legal" data={profile.legal} />
          <ValueGrid title="Finance" data={profile.finance} />
          <ValueGrid title="Localization" data={profile.localization} />
          <ValueGrid title="Contact" data={profile.contact} />
          <ValueGrid title="Compliance" data={profile.compliance} />
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <section className="rounded-md border border-border-default bg-background-surface p-4">
            <h3 className="text-lg font-semibold">Integrations</h3>
            <div className="mt-3 space-y-2">
              {profile.integrations.map((item) => (
                <div key={String(item.id || item.integration_type)} className="flex items-center justify-between rounded-md border border-border-default p-3 text-sm">
                  <span className="font-medium capitalize">{String(item.integration_type || '').replace(/_/g, ' ')}</span>
                  <span className="capitalize text-text-secondary">{item.status || 'planned'}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-md border border-border-default bg-background-surface p-4">
            <h3 className="text-lg font-semibold">Documents</h3>
            <div className="mt-3 space-y-2">
              {profile.documents.map((item) => (
                <div key={String(item.id || item.document_type)} className="flex items-center justify-between rounded-md border border-border-default p-3 text-sm">
                  <span className="font-medium">{item.name || item.document_type}</span>
                  <span className="capitalize text-text-secondary">{item.status || 'pending'}</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="grid gap-4 xl:grid-cols-3">
          <section className="rounded-md border border-border-default bg-background-surface p-4">
            <h3 className="text-lg font-semibold">Settings</h3>
            <div className="mt-3 space-y-2 text-sm">
              {settings.slice(0, 8).map((item) => (
                <div key={`${item.setting_group}-${item.setting_key}`} className="flex items-center justify-between">
                  <span>{String(item.setting_group)}</span>
                  <span className="text-text-secondary">{String(item.setting_value || '')}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-md border border-border-default bg-background-surface p-4">
            <h3 className="text-lg font-semibold">Reports</h3>
            <div className="mt-3 space-y-2 text-sm text-text-secondary">
              {(dashboard?.reports || []).map((report) => <div key={report}>{report}</div>)}
            </div>
          </section>

          <section className="rounded-md border border-border-default bg-background-surface p-4">
            <h3 className="text-lg font-semibold">Audit Timeline</h3>
            <div className="mt-3 space-y-2 text-sm">
              {audit.length > 0 ? audit.map((item) => (
                <div key={item.id} className="rounded-md border border-border-default p-2">
                  <div className="font-medium capitalize">{item.action.replace(/_/g, ' ')}</div>
                  <div className="text-xs text-text-secondary">{item.created_at || 'Recorded'}</div>
                </div>
              )) : <div className="text-text-secondary">No audit entries yet.</div>}
            </div>
          </section>
        </div>

        {health?.missing?.length ? (
          <section className="rounded-md border border-border-default bg-background-surface p-4">
            <h3 className="text-lg font-semibold">AI Configuration Signals</h3>
            <div className="mt-2 text-sm text-text-secondary">
              Missing or weak inputs: {health.missing.slice(0, 8).join(', ')}
            </div>
          </section>
        ) : null}
      </div>
    </AppShell>
  );
}
