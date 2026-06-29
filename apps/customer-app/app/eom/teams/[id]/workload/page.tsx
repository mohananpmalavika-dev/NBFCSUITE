"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function TeamWorkloadPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const [team, setTeam] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [wlRes, teamRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}/workload`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
        ]);
        if (wlRes.ok) { const body = await wlRes.json(); if (mounted) setData(body); }
        if (teamRes.ok) { const body = await teamRes.json(); if (mounted) setTeam(body); }
      } finally { if (mounted) setLoading(false); }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!team) return <AppShell><div className="p-4 text-sm text-text-secondary">Team not found.</div></AppShell>;

  const metrics = [
    { label: 'Assigned Tasks', value: data?.assigned_tasks ?? 0, color: 'bg-blue-500' },
    { label: 'Completed', value: data?.completed ?? 0, color: 'bg-green-500' },
    { label: 'Pending', value: data?.pending ?? 0, color: 'bg-yellow-500' },
    { label: 'Overdue', value: data?.overdue ?? 0, color: 'bg-red-500' },
    { label: 'Average SLA', value: `${data?.average_sla ?? 0}%`, color: 'bg-purple-500' },
    { label: 'Productivity', value: `${data?.productivity ?? 0}%`, color: 'bg-indigo-500' },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Team Workload</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code}</p>
          </div>
          <Link href={`/eom/teams/${params.id}`} className="btn">Back to Team</Link>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {metrics.map((m) => (
            <div key={m.label} className="rounded-md border p-4 space-y-2">
              <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${m.color}`} />
                <span className="text-sm font-medium text-text-secondary">{m.label}</span>
              </div>
              <div className="text-2xl font-bold">{m.value}</div>
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
