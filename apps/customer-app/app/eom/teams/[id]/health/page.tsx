"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { eomApiUrl } from '../../../eomApi';

export default function TeamHealthPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const [team, setTeam] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params?.id) return;
    let mounted = true;
    (async () => {
      try {
        const [hlRes, teamRes] = await Promise.all([
          fetch(eomApiUrl(`/eom/teams/${params.id}/health`)),
          fetch(eomApiUrl(`/eom/teams/${params.id}`)),
        ]);
        if (hlRes.ok) { const body = await hlRes.json(); if (mounted) setData(body); }
        if (teamRes.ok) { const body = await teamRes.json(); if (mounted) setTeam(body); }
      } finally { if (mounted) setLoading(false); }
    })();
    return () => { mounted = false; };
  }, [params?.id]);

  if (loading) return <AppShell><div className="p-4 text-sm text-text-secondary">Loading…</div></AppShell>;
  if (!team) return <AppShell><div className="p-4 text-sm text-text-secondary">Team not found.</div></AppShell>;

  const score = data?.score ?? 0;
  const rating = data?.rating || (score >= 85 ? '★★★★★' : score >= 70 ? '★★★★☆' : '★★★☆☆');

  const dimensions = [
    { label: 'Capacity Utilization', value: (data?.capacity_utilization ?? 0) },
    { label: 'Productivity', value: (data?.productivity ?? 0) },
    { label: 'SLA Compliance', value: (data?.sla_compliance ?? 0) },
    { label: 'Employee Satisfaction', value: (data?.employee_satisfaction ?? 0) },
    { label: 'Training Completion', value: (data?.training_completion ?? 0) },
    { label: 'Project Delivery', value: (data?.project_delivery ?? 0) },
    { label: 'Attrition (inverse)', value: (data?.attrition ?? 0), inverse: true },
    { label: 'Audit Findings (inverse)', value: (data?.audit_findings ?? 0), inverse: true },
  ];

  const barColor = (v: number, inverse?: boolean) => {
    const pct = inverse ? 100 - v : v;
    if (pct >= 80) return 'bg-green-500';
    if (pct >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary-600">Team Health</p>
            <h2 className="text-xl font-semibold">{team.name}</h2>
            <p className="text-sm text-text-secondary">{team.code}</p>
          </div>
          <Link href={`/eom/teams/${params.id}`} className="btn">Back to Team</Link>
        </div>

        <div className="rounded-md border p-6 text-center space-y-2">
          <div className={`text-5xl font-bold ${score >= 85 ? 'text-green-600' : score >= 70 ? 'text-yellow-600' : 'text-red-600'}`}>
            {Math.round(score)}%
          </div>
          <div className="text-xl">{rating}</div>
          <p className="text-sm text-text-secondary">Health Score</p>
        </div>

        <div className="rounded-md border p-4 space-y-4">
          <h3 className="font-semibold">Health Dimensions</h3>
          {dimensions.map((d) => {
            const pct = Math.min(100, d.inverse ? d.value : d.value);
            return (
              <div key={d.label} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{d.label}</span>
                  <span className="text-text-secondary">{Math.round(pct)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className={`h-3 rounded-full ${barColor(pct, d.inverse)}`} style={{ width: `${Math.min(100, pct)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AppShell>
  );
}
