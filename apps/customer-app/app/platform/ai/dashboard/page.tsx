"use client";

import { useEffect, useState } from 'react';
import { AppShell } from '../../../components/AppShell';
import { aiApi, DEFAULT_AI_TENANT } from '../aiApi';

export default function AiDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await aiApi.dashboard(DEFAULT_AI_TENANT);
        setData(res);
      } catch (e) {
        setData(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <AppShell>
      <div className="space-y-6 p-6">
        <div className="rounded-md border border-border-default bg-background-surface p-6">
          <div className="text-sm font-semibold uppercase tracking-wide text-accent-primary">AI Platform</div>
          <h1 className="mt-2 text-2xl font-semibold text-text-primary">AI Dashboard</h1>
        </div>
        {loading ? (
          <div className="rounded-md border border-border-default bg-background-default p-6">Loading…</div>
        ) : (
          <div className="grid gap-4 lg:grid-cols-3">
            <div className="rounded-md border border-border-default bg-background-surface p-4">Status: {data?.status ?? 'unknown'}</div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">Requests last hour: {data?.requests_last_hour ?? 0}</div>
            <div className="rounded-md border border-border-default bg-background-surface p-4">Models: {data?.models ?? 0}</div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
