"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { platformApi, DEFAULT_PLATFORM_TENANT } from '../platformApi';
import type { EdpDashboardResponse } from '../platformApi';

export default function PlatformDashboardPage() {
  const [dashboard, setDashboard] = useState<EdpDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError('');
      try {
        const result = await platformApi.getDashboard(DEFAULT_PLATFORM_TENANT);
        setDashboard(result);
      } catch (err) {
        setError('Unable to load platform dashboard. Ensure the platform service is running.');
        setDashboard(null);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise Data Platform</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">EDP Dashboard</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            A unified view of data catalog coverage, lineage completeness, quality checks, and glossary adoption.
          </p>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">Loading platform dashboard…</div>
        ) : error ? (
          <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-4">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Data assets</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.data_assets ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Data domains</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.data_domains ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Lineage edges</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.lineage_edges ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Quality checks</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.quality_checks ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Glossary terms</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.glossary_terms ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Health score</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.health_score ?? 0}%</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4 lg:col-span-2">
              <div className="text-sm text-text-secondary">Status</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.status ?? 'unknown'}</div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
