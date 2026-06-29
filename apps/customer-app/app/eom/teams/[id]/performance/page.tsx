"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function TeamPerformancePage() {
  const params = useParams<{ id: string }>();
  const [health, setHealth] = useState<any>(null);
  const [kpis, setKpis] = useState<any[]>([]);
  const [team, setTeam] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [hlRes, kpiRes, teamRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}/health`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}/kpis`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
        ]);
        if (hlRes.ok) { const body = await hlRes.json(); if (mounted) setHealth(body); }
        if (kpiRes.ok) { const body = await kpiRes.json(); if (mounted) setKpis(body.items || []); }
        if (teamRes.ok) { const body = await teamRes.json(); if (mounted) setTeam(body); }
      } finally { if (mounted) setLoading(false); }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!team) return <AppShell><div className="p-4 text-sm text-text-secondary">Team not found.</div></AppShell>;

  const hlDims = health ? [
    { label: 'Productivity', value: health.productivity ?? 0 },
    { label: 'SLA Compliance', value: health.sla_compliance ?? 0 },
    { label: 'Employee Satisfaction', value: health.employee_satisfaction ?? 0 },
    { label: 'Capacity Utilization', value: health.capacity_utilization ?? 0 },
    { label: 'Project Delivery', value: health.project_delivery ?? 0 },
  ] : [];

  const barColor = (v: number) => {
    if (v >= 80) return 'bg-green-500';
    if (v >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const scoreColor = (health?.score ?? 0) >= 80 ? 'text-green-600' : (health?.score ?? 0) >= 60 ? 'text-yellow-600' : 'text-red-600';

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Team Performance</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code}</p>
          </div>
          <Link href={`/eom/teams/${params.id}`} className="btn">Back to Team</Link>
        </div>

        {/* Health Score Summary */}
        {health && (
          <div className="rounded-md border p-4 flex items-center gap-6">
            <div className="text-center">
              <div className={`text-3xl font-bold ${scoreColor}`}>{Math.round(health.score ?? 0)}%</div>
              <div className="text-sm text-text-secondary">Health Score</div>
            </div>
            <div className="flex-1 grid gap-3 sm:grid-cols-2">
              {hlDims.map((d) => (
                <div key={d.label} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-medium">{d.label}</span>
                    <span>{Math.round(d.value)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className={`h-2 rounded-full ${barColor(d.value)}`} style={{ width: `${Math.min(100, d.value)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* KPIs Table */}
        <section className="rounded-md border p-4 space-y-3">
          <h3 className="font-semibold">Key Performance Indicators</h3>
          {kpis.length === 0 ? (
            <p className="text-sm text-text-secondary">No KPIs recorded yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left">
                    <th className="p-2 font-medium">KPI Name</th>
                    <th className="p-2 font-medium">Target</th>
                    <th className="p-2 font-medium">Actual</th>
                    <th className="p-2 font-medium">Unit</th>
                    <th className="p-2 font-medium">Period</th>
                  </tr>
                </thead>
                <tbody>
                  {kpis.map((k: any) => (
                    <tr key={k.id} className="border-t hover:bg-gray-50">
                      <td className="p-2 font-medium">{k.kpi_name}</td>
                      <td className="p-2">{k.target ?? '—'}</td>
                      <td className={`p-2 font-semibold ${(k.actual ?? 0) >= (k.target ?? 0) ? 'text-green-600' : 'text-yellow-600'}`}>
                        {k.actual ?? '—'}
                      </td>
                      <td className="p-2">{k.unit || '—'}</td>
                      <td className="p-2">{k.period || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <Link href={`/eom/teams/${params.id}/kpis`} className="text-sm text-primary-600 hover:underline">Manage KPIs →</Link>
        </section>
      </div>
    </AppShell>
  );
}
