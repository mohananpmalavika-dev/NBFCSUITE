"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../components/AppShell';
import { riskApi, DEFAULT_RISK_TENANT } from '../riskApi';
import type { RiskDashboardResponse } from '../riskApi';

export default function RiskDashboardPage() {
  const [dashboard, setDashboard] = useState<RiskDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadDashboard() {
    setLoading(true);
    setError('');
    try {
      const result = await riskApi.getRiskDashboard(DEFAULT_RISK_TENANT);
      setDashboard(result);
    } catch (err) {
      setError('Unable to load risk dashboard. Ensure the risk service is running.');
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
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">Enterprise Risk Management</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">Risk dashboard, register and incident monitoring</h1>
          <p className="mt-2 max-w-3xl text-sm text-text-secondary">
            Track high risks, incidents, control health, and compliance issues for enterprise governance.
          </p>
        </div>

        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-6 text-sm text-text-secondary">Loading risk dashboard…</div>
        ) : error ? (
          <div className="rounded-md border border-border-default bg-danger-surface p-4 text-sm text-danger-foreground">{error}</div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Open risks</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.open_risks ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">High risks</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.high_risks ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Critical risks</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.critical_risks ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Incidents</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.incidents ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Loss events</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.loss_events ?? 0}</div>
            </div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">
              <div className="text-sm text-text-secondary">Risk score</div>
              <div className="mt-2 text-3xl font-semibold text-text-primary">{dashboard?.risk_score ?? '--'}%</div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
