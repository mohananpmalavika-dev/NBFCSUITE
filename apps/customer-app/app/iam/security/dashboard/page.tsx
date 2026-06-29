"use client";

import React, { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
const AUTH_API_BASE = process.env.NEXT_PUBLIC_AUTH_API_URL ?? 'http://localhost:8001';

function authApiUrl(path: string) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${AUTH_API_BASE}${normalizedPath}`;
}

import { KPIWidget } from '../../../components/eds/dashboard/KPIWidget';
import { DashboardGrid } from '../../../components/eds/dashboard/DashboardGrid';

export default function SecurityDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(authApiUrl('/security/dashboard'));
        if (!res.ok) throw new Error(`Failed: ${res.status}`);
        const body = await res.json();
        if (mounted) setData(body);
      } catch (e: any) {
        if (mounted) setError(e?.message ?? 'Failed to load security dashboard');
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  if (loading) {
    return (
      <AppShell>
        <div className="p-4 text-sm text-text-secondary">Loading…</div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell>
        <div className="p-4 text-sm text-text-secondary">{error}</div>
      </AppShell>
    );
  }

  const kpis = data?.kpis ?? {};

  const metrics = [
    { label: 'Users', value: kpis.users ?? 0 },
    { label: 'Active Users', value: kpis.active_users ?? 0 },
    { label: 'Locked Users', value: kpis.locked_users ?? 0 },
    { label: 'MFA Enabled', value: kpis.mfa_enabled ?? 0 },
    { label: 'Active Sessions', value: kpis.active_sessions ?? 0 },
    { label: 'Delegated Access', value: kpis.delegated_access ?? 0 },
    { label: 'High Risk Users', value: kpis.high_risk_users ?? 0 },
    { label: 'Dormant Accounts', value: kpis.dormant_accounts ?? 0 },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="space-y-1">
          <p className="text-sm font-medium text-primary-600">Security Dashboard</p>
          <h2 className="text-xl font-semibold">Enterprise Identity & Access Management</h2>
        </div>

        <DashboardGrid>
          {metrics.map((m) => (
            <KPIWidget
              key={m.label}
              title={m.label}
              value={String(m.value)}
              trend="up"
              change=""
            />
          ))}
        </DashboardGrid>

        {data?.charts ? (
          <div className="rounded-md border p-4">
            <h3 className="font-semibold mb-2">Charts</h3>
            <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(data.charts, null, 2)}</pre>
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}

