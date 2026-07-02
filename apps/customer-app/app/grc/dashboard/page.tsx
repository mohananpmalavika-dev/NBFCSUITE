"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { grcApi, DEFAULT_GRC_TENANT } from '../grcApi';
import type { GrcDashboardResponse } from '../grcApi';

export default function GrcDashboardPage() {
  const [dashboard, setDashboard] = useState<GrcDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadDashboard() {
    setLoading(true);
    setError('');
    try {
      const result = await grcApi.getDashboard(DEFAULT_GRC_TENANT);
      setDashboard(result);
    } catch (err) {
      setError('Unable to load GRC dashboard. Ensure the GRC service is running.');
      setDashboard(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise GRC</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">GRC Dashboard</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Monitor policy coverage, compliance obligations, audits, issues, and corrective actions from one governance cockpit.
          </p>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">Loading GRC dashboard…</div>
        ) : error ? (
          <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Active policies</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.active_policies ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Obligations due</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.obligations_due ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Open audits</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.open_audits ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Open issues</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.open_issues ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Corrective actions</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.corrective_actions ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Compliance score</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.compliance_score ?? '--'}%</div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
